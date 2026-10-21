"""Practice-test results from screenshots: ETS mini quiz, POWERPREP, Manhattan / Magoosh / Kaplan mocks, book sets…

Flow: upload one or more screenshots → offline OCR (Windows built-in engine, tracker/ocr.ps1) → the local Ollama
model turns the text into structured results (scores, per-section counts, per-question right/wrong, type, topic,
time) → you check and correct them in the app → save.

Saved results are then used everywhere: scaled scores go to the practice-test score list (Progress tab and the
predictor's "last practice test"), each question feeds the score predictor and per-topic weak spots, wrong
questions go to the Error log with a redo date, and the AI tutor sees your latest results.
"""
import datetime as dt
import json
import os
import re
import shutil
import subprocess


from . import db, gre, gre_course, gre_verbal

SCHEMA = """
CREATE TABLE IF NOT EXISTS gre_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, date TEXT, name TEXT, source TEXT, kind TEXT, day INTEGER,
    quant INTEGER, verbal INTEGER, awa REAL, images TEXT, ocr TEXT, questions TEXT, notes TEXT, draft INTEGER DEFAULT 1);
"""
DIR = os.path.join(db.DATA_DIR, 'results')
OCR_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr.ps1')
SOURCES = ['ETS', 'Manhattan Prep', 'Magoosh', 'Princeton Review', 'Kaplan', 'Barron\'s', 'GregMat', 'Book / other']
KINDS = ['Full practice test', 'Section', 'Quiz / question set']
QTYPES = ['QC', 'MC', 'MA', 'NE', 'DI', 'TC', 'SE', 'RC', 'CR']
VERBAL_TYPES = {'TC', 'SE', 'RC', 'CR'}
DIFF = {'easy': 1, 'medium': 2, 'hard': 3, 1: 1, 2: 2, 3: 3}
_ready = False


def ensure():
    global _ready
    if _ready:
        return
    gre.ensure()
    with db._lock:
        db.con().executescript(SCHEMA)
        db.con().commit()
    os.makedirs(DIR, exist_ok=True)
    _ready = True


def chapters():
    """Topic choices for a question: every quant and verbal chapter."""
    return ([{'key': c, 'title': gre_course.title(c), 'subject': 'quant'} for c in gre_course.CHAPTERS] +
            [{'key': c, 'title': gre_verbal.title(c), 'subject': 'verbal'} for c in gre_verbal.CHAPTERS])


# ---------------------------------------------------------------- OCR
OCR_WIDTHS = (0, 1400, 1800)  # passes at different sizes (0 = original size): each catches short tokens (times, numbers) the others miss


def _prepare(path, width):
    """Grey-scale, light background, enlarged - the Windows OCR engine reads small dark-mode screenshots badly.
    Returns (prepared file, scale factor from the original)."""
    from PIL import Image, ImageOps
    im = Image.open(path)
    im = ImageOps.exif_transpose(im).convert('L')
    if sum(im.resize((64, 64)).getdata()) / 4096 < 110:  # dark theme: invert to dark text on light
        im = ImageOps.invert(im)
    w, h = im.size
    scale = min(4.0, max(1.0, width / max(w, 1))) if width else 1.0
    if max(w, h) * scale > 9000:
        scale = 9000 / max(w, h)
    if abs(scale - 1) > 0.05:
        im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = f'{path}.ocr{width}.png'
    im.save(out)
    return out, scale


def _ocr_once(path, width):
    src, scale = _prepare(path, width)
    try:
        r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', OCR_SCRIPT, src],
                           capture_output=True, timeout=120, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        out = r.stdout.decode('utf-8', 'replace').strip()
        if r.returncode or not out:
            raise RuntimeError((r.stderr.decode('utf-8', 'replace') or 'OCR failed').strip()[:300])
        data = json.loads(out[out.index('{'):])
    finally:
        try:
            os.remove(src)
        except OSError:
            pass
    lines = data.get('lines') or []
    if isinstance(lines, dict):
        lines = [lines]
    # back to original-image coordinates so both passes line up
    return [{'text': l['text'], 'x': l['x'] / scale, 'y': l['y'] / scale, 'h': max(1, l.get('h') or 12) / scale} for l in lines]


