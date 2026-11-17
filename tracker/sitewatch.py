"""Watch each programme's official web pages and tell you when their content changes.

How it works
- Every programme has up to four official pages (programme, admissions/deadlines, funding, international students);
  the URLs live in tracker/official_pages.py and are copied into the `watch_pages` table at startup.
- check_due() fetches pages whose last check is older than the interval (default 12 h; at startup too), extracts the
  main text (only <main>/<article> when the page has one; never <nav>/<header>/<footer>/scripts/forms/cookie banners),
  removes noise (timestamps, "last updated" lines, copyright, session/tracking tokens) and hashes what is left.
- When the hash differs from the stored one, the added/removed lines are saved in `watch_changes` and you get a
  Windows toast with an "Open page" button plus an unread badge in the app ("Site updates").
- The first fetch of a page only stores a baseline (no notification). A page that keeps failing (404, blocked,
  moved) is reported once after 3 failures in a row, so you can update the link.
Dates inside sentences (e.g. "Deadline: 15 January 2027") are kept on purpose - a changed deadline is a change you
want to see. Only stand-alone date stamps and "updated on ..." lines are ignored.
"""
import datetime as dt
import difflib
import gzip
import hashlib
import html
import re
import threading
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

from . import db, notify

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0 Safari/537.36 MastersTracker/1.0 (personal page-change checker)')
KINDS = {'programme': 'Programme page', 'admissions': 'Admissions & deadlines', 'funding': 'Funding & scholarships',
         'international': 'International students'}
DEFAULT_HOURS = 12
FAIL_ALERT = 3

SCHEMA = """
CREATE TABLE IF NOT EXISTS watch_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, program_id TEXT, kind TEXT, url TEXT, label TEXT, active INTEGER DEFAULT 1,
    last_checked TEXT, last_ok TEXT, last_status TEXT, hash TEXT, text_gz BLOB, chars INTEGER, fails INTEGER DEFAULT 0,
    fail_alerted INTEGER DEFAULT 0, UNIQUE(program_id, kind));
CREATE TABLE IF NOT EXISTS watch_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, page_id INTEGER, program_id TEXT, kind TEXT, url TEXT, at TEXT,
    summary TEXT, added TEXT, removed TEXT, seen INTEGER DEFAULT 0, change_type TEXT DEFAULT 'content');
"""

_SKIP = {'script', 'style', 'noscript', 'svg', 'nav', 'header', 'footer', 'form', 'iframe', 'template', 'button',
         'select', 'aside', 'dialog', 'canvas', 'picture', 'video', 'audio', 'object'}
_BLOCK = {'p', 'div', 'li', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'section', 'article', 'main',
          'dd', 'dt', 'table', 'ul', 'ol', 'blockquote', 'summary', 'details', 'figcaption', 'caption', 'hr'}
_VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'source', 'wbr', 'area', 'base', 'col', 'embed', 'param', 'track'}
# class/id tokens that mark page furniture (whole token or token prefix, so "has-header" on a wrapper is not hit)
_NOISE_ATTR = re.compile(r'(^|\s)(cookie|consent|gdpr|breadcrumbs?|skip-?link|share|sharing|social|newsletter|subscribe|'
                         r'menu|mega-?menu|navbar|nav|site-nav|sidebar|footer|site-footer|header|site-header|global-header|'
                         r'modal|popup|alert-bar|chat|feedback|offcanvas|news|latest-news|events?|related|carousel|slider|testimonials?|ticker)([-_][\w-]*)?(?=\s|$)', re.I)


