"""GRE prep: schedule, daily class, quizzes, vocab spaced repetition, error log, essays, scores,
the quant and verbal tutor courses, score prediction and pacing analysis."""
import datetime as dt
import json
import math
import random
import re
import urllib.request
from collections import Counter

from . import db, gre_course, gre_notes, gre_plan, gre_quiz, gre_verbal, gre_vocab

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
BOX_DAYS = {1: 0, 2: 1, 3: 3, 4: 7, 5: 15}  # Leitner: days until a word in this box is due again
SUBJECTS = {'quant': gre_course, 'verbal': gre_verbal}

SCHEMA = """
CREATE TABLE IF NOT EXISTS gre_progress (
    day INTEGER PRIMARY KEY, done INTEGER DEFAULT 0, done_on TEXT, minutes INTEGER, notes TEXT, parts TEXT);
CREATE TABLE IF NOT EXISTS gre_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT, day INTEGER, at TEXT, score INTEGER, total INTEGER, topics TEXT);
CREATE TABLE IF NOT EXISTS gre_vocab (
    word TEXT PRIMARY KEY, box INTEGER DEFAULT 1, due TEXT, seen INTEGER DEFAULT 0, correct INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS gre_cards (
    id TEXT PRIMARY KEY, box INTEGER DEFAULT 1, due TEXT, seen INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, first_seen TEXT);
CREATE TABLE IF NOT EXISTS gre_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT, kind TEXT, ref TEXT, text TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS gre_vocab_queue (
    word TEXT PRIMARY KEY, added TEXT, hits INTEGER DEFAULT 0, misses INTEGER DEFAULT 0, last TEXT, cleared TEXT);
CREATE TABLE IF NOT EXISTS gre_errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT, day INTEGER, topic TEXT, source TEXT, question TEXT,
    answer TEXT, note TEXT, status TEXT DEFAULT 'Open');
CREATE TABLE IF NOT EXISTS gre_essays (
    id INTEGER PRIMARY KEY AUTOINCREMENT, day INTEGER, at TEXT, prompt TEXT, body TEXT, words INTEGER,
    minutes REAL, self_score REAL);
CREATE TABLE IF NOT EXISTS gre_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, name TEXT, quant INTEGER, verbal INTEGER, awa REAL, notes TEXT);
CREATE TABLE IF NOT EXISTS gre_lessons (chapter TEXT PRIMARY KEY, done TEXT, finished_on TEXT);
CREATE TABLE IF NOT EXISTS gre_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, key TEXT, title TEXT, at TEXT, score INTEGER, total INTEGER,
    seconds INTEGER, minutes INTEGER, detail TEXT);
CREATE TABLE IF NOT EXISTS gre_seen (key TEXT PRIMARY KEY, n INTEGER DEFAULT 0, right INTEGER DEFAULT 0, first TEXT, last TEXT);
"""
# gre_seen: every hand-written question (verbal bank id, 'b:' + text for quiz-bank questions) and every vocab sentence
# ('v:' + sentence) you have answered, anywhere in the app. None of them is served again: right ones are done, wrong ones
# come back only as Error-log redos (questions) or missed-word warm-ups (words) until you get them right REDO_HITS times.
# columns added after the first GRE release
EXTRA_COLS = {
    'gre_tests': {'subject': "TEXT DEFAULT 'quant'"},
    'gre_errors': {'kind': "TEXT DEFAULT 'Unsorted'", 'redo_on': 'TEXT', 'redo_count': 'INTEGER DEFAULT 0', 'detail': 'TEXT', 'secs': 'INTEGER',
                   'redo_hits': 'INTEGER DEFAULT 0'},
    'gre_essays': {'ai_score': 'REAL', 'ai_feedback': 'TEXT', 'ai_at': 'TEXT'},
    'gre_vocab_queue': {'missed_at': 'TEXT', 'eod_at': 'TEXT'},
    'gre_vocab': {'first_seen': 'TEXT', 'last_card': 'TEXT'},  # last_card: last day the word was answered as a flashcard
}

DEFAULTS = {'gre_start': '2026-10-12', 'gre_days': 'Mon,Tue,Wed,Thu,Fri,Sat', 'gre_time': '20:00', 'gre_notify': '1',
            'gre_target_q': '165', 'gre_target_v': '155', 'gre_daily_cards': '30'}
SETTING_KEYS = set(DEFAULTS)

# mistake categories (the error log's "why did I miss it")
ERROR_KINDS = ['Unsorted', 'Concept', 'Careless', 'Timing', 'Vocab', 'Misread']
REASON_KIND = {'Concept gap': 'Concept', 'Careless mistake': 'Careless', 'Ran out of time': 'Timing',
               'Did not know the word': 'Vocab', 'Misread the question': 'Misread'}
REDO_AFTER = 1   # days until a new mistake is due for a redo (the next day)
REDO_AGAIN = 1   # days until a failed redo comes back
REDO_GAP = 2     # days until the next redo after a correct one
REDO_HITS = 3    # correct redos that fix a mistake (also: correct answers that clear a missed word)
KNOWN_DUE = '2099-12-31'  # a word you got right is known: it is not drilled again (only the weekly test checks it)

_ready = False


def ensure():
    global _ready
    if _ready:
        return
    with db._lock:
        c = db.con()
        c.executescript(SCHEMA)
        for table, cols in EXTRA_COLS.items():
            have = {r[1] for r in c.execute(f'PRAGMA table_info({table})')}
            for col, decl in cols.items():
                if col not in have:
                    c.execute(f'ALTER TABLE {table} ADD COLUMN {col} {decl}')
        for k, v in DEFAULTS.items():
            c.execute('INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)', (k, v))
        # old manual error entries kept their reason in the answer column
        for reason, kind in REASON_KIND.items():
            c.execute("UPDATE gre_errors SET kind=? WHERE (kind IS NULL OR kind='Unsorted') AND answer=?", (kind, reason))
        c.execute("UPDATE gre_errors SET redo_on = date(created, '+7 day') WHERE redo_on IS NULL AND created IS NOT NULL")
        # one-time: words already missed before the queue existed (last answer wrong = box 1; due = the day it was missed)
        if not c.execute("SELECT 1 FROM settings WHERE key='vocab_queue_backfill'").fetchone():
            c.execute("INSERT OR IGNORE INTO gre_vocab_queue(word, added, hits, misses) SELECT word, due, 0, 0 FROM gre_vocab WHERE box=1 AND seen > 0")
            c.execute("INSERT INTO settings(key, value) VALUES ('vocab_queue_backfill', '1')")
        # words queued before miss times were recorded: treat the day they were added as the day they were missed
        c.execute("UPDATE gre_vocab_queue SET missed_at = added || 'T00:00:00.000001' WHERE missed_at IS NULL AND added IS NOT NULL")
        if not c.execute("SELECT 1 FROM settings WHERE key='gre_seen_backfill'").fetchone():
            _backfill_seen(c)
            c.execute("INSERT INTO settings(key, value) VALUES ('gre_seen_backfill', '1')")
        if not c.execute("SELECT 1 FROM settings WHERE key='gre_rule3'").fetchone():
            # 24 Nov 2026: only what you got wrong is repeated, until right REDO_HITS times
            t = today().isoformat()
            c.execute('UPDATE gre_vocab_queue SET cleared=? WHERE cleared IS NULL AND hits >= ?', (t, REDO_HITS))
            c.execute('UPDATE gre_vocab SET box=5, due=? WHERE seen > 0 AND word NOT IN (SELECT word FROM gre_vocab_queue WHERE cleared IS NULL)', (KNOWN_DUE,))
            c.execute('UPDATE gre_vocab SET box=1, due=? WHERE word IN (SELECT word FROM gre_vocab_queue WHERE cleared IS NULL)', (t,))
            c.execute("UPDATE gre_errors SET redo_on = MIN(COALESCE(redo_on, '9999'), date(created, '+1 day')) WHERE status='Open' AND COALESCE(redo_count, 0) = 0")
            c.execute("INSERT INTO settings(key, value) VALUES ('gre_rule3', '1')")
        c.commit()
    _ready = True
    load_exclusions()


def _backfill_seen(c):
    """One time: everything answered before gre_seen existed (tests, practice sets, logged mistakes)."""
    now = today().isoformat()
    keys = {}
    for (detail, at) in c.execute('SELECT detail, at FROM gre_tests').fetchall():
        for it in json.loads(detail or '[]'):
            k = item_key(it)
            if k:
                keys[k] = (at or now)[:10]
    if c.execute("SELECT name FROM sqlite_master WHERE name='gre_practice_seen'").fetchone():
        for (k, at) in c.execute('SELECT key, at FROM gre_practice_seen').fetchall():
            keys[k] = at or now
    by_text = {x['q']: x['id'] for x in gre_verbal.QS}
    for (q, created) in c.execute('SELECT question, created FROM gre_errors').fetchall():
        q = (q or '').split(': ', 1)[-1] if q and q not in by_text else q
        if q in by_text:
            keys[by_text[q]] = created or now
    for k, at in keys.items():
        c.execute('INSERT OR IGNORE INTO gre_seen(key, n, right, first, last) VALUES (?, 1, 0, ?, ?)', (k, at, at))


def item_key(it):
    """The gre_seen key of an answered question, or None for questions that are new every time (quant generators)."""
    g = it.get('gen')
    if g and g in gre_verbal.BY_ID:
        return str(g)
    if it.get('word'):
        return 'v:' + str(it.get('q') or '') if it.get('format') in ('tc', 'sentence') or '______' in str(it.get('q') or '') else None
    if (not g or g == 'bank') and it.get('q'):
        return 'b:' + str(it['q'])
    return None


def mark_seen(key, correct=None):
    if not key:
        return
    t = today().isoformat()
    db.execute('INSERT INTO gre_seen(key, n, right, first, last) VALUES (?, 1, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET '
               'n = n + 1, right = right + excluded.right, last = excluded.last', (key, 1 if correct else 0, t, t))


def mark_items(items):
    for it in items or []:
        mark_seen(item_key(it), it.get('correct'))


def seen_keys(days=None):
    ensure()
    if days is None:
        return {r['key'] for r in db.query('SELECT key FROM gre_seen')}
    since = (today() - dt.timedelta(days=days)).isoformat()
    return {r['key'] for r in db.query('SELECT key FROM gre_seen WHERE last >= ?', (since,))}


def refresh_used():
    """Tell the verbal bank which questions you have already answered (they are never served again)."""
    gre_verbal.USED = {k for k in seen_keys() if k in gre_verbal.BY_ID}
    return gre_verbal.USED


def today():
    return dt.date.today()


def setting(k):
    ensure()
    return db.get_setting(k) or DEFAULTS[k]


def mod(subject):
    return SUBJECTS.get(subject or 'quant', gre_course)


def mod_for(ch):
    return gre_verbal if ch in gre_verbal.LESSONS else gre_course


def subject_of(ch):
    return 'verbal' if ch in gre_verbal.LESSONS else 'quant'


# ---------------------------------------------------------------- schedule
def study_days():
    return {x.strip() for x in setting('gre_days').split(',') if x.strip()} or set(DAYS[:6])


def schedule():
    """Planned calendar date for each day of the plan (study days only)."""
    try:
        d = dt.date.fromisoformat(setting('gre_start'))
    except ValueError:
        d = today()
    days = study_days()
    out = []
    while len(out) < len(gre_plan.PLAN):
        if DAYS[d.weekday()] in days:
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def progress():
    ensure()
    return {r['day']: r for r in db.query('SELECT * FROM gre_progress')}


def status(day=None):
    day = day or today()
    sched = schedule()
    prog = progress()
    done = {n for n, r in prog.items() if r['done']}
    current = next((p['day'] for p in gre_plan.PLAN if p['day'] not in done), None)
    due_by_today = sum(1 for d in sched if d <= day)
    planned_today = next((i + 1 for i, d in enumerate(sched) if d == day), None)
    behind = max(0, sum(1 for d in sched if d < day) - len(done))  # today's class is not late yet
    return {'current': current, 'done': len(done), 'total': len(gre_plan.PLAN), 'due_by_today': due_by_today,
            'behind': behind, 'planned_today': planned_today, 'start': sched[0].isoformat(), 'end': sched[-1].isoformat(),
            'started': day >= sched[0], 'current_date': sched[current - 1].isoformat() if current else None}


def replan(day=None):
    """Move the start date so the next class not done (the current day) lands on today, or the next study day."""
    ensure()
    st = status(day)
    cur = st['current']
    if not cur:
        return {'ok': False, 'error': 'Every class is already done.'}
    days = study_days()
    d = day or today()
    while DAYS[d.weekday()] not in days:
        d += dt.timedelta(days=1)
    first = d
    k = cur - 1
    while k > 0:
        d -= dt.timedelta(days=1)
        if DAYS[d.weekday()] in days:
            k -= 1
    old_end = st['end']
    db.set_setting('gre_start', d.isoformat())
    new = status(day)
    return {'ok': True, 'start': d.isoformat(), 'day': cur, 'day_date': first.isoformat(), 'end': new['end'], 'old_end': old_end}


