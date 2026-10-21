"""Study notes: topic-wise reading for each class (the "tuition handout"), revision sheets, and printable pages.

Notes live in gre_notes_quant / gre_notes_verbal as light markup (see gre_notes_quant's docstring). Each plan day
gets its notes through DAY_NOTES (keyed by the day's title, like gre_plan.OFFICIAL). Review and revision days get
a revision sheet instead: the rules, traps and quick checks pulled from the notes being revised.
"""
import html

from . import gre_plan
from .gre_notes_quant import NOTES as _Q
from .gre_notes_verbal import NOTES as _V

NOTES = {**_Q, **_V}

QUANT_ALL = list(_Q)
VERBAL_ALL = [k for k, v in _V.items() if v['subject'] == 'verbal']
WRITING_ALL = ['awa', 'awa_examples', 'awa_counter']

# day title -> ('note', [ids]) to read in full, or ('sheet', [ids]) for a revision sheet
DAY_NOTES = {
    'How the GRE works + baseline': ('note', ['gre_overview']),
    'Math strategy, mental math and QC basics': ('note', ['math_strategy']),
    'How to learn vocab + text completion with clues': ('note', ['tc_clues']),
    'Number line, signs, decimals and order of operations': ('note', ['arith']),
    'Text completion: shift words': ('note', ['tc_shift']),
    'Fractions': ('note', ['fractions']),
    'Two-blank text completions': ('note', ['tc_double']),
    'Fraction word problems and estimation': ('note', ['fraction_wp']),
    'Vocabulary in context: second meanings and word roots': ('note', ['vocab_context']),
    'Divisibility, primes, factors, GCF and LCM': ('note', ['divisibility']),
    'Three-blank text completions': ('note', ['tc_triple']),
    'Odds/evens, remainders and testing cases': ('note', ['odd_even']),
    'Sentence equivalence': ('note', ['se']),
    'Number properties: mixed practice': ('note', ['np_mixed']),
    'Text completion + sentence equivalence: timed set': ('note', ['verbal_pacing']),
    'Exponents': ('note', ['exponents']),
    'Reading comprehension: method': ('note', ['rc_method']),
    'Roots': ('note', ['roots']),
    'Reading comprehension: question types': ('note', ['rc_types']),
    'Algebra: expressions and factoring': ('note', ['algebra_expr']),
    'Linear equations and systems': ('note', ['linear']),
    'Long reading passages': ('note', ['rc_long']),
    'Quadratics and harder equations': ('note', ['quadratics']),
    'Critical reasoning: arguments, weaken and strengthen': ('note', ['cr1']),
    'Inequalities and absolute value': ('note', ['inequalities']),
    'Functions, symbols and formulas': ('note', ['functions']),
    'Critical reasoning: paradox, boldface and flaws': ('note', ['cr2']),
    'Quantitative comparison strategies': ('note', ['qc']),
    'Analytical Writing: the Issue essay': ('note', ['awa']),
    'Critical reasoning + RC mixed set': ('note', ['cr_in_rc']),
    'Percents': ('note', ['percents']),
    'Hard text completions': ('note', ['tc_hard']),
    'Ratios and proportions': ('note', ['ratios']),
    'Reading: science passages and inference': ('note', ['rc_science']),
    'Word problems: setting up, age and motion': ('note', ['word_motion']),
    'Work, growth, mixtures and overlapping sets': ('note', ['work_mix_sets']),
    'Issue essay #2 + RC practice': ('note', ['awa_examples']),
    'Sequences, consecutive integers, backsolving and VICs': ('note', ['sequences']),
    'Mixed text completion + sentence equivalence': ('sheet', ['tc_clues', 'tc_shift', 'tc_double', 'tc_triple', 'se']),
    'Statistics I: mean, median, mode and weighted averages': ('note', ['stats1']),
    'Statistics II: spread, quartiles and the normal distribution': ('note', ['stats2']),
    'Sentence equivalence + RC': ('sheet', ['se', 'rc_types']),
    'Counting': ('note', ['counting']),
    'Critical reasoning: timed set': ('sheet', ['cr1', 'cr2']),
    'Probability basics': ('note', ['prob1']),
    'Full practice test 1 (ETS POWERPREP)': ('note', ['mock_review']),
    'Probability: "at least", combinations and strategy': ('note', ['prob2']),
    'Issue essay #3 + RC': ('note', ['awa_counter']),
    'Data interpretation': ('note', ['di1']),
    'Timed verbal section 1': ('note', ['verbal_section']),
    'Data interpretation II: tricky charts and estimation': ('note', ['di2']),
    'Lines, angles and triangles': ('note', ['triangles']),
    'Reading: humanities and social-science passages': ('note', ['rc_humanities']),
    'Polygons and circles': ('note', ['circles_polys']),
    'Issue essay #4 + critical reasoning review': ('sheet', ['awa', 'awa_examples', 'awa_counter', 'cr1', 'cr2']),
    'Coordinate geometry': ('note', ['coordinate']),
    'Full practice test 2 (Manhattan Prep free test)': ('note', ['mock_review']),
    '3-D shapes and mixed geometry + geometry unit test': ('note', ['solids']),
    'Timed verbal section 2': ('note', ['verbal_section']),
    'Revision: arithmetic and number properties': ('sheet', ['arith', 'fractions', 'fraction_wp', 'divisibility', 'odd_even', 'exponents', 'roots']),
    'Vocabulary sweep + text completion': ('sheet', ['vocab_context', 'tc_hard']),
    'Revision: algebra and inequalities': ('sheet', ['algebra_expr', 'linear', 'quadratics', 'inequalities', 'functions']),
    'Revision: word problems and rates': ('sheet', ['word_motion', 'work_mix_sets', 'sequences']),
    'Two timed verbal sections': ('note', ['verbal_section']),
    'Revision: percents, ratios and statistics': ('sheet', ['percents', 'ratios', 'stats1', 'stats2']),
    'Issue essay #5 + mixed quant': ('sheet', WRITING_ALL),
    'Revision: counting and probability': ('sheet', ['counting', 'prob1', 'prob2']),
    'Full practice test 3': ('note', ['mock_review']),
    'Revision: geometry and coordinate geometry': ('sheet', ['triangles', 'circles_polys', 'coordinate', 'solids']),
    'Reading endurance: long passages under time': ('sheet', ['rc_method', 'rc_types', 'rc_long']),
    'Two timed quant sections': ('note', ['quant_pacing']),
    'Critical reasoning + boldface revision': ('sheet', ['cr1', 'cr2']),
    'Hard-problem day': ('note', ['hard_quant']),
    'Full practice test 4': ('note', ['mock_review']),
    'Weak-area day (quant) + unit retests': ('note', ['hard_quant']),
    'Weak-area day (verbal) + vocab sweep': ('sheet', ['vocab_context', 'tc_hard', 'se']),
    'Issue essay #6 under test conditions': ('sheet', WRITING_ALL),
    'Quant section simulation + review': ('note', ['quant_pacing']),
    'Verbal section simulation + review': ('note', ['verbal_section']),
    'Full practice test 5 (official ETS questions)': ('note', ['mock_review']),
    'Review test 5 + Error-log sweep + unit retests': ('note', ['mock_review']),
    'Speed day: data interpretation and quantitative comparison': ('sheet', ['qc', 'di1', 'di2']),
    'Full verbal under time (two sections)': ('note', ['verbal_section']),
    'Final essay + your essay template': ('sheet', WRITING_ALL),
    'Light quant review': ('sheet', QUANT_ALL),
    'Final full practice test (ETS POWERPREP 2)': ('note', ['mock_review']),
    'Review the final test + Error log': ('note', ['mock_review']),
    'Light verbal review': ('sheet', VERBAL_ALL),
    'Test-day preparation': ('note', ['test_day']),
    'Rest day / test day': ('note', ['test_day']),
}