class _Extract(HTMLParser):
    """Collects visible text; keeps <main>/<article>/[role=main] text separately so we can prefer it."""

    def __init__(self, use_attrs=True):
        super().__init__(convert_charrefs=True)
        self.use_attrs = use_attrs
        self.stack = []          # (tag, skip, is_main)
        self.all, self.main = [], []
        self.title = ''
        self._in_title = False

    def _skip(self):
        return any(s for _, s, _ in self.stack)

    def _main(self):
        return any(m for _, _, m in self.stack)

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self._in_title = True
        if tag in _VOID:
            if tag in _BLOCK:
                self._nl()
            return
        a = dict(attrs)
        hint = ' '.join(str(a.get(k) or '') for k in ('id', 'class', 'role', 'aria-label'))
        skip = tag in _SKIP or a.get('aria-hidden') == 'true' or a.get('hidden') is not None or \
            (self.use_attrs and bool(_NOISE_ATTR.search(hint)) and tag not in ('main', 'article', 'body', 'html'))
        if a.get('role') in ('navigation', 'banner', 'contentinfo', 'search', 'dialog'):
            skip = True
        is_main = tag in ('main', 'article') or a.get('role') == 'main' or a.get('id') in ('main', 'main-content', 'content')
        self.stack.append((tag, skip, is_main))
        if tag in _BLOCK:
            self._nl()

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
        for i in range(len(self.stack) - 1, -1, -1):  # tolerate unclosed tags
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag in _BLOCK:
            self._nl()

    def _nl(self):
        self.all.append('\n')
        self.main.append('\n')

    def handle_data(self, data):
        if self._in_title:
            self.title += data
            return
        if self._skip():
            return
        self.all.append(data)
        if self._main():
            self.main.append(data)


_TIME = re.compile(r'\b\d{1,2}:\d{2}(:\d{2})?\s*(am|pm|a\.m\.|p\.m\.)?(\s*[A-Z]{2,4})?\b', re.I)
_MONTH = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?'
_DATE_ONLY = re.compile(r'^\W*(\d{1,2}(st|nd|rd|th)?\s+' + _MONTH + r',?\s+\d{4}|' + _MONTH + r'\s+\d{1,2}(st|nd|rd|th)?,?\s+\d{4}|'
                        r'\d{4}-\d{2}-\d{2}|\d{1,2}[/.]\d{1,2}[/.]\d{2,4})\W*$', re.I)
_NOISE_LINE = re.compile(r'(last\s+(updated|modified|reviewed|edited)|page\s+(updated|reviewed)|updated\s+on|published\s+on|'
                         r'posted\s+on|©|copyright|all rights reserved|cookie|javascript|you are using an outdated|'
                         r'skip to (main )?content|back to top|share (this|on)|print this page|'
                         r'\bviews?\b\s*:?\s*\d+$|^\d+\s+(views|comments)$)', re.I)
_TOKENS = re.compile(r'\b[0-9a-f]{16,}\b|\b[A-Za-z0-9_-]{32,}\b|utm_[a-z]+=\S+|[?&](fbclid|gclid|sid|session)=\S+', re.I)


def _is_today_stamp(ln):
    """A stand-alone date that is today/yesterday/tomorrow is a page-generation stamp, not content.
    Other stand-alone dates are kept: in deadline tables the dates sit in their own cells."""
    d = dt.date.today()
    for k in (-1, 0, 1):
        x = d + dt.timedelta(days=k)
        for f in ('%d %B %Y', '%d %b %Y', '%B %d, %Y', '%b %d, %Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y'):
            if x.strftime(f).lower().lstrip('0') in ln.lower().replace(' 0', ' ').lstrip('0'):
                return True
    return False


def _parse(raw_html, use_attrs):
    p = _Extract(use_attrs)
    try:
        p.feed(raw_html)
        p.close()
    except Exception:
        pass
    main = ''.join(p.main)
    return p, (main if len(main.strip()) >= 400 else ''.join(p.all))


def clean_text(raw_html):
    p, text = _parse(raw_html, True)
    if len(text.strip()) < 300 and len(raw_html) > 20000:  # class-name heuristics hid everything: use tags only
        p, text = _parse(raw_html, False)
    lines = []
    seen = set()
    for ln in text.split('\n'):
        ln = html.unescape(ln)
        ln = _TOKENS.sub('', ln)
        ln = _TIME.sub('', ln)
        ln = re.sub(r'\s+', ' ', ln).strip()
        if len(ln) < 3 or _NOISE_LINE.search(ln) or (_DATE_ONLY.match(ln) and _is_today_stamp(ln)):
            continue
        if ln in seen and len(ln) > 40:  # repeated blocks (carousels, duplicated menus); short cells like dates repeat legitimately
            continue
        seen.add(ln)
        lines.append(ln)
    return re.sub(r'\s+', ' ', p.title).strip(), '\n'.join(lines)


