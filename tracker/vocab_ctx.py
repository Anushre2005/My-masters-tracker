"""GRE-style vocabulary questions: each GregMat word is tested inside a one-blank text-completion sentence.

The local Ollama model writes a sentence with a context clue for each word, then a second, independent pass solves
the question from the five choices; only sentences it answers with the intended word are kept. Sentences are cached
in the database, prepared in the background a few days ahead, and reused (a different sentence each time when
several exist). Until a word has a checked sentence, its quiz question asks you to pick the word that matches a
meaning - still five GRE words as choices.
"""
import datetime as dt
import json
import random
import re
import threading

from . import db, gre_vocab

SCHEMA = """
CREATE TABLE IF NOT EXISTS gre_vocab_ctx (
    word TEXT, sentence TEXT, clue TEXT, ok INTEGER, created TEXT, PRIMARY KEY (word, sentence));
"""
BATCH = 6          # words per model call
MAX_TRIES = 3      # attempts per word before giving up (falls back to the meaning question)
_lock = threading.Lock()
_state = {'running': False, 'last_error': None}
_ready = False
STOP = {'having', 'being', 'which', 'something', 'someone', 'their', 'about', 'without', 'other', 'things', 'thing', 'very', 'extremely',
        'person', 'people', 'quality', 'state', 'showing', 'making', 'causing', 'given', 'great'}


def ensure():
    global _ready
    if not _ready:
        with db._lock:
            db.con().executescript(SCHEMA)
            db.con().commit()
        _ready = True


def _keys(defn):
    return {w for w in re.findall(r'[a-z]{5,}', defn.lower()) if w not in STOP}


def _stem(word):
    w = word.lower()
    return w[:max(4, len(w) - 3)]


def distractors(word, rng, pool, k=4):
    """Other GRE words whose meanings are clearly different from the target's (so only one choice fits)."""
    target = _keys(gre_vocab.DEFS[word])
    cands = [w for w in pool if w != word and not (target & _keys(gre_vocab.DEFS[w])) and _stem(w) != _stem(word)]
    if len(cands) < k:
        cands = [w for w in gre_vocab.DEFS if w != word and not (target & _keys(gre_vocab.DEFS[w]))]
    return rng.sample(cands, k)


def sentences(word):
    ensure()
    return db.query('SELECT sentence, clue FROM gre_vocab_ctx WHERE word=? AND ok=1', (word,))


def status(words):
    ensure()
    if not words:
        return {'ready': 0, 'total': 0, 'running': _state['running']}
    rows = db.query(f"SELECT DISTINCT word FROM gre_vocab_ctx WHERE ok=1 AND word IN ({','.join('?' * len(words))})", tuple(words))
    return {'ready': len(rows), 'total': len(words), 'running': _state['running'], 'error': _state['last_error']}


def question(word, rng, pool):
    """One vocabulary question in GRE format (5 choices, one right)."""
    others = distractors(word, rng, pool)
    choices = others + [word]
    rng.shuffle(choices)
    ss = sentences(word)
    if ss:
        s = rng.choice(ss)
        return {'topic': 'vocab', 'kind': 'mc', 'word': word, 'q': s['sentence'], 'c': choices, 'a': choices.index(word),
                'x': f"{word}: {gre_vocab.DEFS[word]}. {s['clue'] or ''}".strip(), 'chapter': 'vocab', 'ctitle': 'Vocabulary in context',
                'cname': 'Text completion with this week\'s words', 'diff': 2, 'format': 'tc'}
    return {'topic': 'vocab', 'kind': 'mc', 'word': word, 'q': f'Which word means: “{gre_vocab.DEFS[word]}”?', 'c': choices, 'a': choices.index(word),
            'x': f'{word}: {gre_vocab.DEFS[word]}', 'chapter': 'vocab', 'ctitle': 'Vocabulary', 'cname': 'Word meaning', 'diff': 1, 'format': 'meaning'}