def ocr(path):
    """Text of an image as rows, top to bottom (Windows.Media.Ocr via PowerShell - no internet, no extra install)."""
    lines = []
    for i, width in enumerate(OCR_WIDTHS):
        try:
            got = _ocr_once(path, width)
        except Exception:
            if i == 0:
                raise
            continue
        for l in got:  # keep a line from the second pass only if nothing sits at that spot already
            same_row = [k for k in lines if abs(l['y'] - k['y']) < k['h'] * 0.6]
            norm = re.sub(r'[^a-z0-9:]', '', l['text'].lower())
            if not any(abs(l['x'] - k['x']) < max(k['h'], 8) * 2 or (norm and norm in re.sub(r'[^a-z0-9:]', '', k['text'].lower())) for k in same_row):
                lines.append(l)
    # group lines into rows by vertical overlap (OCR returns one line per column of a table), then read left to right
    lines.sort(key=lambda l: l['y'])
    rows = []
    for l in lines:
        row = rows[-1] if rows else None
        if row and abs((l['y'] + l['h'] / 2) - row['mid']) < max(row['h'], l['h']) * 0.6:
            row['items'].append(l)
        else:
            rows.append({'mid': l['y'] + l['h'] / 2, 'h': l['h'], 'items': [l]})
    return '\n'.join('   '.join(i['text'] for i in sorted(r['items'], key=lambda i: i['x'])) for r in rows)


# ---------------------------------------------------------------- parsing
def _regex(text):
    """Scores the text states outright (works without the AI)."""
    out = {}
    t = text.replace('\n', ' ')
    m = re.search(r'(?:Quantitative(?: Reasoning)?|Quant)\D{0,40}?\b(1[3-6]\d|170)\b', t, re.I)
    if m:
        out['quant'] = int(m.group(1))
    m = re.search(r'Verbal(?: Reasoning)?\D{0,40}?\b(1[3-6]\d|170)\b', t, re.I)
    if m:
        out['verbal'] = int(m.group(1))
    m = re.search(r'(?:Analytical Writing|AWA)\D{0,40}?\b([0-6](?:\.[05])?)\b', t, re.I)
    if m:
        out['awa'] = float(m.group(1))
    return out


def _ai(text, hint):
    keys = ', '.join(f"{c['key']} ({c['title']})" for c in chapters())
    system = ('You read OCR text from screenshots of GRE practice-test result pages (ETS POWERPREP score reports, the ETS mini quiz, '
              'Magoosh, Manhattan Prep, Kaplan, Princeton Review…). OCR text can be garbled; never invent numbers that are not in the text. '
              'Reply ONLY with JSON: {"name": test name or null, "source": one of ' + json.dumps(SOURCES) + ' or null, '
              '"date": "YYYY-MM-DD" or null, "quant": scaled 130-170 or null, "verbal": scaled 130-170 or null, "awa": 0-6 or null, '
              '"sections": [{"section": "Quant" or "Verbal", "correct": int, "total": int}], '
              '"questions": [{"n": question number, "section": "Quant" or "Verbal", "type": one of ' + json.dumps(QTYPES) + ' or null, '
              '"chapter": the best matching topic key from the list or null, "correct": true/false/null, "seconds": int or null, '
              '"difficulty": "easy"/"medium"/"hard" or null}]}. Topic keys: ' + keys)
    raw = gre._ollama_json(system, f'{hint}\n\nOCR TEXT:\n{text[:12000]}', timeout=300)
    try:
        return json.loads(raw)
    except ValueError:
        m = re.search(r'\{.*\}', raw, re.S)
        return json.loads(m.group(0)) if m else {}