# Set by main.py when the desktop window is running: fn(url) -> (final_url, html) or None. Used for sites that refuse
# scripted requests (HTTP 403 / bot check) - a hidden window of the app's own browser engine reads them instead.
browser_fetch = None


def fetch(url, timeout=25):
    """(status, final_url, title, text). status is 'ok' or an error string."""
    r = _fetch_direct(url, timeout)
    if browser_fetch and (r[0] in ('HTTP 403', 'HTTP 429', 'HTTP 503') or r[0].startswith('blocked')):
        got = None
        for _attempt in range(2):  # the first hidden window after start-up can be slow to load
            try:
                got = browser_fetch(url)
            except Exception as e:
                print('browser fetch failed:', url, e)
            if got and got[1]:
                break
        if got and got[1]:
            st, final, title, text = _finish(got[1].encode('utf-8'), 'text/html', 'utf-8', got[0] or url)
            if st == 'ok':
                return 'ok', final, title, text
            return st + ' (app browser too)', final, title, text
    return r


def _fetch_direct(url, timeout):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
                                               'Accept-Language': 'en-GB,en;q=0.9', 'Accept-Encoding': 'gzip'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read(6_000_000)
            if r.headers.get('Content-Encoding') == 'gzip':
                data = gzip.decompress(data)
            ctype = r.headers.get('Content-Type', '')
            enc = r.headers.get_content_charset() or 'utf-8'
            final = r.geturl()
    except urllib.error.HTTPError as e:
        return f'HTTP {e.code}', url, '', ''
    except Exception as e:
        if 'CERTIFICATE_VERIFY_FAILED' in str(e):  # server omits an intermediate cert: Windows curl (Schannel) fetches it
            return _fetch_curl(url, timeout)
        return f'error: {type(e).__name__}: {str(e)[:120]}', url, '', ''
    return _finish(data, ctype, enc, final)


def _fetch_curl(url, timeout):
    import os
    import subprocess
    import tempfile
    exe = os.path.join(os.environ.get('SystemRoot', r'C:\Windows'), 'System32', 'curl.exe')
    if not os.path.exists(exe):
        return 'error: certificate check failed', url, '', ''
    fd, path = tempfile.mkstemp(suffix='.html')
    os.close(fd)
    try:
        r = subprocess.run([exe, '-sSL', '--compressed', '--max-time', str(timeout), '-A', UA, '-o', path,
                            '-w', '%{http_code}\\t%{content_type}\\t%{url_effective}', url],
                           capture_output=True, text=True, timeout=timeout + 10, creationflags=0x08000000)
        parts = (r.stdout or '').split('\t', 2)
        if r.returncode or len(parts) < 3:
            return f'error: curl {r.returncode} {r.stderr.strip()[:100]}', url, '', ''
        code, ctype, final = parts
        if not code.startswith('2'):
            return f'HTTP {code}', url, '', ''
        with open(path, 'rb') as f:
            data = f.read(6_000_000)
        m = re.search(r'charset=([\w-]+)', ctype)
        return _finish(data, ctype, m.group(1) if m else 'utf-8', final)
    except Exception as e:
        return f'error: curl {type(e).__name__}', url, '', ''
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _finish(data, ctype, enc, final):
    if 'pdf' in ctype:
        return 'ok', final, '(PDF)', hashlib.sha256(data).hexdigest()
    raw = data.decode(enc, errors='replace')
    title, text = clean_text(raw)
    if len(text) < 200 and re.search(r'just a moment|access denied|cf-chl|captcha|are you a robot|_Incapsula_|Request unsuccessful', raw, re.I):
        return 'blocked (bot check)', final, title, ''
    return 'ok', final, title, text


def _ensure_schema():
    with db._lock:
        db.con().executescript(SCHEMA)
        db.con().commit()