# ---------------------------------------------------------------- parsing
def parse(body):
    """Markup → list of blocks: {'t': 'h'|'h2'|'p'|'rule'|'tip'|'trap'|'ex'|'check'|'list'|'table', ...}."""
    blocks = []
    for raw in body.strip('\n').split('\n'):
        line = raw.strip()
        if not line:
            continue
        if line.startswith('## '):
            blocks.append({'t': 'h2', 'text': line[3:]})
        elif line.startswith('# '):
            blocks.append({'t': 'h', 'text': line[2:]})
        elif line.startswith('! '):
            blocks.append({'t': 'rule', 'text': line[2:]})
        elif line.startswith('> '):
            blocks.append({'t': 'tip', 'text': line[2:]})
        elif line.startswith('x '):
            blocks.append({'t': 'trap', 'text': line[2:]})
        elif line.startswith('EX:'):
            parts = [p.strip() for p in line[3:].split(' || ')]
            ans = parts[-1][2:].strip() if parts[-1].startswith('=>') else ''
            steps = parts[1:-1] if ans else parts[1:]
            blocks.append({'t': 'ex', 'q': parts[0], 'steps': steps, 'a': ans})
        elif line.startswith('Q:'):
            q, _, a = line[2:].rpartition(' => ')
            blocks.append({'t': 'check', 'q': (q or a).strip(), 'a': a.strip() if q else ''})
        elif line.startswith('|'):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if blocks and blocks[-1]['t'] == 'table':
                blocks[-1]['rows'].append(cells)
            else:
                blocks.append({'t': 'table', 'head': cells, 'rows': []})
        elif line.startswith('- '):
            if blocks and blocks[-1]['t'] == 'list':
                blocks[-1]['items'].append(line[2:])
            else:
                blocks.append({'t': 'list', 'items': [line[2:]]})
        else:
            blocks.append({'t': 'p', 'text': line})
    return blocks