def unlocked_groups(upto_day):
    """Vocab groups introduced on or before plan day `upto_day`."""
    return sorted({p['vocab']['new'] for p in gre_plan.PLAN if 'new' in p['vocab'] and p['day'] <= upto_day})


def vocab_group_for(n):
    p = gre_plan.PLAN[n - 1]
    if 'new' in p['vocab']:
        return p['vocab']['new']
    return None


# ---------------------------------------------------------------- quizzes
def _vocab_mcq(word, rng, pool):
    right = gre_vocab.DEFS[word]
    wrong = rng.sample([gre_vocab.DEFS[w] for w in pool if w != word and gre_vocab.DEFS[w] != right], 3)
    choices = wrong + [right]
    rng.shuffle(choices)
    return {'topic': 'vocab', 'kind': 'mc', 'q': f'What does “{word}” mean?', 'c': choices, 'a': choices.index(right),
            'x': f'{word}: {right}', 'word': word}


def _bank_item(b, topic):
    kind = 'ma' if isinstance(b['a'], list) else ('qc' if b['c'] == gre_quiz.QC else 'mc')
    return {'kind': kind, **b, 'topic': topic}


_QC_GENS = None


def _qc_gens():
    """Quant generators that produce quantitative-comparison questions (found by running each once)."""
    global _QC_GENS
    if _QC_GENS is None:
        _QC_GENS = []
        for ch, gens in gre_course.GENS.items():
            for g in gens:
                try:
                    if any(g[0](random.Random(s)).get('kind') == 'qc' for s in range(3)):
                        _QC_GENS.append((ch, g))
                except Exception:
                    pass
    return _QC_GENS


def _qc_items(rng, k, upto_day):
    pool = [(ch, g) for ch, g in _qc_gens() if gre_course.CH_DAY[ch] <= max(upto_day, 4)] or _qc_gens()
    out = []
    for _ in range(k * 4):
        if len(out) >= k:
            break
        ch, (fn, d, c) = rng.choice(pool)
        q = gre_course._make(ch, fn, d, c, rng)
        if q['kind'] == 'qc' and q['q'] not in {o['q'] for o in out}:
            out.append({**q, 'topic': 'qc'})
    return out


QUIZ_VOCAB = 8  # vocabulary questions in a daily quiz


def quiz_words(n, rng=None):
    """The day's vocabulary for its quiz: today's new GregMat group, or on review days your weakest unlocked words."""
    p = gre_plan.PLAN[n - 1]
    rng = rng or random.Random()
    if 'new' in p['vocab']:
        return rng.sample(gre_vocab.GROUPS[p['vocab']['new']], QUIZ_VOCAB)
    groups = unlocked_groups(n)
    pool = [w for g in groups for w in gre_vocab.GROUPS[g]]
    if not pool:
        return []
    # only words still to be learnt: missed words first, then words not met yet - words you got right are not repeated
    missed = {r['word'] for r in db.query('SELECT word FROM gre_vocab_queue WHERE cleared IS NULL')}
    met = {r['word'] for r in db.query('SELECT word FROM gre_vocab WHERE seen > 0')}
    rng.shuffle(pool)
    pool = [w for w in pool if w in missed] + [w for w in pool if w not in met]
    return pool[:QUIZ_VOCAB]


def prepare_vocab(n):
    """Write GRE-style sentences in the background for this day's words and the next class's new group."""
    from . import vocab_ctx
    words = list(gre_vocab.GROUPS[gre_plan.PLAN[n - 1]['vocab']['new']]) if 'new' in gre_plan.PLAN[n - 1]['vocab'] else []
    for k in range(n, min(n + 2, len(gre_plan.PLAN))):
        nxt = gre_plan.PLAN[k]['vocab']
        if 'new' in nxt:
            words += gre_vocab.GROUPS[nxt['new']]
            break
    vocab_ctx.prepare_async(words)


def _quiz_item(q, t, ch=None):
    return {**q, 'topic': t, 'chapter': q.get('chapter') or ch or t, 'ctitle': q.get('ctitle') or topic_name(t), 'diff': q.get('diff') or 2}


def build_quiz(n, seed=None):
    """Daily quiz in GRE format, on the day's own topics and vocabulary: a timed Quant section (course generators -
    fresh numbers every time - plus one hand-written question per topic) and a timed Verbal section (the day's
    words as text-completion questions, then the day's verbal topics from the verbal bank, unseen first)."""
    from . import vocab_ctx
    p = gre_plan.PLAN[n - 1]
    rng = random.Random(seed if seed is not None else f'{n}-{random.random()}')
    quant, verbal = [], []
    per = 5 if len(p['quiz']) <= 2 else 3
    refresh_used()
    used = seen_keys()
    fresh_bank = lambda t: [b for b in gre_quiz.BANK.get(t, []) if b['q'] not in gre_course.EXCLUDED_TEXT and 'b:' + b['q'] not in used]
    for t in p['quiz']:
        if t in gre_verbal.LESSONS:
            got = [_quiz_item(it, t) for it in gre_verbal.quiz_items(t, per, rng, _seen('verbal'))]
            verbal += got + _fresh_vocab_fill(t, per - len(got), rng)  # bank used up: new sentences on your words
        elif t in gre_course.GENS:
            bank = fresh_bank(t)
            nb = 1 if bank else 0
            quant += [_quiz_item(q, t) for q in gre_course._pick(rng, t, per - nb, gre_course.DIFF_MIX['mixed'])]
            quant += [_quiz_item(_bank_item(b, t), t) for b in rng.sample(bank, nb)]
        elif t == 'qc':
            got = _qc_items(rng, per, n)
            bank = fresh_bank('qc')
            quant += [_quiz_item(q, 'qc', q.get('chapter')) for q in got]
            quant += [_quiz_item(_bank_item(b, t), t) for b in rng.sample(bank, min(len(bank), per - len(got)))]
        else:
            bank = fresh_bank(t)
            (verbal if t in ('tc_basic', 'tc_shift', 'tc_double', 'tc_triple', 'se', 'rc', 'cr', 'cr2') else quant).extend(
                _quiz_item(_bank_item(b, t), t) for b in rng.sample(bank, min(per, len(bank))))
    words = quiz_words(n, rng) if unlocked_groups(n) else []
    vocab = []
    if words:
        pool = [w for g in unlocked_groups(n) for w in gre_vocab.GROUPS[g]]
        vocab = [vocab_ctx.question(w, rng, pool if len(pool) > 20 else list(gre_vocab.DEFS)) for w in words]
        vocab.sort(key=lambda q: q['format'] != 'tc')  # sentence questions first, like the start of a verbal section
    # GRE order inside verbal: text completions (incl. vocabulary), sentence equivalence, then reading / reasoning
    rank = {'tc_basic': 1, 'tc_shift': 1, 'tc_double': 2, 'tc_triple': 3, 'se': 4, 'rc': 5, 'cr': 6, 'cr2': 6}
    verbal = vocab + sorted(verbal, key=lambda q: (rank.get(q.get('chapter'), 5), q.get('pid') or ''))
    secs_v = sum(60 if q.get('topic') == 'vocab' else 105 if q.get('chapter') in ('rc', 'cr', 'cr2') else 75 for q in verbal)
    sections = []
    if quant:
        sections.append({'subject': 'quant', 'title': f'Day {n} quiz · Quant', 'minutes': max(3, round(len(quant) * 1.75)), 'questions': quant})
    if verbal:
        sections.append({'subject': 'verbal', 'title': f'Day {n} quiz · Verbal' + (' & vocabulary' if vocab else ''),
                         'minutes': max(3, round(secs_v / 60)), 'questions': verbal})
    prepare_vocab(n)
    return {'day': n, 'title': f'Day {n} quiz', 'sections': sections, 'vocab': vocab_ctx.status(words)}


def _fresh_vocab_fill(ch, k, rng):
    """Up to k text-completion questions in sentences you have never answered, on your studied words (for when the
    hand-written bank of a text-completion chapter is used up). Only single-blank chapters can be filled this way."""
    if k <= 0 or ch not in ('tc_basic', 'tc_shift'):
        return []
    out = _test_vocab(ch, set(), k, rng)
    for q in out:
        q.update(topic='vocab', cname='New sentence on a word you studied')
    return out


def _detail(it):
    """What the error log needs to let you redo a question later."""
    keep = ('kind', 'q', 'c', 'a', 'v', 'x', 'passage', 'ptitle', 'chapter', 'concept', 'diff', 'gen', 'word')
    return json.dumps({k: it[k] for k in keep if k in it and it[k] is not None})


def topic_name(t):
    if t == 'vocab':
        return 'Vocabulary'
    return gre_verbal.TITLES.get(t) or gre_quiz.TOPIC_NAMES.get(t, t)


def record_quiz(b):
    ensure()
    now = dt.datetime.now().isoformat(timespec='seconds')
    topics = {}
    mark_items(b.get('items'))
    for it in b.get('items', []):
        t = topics.setdefault(it['topic'], [0, 0])
        t[0] += 1 if it['correct'] else 0
        t[1] += 1
        if it['topic'] == 'vocab':
            vocab_answer(it['word'], it['correct'])
        elif not it['correct']:
            add_error(b.get('day'), topic_name(it['topic']), f"Quiz - day {b.get('day')}", it['q'],
                      f"Your answer: {it.get('yours') or '(blank)'} | Correct: {it.get('right')}", it.get('x', ''), detail=_detail(it))
    db.execute('INSERT INTO gre_quiz(day,at,score,total,topics) VALUES (?,?,?,?,?)',
               (b.get('day'), now, b.get('score'), b.get('total'), json.dumps(topics)))
    return {'ok': True}