def _clean_q(q, i):
    sec = 'Verbal' if str(q.get('section', '')).lower().startswith('v') else 'Quant'
    typ = str(q.get('type') or '').upper()
    typ = typ if typ in QTYPES else ''
    if typ in VERBAL_TYPES:
        sec = 'Verbal'
    ch = q.get('chapter') if q.get('chapter') in {c['key'] for c in chapters()} else ''
    if ch:
        sec = 'Verbal' if ch in gre_verbal.LESSONS else 'Quant'
    corr = q.get('correct')
    corr = corr if isinstance(corr, bool) else (None if corr is None else str(corr).lower() in ('true', 'yes', 'correct', '1'))
    try:
        secs = int(q.get('seconds')) if q.get('seconds') not in (None, '') else None
    except (TypeError, ValueError):
        secs = None
    try:
        n = int(q.get('n') or i + 1)
    except (TypeError, ValueError):
        n = i + 1
    return {'n': n, 'section': sec, 'type': typ, 'chapter': ch, 'correct': corr, 'seconds': secs,
            'difficulty': DIFF.get(str(q.get('difficulty') or '').lower()) if q.get('difficulty') else None}


def _num(v, lo, hi, cast=int):
    try:
        v = cast(v)
        return v if lo <= v <= hi else None
    except (TypeError, ValueError):
        return None


def scan(files, name='', day=None, kind='', source=''):
    """Save the uploaded images, OCR them and propose structured results (a draft the user then checks)."""
    ensure()
    rid = db.execute('INSERT INTO gre_results(created, name, day, kind, source, draft) VALUES (?,?,?,?,?,1)',
                     (dt.datetime.now().isoformat(timespec='seconds'), name, day, kind, source))
    folder = os.path.join(DIR, str(rid))
    os.makedirs(folder, exist_ok=True)
    images, texts, errors = [], [], []
    for i, f in enumerate(files):
        ext = os.path.splitext(f.filename or '')[1].lower()
        ext = ext if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp') else '.png'
        fn = f'{i + 1}{ext}'
        path = os.path.join(folder, fn)
        f.save(path)
        images.append(fn)
        try:
            texts.append(ocr(path))
        except Exception as e:
            errors.append(f'Screenshot {i + 1}: {e}')
    text = '\n\n'.join(texts)
    parsed, ai_error = {}, None
    if text.strip():
        try:
            parsed = _ai(text, f'The student says this is: {name or "a GRE practice test"}' + (f' ({source})' if source else ''))
        except Exception as e:
            ai_error = f'The local AI could not read the results ({e}). Fill them in below - the screenshots are saved.'
    rx = _regex(text)
    qs = [_clean_q(q, i) for i, q in enumerate(parsed.get('questions') or []) if isinstance(q, dict)]
    secs = []
    for s in parsed.get('sections') or []:
        if isinstance(s, dict) and _num(s.get('total'), 1, 100):
            secs.append({'section': 'Verbal' if str(s.get('section', '')).lower().startswith('v') else 'Quant',
                         'correct': _num(s.get('correct'), 0, 100) or 0, 'total': _num(s.get('total'), 1, 100)})
    draft = {
        'id': rid, 'images': images, 'ocr': text, 'errors': errors, 'ai_error': ai_error,
        'name': name or parsed.get('name') or '', 'source': source or (parsed.get('source') if parsed.get('source') in SOURCES else ''),
        'kind': kind, 'day': day, 'date': parsed.get('date') if re.match(r'^\d{4}-\d{2}-\d{2}$', str(parsed.get('date') or '')) else dt.date.today().isoformat(),
        'quant': rx.get('quant') or _num(parsed.get('quant'), 130, 170), 'verbal': rx.get('verbal') or _num(parsed.get('verbal'), 130, 170),
        'awa': rx.get('awa') if rx.get('awa') is not None else _num(parsed.get('awa'), 0, 6, float),
        'sections': secs, 'questions': qs,
    }
    db.execute('UPDATE gre_results SET images=?, ocr=?, questions=?, date=? WHERE id=?', (json.dumps(images), text, json.dumps(qs), draft['date'], rid))
    return draft


def create_manual(name='', day=None, kind='', source=''):
    """A result typed in by hand (no screenshots)."""
    ensure()
    rid = db.execute('INSERT INTO gre_results(created, name, day, kind, source, images, draft) VALUES (?,?,?,?,?,?,1)',
                     (dt.datetime.now().isoformat(timespec='seconds'), name, day, kind, source, '[]'))
    return {'id': rid}