# ---------------------------------------------------------------- generation (background)
def _ask(system, user, temperature):
    body_opts = {'temperature': temperature}
    import urllib.request
    req = urllib.request.Request(db.get_setting('ollama_url').rstrip('/') + '/api/chat', headers={'Content-Type': 'application/json'},
                                 data=json.dumps({'model': db.get_setting('ollama_model'), 'stream': False, 'format': 'json', 'options': body_opts,
                                                  'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]}).encode())
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = json.loads(r.read())['message']['content']
    try:
        return json.loads(raw)
    except ValueError:
        m = re.search(r'\{.*\}', raw, re.S)
        return json.loads(m.group(0)) if m else {}


GEN_SYSTEM = (
    'You write GRE Text Completion sentences to test vocabulary. For each word you get, write ONE sentence (15-35 words) with exactly one '
    'blank written as ______ where the given word, in the given meaning, is the only good fit. The sentence MUST contain a clear context clue: '
    'a restatement after a colon or semicolon, a contrast ("although", "but", "rather than"), or a cause ("because", "so"). Do not use the '
    'word itself or any form of it anywhere in the sentence. Sound like the GRE: academic topics (science, history, art, economics, '
    'politics, literature). Reply ONLY with JSON: {"items": [{"word": "...", "sentence": "...", "clue": "one short sentence explaining which words point to the answer"}]}')
SOLVE_SYSTEM = ('You are taking GRE Text Completion questions. For each one, choose the single choice that best fills the blank. '
                'Reply ONLY with JSON: {"answers": [{"id": 1, "choice": "the word you chose"}]}')


def _valid(word, s):
    s = (s or '').strip()
    return (s.count('______') == 1 and 60 <= len(s) <= 320 and _stem(word) not in s.lower() and word.lower() not in s.lower())


def generate(words):
    """Write and check sentences for these words (skips words that already have one or have failed MAX_TRIES times)."""
    ensure()
    tries = {r['word']: r['n'] for r in db.query('SELECT word, COUNT(*) n FROM gre_vocab_ctx WHERE ok=0 GROUP BY word')}
    done = {r['word'] for r in db.query('SELECT DISTINCT word FROM gre_vocab_ctx WHERE ok=1')}
    todo = [w for w in words if w in gre_vocab.DEFS and w not in done and tries.get(w, 0) < MAX_TRIES]
    rng = random.Random()
    made = 0
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        got = _ask(GEN_SYSTEM, '\n'.join(f'- {w}: {gre_vocab.DEFS[w]}' for w in batch), 0.7).get('items') or []
        cands = []
        for it in got:
            w = str(it.get('word', '')).strip().lower()
            w = next((b for b in batch if b.lower() == w), None)
            if w and _valid(w, it.get('sentence')):
                cands.append({'word': w, 'sentence': re.sub(r'_{3,}', '______', it['sentence'].strip()), 'clue': str(it.get('clue') or '')[:300]})
        failed = set(batch) - {c['word'] for c in cands}
        if cands:  # independent check: can the question be solved, and only with the intended word?
            qs = []
            for k, c in enumerate(cands):
                ch = distractors(c['word'], rng, list(gre_vocab.DEFS)) + [c['word']]
                rng.shuffle(ch)
                qs.append({'id': k + 1, 'sentence': c['sentence'], 'choices': ch})
            ans = {a.get('id'): str(a.get('choice', '')).strip().lower() for a in (_ask(SOLVE_SYSTEM, json.dumps({'questions': qs}), 0).get('answers') or [])
                   if isinstance(a, dict)}
            now = dt.datetime.now().isoformat(timespec='seconds')
            for k, c in enumerate(cands):
                ok = ans.get(k + 1) == c['word'].lower()
                db.execute('INSERT OR IGNORE INTO gre_vocab_ctx(word, sentence, clue, ok, created) VALUES (?,?,?,?,?)',
                           (c['word'], c['sentence'], c['clue'], 1 if ok else 0, now))
                made += ok
        now = dt.datetime.now().isoformat(timespec='seconds')
        for w in failed:  # count unusable output as a failed try too
            db.execute('INSERT OR IGNORE INTO gre_vocab_ctx(word, sentence, clue, ok, created) VALUES (?,?,?,?,?)', (w, f'(invalid {now} {random.random()})', '', 0, now))
    return made


def prepare_async(words):
    """Start background generation for these words unless it is already running or Ollama is down."""
    words = [w for w in words if w in gre_vocab.DEFS]
    if not words:
        return False
    with _lock:
        if _state['running']:
            return False
        _state['running'] = True

    def run():
        try:
            from . import ai
            if not ai.models().get('ok'):
                _state['last_error'] = 'Ollama is not running'
                return
            _state['last_error'] = None
            generate(words)
        except Exception as e:
            _state['last_error'] = str(e)[:200]
            print('vocab sentence generation failed:', e)
        finally:
            _state['running'] = False

    threading.Thread(target=run, daemon=True).start()
    return True