# ---------------------------------------------------------------- error log
def add_error(day, topic, source, question, answer, note, kind='Unsorted', detail=None, secs=None, created=None):
    ensure()
    created = created or today().isoformat()
    redo = (dt.date.fromisoformat(created) + dt.timedelta(days=REDO_AFTER)).isoformat()
    same = db.one("SELECT id FROM gre_errors WHERE status='Open' AND question=? AND source NOT LIKE 'Test result%'", (question,)) if question else None
    if same:  # missed again while still open: start its count again, redo tomorrow
        db.execute('UPDATE gre_errors SET redo_on=?, redo_hits=0 WHERE id=?', (redo, same['id']))
        return same['id']
    return db.execute('INSERT INTO gre_errors(created,day,topic,source,question,answer,note,status,kind,redo_on,redo_count,detail,secs) '
                      'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (created, day, topic, source, question, answer, note, 'Open', kind if kind in ERROR_KINDS else 'Unsorted', redo, 0, detail, secs))


def errors():
    ensure()
    rows = db.query("SELECT * FROM gre_errors ORDER BY status = 'Open' DESC, id DESC")
    t0 = today().isoformat()
    for r in rows:
        r['due'] = r['status'] == 'Open' and (r['redo_on'] or '') <= t0
        r['detail'] = _reshuffle(json.loads(r['detail'])) if r.get('detail') else None
        r['redo_hits'] = r.get('redo_hits') or 0
        r['redo_target'] = REDO_HITS
    return rows


def _reshuffle(d):
    """Redo a mistake with its answer choices in a new order, so you solve it rather than remember a letter."""
    try:
        rng = random.Random()
        if d.get('kind') == 'mc' and isinstance(d.get('a'), int) and isinstance(d.get('c'), list):
            order = list(range(len(d['c'])))
            rng.shuffle(order)
            d['c'], d['a'] = [d['c'][i] for i in order], order.index(d['a'])
        elif d.get('kind') == 'ma' and isinstance(d.get('a'), list):
            order = list(range(len(d['c'])))
            rng.shuffle(order)
            d['c'], d['a'] = [d['c'][i] for i in order], sorted(order.index(i) for i in d['a'])
        elif d.get('kind') == 'tc' and d.get('c') and isinstance(d['c'][0], list):
            cols, ans = [], []
            for col, a in zip(d['c'], d['a']):
                order = list(range(len(col)))
                rng.shuffle(order)
                cols.append([col[i] for i in order])
                ans.append(order.index(a))
            d['c'], d['a'] = cols, ans
    except (TypeError, ValueError, IndexError):
        pass
    return d


def errors_summary():
    """Open mistakes by kind, and how many mistakes of each kind were made in each of the last 6 weeks."""
    ensure()
    t0 = today()
    monday = t0 - dt.timedelta(days=t0.weekday())
    weeks = [(monday - dt.timedelta(weeks=i)) for i in range(5, -1, -1)]
    trend = {k: [0] * 6 for k in ERROR_KINDS}
    open_by = Counter()
    due = 0
    for r in db.query('SELECT created, kind, status, redo_on FROM gre_errors'):
        k = r['kind'] if r['kind'] in ERROR_KINDS else 'Unsorted'
        if r['status'] == 'Open':
            open_by[k] += 1
            if (r['redo_on'] or '') <= t0.isoformat():
                due += 1
        try:
            c = dt.date.fromisoformat(r['created'])
        except (TypeError, ValueError):
            continue
        for i, w in enumerate(weeks):
            if w <= c < w + dt.timedelta(days=7):
                trend[k][i] += 1
    return {'kinds': ERROR_KINDS, 'open': {k: open_by.get(k, 0) for k in ERROR_KINDS}, 'due': due,
            'weeks': [w.isoformat() for w in weeks], 'trend': trend}


PRACTICE_SRC = 'Practice · '  # Error-log source prefix for Magoosh practice questions marked wrong in a class


def practice_source(code, n):
    return f'{PRACTICE_SRC}Magoosh {gre_plan.PNAMES[code]} Q{n}'


def practice_marks(n):
    """{'MC:42': 'Open' / 'Fixed'} for this day's practice questions that were marked wrong."""
    ensure()
    p = gre_plan.PLAN[n - 1]
    keys = {practice_source(s['code'], it['n']): f"{s['code']}:{it['n']}" for s in p['practice'] for it in s['items']}
    if not keys:
        return {}
    rows = db.query(f"SELECT source, status FROM gre_errors WHERE source IN ({','.join('?' * len(keys))}) ORDER BY id", tuple(keys))
    return {keys[r['source']]: r['status'] for r in rows}


def mark_practice(b):
    """Tick a Magoosh practice question as wrong (→ Error log with links to the question and video solution) or untick it."""
    ensure()
    day, code, qn = int(b['day']), b['code'], int(b['n'])
    p = gre_plan.PLAN[day - 1]
    st = next((s for s in p['practice'] if s['code'] == code), None)
    it = next((x for x in (st or {}).get('items', []) if x['n'] == qn), None)
    if not it:
        return {'ok': False, 'error': 'Question not in this class'}
    src = practice_source(code, qn)
    if not b.get('wrong'):
        db.execute("DELETE FROM gre_errors WHERE source=? AND status='Open'", (src,))
        return {'ok': True, 'status': None}
    if db.one("SELECT id FROM gre_errors WHERE source=? AND status='Open'", (src,)):
        return {'ok': True, 'status': 'Open'}
    links = [{'label': 'Question' if i == 0 else f'Question page {i + 1}', 'url': u} for i, u in enumerate(it['q'])]
    if it['s']:
        links.append({'label': '▶ Video solution', 'url': it['s']})
    add_error(day, f"{gre_plan.PNAMES[code]} · {p['title']}", src, f"Magoosh {gre_plan.PNAMES[code].lower()} question {qn} (Day {day} practice)",
              'Watch the video solution after you redo it', '', detail=json.dumps({'kind': 'link', 'links': links}))
    return {'ok': True, 'status': 'Open'}


def redo_error(eid, correct):
    """Result of redoing a logged mistake: REDO_HITS correct redos (on different days) → Fixed.
    Right → next redo in REDO_GAP days; wrong → back tomorrow (the correct answers so far still count)."""
    ensure()
    r = db.one('SELECT * FROM gre_errors WHERE id=?', (eid,))
    if not r:
        return {'ok': False}
    n = (r['redo_count'] or 0) + 1
    hits = (r.get('redo_hits') or 0) + (1 if correct else 0)
    if correct and hits >= REDO_HITS:
        db.execute("UPDATE gre_errors SET status='Fixed', redo_count=?, redo_hits=? WHERE id=?", (n, hits, eid))
    else:
        gap = REDO_GAP if correct else REDO_AGAIN
        db.execute('UPDATE gre_errors SET redo_on=?, redo_count=?, redo_hits=? WHERE id=?',
                   ((today() + dt.timedelta(days=gap)).isoformat(), n, hits, eid))
    return {'ok': True, 'fixed': bool(correct) and hits >= REDO_HITS, 'hits': hits, 'target': REDO_HITS,
            'next': None if correct and hits >= REDO_HITS else (today() + dt.timedelta(days=REDO_GAP if correct else REDO_AGAIN)).isoformat()}


# ---------------------------------------------------------------- vocab (Leitner boxes)
def vocab_answer(word, correct, card=False):
    """card=True for the flashcard deck (desktop or phone): counts towards today's card limit."""
    ensure()
    if word not in gre_vocab.DEFS:
        return
    r = db.one('SELECT * FROM gre_vocab WHERE word=?', (word,)) or {'box': 1, 'seen': 0, 'correct': 0}
    q = db.one('SELECT * FROM gre_vocab_queue WHERE word=? AND cleared IS NULL', (word,))
    if correct and q:  # a missed word answered right anywhere (quiz, test, practice): one step towards clearing it
        res = queue_answer(word, True)
        box, due = (5, KNOWN_DUE) if res.get('cleared') else (1, today().isoformat())
    elif correct:      # right → known; it is not drilled again
        box, due = 5, KNOWN_DUE
    else:              # wrong → missed-words queue until right REDO_HITS times
        box, due = 1, today().isoformat()
    db.execute('INSERT INTO gre_vocab(word,box,due,seen,correct,first_seen) VALUES (?,?,?,?,?,?) ON CONFLICT(word) DO UPDATE SET '
               'box=excluded.box, due=excluded.due, seen=excluded.seen, correct=excluded.correct',
               (word, box, due, r['seen'] + 1, r['correct'] + (1 if correct else 0), today().isoformat()))
    if card:
        db.execute('UPDATE gre_vocab SET last_card=? WHERE word=?', (today().isoformat(), word))
    if not correct:
        queue_add(word)


# ---------------------------------------------------------------- missed-words queue
# Every word you miss (flashcards, phone, quiz, tests) joins the queue. From the next day it is tested in a mixed warm-up
# before the day's flashcards (at most once a day); QUEUE_TARGET correct answers remove it and it becomes known.
QUEUE_TARGET = REDO_HITS
WARMUP_CAP = 25                                   # most missed words in one morning warm-up (oldest first)
NEW_WORDS = [(40, 30), (70, 15), (10 ** 9, 8)]    # (missed-words queue up to, new flashcard words per day)


def new_word_budget():
    """How many never-seen words today's flashcards may introduce: fewer when the missed-words queue is big,
    so new words never pile up faster than you can clear the old ones. Held-back words simply come the next day."""
    ensure()
    open_ = db.one('SELECT COUNT(*) n FROM gre_vocab_queue WHERE cleared IS NULL')['n']
    cap = next(c for lim, c in NEW_WORDS if open_ <= lim)
    intro = db.one('SELECT COUNT(*) n FROM gre_vocab WHERE first_seen=?', (today().isoformat(),))['n']
    return {'cap': cap, 'introduced': intro, 'left': max(0, cap - intro), 'queue': open_}


def _now():
    return dt.datetime.now().isoformat(timespec='microseconds')


def queue_add(word):
    """Add a missed word (again) - a word that was cleared earlier comes back with a fresh count."""
    t = today().isoformat()
    r = db.one('SELECT * FROM gre_vocab_queue WHERE word=?', (word,))
    if not r:
        db.execute('INSERT INTO gre_vocab_queue(word, added, hits, misses, missed_at) VALUES (?,?,0,0,?)', (word, t, _now()))
    elif r['cleared']:
        db.execute('UPDATE gre_vocab_queue SET added=?, hits=0, misses=0, last=NULL, cleared=NULL, missed_at=? WHERE word=?', (t, _now(), word))
    else:
        db.execute('UPDATE gre_vocab_queue SET missed_at=? WHERE word=?', (_now(), word))


def queue_state():
    """The open queue, and today's warm-up: words added before today and not yet tested today, as mixed questions."""
    ensure()
    from . import vocab_ctx
    t = today().isoformat()
    rows = db.query('SELECT * FROM gre_vocab_queue WHERE cleared IS NULL ORDER BY added, word')
    due = [r for r in rows if r['added'] < t and (r['last'] or '') < t]
    qs = _word_questions(due[:WARMUP_CAP])  # oldest first; the rest wait for tomorrow
    cleared = db.one('SELECT COUNT(*) n FROM gre_vocab_queue WHERE cleared IS NOT NULL')['n']
    return {'target': QUEUE_TARGET, 'warmup': qs, 'cleared': cleared, 'warmup_waiting': max(0, len(due) - WARMUP_CAP), 'cap': WARMUP_CAP,
            'queue': [{'word': r['word'], 'def': gre_vocab.DEFS.get(r['word'], ''), 'hits': r['hits'], 'misses': r['misses'], 'added': r['added'],
                       'today': r['added'] >= t, 'done_today': (r['last'] or '') >= t} for r in rows]}


def _word_questions(rows):
    """Mixed questions for queue rows: pick the meaning, pick the word, or fill a sentence blank."""
    from . import vocab_ctx
    rng = random.Random()
    pool = list(gre_vocab.DEFS)
    qs = []
    for i, r in enumerate(rows):
        w = r['word']
        kinds = ['meaning', 'word'] + (['sentence'] if vocab_ctx.sentences(w) else [])
        kind = kinds[(i + r['hits'] + rng.randrange(len(kinds))) % len(kinds)]  # vary the format word to word and day to day
        others = vocab_ctx.distractors(w, rng, pool, k=3)
        if kind == 'meaning':
            choices = [gre_vocab.DEFS[x] for x in others] + [gre_vocab.DEFS[w]]
            rng.shuffle(choices)
            q = {'q': f'What does “{w}” mean?', 'c': choices, 'a': choices.index(gre_vocab.DEFS[w])}
        else:
            choices = others + [w]
            rng.shuffle(choices)
            if kind == 'sentence':
                q = {'q': rng.choice(vocab_ctx.sentences(w))['sentence'], 'c': choices, 'a': choices.index(w)}
            else:
                q = {'q': f'Which word means: “{gre_vocab.DEFS[w]}”?', 'c': choices, 'a': choices.index(w)}
        qs.append({**q, 'word': w, 'format': kind, 'def': gre_vocab.DEFS[w], 'hits': r['hits']})
    rng.shuffle(qs)
    return qs


def queue_answer(word, correct, q=None):
    """Result of one warm-up question (or a missed word answered right elsewhere). QUEUE_TARGET correct answers, on
    different days, clear the word. q: the sentence shown, so it is not used again."""
    ensure()
    if q and '______' in q:
        mark_seen('v:' + q, correct)
    r = db.one('SELECT * FROM gre_vocab_queue WHERE word=? AND cleared IS NULL', (word,))
    if not r:
        return {'ok': False}
    t = today().isoformat()
    if correct and ((r['last'] or '') >= t or (r['added'] or '') >= t):  # one per day, from the day after the miss
        return {'ok': True, 'hits': r['hits'], 'cleared': False, 'counted': False}
    hits = r['hits'] + (1 if correct else 0)
    cleared = t if hits >= QUEUE_TARGET else None
    db.execute('UPDATE gre_vocab_queue SET hits=?, misses=?, last=?, cleared=?, missed_at=COALESCE(?, missed_at) WHERE word=?',
               (hits, r['misses'] + (0 if correct else 1), t, cleared, None if correct else _now(), word))
    if cleared:
        db.execute('UPDATE gre_vocab SET box=5, due=? WHERE word=?', (KNOWN_DUE, word))
    return {'ok': True, 'hits': hits, 'cleared': bool(cleared)}


# ---------------------------------------------------------------- end-of-day review: every word missed today, once more
def eod_rows():
    """Words missed today (flashcards, phone, quiz or warm-up) not yet reviewed since their latest miss."""
    ensure()
    t = today().isoformat()
    return db.query("SELECT * FROM gre_vocab_queue WHERE substr(missed_at, 1, 10) = ? AND (eod_at IS NULL OR eod_at < missed_at) ORDER BY missed_at", (t,))


def eod_state():
    ensure()
    t = today().isoformat()
    rows = eod_rows()
    reviewed = db.one("SELECT COUNT(*) n FROM gre_vocab_queue WHERE substr(eod_at, 1, 10) = ? AND eod_at >= missed_at", (t,))['n']
    return {'questions': _word_questions(rows), 'pending': len(rows), 'reviewed': reviewed}


def eod_answer(word, correct, q=None):
    """Extra same-day practice: marks the word reviewed (a wrong answer does not put it back in today's review,
    and it does not count towards clearing the word - that happens in next-day warm-ups)."""
    ensure()
    if q and '______' in q:
        mark_seen('v:' + q, correct)
    db.execute('UPDATE gre_vocab_queue SET eod_at=? WHERE word=?', (_now(), word))
    return {'ok': True, 'correct': bool(correct)}


def vocab_state():
    ensure()
    st = status()
    upto = st['current'] or len(gre_plan.PLAN)
    groups = unlocked_groups(upto)
    rows = {r['word']: r for r in db.query('SELECT * FROM gre_vocab')}
    missed = {r['word'] for r in db.query('SELECT word FROM gre_vocab_queue WHERE cleared IS NULL')}
    t0 = today().isoformat()
    out_groups, due = [], []
    for g, words in gre_vocab.GROUPS.items():
        unlocked = g in groups
        ws = []
        for w in words:
            r = rows.get(w)
            box = r['box'] if r else 0
            ws.append({'word': w, 'def': gre_vocab.DEFS[w], 'box': box})
            # flashcards = words not met yet; missed words are practised in the warm-up instead, known words not at all
            if unlocked and w not in missed and (not r or (r['due'] or '') <= t0):
                due.append({'word': w, 'def': gre_vocab.DEFS[w], 'box': box, 'group': g})
        out_groups.append({'group': g, 'unlocked': unlocked, 'words': ws,
                           'mastered': sum(1 for x in ws if x['box'] >= 4), 'seen': sum(1 for x in ws if x['box'] > 0)})
    boxes = {b: sum(1 for r in rows.values() if r['box'] == b) for b in range(1, 6)}
    learn = {'known': sum(1 for w, r in rows.items() if r['seen'] and w not in missed), 'missed': len(missed),
             'new': sum(1 for g in groups for w in gre_vocab.GROUPS[g] if not (rows.get(w) or {}).get('seen'))}
    # today's deck: at most gre_daily_cards cards a day (default 30), counting cards already answered today.
    # About half the slots go to due reviews (weakest box first), half to new words (within the new-word budget);
    # if one side runs short the other fills the gap. Everything else waits for the next days.
    budget = new_word_budget()
    new = sorted([x for x in due if x['box'] == 0], key=lambda x: x['group'])[:budget['left']]
    rev = sorted([x for x in due if x['box'] != 0], key=lambda x: (x['box'], x['group']))
    try:
        cap = max(1, int(setting('gre_daily_cards')))
    except ValueError:
        cap = 30
    # cards answered today (+ words first met today before this counter existed)
    done = db.one('SELECT COUNT(*) n FROM gre_vocab WHERE last_card=? OR (last_card IS NULL AND first_seen=?)', (t0, t0))['n']
    left = max(0, cap - done)
    n_new = min(len(new), max(left // 2, left - len(rev)))
    n_rev = min(len(rev), left - n_new)
    n_new = min(len(new), left - n_rev)
    deck = new[:n_new] + rev[:n_rev]
    budget.update(held=sum(1 for x in due if x['box'] == 0) - n_new, daily_cap=cap, done_today=done,
                  waiting=len(due) - len(deck))
    return {'groups': out_groups, 'due': deck, 'boxes': boxes, 'learn': learn, 'unlocked': groups, 'total': len(gre_vocab.DEFS), 'budget': budget}


# ---------------------------------------------------------------- day payload
def day_payload(n):
    ensure()
    try:
        prepare_vocab(n)
    except Exception as e:
        print('vocab prepare failed:', e)
    p = gre_plan.PLAN[n - 1]
    sched = schedule()
    prog = progress().get(n) or {}
    g = vocab_group_for(n)
    quizzes = db.query('SELECT * FROM gre_quiz WHERE day=? ORDER BY at DESC', (n,))
    essay_prompt = gre_quiz.ESSAY_PROMPTS[sum(1 for x in gre_plan.PLAN[:n] if x['essay']) - 1] if p['essay'] else None
    return {
        **{k: p[k] for k in ('day', 'week', 'section', 'title', 'notes', 'homework', 'mock', 'essay', 'minutes', 'videos',
                             'read', 'books', 'practice', 'vocab')},
        'topics': [{'key': t, 'name': topic_name(t)} for t in p['quiz']],
        'date': sched[n - 1].isoformat(),
        'vocab_words': [{'word': w, 'def': gre_vocab.DEFS[w]} for w in gre_vocab.GROUPS[g]] if g else [],
        'vocab_group': g,
        'review_groups': unlocked_groups(n) if not g else [],
        'progress': {**prog, 'parts': json.loads(prog.get('parts') or '{}')},
        'quizzes': quizzes,
        'essay_prompt': essay_prompt,
        'essays': db.query('SELECT id, at, words, minutes, self_score, ai_score FROM gre_essays WHERE day=? ORDER BY at DESC', (n,)),
        'has_quiz': bool(p['quiz']) or bool(unlocked_groups(n)),
        'course': day_course(n),
        'practice_marks': practice_marks(n),
        'study': gre_notes.for_day(n),
        'vocab_warmup': len(queue_state()['warmup']),
        'vocab_eod': {k: v for k, v in eod_state().items() if k != 'questions'},
        'vocab_ctx': _vocab_status(g),
        'weekly': week_info(n),
    }


def _vocab_status(group):
    from . import vocab_ctx
    return vocab_ctx.status(list(gre_vocab.GROUPS[group])) if group else {}


def save_progress(n, b):
    ensure()
    cur = progress().get(n) or {}
    parts = json.loads(cur.get('parts') or '{}')
    parts.update(b.get('parts') or {})
    done = b.get('done', cur.get('done', 0))
    db.execute('INSERT INTO gre_progress(day,done,done_on,minutes,notes,parts) VALUES (?,?,?,?,?,?) ON CONFLICT(day) DO UPDATE SET '
               'done=excluded.done, done_on=excluded.done_on, minutes=excluded.minutes, notes=excluded.notes, parts=excluded.parts',
               (n, 1 if done else 0, (cur.get('done_on') or today().isoformat()) if done else None,
                b.get('minutes', cur.get('minutes')), b.get('notes', cur.get('notes')), json.dumps(parts)))
    return {'ok': True}


# ---------------------------------------------------------------- overview
def overview():
    ensure()
    sched = schedule()
    prog = progress()
    best = {r['day']: r for r in db.query('SELECT day, MAX(CAST(score AS REAL)/total) AS pct FROM gre_quiz WHERE total > 0 GROUP BY day')}
    days = [{'day': p['day'], 'week': p['week'], 'section': p['section'], 'title': p['title'], 'date': sched[i].isoformat(),
             'done': bool(prog.get(p['day'], {}).get('done')), 'quiz_pct': round(100 * best[p['day']]['pct']) if p['day'] in best else None,
             'vocab_group': p['vocab'].get('new'), 'mock': bool(p['mock']), 'essay': p['essay']}
            for i, p in enumerate(gre_plan.PLAN)]
    topic = {}
    for r in db.query('SELECT topics FROM gre_quiz'):
        for t, (c, n) in json.loads(r['topics'] or '{}').items():
            x = topic.setdefault(t, [0, 0])
            x[0] += c
            x[1] += n
    topics = sorted([{'key': t, 'name': topic_name(t), 'correct': c, 'total': n,
                      'pct': round(100 * c / n)} for t, (c, n) in topic.items() if n], key=lambda x: x['pct'])
    vs = vocab_state()
    es = errors_summary()
    return {'status': status(), 'days': days, 'topics': topics, 'weeks': gre_plan.WEEKS,
            'quizzes': db.query('SELECT * FROM gre_quiz ORDER BY at DESC LIMIT 50'),
            'scores': db.query('SELECT * FROM gre_scores ORDER BY date'),
            'vocab': {'boxes': vs['boxes'], 'due': len(vs['due']), 'unlocked': len(vs['unlocked']), 'total_groups': len(gre_vocab.GROUPS)},
            'errors_open': db.one("SELECT COUNT(*) n FROM gre_errors WHERE status='Open'")['n'],
            'errors_due': es['due'],
            'minutes': db.one('SELECT COALESCE(SUM(minutes),0) m FROM gre_progress WHERE done=1')['m'],
            'settings': {k: setting(k) for k in DEFAULTS}}


def today_card(day=None):
    """Small summary for the Today screen."""
    try:
        st = status(day)
    except Exception:
        return None
    n = st['current']
    if not n:
        return {'finished': True, **st}
    p = gre_plan.PLAN[n - 1]
    vs_due = len(vocab_state()['due']) if (st['started'] or st['done']) else 0
    return {**st, 'day': n, 'title': p['title'], 'section': p['section'], 'minutes': p['minutes'],
            'time': setting('gre_time'), 'vocab_due': vs_due, 'study_today': st['planned_today'] is not None,
            'errors_due': errors_summary()['due']}


def library():
    try:
        from .gre_resources import FILES, FOLDERS, LESSONS, PRACTICE, ROOT
    except ImportError:
        from .gre_resources_example import FILES, FOLDERS, LESSONS, PRACTICE, ROOT
    return {'root': ROOT, 'folders': [{'name': n, 'url': f'https://drive.google.com/drive/folders/{i}'} for n, i in FOLDERS],
            'files': [{'path': p, 'name': n, 'url': f'https://drive.google.com/file/d/{i}/view'} for p, n, i in FILES],
            'lessons': [{'name': gre_plan.topic_label(k), 'url': v['url'], 'count': len(v['videos'])} for k, v in LESSONS.items()],
            'practice': [{'name': gre_plan.PNAMES[c], 'url': PRACTICE[f]['url'], 'count': len(PRACTICE[f]['items']),
                          'used': sum(d['drill'].get(c, 0) for d in gre_plan.PLAN)} for c, f in gre_plan.PTYPES.items() if f in PRACTICE],
            'official': gre_plan.OFFICIAL_LIBRARY, 'order': gre_plan.STUDY_ORDER}


def tutor_system(n):
    p = gre_plan.PLAN[(n or 1) - 1]
    return ("You are a patient, encouraging GRE tutor for an Indian engineering graduate preparing for the GRE "
            f"(target: {setting('gre_target_q')}+ Quant, {setting('gre_target_v')}+ Verbal) for Master's in business analytics. "
            "Teach like a good private tutor: short explanations, a worked example, then a question for the student to try. "
            "Use plain text maths (x^2, sqrt(x)). When you set practice questions, do NOT reveal answers until the student replies. "
            "Be honest if you are unsure; the student should trust the official answer keys over you.\n\n"
            f"TODAY'S CLASS: Day {p['day']} (week {p['week']}) - {p['section']}: {p['title']}\n"
            "Key ideas taught today:\n" + '\n'.join('- ' + x for x in p['notes']) +
            ('\nQuiz topics: ' + ', '.join(topic_name(t) for t in p['quiz']) if p['quiz'] else '') + _results_summary())


def _results_summary():
    from . import results  # results imports this module
    return results.tutor_summary()


# ---------------------------------------------------------------- courses (quant + verbal, tutor-style chapters and tests)
def _lessons():
    return {r['chapter']: {'done': set(json.loads(r['done'] or '[]')), 'finished_on': r['finished_on']} for r in db.query('SELECT * FROM gre_lessons')}


def save_lesson(ch, concept):
    ensure()
    cur = _lessons().get(ch, {'done': set(), 'finished_on': None})
    done = cur['done'] | {int(concept)}
    fin = cur['finished_on'] or (today().isoformat() if len(done) >= len(mod_for(ch).LESSONS[ch]) else None)
    db.execute('INSERT INTO gre_lessons(chapter,done,finished_on) VALUES (?,?,?) ON CONFLICT(chapter) DO UPDATE SET done=excluded.done, '
               'finished_on=excluded.finished_on', (ch, json.dumps(sorted(done)), fin))
    return {'ok': True, 'done': sorted(done)}


# a question taking longer than this (seconds) counts as slow
SLOW = {'quant': 120, 'tc': 90, 'reading': 150}
PACE = {'quant': 21 * 60 / 12, 'verbal': 18 * 60 / 12}  # real GRE seconds per question


def slow_limit(ch):
    if ch in gre_verbal.LESSONS:
        return SLOW['reading'] if ch in gre_verbal.READING else SLOW['tc']
    return SLOW['quant']


def save_test(b):
    """Store a finished course test; wrong answers go to the Error log (tagged Timing if blank or very slow)."""
    ensure()
    now = dt.datetime.now().isoformat(timespec='seconds')
    items = b.get('items', [])
    subject = b.get('subject') or 'quant'
    mark_items(items)
    tid = db.execute('INSERT INTO gre_tests(kind,key,title,at,score,total,seconds,minutes,detail,subject) VALUES (?,?,?,?,?,?,?,?,?,?)',
                     (b.get('kind'), b.get('key'), b.get('title'), now, sum(1 for i in items if i.get('correct')), len(items),
                      b.get('seconds'), b.get('minutes'), json.dumps(items), subject))
    for it in items:
        if it.get('word') and it.get('topic') == 'vocab':  # your-word question: vocab boxes + missed-words queue
            vocab_answer(str(it['word']), bool(it.get('correct')))
            continue
        if not it.get('correct'):
            ch, c = it.get('chapter'), it.get('concept')
            m = mod_for(ch)
            topic = m.title(ch) + (f' · {m.concept_name(ch, c)}' if c is not None else '')
            secs = it.get('secs') or 0
            blank = not it.get('yours')
            kind = 'Timing' if blank or secs > slow_limit(ch) else 'Unsorted'
            add_error(b.get('day'), topic, b.get('title'), it.get('q'),
                      f"Your answer: {it.get('yours') or '(blank)'} | Correct: {it.get('right')}", it.get('x', ''),
                      kind=kind, detail=_detail(it), secs=secs or None)
    return {'ok': True, 'id': tid}


def test_detail(tid):
    ensure()
    r = db.one('SELECT * FROM gre_tests WHERE id=?', (tid,))
    if not r:
        return None
    return {**{k: r[k] for k in ('id', 'kind', 'key', 'title', 'at', 'score', 'total', 'seconds', 'minutes')},
            'subject': r.get('subject') or 'quant', 'items': json.loads(r['detail'] or '[]')}


def _pct(r):
    return round(100 * r['score'] / r['total']) if r['total'] else 0


def _tests(subject):
    return db.query("SELECT id, kind, key, title, at, score, total, seconds, minutes, detail FROM gre_tests "
                    "WHERE COALESCE(subject, 'quant') = ? ORDER BY at", (subject,))


def _seen(subject):
    """How many times each bank question (by id) has been answered anywhere. Also refreshes gre_verbal.USED, the
    questions that are never served again."""
    if subject != 'verbal':
        return {}
    ensure()
    refresh_used()
    return {r['key']: r['n'] for r in db.query('SELECT key, n FROM gre_seen') if r['key'] in gre_verbal.BY_ID}


def taught_chapters(upto=None, subject='quant'):
    m = mod(subject)
    upto = upto or status()['current'] or len(gre_plan.PLAN)
    return [c for c in m.CHAPTERS if m.CH_DAY[c] <= upto]


def course_state(subject='quant'):
    ensure()
    m = mod(subject)
    st = status()
    cur = st['current'] or len(gre_plan.PLAN)
    sched = schedule()
    les = _lessons()
    tests = _tests(subject)
    by_ch, by_unit, cstat = {}, {}, {}
    for t in tests:
        if t['kind'] == 'chapter':
            by_ch.setdefault(t['key'], []).append(_pct(t))
        elif t['kind'] == 'unit':
            by_unit.setdefault(t['key'], []).append(_pct(t))
        for it in json.loads(t['detail'] or '[]'):
            if it.get('concept') is None or it.get('chapter') not in m.LESSONS:
                continue
            x = cstat.setdefault((it['chapter'], it['concept']), [0, 0])
            x[0] += 1 if it.get('correct') else 0
            x[1] += 1
    taught = taught_chapters(cur, subject)
    chapters = []
    for ch in m.CHAPTERS:
        n = len(m.LESSONS[ch])
        done = len(les.get(ch, {}).get('done', ()))
        ps = by_ch.get(ch, [])
        best, last = (max(ps), ps[-1]) if ps else (None, None)
        if best is not None and best >= 80:
            state = 'mastered'
        elif last is not None and last < 60:
            state = 'relearn'
        elif ps:
            state = 'tested'
        elif done:
            state = 'learning'
        else:
            state = 'due' if ch in taught else 'later'
        chapters.append({'key': ch, 'title': m.title(ch), 'unit': m.UNIT_OF[ch], 'day': m.CH_DAY[ch],
                         'date': sched[m.CH_DAY[ch] - 1].isoformat(), 'concepts': n, 'learnt': done, 'attempts': len(ps),
                         'best': best, 'last': last, 'state': state, 'taught': ch in taught})
    units = []
    for u in m.UNITS:
        ps = by_unit.get(u['key'], [])
        units.append({'key': u['key'], 'title': u['title'], 'chapters': u['chapters'], 'day': u['day'], 'date': sched[u['day'] - 1].isoformat(),
                      'attempts': len(ps), 'best': max(ps) if ps else None, 'last': ps[-1] if ps else None,
                      'ready': all(by_ch.get(c) for c in u['chapters']), 'due': u['day'] <= cur})
    weak = sorted([{'chapter': ch, 'concept': c, 'title': m.title(ch), 'name': m.concept_name(ch, c), 'correct': a, 'total': n,
                    'pct': round(100 * a / n)} for (ch, c), (a, n) in cstat.items() if n >= 2 and a / n < .7],
                  key=lambda w: (w['pct'], -w['total']))[:6]
    cls = None
    if st['current'] and st['current_date'] and st['current_date'] <= today().isoformat():
        p = gre_plan.PLAN[st['current'] - 1]
        cls = {'day': st['current'], 'title': p['title'], 'section': p['section'], 'date': st['current_date']}
    spec = m.TEST_SPEC
    return {'subject': subject, 'chapters': chapters, 'units': units, 'weak': weak, 'current_day': cur,
            'next': _next_step(chapters, units, weak, subject, cls),
            'recent': [{k: t[k] for k in ('id', 'kind', 'key', 'title', 'at', 'score', 'total', 'seconds', 'minutes')} for t in reversed(tests[-15:])],
            'tests_taken': len(tests), 'behind': st['behind'], 'class': cls, 'predict': predict(subject), 'test_weak': _test_weak(subject),
            'spec': {k: {'n': v[0], 'minutes': v[1]} for k, v in spec.items()}}


def _test_weak(subject):
    from . import results
    return results.weak_topics(subject)


def _next_step(chapters, units, weak, subject='quant', cls=None):
    """What a tutor would ask you to do next, in priority order."""
    m = mod(subject)
    (cn, cm), (un, um) = m.TEST_SPEC['chapter'], m.TEST_SPEC['unit']
    (s1n, s1m), (s2n, s2m) = m.TEST_SPEC['section1'], m.TEST_SPEC['section2']
    name = 'quant' if subject == 'quant' else 'verbal'
    taught = [c for c in chapters if c['taught']]
    for c in chapters:  # a failed test counts even if the chapter was started early
        if c['state'] == 'relearn':
            return {'type': 'lesson', 'key': c['key'], 'label': f"Re-learn {c['title']}",
                    'why': f"Your last {c['title']} test was {c['last']}%. Go through the lesson again (focus on the concepts you missed), then retake the chapter test."}
    for c in taught:
        if c['learnt'] < c['concepts']:
            return {'type': 'lesson', 'key': c['key'], 'label': f"Learn {c['title']}",
                    'why': f"This chapter was scheduled for day {c['day']}. Work through the lesson ({c['learnt']}/{c['concepts']} concepts done) - each concept ends with a question for you."}
    for c in taught:
        if not c['attempts']:
            return {'type': 'chapter', 'key': c['key'], 'label': f"Chapter test: {c['title']}",
                    'why': f'You have finished the lesson. Now prove it: {cn} questions, {cm} minutes, no hints. 80% or more = mastered.'}
    for u in units:
        if u['due'] and (u['last'] is None or u['last'] < 70):
            return {'type': 'unit', 'key': u['key'], 'label': f"{u['title']} - combined test",
                    'why': f'Combined tests mix the chapters together, like the real exam, so you have to recognise what each question needs. {un} questions, {um} minutes.'
                    if u['last'] is None else f"Your last unit score was {u['last']}%. Review the misses in the Error log, then retake for 70%+."}
    for c in taught:
        if c['state'] == 'tested':
            return {'type': 'chapter', 'key': c['key'], 'label': f"Retake: {c['title']}",
                    'why': f"Best so far is {c['best']}%. Retake (new questions every time) until you reach 80% - that is mastery."}
    if weak:
        return {'type': 'drill', 'label': 'Weak-spot drill',
                'why': 'These concepts are below 70% across your tests: ' + ', '.join(w['name'] for w in weak[:3]) + '. A 10-question drill targets just them.'}
    if taught:
        return {'type': 'section', 'label': f'{name.capitalize()} section simulation',
                'why': f'You are up to date. Practise under real GRE timing: section 1 ({s1n} Q, {s1m} min), then an adaptive section 2 ({s2n} Q, {s2m} min).'}
    if cls:  # nothing from this course is due yet, but a plan class is waiting
        return {'type': 'class', 'key': cls['day'], 'label': f"Start Day {cls['day']}: {cls['title']}",
                'why': f"Day {cls['day']} of your plan ({cls['section']}) is due. Your first {name} chapter comes later in the plan - start with today's class."}
    first = chapters[0]
    return {'type': 'lesson', 'key': first['key'], 'label': f"Get ahead: {first['title']}",
            'why': f'Your first {name} chapter is not scheduled yet - you can start early.'}


def course_test(kind, key=None, level='mixed', subject='quant'):
    ensure()
    m = mod(subject)
    seen = _seen(subject)  # verbal: also marks every answered question as used - it is never served again
    extra = {'seen': seen} if subject == 'verbal' else {}
    if subject == 'verbal':
        t = _verbal_test(kind, key, level, extra)
        if not t['questions']:
            return {'error': 'You have already answered every question this test could use, and no new sentences are ready yet. '
                             'Start Ollama and open a class - the app writes new sentences on your words in the background.'}
        return t
    if kind in ('chapter', 'unit'):
        return m.build_test(kind, key, **extra)
    if kind in ('section1', 'section2'):
        return m.build_test(kind, level=level, chapters=taught_chapters(subject=subject) or None, **extra)
    if kind == 'drill':
        concepts = [(w['chapter'], w['concept']) for w in course_state(subject)['weak'][:3]]
        if not concepts:
            pool = taught_chapters(subject=subject) or m.CHAPTERS[:4]
            concepts = [(c, i) for c in pool for i in range(len(m.LESSONS[c]))]
            random.shuffle(concepts)
            concepts = concepts[:4]
        return m.build_test('drill', concepts=concepts, **extra)
    raise ValueError(kind)


def _verbal_test(kind, key, level, extra):
    """A verbal test from hand-written questions you have never answered. Text-completion tests that run short are
    filled with new sentences (never answered before) on words you studied; the rest of the test is just shorter."""
    m = gre_verbal
    rng = random.Random()
    if kind in ('chapter', 'unit'):
        t = m.build_test(kind, key, avoid=gre_verbal.EXAMPLE_LIKE, **extra)
    elif kind in ('section1', 'section2'):
        t = m.build_test(kind, level=level, chapters=taught_chapters(subject='verbal') or None, **extra)
    elif kind == 'drill':
        concepts = [(w['chapter'], w['concept']) for w in course_state('verbal')['weak'][:3]]
        if not concepts:
            pool = taught_chapters(subject='verbal') or m.CHAPTERS[:4]
            concepts = [(c, i) for c in pool for i in range(len(m.LESSONS[c]))]
            random.shuffle(concepts)
            concepts = concepts[:4]
        t = m.build_test('drill', concepts=concepts, **extra)
    else:
        raise ValueError(kind)
    want = m.TEST_SPEC[kind][0]
    chs = ([key] if kind == 'chapter' else m.UNIT_BY_KEY[key]['chapters'] if kind == 'unit'
           else taught_chapters(subject='verbal') or ['tc_basic'])
    fill_ch = next((c for c in chs if c in ('tc_basic', 'tc_shift')), None)
    short = want - len(t['questions'])
    if fill_ch and (short > 0 or (kind == 'chapter' and key in VOCAB_CHAPTERS)):
        k = max(short, 3 if kind == 'chapter' else 0)  # chapter tests always include a few of your words in new sentences
        voc = _test_vocab(fill_ch, set(), k, rng)
        if voc and short < len(voc):  # make room: drop the easiest hand-written ones (they stay unseen for later)
            qs = t['questions']
            keep = set(sorted(range(len(qs)), key=lambda i: -qs[i].get('diff', 2))[:max(0, want - len(voc))])
            qs = [q for i, q in enumerate(qs) if i in keep]
        else:
            qs = t['questions']
        if kind == 'chapter':
            qs = sorted(qs + voc, key=lambda q: q.get('diff', 2))
        else:  # keep the GRE order: one-blank completions come first, passages stay together
            qs = voc + qs
        t['questions'] = qs
    t['fresh_note'] = (f"Only {len(t['questions'])} new questions were available (you have answered the rest)."
                       if len(t['questions']) < want else None)
    return t


def course_lesson(ch):
    ensure()
    m = mod_for(ch)
    if ch in VOCAB_CHAPTERS:  # start writing your-word sentences for this chapter's first clue style while you read the lesson
        try:
            from . import vocab_ctx
            done = _lessons().get(ch, {}).get('done', set())
            nxt = next((i for i in range(len(m.LESSONS[ch])) if i not in done), 0)
            style = CONCEPT_STYLE.get((ch, nxt)) or next((s for (k, _), s in CONCEPT_STYLE.items() if k == ch), None)
            words = [w for w in studied_words() if not vocab_ctx.styled_sentences(w, style)]
            if words:
                vocab_ctx.prepare_async(words[:12], style)
        except Exception as e:
            print('practice sentence prep failed:', e)
    return {**m.lesson(ch), 'subject': subject_of(ch), 'done': sorted(_lessons().get(ch, {}).get('done', ())),
            'tests': [_pct(t) for t in db.query("SELECT score, total FROM gre_tests WHERE kind='chapter' AND key=? ORDER BY at", (ch,))]}


def try_question(ch, c):
    if ch in gre_verbal.LESSONS:
        return gre_verbal.try_question(ch, c, _seen('verbal'))
    return gre_course.try_question(ch, c)


# ---------------------------------------------------------------- 10-question practice set after each lesson concept
PRACTICE_N = 10
VOCAB_CHAPTERS = {'tc_basic', 'tc_shift', 'tc_double', 'tc_triple'}  # text-completion chapters get questions on your own words
CONCEPT_STYLE = {('tc_basic', 1): 'restate', ('tc_basic', 2): 'cause', ('tc_shift', 0): 'contrast',
                 ('tc_shift', 1): 'time', ('tc_shift', 2): 'reversal'}  # the kind of clue each concept teaches


def studied_words():
    """Words from earlier sessions, missed-queue words first, then the shakiest ones (low Leitner box)."""
    ensure()
    t = today().isoformat()
    queue = [r['word'] for r in db.query('SELECT word FROM gre_vocab_queue WHERE cleared IS NULL AND added < ? ORDER BY added', (t,))]
    rest = [r['word'] for r in db.query("SELECT word FROM gre_vocab WHERE seen > 0 AND COALESCE(first_seen, '') < ? ORDER BY box, due", (t,))]
    words = list(dict.fromkeys(queue + rest))
    if not words:  # nothing practised yet: the groups introduced before the current class
        cur = status()['current'] or 1
        for g in unlocked_groups(cur - 1):
            words += gre_vocab.GROUPS.get(g, [])
    return [w for w in words if w in gre_vocab.DEFS]


def _vocab_tc(word, s, rng):
    from . import vocab_ctx
    choices = vocab_ctx.distractors(word, rng, list(gre_vocab.DEFS)) + [word]
    rng.shuffle(choices)
    return {'topic': 'vocab', 'kind': 'mc', 'word': word, 'q': s['sentence'], 'c': choices, 'a': choices.index(word), 'diff': 2,
            'x': f"{word}: {gre_vocab.DEFS[word]}. {s['clue'] or ''}".strip(), 'chapter': 'vocab', 'ctitle': 'Vocabulary in context',
            'cname': 'A word from your earlier sessions', 'format': 'tc'}


def practice_set(ch, c, n=PRACTICE_N):
    """n questions for one lesson concept. Quant: fresh generated questions. Verbal: the concept's hand-written questions
    (unseen first); in text-completion chapters about half are sentences built on words from your earlier sessions, using
    the clue type the concept teaches. Missing sentences are written in the background for the next set."""
    from . import vocab_ctx
    rng = random.Random()
    if ch not in gre_verbal.LESSONS:
        qs, texts = [], set()
        for _ in range(n * 3):
            q = gre_course.try_question(ch, c)
            if q['q'] not in texts:
                texts.add(q['q'])
                qs.append(q)
            if len(qs) >= n:
                break
        return {'questions': qs, 'vocab': 0, 'missing': 0, 'preparing': False, 'style': None}
    style = CONCEPT_STYLE.get((ch, c))
    vocab_qs, missing = [], []
    if ch in VOCAB_CHAPTERS:
        words = studied_words()
        head, tail = words[:10], words[10:]  # missed-queue / weakest words always get a chance, the rest rotate
        rng.shuffle(tail)
        for w in head + tail:
            ss = vocab_ctx.styled_sentences(w, style)
            if not ss:
                missing.append(w)
            elif len(vocab_qs) < n:
                vocab_qs.append(_vocab_tc(w, rng.choice(ss), rng))
        if missing:
            vocab_ctx.prepare_async(missing[:12], style)
    seen = _seen('verbal')
    mix = gre_verbal.DIFF_W['mixed']
    spare = vocab_qs[n // 2:]  # used only when the hand-written questions you have not answered run out
    vocab_qs = vocab_qs[:n // 2]
    want = n - len(vocab_qs)
    skip = gre_verbal.EXCLUDED | gre_verbal.EXAMPLE_LIKE  # bad ones, and near-copies of the worked example shown above
    skip = skip | gre_verbal.USED  # answered before: never again
    pool = [x for x in gre_verbal.QS if x['chapter'] == ch and x['concept'] == c and x['id'] not in skip]
    bank = gre_verbal._draw(rng, pool, want, seen, mix)
    if len(bank) < want:  # top up from the rest of the chapter
        ids = {x['id'] for x in bank}
        rest = [x for x in gre_verbal.QS if x['chapter'] == ch and x['id'] not in ids and x['id'] not in skip]
        bank += gre_verbal._draw(rng, rest, want - len(bank), seen, mix)
    bank.sort(key=lambda q: (q['diff'], q.get('pid') or ''))
    bank = [gre_verbal.serve(q, rng) for q in bank]
    vocab_qs += spare[:max(0, want - len(bank))]
    qs = []  # easy hand-written ones first, then alternate with your-word questions
    while bank or vocab_qs:
        if bank:
            qs.append(bank.pop(0))
        if vocab_qs:
            qs.append(vocab_qs.pop(0))
    return {'questions': qs, 'vocab': sum(1 for q in qs if q.get('word')), 'missing': min(len(missing), 12),  # one background batch
            'preparing': bool(missing) and vocab_ctx._state['running'], 'style': style}


def flag_sentence(word, sentence):
    """A vocab sentence the student reported as wrong or unclear: never served again (ok = -1)."""
    from . import vocab_ctx
    vocab_ctx.ensure()
    db.execute('UPDATE gre_vocab_ctx SET ok=-1 WHERE word=? AND sentence=?', (word, sentence))
    return {'ok': True}


def _practice_seen(days=None):
    """Keys of everything answered (gre_seen): bank ids, and 'v:<sentence>' for your-word sentences."""
    return seen_keys(days)


def _test_vocab(ch, avoided, n, rng):
    """Up to n your-word questions for a test, in sentences you have NOT met in practice. Words from questions that were
    left out because you just practised them come first (same word, new question), then your studied words."""
    from . import vocab_ctx
    seen = _practice_seen()
    first = []
    for q in gre_verbal.QS:  # answer words of the practised single-blank questions in this chapter
        if q['id'] in avoided and q['chapter'] == ch and q['kind'] == 'tc' and len(q['c']) == 1:
            w = q['c'][0][q['a'][0]]
            if w in gre_vocab.DEFS:
                first.append(w)
    styles = [s for (k, _), s in CONCEPT_STYLE.items() if k == ch] or [None]
    out, used = [], set()
    for w in list(dict.fromkeys(first)) + studied_words():
        if len(out) >= n or w in used:
            continue
        fresh = [s for s in vocab_ctx.sentences(w) if 'v:' + s['sentence'] not in seen]
        pref = [s for s in fresh if vocab_ctx.style_of(s['sentence']) & set(styles)] or fresh
        if pref:
            q = _vocab_tc(w, rng.choice(pref), rng)
            q['cname'] = 'Same word, new sentence' if w in first else q['cname']
            out.append(q)
            used.add(w)
    return out


def practice_answer(ch, c, b):
    """One practice answer: words feed the vocab boxes and missed-words queue; wrong course questions go to the error log.
    Every answered question is remembered and never served again (wrong ones come back as Error-log redos)."""
    ensure()
    correct = bool(b.get('correct'))
    key = str(b['gen']) if b.get('gen') in gre_verbal.BY_ID and not b.get('word') else ('v:' + str(b.get('q') or '')) if b.get('word') else None
    mark_seen(key, correct)
    if b.get('word'):
        vocab_answer(str(b['word']), correct)
    elif not correct and b.get('q'):
        m = mod_for(ch)
        it = b.get('item') if isinstance(b.get('item'), dict) else {}
        add_error(status()['current'], f"{m.title(ch)} · {m.concept_name(ch, c)}", 'Lesson practice', str(b['q'])[:2000],
                  str(b.get('answer') or '')[:500], str(b.get('x') or '')[:1000],
                  detail=_detail({**it, 'chapter': ch, 'concept': c}) if it.get('c') or it.get('kind') == 'ne' else None)
    return {'ok': True}


# ---------------------------------------------------------------- weekly summary test (last class of every week)
WEEK_QUANT = 20      # quant questions: fresh numbers on every quant topic of the week
WEEK_VERBAL = 10     # hand-written verbal questions you have not answered yet, on the week's verbal topics
WEEK_VOCAB_CHUNK = 40  # vocabulary is split into sections of this many words, so you get breaks


def week_of(n):
    return gre_plan.PLAN[n - 1]['week']


def week_days(w):
    return [p for p in gre_plan.PLAN if p['week'] == w]


def week_words(w):
    """Every word introduced in that week's classes."""
    return [x for p in week_days(w) if 'new' in p['vocab'] for x in gre_vocab.GROUPS[p['vocab']['new']]]


def _week_topics(w):
    out = []
    for p in week_days(w):
        out += p['quiz'] + list((p.get('course') or {}).get('ch') or [])
    return list(dict.fromkeys(out))


def week_info(n):
    """For the last class of a week: what its weekly test covers and your attempts so far."""
    days = week_days(week_of(n))
    if n != days[-1]['day']:
        return None
    w = week_of(n)
    topics = _week_topics(w)
    words = week_words(w)
    rows = db.query("SELECT title, score, total, at, COALESCE(subject,'quant') subject FROM gre_tests WHERE kind='week' AND key=? ORDER BY at", (str(w),))
    by_day = {}
    for r in rows:
        x = by_day.setdefault(r['at'][:10], [0, 0])
        x[0] += r['score'] or 0
        x[1] += r['total'] or 0
    try:
        from . import vocab_ctx
        vocab_ctx.prepare_async([x for x in words if not vocab_ctx.sentences(x)])
    except Exception as e:
        print('weekly sentence prep failed:', e)
    return {'week': w, 'words': len(words), 'quant': [topic_name(t) for t in topics if t in gre_course.GENS or t == 'qc'],
            'verbal': [topic_name(t) for t in topics if t in gre_verbal.LESSONS], 'days': [d['day'] for d in days],
            'attempts': [{'date': d, 'score': s, 'total': t, 'pct': round(100 * s / t) if t else 0} for d, (s, t) in by_day.items()],
            'missed_words': db.one("SELECT COUNT(*) n FROM gre_vocab_queue WHERE cleared IS NULL AND word IN (%s)" % ','.join('?' * len(words)),
                                   tuple(words))['n'] if words else 0}


def week_test(w):
    """Weekly summary test: Quant on every quant topic of the week (new numbers), Verbal on the week's verbal topics
    (questions you have never answered), and EVERY word introduced that week. Wrong answers go to the Error log /
    missed-words queue and come back until you get them right REDO_HITS times."""
    ensure()
    rng = random.Random()
    refresh_used()
    topics = _week_topics(w)
    last = week_days(w)[-1]['day']
    mix = gre_course.DIFF_MIX['mixed']
    qpool = [t for t in topics if t in gre_course.GENS or t == 'qc']
    count = Counter(qpool[i % len(qpool)] for i in range(WEEK_QUANT)) if qpool else {}
    quant = []
    for t, k in count.items():
        if t == 'qc':
            quant += [_quiz_item(q, 'qc', q.get('chapter')) for q in _qc_items(rng, k, last)]
        else:
            quant += [_quiz_item(q, t) for q in gre_course._pick(rng, t, k, mix)]
    rng.shuffle(quant)
    quant.sort(key=lambda q: q.get('diff', 2))
    verbal = []
    vt = [t for t in topics if t in gre_verbal.LESSONS]
    for i, t in enumerate(vt):
        k = WEEK_VERBAL // len(vt) + (1 if i < WEEK_VERBAL % len(vt) else 0)
        got = [gre_verbal.serve(q, rng) for q in gre_verbal.pick(rng, t, k, _seen('verbal'), 'mixed', avoid=gre_verbal.EXAMPLE_LIKE)]
        verbal += got + _fresh_vocab_fill(t, k - len(got), rng)
    words = week_words(w)
    vocab = []
    for q in _word_questions([{'word': x, 'hits': i} for i, x in enumerate(words)]):
        vocab.append({**q, 'kind': 'mc', 'topic': 'vocab', 'chapter': 'vocab', 'ctitle': 'Vocabulary', 'cname': f'Week {w} words',
                      'x': f"{q['word']}: {q['def']}", 'diff': 2 if q['format'] == 'sentence' else 1})
    sections = []
    if quant:
        sections.append({'subject': 'quant', 'title': f'Week {w} test · Quant', 'minutes': max(5, round(len(quant) * 1.75)), 'questions': quant})
    if verbal:
        sections.append({'subject': 'verbal', 'title': f'Week {w} test · Verbal', 'minutes': max(3, round(len(verbal) * 1.5)), 'questions': verbal})
    chunks = [vocab[i:i + WEEK_VOCAB_CHUNK] for i in range(0, len(vocab), WEEK_VOCAB_CHUNK)]
    for i, ch in enumerate(chunks):
        sections.append({'subject': 'verbal', 'title': f'Week {w} test · Vocabulary' + (f' ({i + 1} of {len(chunks)})' if len(chunks) > 1 else ''),
                         'minutes': max(3, round(len(ch) * 0.5)), 'questions': ch})
    return {'week': w, 'day': last, 'title': f'Week {w} summary test', 'sections': sections,
            'counts': {'quant': len(quant), 'verbal': len(verbal), 'words': len(vocab)}}


def day_course(n):
    """Tutor items attached to a plan day: chapter lessons/tests, unit tests, section simulations (quant and verbal)."""
    items = []
    for subject, m in SUBJECTS.items():
        items += [{'type': 'chapter', 'key': c, 'title': m.title(c), 'subject': subject} for c in m.CHAPTERS if m.CH_DAY[c] == n]
        units = [u['key'] for u in m.UNITS if u['day'] == n] + m.RETEST_DAYS.get(n, [])
        items += [{'type': 'unit', 'key': k, 'title': m.UNIT_BY_KEY[k]['title'], 'retest': n in m.RETEST_DAYS, 'subject': subject} for k in dict.fromkeys(units)]
        if n in m.SECTION_DAYS:
            (a, am), (b, bm) = m.TEST_SPEC['section1'], m.TEST_SPEC['section2']
            items.append({'type': 'section', 'subject': subject,
                          'title': f'{subject.capitalize()} section simulation ({a} Q / {am} min, then an adaptive {b} Q / {bm} min)'})
    if not items:
        return []
    les = _lessons()
    best = {}
    for t in db.query("SELECT kind, key, score, total FROM gre_tests WHERE kind IN ('chapter','unit')"):
        best[(t['kind'], t['key'])] = max(best.get((t['kind'], t['key']), 0), _pct(t))
    for it in items:
        if it['type'] == 'chapter':
            it.update(learnt=len(les.get(it['key'], {}).get('done', ())), concepts=len(mod_for(it['key']).LESSONS[it['key']]),
                      best=best.get(('chapter', it['key'])))
        elif it['type'] == 'unit':
            it['best'] = best.get(('unit', it['key']))
    return items


# ---------------------------------------------------------------- score prediction
DIFF_B = {1: -1.0, 2: 0.2, 3: 1.3}          # item difficulty on a logistic scale
SCALE = {'quant': (152, 7), 'verbal': (150, 7)}  # scaled score = base + slope × ability
PREDICT_DAYS = 45
PREDICT_MIN = 15


def predict(subject='quant'):
    """Rough GRE section score from your recent tests: a one-parameter logistic (Rasch-style) ability estimate
    with a mild prior, using each question's difficulty; section simulations count 1.5×. Drills are left out
    because they only target weak spots."""
    ensure()
    since = (today() - dt.timedelta(days=PREDICT_DAYS)).isoformat()
    obs, secs = [], []
    for t in _tests(subject):
        if t['kind'] == 'drill' or (t['at'] or '') < since:
            continue
        w = 1.5 if t['kind'] in ('section1', 'section2') else 1.0
        for it in json.loads(t['detail'] or '[]'):
            obs.append((DIFF_B.get(it.get('diff'), 0.2), 1 if it.get('correct') else 0, w))
            if it.get('secs'):
                secs.append(it['secs'])
    from . import results  # uploaded practice-test results (official ETS questions count 1.5×)
    for d, y, w, s in results.observations(subject, since):
        obs.append((DIFF_B.get(d, 0.2), y, w))
        if s:
            secs.append(s)
    col = 'quant' if subject == 'quant' else 'verbal'
    target = int(setting('gre_target_q' if subject == 'quant' else 'gre_target_v') or 0)
    last_mock = db.one(f'SELECT date, name, {col} AS score FROM gre_scores WHERE {col} IS NOT NULL ORDER BY date DESC LIMIT 1')
    base = {'subject': subject, 'n': len(obs), 'need': PREDICT_MIN, 'target': target, 'last_mock': last_mock}
    if len(obs) < PREDICT_MIN:
        return {**base, 'ready': False}
    th = 0.0
    for _ in range(30):
        g, h = -th, -1.0
        for b, y, w in obs:
            p = 1 / (1 + math.exp(-(th - b)))
            g += w * (y - p)
            h -= w * p * (1 - p)
        th -= g / h
    info = 1 + sum(w * p * (1 - p) for b, y, w in obs for p in [1 / (1 + math.exp(-(th - b)))])
    se = 1 / math.sqrt(info)
    b0, k = SCALE[subject]
    pace = sum(secs) / len(secs) if secs else None
    slow_by = (pace / PACE[subject] - 1) if pace else 0
    penalty = min(3, int(slow_by / 0.25)) if slow_by > 0.25 else 0  # the real test punishes slow pacing
    score = max(130, min(170, round(b0 + k * th - penalty)))
    lo = max(130, round(score - 1.3 * k * se))
    hi = min(170, round(score + 1.3 * k * se))
    return {**base, 'ready': True, 'score': score, 'lo': lo, 'hi': hi, 'pace': round(pace) if pace else None,
            'pace_target': round(PACE[subject]), 'penalty': penalty,
            'accuracy': round(100 * sum(y * w for _, y, w in obs) / sum(w for *_, w in obs))}


# ---------------------------------------------------------------- pacing
def speed_stats():
    """Per chapter: average seconds per question, share of slow questions, and accuracy fast vs slow."""
    ensure()
    rows = {}
    for t in db.query('SELECT detail FROM gre_tests'):
        for it in json.loads(t['detail'] or '[]'):
            ch, s = it.get('chapter'), it.get('secs')
            if not ch or not s or ch == 'vocab':  # your-word questions are not a course chapter
                continue
            x = rows.setdefault(ch, {'n': 0, 'secs': 0, 'slow': 0, 'slow_right': 0, 'fast_right': 0})
            x['n'] += 1
            x['secs'] += s
            if s > slow_limit(ch):
                x['slow'] += 1
                x['slow_right'] += 1 if it.get('correct') else 0
            else:
                x['fast_right'] += 1 if it.get('correct') else 0
    out = []
    for ch, x in rows.items():
        fast = x['n'] - x['slow']
        out.append({'chapter': ch, 'title': mod_for(ch).title(ch), 'subject': subject_of(ch), 'n': x['n'], 'avg': round(x['secs'] / x['n']),
                    'limit': slow_limit(ch), 'slow': x['slow'], 'slow_pct': round(100 * x['slow'] / x['n']),
                    'acc_fast': round(100 * x['fast_right'] / fast) if fast else None,
                    'acc_slow': round(100 * x['slow_right'] / x['slow']) if x['slow'] else None})
    return sorted(out, key=lambda r: -r['avg'])


def insights():
    return {'predict': {s: predict(s) for s in SUBJECTS}, 'speed': speed_stats(), 'errors': errors_summary(),
            'pace': {s: round(v) for s, v in PACE.items()}}


# ---------------------------------------------------------------- essays: AI feedback (local Ollama)
RUBRIC = """GRE Analytical Writing - Analyze an Issue - official score levels (summary):
6: insightful position; compelling, well-chosen examples; well organised; precise, fluent language; minor errors only.
5: thoughtful position; logically sound, well-chosen examples; well organised; clear language with only minor errors.
4: clear position; relevant but general or uneven support; adequately organised; adequate control of language, some errors.
3: vague or limited position or reasoning; weak or irrelevant examples; poor organisation; frequent problems in language.
2: seriously flawed: unclear position, little relevant support, serious language errors that obscure meaning.
1: fundamentally deficient: little evidence of an organised response; severe language errors.
0: off-topic, copied the prompt, or not in English."""

LENGTH_CAPS = [(120, 1.0), (200, 2.0), (300, 3.0), (380, 4.0)]  # (fewer than N words, highest score allowed)
EXAMPLE_MARKERS = ('for example', 'for instance', 'such as', 'consider', 'in 19', 'in 20', 'when i', 'case of')
TRANSITIONS = ('however', 'moreover', 'furthermore', 'therefore', 'consequently', 'nevertheless', 'in contrast', 'on the other hand',
               'admittedly', 'although', 'thus', 'in addition', 'ultimately', 'in conclusion')


def essay_stats(body):
    text = body or ''
    words = len(text.split())
    paras = [p for p in re.split(r'\n\s*\n|\n', text) if p.strip()]
    sents = [s for s in re.split(r'[.!?]+(?:\s|$)', text) if s.strip()]
    low = text.lower()
    st = {'words': words, 'paragraphs': len(paras), 'sentences': len(sents),
          'avg_sentence': round(words / len(sents), 1) if sents else 0,
          'examples': sum(low.count(m) for m in EXAMPLE_MARKERS), 'transitions': sum(low.count(t) for t in TRANSITIONS)}
    notes = []
    if words < 350:
        notes.append(f'{words} words is short. High-scoring Issue essays are usually about 450-600 words: two or three developed body paragraphs.')
    if len(paras) < 4:
        notes.append(f'Only {len(paras)} paragraph(s). Use intro → 2-3 body paragraphs (one example each) → counter-argument → conclusion.')
    if st['examples'] == 0:
        notes.append('No clear example markers ("for example", "consider…"). Raters reward specific, concrete examples.')
    if st['avg_sentence'] > 32:
        notes.append(f'Average sentence length is {st["avg_sentence"]} words - split some long sentences for clarity.')
    elif 0 < st['avg_sentence'] < 11:
        notes.append(f'Average sentence length is {st["avg_sentence"]} words - vary sentence structure with some longer, connected sentences.')
    if st['transitions'] < 3:
        notes.append('Few transition words (however, therefore, admittedly…). They make your reasoning easier to follow.')
    return st, notes


def _ollama_json(system, user, timeout=300):
    body = json.dumps({'model': db.get_setting('ollama_model'), 'stream': False, 'format': 'json',
                       'options': {'temperature': 0.2},
                       'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}).encode()
    req = urllib.request.Request(db.get_setting('ollama_url').rstrip('/') + '/api/chat', data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())['message']['content']


def essay_feedback(eid):
    """Score an essay against the ETS Issue rubric with the local model, plus rule-based notes that work offline."""
    ensure()
    e = db.one('SELECT * FROM gre_essays WHERE id=?', (eid,))
    if not e:
        return {'ok': False, 'error': 'Essay not found'}
    st, notes = essay_stats(e['body'])
    fb = {'stats': st, 'notes': notes, 'model': db.get_setting('ollama_model')}
    system = ('You are an experienced ETS rater scoring GRE "Analyze an Issue" essays. Be honest and specific; most practice essays '
              'score 3-4.5. Score holistically using this rubric:\n' + RUBRIC +
              '\nReply ONLY with JSON: {"score": number from 0 to 6 in steps of 0.5, "summary": one sentence, '
              '"strengths": [3 short strings], "improvements": [3 specific, actionable strings that quote or point to parts of the essay], '
              '"rewrite": "an improved version of the weakest paragraph"}')
    user = f"PROMPT: {e['prompt']}\n\nESSAY ({st['words']} words, written in {e['minutes'] or '?'} minutes):\n{e['body']}"
    try:
        raw = _ollama_json(system, user)
        try:
            data = json.loads(raw)
        except ValueError:
            m = re.search(r'\{.*\}', raw, re.S)
            data = json.loads(m.group(0)) if m else {'summary': raw}
        score = data.get('score')
        try:
            score = max(0.0, min(6.0, round(float(score) * 2) / 2))
        except (TypeError, ValueError):
            score = None
        # a small local model is generous with short essays; underdeveloped essays cannot score high on the real rubric
        cap = next((c for limit, c in LENGTH_CAPS if st['words'] < limit), None)
        if score is not None and cap is not None and score > cap:
            fb['capped_from'] = score
            notes.insert(0, f'The model gave {score}, capped at {cap} because a {st["words"]}-word essay is too short to be well developed.')
            score = cap
        fb.update(score=score, summary=str(data.get('summary') or ''),
                  strengths=[str(x) for x in (data.get('strengths') or [])][:4],
                  improvements=[str(x) for x in (data.get('improvements') or [])][:4], rewrite=str(data.get('rewrite') or ''))
        ok, err = True, None
    except Exception as ex:
        score, ok, err = None, False, f"Could not reach Ollama at {db.get_setting('ollama_url')} ({ex}). Start Ollama and try again - the notes below work without it."
        fb['error'] = err
    db.execute('UPDATE gre_essays SET ai_score=?, ai_feedback=?, ai_at=? WHERE id=?',
               (score, json.dumps(fb), dt.datetime.now().isoformat(timespec='seconds'), eid))
    return {'ok': ok, 'error': err, 'id': eid, 'ai_score': score, 'feedback': fb}


def essays():
    ensure()
    rows = db.query('SELECT * FROM gre_essays ORDER BY at DESC')
    for r in rows:
        r['ai_feedback'] = json.loads(r['ai_feedback']) if r.get('ai_feedback') else None
    return rows


# ---------------------------------------------------------------- notifications (called from engine.tick)
def tick(now, once, toast):
    ensure()
    if setting('gre_notify') != '1':
        return
    if now.weekday() == 6 and now.hour >= 18 and once(f"gre-week:{now.date()}"):
        try:
            toast('GRE weekly report', report_text(weekly_report(now.date()))[:200] + ' - open GRE Prep > Progress')
        except Exception as e:
            print('weekly report failed:', e)
    card = today_card(now.date())
    if not card or card.get('finished') or not card.get('study_today'):
        return
    h, m = (setting('gre_time') or '20:00').split(':')
    start = int(h) * 60 + int(m)
    mins = now.hour * 60 + now.minute
    lead = int(db.get_setting('lead_minutes') or 10)
    if start - lead <= mins <= start + 5 and once(f"gre:{now.date()}"):
        extra = f" | {card['vocab_due']} vocab cards due" if card['vocab_due'] else ''
        extra += f" | {card['errors_due']} mistakes to redo" if card.get('errors_due') else ''
        behind = f" | {card['behind']} day(s) behind" if card['behind'] else ''
        toast(f"GRE class at {card['time']}: Day {card['day']}", f"{card['section']} - {card['title']}{extra}{behind}"[:200])


# ---------------------------------------------------------------- formula & rule cards (spaced repetition of the notes' rule boxes)
CARDS_NEW_PER_DAY = 15
_CARDS = None


def _cloze(text):
    """Turn a rule into a recall card: hide what comes after the first ':' / '=' / '→'."""
    for sep in (': ', ' = ', ' → '):
        i = text.find(sep)
        if 3 < i < 90:
            return text[:i + len(sep)].rstrip() + ' …?'
    words = text.split()
    k = max(3, len(words) // 3)
    return 'Complete the rule: ' + ' '.join(words[:k]) + ' …'


def card_list():
    """Every rule box of the quant and verbal notes, with the day its note is first read."""
    global _CARDS
    if _CARDS is None:
        days = {x['id']: (min(x['days']) if x['days'] else None) for x in gre_notes.library()}
        out = []
        for key, n in gre_notes.NOTES.items():
            if n['subject'] not in ('quant', 'verbal'):
                continue
            for i, b in enumerate(gre_notes.get(key)['blocks']):
                if b['t'] == 'rule':
                    out.append({'id': f'{key}:{i}', 'note': key, 'topic': n['title'], 'subject': n['subject'],
                                'front': _cloze(b['text']), 'back': b['text'], 'day': days.get(key)})
        _CARDS = out
    return _CARDS


def cards_state():
    ensure()
    cur = status()['current'] or len(gre_plan.PLAN)
    t0 = today().isoformat()
    rows = {r['id']: r for r in db.query('SELECT * FROM gre_cards')}
    unlocked = [c for c in card_list() if c['day'] and c['day'] <= cur]
    intro = db.one('SELECT COUNT(*) n FROM gre_cards WHERE first_seen=?', (t0,))['n']
    left = max(0, CARDS_NEW_PER_DAY - intro)
    due_seen = [c for c in unlocked if c['id'] in rows and (rows[c['id']]['due'] or '') <= t0]
    new = [c for c in unlocked if c['id'] not in rows]
    due = [{**c, 'box': rows[c['id']]['box']} for c in due_seen] + [{**c, 'box': 0} for c in new[:left]]
    random.shuffle(due)
    boxes = {b: sum(1 for r in rows.values() if r['box'] == b) for b in range(1, 6)}
    return {'due': due, 'boxes': boxes, 'unlocked': len(unlocked), 'total': len(card_list()), 'new_left': left, 'new_waiting': max(0, len(new) - left)}


def card_answer(cid, correct):
    ensure()
    r = db.one('SELECT * FROM gre_cards WHERE id=?', (cid,)) or {'box': 1, 'seen': 0, 'correct': 0}
    box = min(5, r['box'] + 1) if correct else 1
    due = (today() + dt.timedelta(days=BOX_DAYS[box])).isoformat()
    db.execute('INSERT INTO gre_cards(id,box,due,seen,correct,first_seen) VALUES (?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET '
               'box=excluded.box, due=excluded.due, seen=excluded.seen, correct=excluded.correct',
               (cid, box, due, r['seen'] + 1, r['correct'] + (1 if correct else 0), today().isoformat()))
    return {'ok': True, 'box': box}


# ---------------------------------------------------------------- "report a bad question"
def load_exclusions():
    """Questions you reported are not served again: verbal bank ids, quant generators, hand-written quiz questions."""
    rows = db.query('SELECT kind, ref, text FROM gre_flags')
    gre_verbal.EXCLUDED = {r['ref'] for r in rows if r['kind'] == 'verbal'}
    gre_course.EXCLUDED_GENS = {r['ref'] for r in rows if r['kind'] == 'quant'}
    gre_course.EXCLUDED_TEXT = {r['text'] for r in rows if r['kind'] == 'bank'}


def flag_question(b):
    ensure()
    kind = b.get('kind') if b.get('kind') in ('vocab_sentence', 'verbal', 'quant', 'bank', 'other') else 'other'
    ref, text = str(b.get('ref') or '')[:200], str(b.get('text') or '')[:2000]
    db.execute('INSERT INTO gre_flags(at, kind, ref, text, note) VALUES (?,?,?,?,?)',
               (dt.datetime.now().isoformat(timespec='seconds'), kind, ref, text, str(b.get('note') or '')[:500]))
    if kind == 'vocab_sentence':  # hide that sentence; the generator writes a new one later
        db.execute('UPDATE gre_vocab_ctx SET ok=-1 WHERE word=? AND sentence=?', (ref, text))
    load_exclusions()
    return {'ok': True}


# ---------------------------------------------------------------- weekly report
def weekly_report(end=None):
    """The last 7 days: classes, time, quizzes, tests, vocab, mistakes, predicted scores, weak topics, next week."""
    ensure()
    end = end or today()
    start = end - dt.timedelta(days=6)
    a, z = start.isoformat(), end.isoformat()
    zz = z + 'T99'
    prog = db.query('SELECT day, minutes FROM gre_progress WHERE done=1 AND done_on BETWEEN ? AND ?', (a, z))
    quizzes = db.query('SELECT score, total FROM gre_quiz WHERE at BETWEEN ? AND ?', (a, zz))
    tests = db.query("SELECT COALESCE(subject,'quant') subject, score, total FROM gre_tests WHERE at BETWEEN ? AND ?", (a, zz))
    pct = lambda rs: round(100 * sum(r['score'] for r in rs) / max(1, sum(r['total'] for r in rs))) if rs else None
    sched = schedule()
    nxt = [{'day': i + 1, 'date': d.isoformat(), 'title': gre_plan.PLAN[i]['title'], 'section': gre_plan.PLAN[i]['section']}
           for i, d in enumerate(sched) if end < d <= end + dt.timedelta(days=7)]
    weak = []
    for subj in SUBJECTS:
        weak += [{'title': w['name'], 'topic': w['title'], 'pct': w['pct']} for w in course_state(subj)['weak'][:2]]
    from . import results
    weak += [{'title': w['title'], 'topic': 'Practice tests', 'pct': w['pct']} for w in results.weak_topics()[:2]]
    st = status(end)
    return {
        'start': a, 'end': z,
        'classes': len(prog), 'minutes': sum(r['minutes'] or 0 for r in prog), 'behind': st['behind'], 'current': st['current'],
        'quizzes': len(quizzes), 'quiz_pct': pct(quizzes),
        'tests': {s: {'n': sum(1 for t in tests if t['subject'] == s), 'pct': pct([t for t in tests if t['subject'] == s])} for s in SUBJECTS},
        'new_words': db.one('SELECT COUNT(*) n FROM gre_vocab WHERE first_seen BETWEEN ? AND ?', (a, z))['n'],
        'words_cleared': db.one('SELECT COUNT(*) n FROM gre_vocab_queue WHERE cleared BETWEEN ? AND ?', (a, z))['n'],
        'words_missed': db.one('SELECT COUNT(*) n FROM gre_vocab_queue WHERE added BETWEEN ? AND ?', (a, z))['n'],
        'queue_open': db.one('SELECT COUNT(*) n FROM gre_vocab_queue WHERE cleared IS NULL')['n'],
        'mistakes': db.one('SELECT COUNT(*) n FROM gre_errors WHERE created BETWEEN ? AND ?', (a, z))['n'],
        'errors_open': db.one("SELECT COUNT(*) n FROM gre_errors WHERE status='Open'")['n'],
        'predict': {s: {k: predict(s).get(k) for k in ('ready', 'score', 'lo', 'hi', 'target', 'n', 'need')} for s in SUBJECTS},
        'weak': weak[:6], 'next': nxt,
    }


def report_text(r):
    bits = [f"{r['classes']} classes ({round(r['minutes'] / 60, 1)} h)"]
    if r['quiz_pct'] is not None:
        bits.append(f"quizzes {r['quiz_pct']}%")
    bits.append(f"{r['words_cleared']} words cleared, {r['queue_open']} in queue")
    if r['behind']:
        bits.append(f"{r['behind']} behind plan")
    return ' | '.join(bits)


# ---------------------------------------------------------------- smart revision (what to revise right now)
def smart_revision():
    ensure()
    qs = queue_state()
    cs = cards_state()
    return {
        'warmup': len(qs['warmup']), 'eod': len(eod_rows()), 'errors_due': errors_summary()['due'],
        'cards': len(cs['due']),
        'weak': {s: course_state(s)['weak'][:3] for s in SUBJECTS},
        'test_weak': _test_weak_all(),
    }


def _test_weak_all():
    from . import results
    return results.weak_topics()[:4]


# ---------------------------------------------------------------- full-length practice test inside the app
def mock_start():
    rng = random.Random()
    return {'prompt': rng.choice(gre_quiz.ESSAY_PROMPTS),
            'plan': [{'type': 'essay', 'title': 'Analytical Writing - Issue essay', 'minutes': 30},
                     {'type': 'section', 'subject': 'verbal', 'kind': 'section1'},
                     {'type': 'section', 'subject': 'quant', 'kind': 'section1'},
                     {'type': 'section', 'subject': 'verbal', 'kind': 'section2'},
                     {'type': 'section', 'subject': 'quant', 'kind': 'section2'}]}


def _estimate(obs, subject):
    """Scaled-score estimate from (difficulty, correct, weight) observations - the predictor's model without the prior window."""
    if not obs:
        return None
    th = 0.0
    for _ in range(30):
        g, h = -th, -1.0
        for b, y, w in obs:
            p = 1 / (1 + math.exp(-(th - b)))
            g += w * (y - p)
            h -= w * p * (1 - p)
        th -= g / h
    b0, k = SCALE[subject]
    return max(130, min(170, round(b0 + k * th)))


def mock_finish(b):
    """Estimated Quant / Verbal scores for an in-app full test; saved to the practice-test score list."""
    ensure()
    out = {}
    for subj in SUBJECTS:
        items = [it for s in b.get('sections', []) if s.get('subject') == subj for it in s.get('items', [])]
        # section 2 questions weigh more, as on the real section-adaptive test
        obs = [(DIFF_B.get(it.get('diff'), 0.2), 1 if it.get('correct') else 0, 1.5 if s.get('kind') == 'section2' else 1.0)
               for s in b.get('sections', []) if s.get('subject') == subj for it in s.get('items', [])]
        out[subj] = {'score': _estimate(obs, subj), 'right': sum(1 for it in items if it.get('correct')), 'total': len(items)}
    name = f"In-app full practice test ({today().strftime('%d %b')})"
    db.execute('INSERT INTO gre_scores(date,name,quant,verbal,awa,notes) VALUES (?,?,?,?,?,?)',
               (today().isoformat(), name, out['quant']['score'], out['verbal']['score'], b.get('awa'), 'In-app mock'))
    return {'ok': True, 'scores': out, 'name': name}