_cache = {}


def get(key):
    if key not in _cache:
        n = NOTES[key]
        _cache[key] = {'id': key, 'title': n['title'], 'minutes': n['minutes'], 'subject': n['subject'], 'blocks': parse(n['body'])}
    return _cache[key]


def sheet(keys, title):
    """Revision sheet: rules, traps, a worked example and the quick checks of each note."""
    secs = []
    for k in keys:
        n = get(k)
        keep = [b for b in n['blocks'] if b['t'] in ('rule', 'trap', 'check', 'table')]
        ex = next((b for b in n['blocks'] if b['t'] == 'ex'), None)
        if ex:
            keep.append(ex)
        secs.append({'id': k, 'title': n['title'], 'blocks': keep})
    return {'title': title, 'minutes': max(10, min(30, 3 * len(keys))), 'sections': secs}


# ---------------------------------------------------------------- per day
def _week_notes(day):
    """Full notes read during this day's week, before this day (for Saturday reviews)."""
    week = gre_plan.PLAN[day - 1]['week']
    out = []
    for p in gre_plan.PLAN:
        if p['week'] == week and p['day'] < day:
            kind, ids = DAY_NOTES.get(p['title'], ('', []))
            if kind == 'note':
                out += [i for i in ids if i not in out and i not in ('gre_overview', 'mock_review')]
    return out


def for_day(n):
    p = gre_plan.PLAN[n - 1]
    kind, ids = DAY_NOTES.get(p['title'], (None, []))
    if kind is None and p['section'] == 'Review':
        ids = _week_notes(n)
        kind = 'sheet' if ids else None
    out = {'notes': [], 'sheet': None}
    if kind == 'note':
        out['notes'] = [get(i) for i in ids]
    elif kind == 'sheet':
        title = f"Week {p['week']} revision sheet" if p['section'] == 'Review' and p['title'] not in DAY_NOTES else f"Revision sheet: {p['title']}"
        out['sheet'] = sheet(ids, title)
    return out


def library():
    used = {}
    for p in gre_plan.PLAN:
        kind, ids = DAY_NOTES.get(p['title'], ('', []))
        if kind == 'note':
            for i in ids:
                used.setdefault(i, []).append(p['day'])
    return [{'id': k, 'title': v['title'], 'minutes': v['minutes'], 'subject': v['subject'], 'days': used.get(k, [])}
            for k, v in NOTES.items()]


def _check():
    titles = {p['title'] for p in gre_plan.PLAN}
    bad = [t for t in DAY_NOTES if t not in titles]
    assert not bad, f'DAY_NOTES titles not in the plan: {bad}'
    for t, (_, ids) in DAY_NOTES.items():
        for i in ids:
            assert i in NOTES, (t, i)
    for k in NOTES:
        get(k)


_check()


# ---------------------------------------------------------------- printable HTML (open in the browser → Print → Save as PDF)
def _inline(s):
    return html.escape(s)