# ---------------------------------------------------------------- save / list / delete
def _source_tag(rid):
    return f'Test result #{rid}'


def save(rid, b):
    """Store the checked results and push them to the score list and Error log."""
    ensure()
    r = db.one('SELECT * FROM gre_results WHERE id=?', (rid,))
    if not r:
        return {'ok': False, 'error': 'not found'}
    qs = [_clean_q(q, i) for i, q in enumerate(b.get('questions') or [])]
    sections = b.get('sections') or []
    for s in ('Quant', 'Verbal'):  # per-section counts from the question list when not given
        xs = [q for q in qs if q['section'] == s and q['correct'] is not None]
        if xs and not any(x.get('section') == s for x in sections):
            sections.append({'section': s, 'correct': sum(1 for q in xs if q['correct']), 'total': len(xs)})
    name = (b.get('name') or '').strip() or 'Practice test'
    date = b.get('date') or dt.date.today().isoformat()
    quant, verbal = _num(b.get('quant'), 130, 170), _num(b.get('verbal'), 130, 170)
    awa = _num(b.get('awa'), 0, 6, float)
    db.execute('UPDATE gre_results SET date=?, name=?, source=?, kind=?, day=?, quant=?, verbal=?, awa=?, questions=?, notes=?, draft=0 WHERE id=?',
               (date, name, b.get('source') or '', b.get('kind') or '', b.get('day'), quant, verbal, awa,
                json.dumps({'questions': qs, 'sections': sections}), b.get('notes') or '', rid))
    tag = _source_tag(rid)
    # scaled scores → the practice-test score list (one row per result)
    db.execute('DELETE FROM gre_scores WHERE notes=?', (tag,))
    if quant or verbal or awa is not None:
        db.execute('INSERT INTO gre_scores(date,name,quant,verbal,awa,notes) VALUES (?,?,?,?,?,?)', (date, name, quant, verbal, awa, tag))
    # wrong questions → Error log (re-saving replaces the open ones from this result)
    db.execute("DELETE FROM gre_errors WHERE source LIKE ? AND status='Open'", (tag + ':%',))
    have = {row['question'] for row in db.query('SELECT question FROM gre_errors WHERE source LIKE ?', (tag + ':%',))}
    added = 0
    for q in qs:
        if q['correct'] is not False:
            continue
        ch = q['chapter']
        topic = (gre.mod_for(ch).title(ch) if ch else f"{q['section']}{' · ' + q['type'] if q['type'] else ''}")
        question = f"Question {q['n']} of {name}{' (' + q['type'] + ')' if q['type'] else ''} - redo it from the test's review screen"
        if question in have:  # already fixed earlier
            continue
        slow = q['seconds'] and q['seconds'] > (gre.slow_limit(ch) if ch else (120 if q['section'] == 'Quant' else 90))
        gre.add_error(b.get('day'), topic, f'{tag}: {name}', question, 'Marked wrong in your uploaded result', '',
                      kind='Timing' if slow else 'Unsorted', secs=q['seconds'], created=date)
        added += 1
    return {'ok': True, 'id': rid, 'errors_added': added}


def _row(r):
    d = json.loads(r['questions'] or '{}')
    if isinstance(d, list):
        d = {'questions': d, 'sections': []}
    qs = d.get('questions', [])
    out = {k: r[k] for k in ('id', 'created', 'date', 'name', 'source', 'kind', 'day', 'quant', 'verbal', 'awa', 'notes')}
    out.update(images=json.loads(r['images'] or '[]'), questions=qs, sections=d.get('sections', []))
    for s in ('Quant', 'Verbal'):
        sec = [x for x in out['sections'] if x.get('section') == s]
        out[s.lower() + '_acc'] = f"{sec[0]['correct']}/{sec[0]['total']}" if sec else None
    return out