def sync_pages():
    """Copy the URL list from official_pages.py into the DB (adds new ones, updates changed URLs)."""
    from .official_pages import NOT_FETCHABLE, PAGES
    _ensure_schema()
    for pid, kinds in PAGES.items():
        for kind, url in kinds.items():
            if not url:
                continue
            row = db.one('SELECT id, url FROM watch_pages WHERE program_id=? AND kind=?', (pid, kind))
            if not row:
                db.execute('INSERT INTO watch_pages(program_id, kind, url, label) VALUES (?,?,?,?)', (pid, kind, url, KINDS[kind]))
            elif row['url'] != url:  # link fixed in code: start a fresh baseline
                db.execute('UPDATE watch_pages SET url=?, hash=NULL, text_gz=NULL, fails=0, fail_alerted=0 WHERE id=?', (url, row['id']))
            if pid in NOT_FETCHABLE:
                db.execute("UPDATE watch_pages SET active=0, last_status='Not checked automatically: the site shows a CAPTCHA. Open it by hand.' "
                           'WHERE program_id=? AND kind=?', (pid, kind))


def _diff(old, new):
    o, n = old.split('\n'), new.split('\n')
    sm = difflib.SequenceMatcher(None, o, n, autojunk=False)
    added, removed = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ('replace', 'delete'):
            removed += o[i1:i2]
        if tag in ('replace', 'insert'):
            added += n[j1:j2]
    return added, removed


def _summary(added, removed):
    def pick(lines):  # most informative lines first: ones with numbers/dates/money
        return sorted(lines, key=lambda s: (not re.search(r'\d|\$|£|€|deadline|scholar|fund|fee|tuition', s, re.I), -len(s)))
    parts = []
    if added:
        parts.append('New: ' + ' | '.join(x[:110] for x in pick(added)[:2]))
    if removed:
        parts.append('Removed: ' + ' | '.join(x[:110] for x in pick(removed)[:1]))
    return f'{len(added)} line(s) added, {len(removed)} removed. ' + ' '.join(parts)


def _program_name(pid):
    p = db.one('SELECT short_name FROM programs WHERE id=?', (pid,))
    return p['short_name'] if p else pid


def toast_change(pid, label, summary, url):
    if db.get_setting('notifications') == '0' or db.get_setting('watch_notify') == '0':
        return
    notify.toast(f'{_program_name(pid)}: {label} changed', summary[:230], url=url, button='Open page')


def check_page(page, alert=True):
    """Fetch one page, compare with the stored text, record a change. Returns 'new'|'same'|'changed'|'fail'."""
    now = dt.datetime.now().isoformat(timespec='seconds')
    status, final, title, text = fetch(page['url'])
    if status != 'ok' or len(text) < 80:
        fails = (page['fails'] or 0) + 1
        st = status if status != 'ok' else 'ok but almost no text (page built by JavaScript?)'
        db.execute('UPDATE watch_pages SET last_checked=?, last_status=?, fails=? WHERE id=?', (now, st, fails, page['id']))
        if status != 'ok' and fails >= FAIL_ALERT and not page['fail_alerted']:
            db.execute('UPDATE watch_pages SET fail_alerted=1 WHERE id=?', (page['id'],))
            msg = f'Could not load this page {fails} times in a row ({st}). It may have moved - open it and update the link.'
            db.execute('INSERT INTO watch_changes(page_id, program_id, kind, url, at, summary, added, removed, change_type) '
                       'VALUES (?,?,?,?,?,?,?,?,?)', (page['id'], page['program_id'], page['kind'], page['url'], now, msg, '', '', 'error'))
            if alert:
                toast_change(page['program_id'], page['label'], msg, page['url'])
        return 'fail'
    h = hashlib.sha256(text.encode('utf-8')).hexdigest()
    gz = gzip.compress(text.encode('utf-8'))
    if not page['hash']:
        db.execute('UPDATE watch_pages SET last_checked=?, last_ok=?, last_status=?, hash=?, text_gz=?, chars=?, fails=0, '
                   'fail_alerted=0 WHERE id=?', (now, now, 'ok (baseline saved)', h, gz, len(text), page['id']))
        return 'new'
    if h == page['hash']:
        db.execute("UPDATE watch_pages SET last_checked=?, last_ok=?, last_status='ok - no change', fails=0, fail_alerted=0 WHERE id=?",
                   (now, now, page['id']))
        return 'same'
    old = gzip.decompress(page['text_gz']).decode('utf-8') if page['text_gz'] else ''
    added, removed = _diff(old, text)
    # tiny churn (a rotating news headline, an event teaser) is still recorded but not toasted
    meaningful = sum(len(x) for x in added + removed) >= 40 or         any(re.search(r'\d{4}|\d+\s*(%|k)|[$£€]|deadline|round|scholar|fee|tuition', x, re.I) for x in added + removed)
    summary = _summary(added, removed)
    db.execute('UPDATE watch_pages SET last_checked=?, last_ok=?, last_status=?, hash=?, text_gz=?, chars=?, fails=0, fail_alerted=0 '
               'WHERE id=?', (now, now, 'ok - CHANGED', h, gz, len(text), page['id']))
    db.execute('INSERT INTO watch_changes(page_id, program_id, kind, url, at, summary, added, removed, seen, change_type) '
               'VALUES (?,?,?,?,?,?,?,?,?,?)',
               (page['id'], page['program_id'], page['kind'], final or page['url'], now, summary,
                '\n'.join(added[:200]), '\n'.join(removed[:200]), 0 if meaningful else 1, 'content' if meaningful else 'minor'))
    if alert and meaningful:
        toast_change(page['program_id'], page['label'], summary, final or page['url'])
    return 'changed'