def _blocks_html(blocks):
    out = []
    for b in blocks:
        t = b['t']
        if t == 'h':
            out.append(f"<h2>{_inline(b['text'])}</h2>")
        elif t == 'h2':
            out.append(f"<h3>{_inline(b['text'])}</h3>")
        elif t == 'p':
            out.append(f"<p>{_inline(b['text'])}</p>")
        elif t == 'rule':
            out.append(f"<div class='rule'>{_inline(b['text'])}</div>")
        elif t == 'tip':
            out.append(f"<div class='tip'><b>Tip</b> {_inline(b['text'])}</div>")
        elif t == 'trap':
            out.append(f"<div class='trap'><b>Trap</b> {_inline(b['text'])}</div>")
        elif t == 'list':
            out.append('<ul>' + ''.join(f'<li>{_inline(i)}</li>' for i in b['items']) + '</ul>')
        elif t == 'table':
            out.append('<table><thead><tr>' + ''.join(f'<th>{_inline(c)}</th>' for c in b['head']) + '</tr></thead><tbody>' +
                       ''.join('<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in r) + '</tr>' for r in b['rows']) + '</tbody></table>')
        elif t == 'ex':
            out.append(f"<div class='ex'><div class='lab'>Worked example</div><div class='q'>{_inline(b['q'])}</div><ol>" +
                       ''.join(f'<li>{_inline(s)}</li>' for s in b['steps']) + f"</ol><div class='ans'>Answer: {_inline(b['a'])}</div></div>")
        elif t == 'check':
            out.append(f"<div class='check'><b>Check yourself:</b> {_inline(b['q'])}<div class='ans'>Answer: {_inline(b['a'])}</div></div>")
    return '\n'.join(out)


PRINT_CSS = """
body{font:15px/1.55 'Segoe UI',system-ui,sans-serif;color:#1b2333;max-width:820px;margin:24px auto;padding:0 20px}
h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:22px 0 8px;color:#1f3864;border-bottom:1px solid #dde3ee;padding-bottom:3px}h3{font-size:15px}
.meta{color:#6b7385;font-size:13px}.rule{background:#e6ecf8;border-left:4px solid #1f3864;padding:7px 10px;margin:6px 0;font-weight:600}
.tip{background:#dff3e8;padding:7px 10px;margin:6px 0;border-radius:4px}.trap{background:#fbe4e2;padding:7px 10px;margin:6px 0;border-radius:4px}
.ex{border:1px solid #dde3ee;border-radius:6px;padding:10px 12px;margin:10px 0}.ex .lab{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#6b7385}
.ex .q{font-weight:600;margin:4px 0}.ans{font-weight:600;color:#1e7b4b;margin-top:4px}.check{border-top:1px dashed #ccd;padding:8px 0;margin-top:6px}
table{border-collapse:collapse;margin:8px 0;width:100%}th,td{border:1px solid #dde3ee;padding:4px 8px;text-align:left;font-size:14px}th{background:#f2f5fa}
.note{page-break-after:always}.note:last-child{page-break-after:auto}.bar{margin:10px 0 18px}
@media print{.bar{display:none}body{margin:0}}
"""


def page(title, notes=(), sheet_=None, subtitle=''):
    parts = []
    for n in notes:
        parts.append(f"<div class='note'><h1>{_inline(n['title'])}</h1><div class='meta'>About {n['minutes']} minutes · GRE study notes</div>{_blocks_html(n['blocks'])}</div>")
    if sheet_:
        parts.append(f"<div class='note'><h1>{_inline(sheet_['title'])}</h1><div class='meta'>Revision sheet - rules, traps and quick checks</div>" +
                     ''.join(f"<h2>{_inline(s['title'])}</h2>{_blocks_html(s['blocks'])}" for s in sheet_['sections']) + '</div>')
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{_inline(title)}</title><style>{PRINT_CSS}</style></head><body>"
            f"<div class='bar'><button onclick='print()'>Print / Save as PDF</button> <span class='meta'>{_inline(subtitle)}</span></div>"
            + ''.join(parts) + '</body></html>')


def day_page(n):
    p = gre_plan.PLAN[n - 1]
    d = for_day(n)
    return page(f"Day {n} - {p['title']}", d['notes'], d['sheet'], f"Day {n} of {len(gre_plan.PLAN)} · {p['title']}")


def note_page(key):
    n = get(key)
    return page(n['title'], [n])


def all_page(subject=None):
    keys = [k for k, v in NOTES.items() if subject in (None, v['subject'])]
    return page('GRE study notes', [get(k) for k in keys], subtitle=f'{len(keys)} topics')