def listing():
    ensure()
    db.execute("DELETE FROM gre_results WHERE draft=1 AND created < ?", ((dt.datetime.now() - dt.timedelta(days=2)).isoformat(),))
    return [_row(r) for r in db.query('SELECT * FROM gre_results WHERE draft=0 ORDER BY date DESC, id DESC')]


def get(rid):
    ensure()
    r = db.one('SELECT * FROM gre_results WHERE id=?', (rid,))
    return {**_row(r), 'ocr': r['ocr'], 'draft': bool(r['draft'])} if r else None


def delete(rid):
    ensure()
    tag = _source_tag(rid)
    db.execute('DELETE FROM gre_scores WHERE notes=?', (tag,))
    db.execute("DELETE FROM gre_errors WHERE source LIKE ? AND status='Open'", (tag + ':%',))
    db.execute('DELETE FROM gre_results WHERE id=?', (rid,))
    shutil.rmtree(os.path.join(DIR, str(int(rid))), ignore_errors=True)
    return {'ok': True}


def image_path(rid, name):
    if not re.match(r'^\d+\.(png|jpe?g|bmp|gif|webp)$', name):
        return None
    p = os.path.join(DIR, str(int(rid)), name)
    return p if os.path.exists(p) else None


# ---------------------------------------------------------------- used by the predictor, weak spots and the tutor
def observations(subject, since):
    """(difficulty, correct, weight) per question from saved results - official ETS questions weigh more."""
    ensure()
    sec = 'Quant' if subject == 'quant' else 'Verbal'
    out = []
    for r in db.query('SELECT source, date, questions FROM gre_results WHERE draft=0 AND date >= ?', (since,)):
        w = 1.5 if (r['source'] or '') == 'ETS' else 1.0
        d = json.loads(r['questions'] or '{}')
        for q in (d.get('questions', []) if isinstance(d, dict) else d):
            if q.get('section') == sec and q.get('correct') is not None:
                out.append((q.get('difficulty') or 2, 1 if q['correct'] else 0, w, q.get('seconds')))
    return out


def topic_stats():
    """Accuracy per chapter from saved results (only questions tagged with a topic)."""
    ensure()
    st = {}
    for r in db.query('SELECT questions FROM gre_results WHERE draft=0'):
        d = json.loads(r['questions'] or '{}')
        for q in (d.get('questions', []) if isinstance(d, dict) else d):
            if q.get('chapter') and q.get('correct') is not None:
                x = st.setdefault(q['chapter'], [0, 0])
                x[0] += 1 if q['correct'] else 0
                x[1] += 1
    return {ch: {'correct': c, 'total': n, 'pct': round(100 * c / n), 'title': gre.mod_for(ch).title(ch), 'subject': gre.subject_of(ch)}
            for ch, (c, n) in st.items()}


def weak_topics(subject=None, limit=6):
    rows = [dict(chapter=k, **v) for k, v in topic_stats().items() if v['total'] >= 2 and v['pct'] < 70 and (subject is None or v['subject'] == subject)]
    return sorted(rows, key=lambda r: (r['pct'], -r['total']))[:limit]


def tutor_summary():
    """A few lines about recent results for the AI tutor's system prompt."""
    try:
        rs = listing()[:3]
    except Exception:
        return ''
    if not rs:
        return ''
    lines = ['\nRECENT PRACTICE-TEST RESULTS (uploaded by the student):']
    for r in rs:
        bits = [f"Q {r['quant']}" if r['quant'] else '', f"V {r['verbal']}" if r['verbal'] else '', f"AWA {r['awa']}" if r['awa'] is not None else '',
                f"Quant {r['quant_acc']} right" if r['quant_acc'] else '', f"Verbal {r['verbal_acc']} right" if r['verbal_acc'] else '']
        lines.append(f"- {r['date']} {r['name']}: " + ', '.join(b for b in bits if b))
    weak = weak_topics()
    if weak:
        lines.append('Weak topics in those tests: ' + ', '.join(f"{w['title']} ({w['correct']}/{w['total']})" for w in weak))
    return '\n'.join(lines) + '\nUse this to focus your explanations and extra questions on these weaknesses.'