_running = threading.Lock()


def check_due(force=False, program_id=None, alert=True, pause=2.0):
    """Check every active page whose last check is older than the interval. Safe to call from several threads."""
    if not _running.acquire(blocking=False):
        return {'busy': True}
    try:
        _ensure_schema()
        hours = float(db.get_setting('watch_hours') or DEFAULT_HOURS)
        cutoff = (dt.datetime.now() - dt.timedelta(hours=hours)).isoformat(timespec='seconds')
        sql = 'SELECT * FROM watch_pages WHERE active=1'
        args = []
        if program_id:
            sql += ' AND program_id=?'
            args.append(program_id)
        if not force:
            sql += ' AND (last_checked IS NULL OR last_checked < ?)'
            args.append(cutoff)
        counts = {}
        changed = []
        for page in db.query(sql + ' ORDER BY last_checked IS NOT NULL, last_checked', args):
            r = check_page(page, alert=alert)
            counts[r] = counts.get(r, 0) + 1
            if r == 'changed':
                changed.append(page['program_id'])
            time.sleep(pause)
        return {'counts': counts, 'changed': changed}
    finally:
        _running.release()


def start_background(stop_event, first_delay=90):
    """Startup check (after a short delay so the app opens fast), then every 30 min look for pages that are due."""
    def run():
        try:
            sync_pages()
        except Exception as e:
            print('watch sync failed:', e)
        if stop_event.wait(first_delay):
            return
        while not stop_event.is_set():
            if db.get_setting('watch_enabled') != '0':
                try:
                    check_due()
                except Exception as e:
                    print('site watch error:', e)
            stop_event.wait(1800)
    threading.Thread(target=run, daemon=True).start()


# ---------------------------------------------------------------- API helpers
def pages_for(pid):
    _ensure_schema()
    rows = db.query('SELECT id, program_id, kind, url, label, active, last_checked, last_ok, last_status, chars, fails FROM watch_pages '
                    "WHERE program_id=? ORDER BY CASE kind WHEN 'programme' THEN 0 WHEN 'admissions' THEN 1 "
                    "WHEN 'funding' THEN 2 ELSE 3 END", (pid,))
    return rows


def changes(pid=None, unseen_only=False, limit=200):
    _ensure_schema()
    sql = ('SELECT c.*, p.short_name FROM watch_changes c LEFT JOIN programs p ON p.id=c.program_id WHERE 1=1')
    args = []
    if pid:
        sql += ' AND c.program_id=?'
        args.append(pid)
    if unseen_only:
        sql += ' AND c.seen=0'
    sql += ' ORDER BY c.id DESC LIMIT ?'
    args.append(limit)
    out = db.query(sql, args)
    for c in out:
        c['label'] = KINDS.get(c['kind'], c['kind'])
    return out


def unseen_count():
    _ensure_schema()
    return db.one('SELECT COUNT(*) AS n FROM watch_changes WHERE seen=0')['n']


def mark_seen(change_id=None, pid=None):
    if change_id:
        db.execute('UPDATE watch_changes SET seen=1 WHERE id=?', (change_id,))
    elif pid:
        db.execute('UPDATE watch_changes SET seen=1 WHERE program_id=?', (pid,))
    else:
        db.execute('UPDATE watch_changes SET seen=1')
