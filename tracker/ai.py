"""Local Ollama assistant. The tracker state is passed as context; nothing leaves the laptop."""
import datetime as dt
import json
import urllib.request

from . import db, engine

SYSTEM = (
    "You are a concise personal planning assistant for a student applying to Master's programmes "
    "(business analytics / AI) abroad for the Aug-Sept 2029 intake. Profile: BTech Computer Engineering, "
    "joining ZS Associates in Jan 2027. Use ONLY the tracker data provided for dates and facts; if something "
    "isn't in the data, say so instead of guessing. Prefer short bullet lists and concrete time blocks."
)


def _get(path, timeout=5):
    with urllib.request.urlopen(db.get_setting('ollama_url').rstrip('/') + path, timeout=timeout) as r:
        return json.loads(r.read())


def models():
    try:
        return {'ok': True, 'models': [m['name'] for m in _get('/api/tags')['models']],
                'selected': db.get_setting('ollama_model')}
    except Exception as e:
        return {'ok': False, 'error': str(e), 'models': [], 'selected': db.get_setting('ollama_model')}


def context_text():
    s = engine.today_summary()
    t0 = engine.today()
    lines = [f"Today: {t0.strftime('%A %d %b %Y')}"]
    if s['phase']:
        lines.append(f"Current phase: {s['phase']['name']} ({s['phase']['days_left']} days left) - {s['phase']['milestones']}")
    if s['first_deadline']:
        f = s['first_deadline']
        lines.append(f"Next application date: {f['program']} {f['kind'].replace('_', ' ')} on {f['date']} ({f['days']} days)")
    lines.append('Today\'s schedule:')
    for x in s['sessions']:
        lines.append(f"  {x['start']}-{x['end']} {x['name']}{' (done)' if x['done'] else ''}")
    for r in s['reminders']:
        lines.append(f"  {r['time']} reminder: {r['title']}")
    w = s['week']
    lines.append(f"This week's habits: {w['done']}/{w['planned']} sessions done")
    if s['overdue']:
        lines.append('Overdue tasks:')
        lines += [f"  - [{t['priority']}] {t['title']} (due {t['due']})" for t in s['overdue'][:10]]
    lines.append('Next open tasks:')
    lines += [f"  - [{t['priority']}] {t['title']}{' - ' + t['program'] if t['program'] else ''} (due {t['due']}, "
              f"{t['days_left']} days, status {t['status']})" for t in s['next_tasks']]
    g = s.get('gre')
    if g and not g.get('finished'):
        lines.append(f"GRE prep: next class Day {g['day']} of {g['total']} - {g['section']}: {g['title']} "
                     f"({g['behind']} days behind plan, {g['vocab_due']} vocab cards due)")
    lines.append('Upcoming key dates:')
    lines += [f"  - {e['date']}: {e['title']}" for e in s['upcoming']]
    return '\n'.join(lines)


def chat_stream(messages, model=None, system=None):
    model = model or db.get_setting('ollama_model')
    msgs = [{'role': 'system', 'content': system or (SYSTEM + '\n\nTRACKER DATA:\n' + context_text())}] + messages[-12:]
    body = json.dumps({'model': model, 'messages': msgs, 'stream': True}).encode()
    req = urllib.request.Request(db.get_setting('ollama_url').rstrip('/') + '/api/chat', data=body,
                                 headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            for line in r:
                if not line.strip():
                    continue
                part = json.loads(line)
                if 'message' in part:
                    yield part['message'].get('content', '')
                if part.get('done'):
                    break
    except Exception as e:
        yield f"\n\n[Could not reach Ollama at {db.get_setting('ollama_url')}: {e}. Is `ollama serve` running?]"
