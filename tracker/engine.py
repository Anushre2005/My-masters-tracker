"""Date logic: schedules, due tasks, upcoming events, and the reminder loop."""
import datetime as dt
import threading
import time

from . import db, notify

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def today():
    return dt.date.today()


def pdate(s):
    try:
        return dt.date.fromisoformat(s[:10]) if s else None
    except ValueError:
        return None


# ---------------- habits / schedule ----------------
def active_on(h, day):
    a, b = pdate(h['active_from']), pdate(h['active_until'])
    if not a or not b:
        return False
    return a <= day <= b


def scheduled_on(h, day):
    """days spec: 'Daily' | 'Weekdays' | 'Mon,Wed' | 'Monthly-Sat' (first Saturday of the month)."""
    if not active_on(h, day):
        return False
    spec = (h['days'] or '').strip()
    wd = DAYS[day.weekday()]
    if spec == 'Daily':
        return True
    if spec == 'Weekdays':
        return day.weekday() < 5
    if spec.startswith('Monthly-'):
        return wd == spec.split('-', 1)[1] and day.day <= 7
    return wd in [x.strip() for x in spec.split(',')]


def sessions_for(day):
    out = []
    logs = {r['habit_id']: r['done'] for r in db.query('SELECT * FROM habit_log WHERE date=?', (day.isoformat(),))}
    for h in db.query('SELECT * FROM habits ORDER BY start_time, sort'):
        if scheduled_on(h, day):
            st = dt.datetime.combine(day, dt.time.fromisoformat(h['start_time'] or '09:00'))
            out.append({**h, 'start': st.strftime('%H:%M'),
                        'end': (st + dt.timedelta(minutes=h['minutes'] or 30)).strftime('%H:%M'),
                        'done': bool(logs.get(h['id'])), 'date': day.isoformat()})
    return out


def week_start(day):
    return day - dt.timedelta(days=day.weekday())


def week_progress(day):
    ws = week_start(day)
    planned = done = 0
    per = {}
    for k in range(7):
        dd = ws + dt.timedelta(days=k)
        for s in sessions_for(dd):
            if s['kind'] != 'habit':
                continue
            planned += 1
            done += s['done']
            p = per.setdefault(s['id'], {'id': s['id'], 'name': s['name'], 'planned': 0, 'done': 0})
            p['planned'] += 1
            p['done'] += s['done']
    return {'week_start': ws.isoformat(), 'planned': planned, 'done': done, 'habits': list(per.values())}


# ---------------- tasks ----------------
def programs_by_id():
    return {p['id']: p for p in db.query('SELECT * FROM programs')}


def task_due(t, progs):
    if t['scope'] == 'program':
        p = progs.get(t['program_id'])
        ps = pdate(p['planned_submit']) if p else None
        return ps - dt.timedelta(days=t['days_before'] or 0) if ps else None
    return pdate(t['due_date'])


def all_tasks():
    progs = programs_by_id()
    out = []
    t0 = today()
    for t in db.query('SELECT * FROM tasks ORDER BY sort, id'):
        due = task_due(t, progs)
        p = progs.get(t['program_id']) if t['program_id'] else None
        t['program'] = p['short_name'] if p else None
        t['due'] = due.isoformat() if due else None
        t['days_left'] = (due - t0).days if due else None
        t['open'] = t['status'] not in ('Done', 'N/A')
        out.append(t)
    return out


def open_tasks_sorted(limit=None, scope=None):
    ts = [t for t in all_tasks() if t['open'] and t['due'] and (scope is None or t['scope'] == scope)]
    ts.sort(key=lambda t: (t['due'], {'High': 0, 'Medium': 1}.get(t['priority'], 2)))
    return ts[:limit] if limit else ts


# ---------------- costs (same method as the Excel Budget tab) ----------------
def _num(v):
    try:
        return float(str(v).replace(',', ''))
    except (TypeError, ValueError):
        return None


def program_cost(p):
    fx = _num(db.get_setting(f"fx_{p['currency']}")) if p.get('currency') else None
    uplift = _num(db.get_setting('fee_uplift')) or 0
    tuition = _num(p.get('tuition'))
    living = _num(p.get('living_cost'))
    if not fx:
        return {'fx': None, 'currency': p.get('currency')}
    t29 = tuition * (1 + uplift) if tuition is not None else None
    total_local = (t29 or 0) + (living or 0)
    inr = lambda x: round(x * fx) if x is not None else None
    return {
        'currency': p['currency'], 'fx': fx, 'uplift': uplift,
        'tuition_local': tuition, 'tuition_2029_local': t29, 'living_local': living, 'total_local': total_local,
        'tuition_inr': inr(tuition), 'tuition_2029_inr': inr(t29), 'living_inr': inr(living),
        'total_inr': inr(total_local), 'total_lakh': round(total_local * fx / 1e5, 1),
    }


# ---------------- events ----------------
def events(start, end):
    ev = []
    for k in db.query('SELECT * FROM key_dates WHERE done=0'):
        dd = pdate(k['date'])
        if dd and start <= dd <= end:
            ev.append({'date': dd.isoformat(), 'title': k['title'], 'type': k['type'] or 'Key date',
                       'program': k['program'], 'link': k['link'], 'kind': 'key_date', 'id': k['id']})
    for p in db.query("SELECT * FROM programs WHERE status NOT IN ('Not applying','Withdrawn')"):
        for field, label, typ in (('planned_submit', 'Planned submit', 'Application'),
                                  ('deadline', 'Official deadline (expected)', 'Programme deadline')):
            dd = pdate(p[field])
            if dd and start <= dd <= end:
                ev.append({'date': dd.isoformat(), 'title': f"{label}: {p['short_name']}", 'type': typ,
                           'program': p['short_name'], 'link': p['link'], 'kind': 'program'})
    for t in all_tasks():
        if t['open'] and t['due']:
            dd = pdate(t['due'])
            if start <= dd <= end:
                ev.append({'date': t['due'], 'title': t['title'], 'type': 'Task', 'program': t['program'] or t['category'],
                           'kind': 'task', 'id': t['id'], 'priority': t['priority']})
    ev.sort(key=lambda e: (e['date'], e['kind'] != 'program', e['kind'] == 'task'))
    return ev


def current_phase(day=None):
    day = day or today()
    for p in db.query('SELECT * FROM phases ORDER BY start'):
        if pdate(p['start']) <= day <= pdate(p['end']):
            p['days_left'] = (pdate(p['end']) - day).days
            return p
    return None


def first_deadline():
    t0 = today()
    best = None
    for p in db.query("SELECT short_name, planned_submit, deadline FROM programs WHERE status NOT IN ('Not applying','Withdrawn')"):
        for f in ('planned_submit', 'deadline'):
            dd = pdate(p[f])
            if dd and dd >= t0 and (best is None or dd < best[0]):
                best = (dd, p['short_name'], f)
    if not best:
        return None
    return {'date': best[0].isoformat(), 'program': best[1], 'kind': best[2], 'days': (best[0] - t0).days}


def today_summary(day=None):
    day = day or today()
    tasks = open_tasks_sorted()
    overdue = [t for t in tasks if t['days_left'] is not None and t['days_left'] < 0]
    due_soon = [t for t in tasks if t['days_left'] is not None and 0 <= t['days_left'] <= 14]
    upcoming = [e for e in events(day, day + dt.timedelta(days=1200)) if e['kind'] != 'task'][:8]
    rem = [r for r in reminders_on(day)]
    return {
        'date': day.isoformat(), 'phase': current_phase(day), 'first_deadline': first_deadline(),
        'sessions': sessions_for(day), 'overdue': overdue[:20], 'due_soon': due_soon[:20],
        'next_tasks': tasks[:8], 'upcoming': upcoming, 'week': week_progress(day), 'reminders': rem,
        'gre': _gre_card(day),
    }


def _gre_card(day):
    from . import gre
    try:
        return gre.today_card(day)
    except Exception as e:  # never break the Today screen
        print('gre card error:', e)
        return None


# ---------------- reminders ----------------
def next_occurrence(r, after):
    """Next fire datetime strictly after `after` for a repeating reminder."""
    base = dt.datetime.fromisoformat(r['due_at'])
    if r['repeat'] == 'none':
        return base if base > after else None
    cand = dt.datetime.combine(after.date(), base.time())
    if cand <= after:
        cand += dt.timedelta(days=1)
    cand = max(cand, base)
    for _ in range(8):
        if r['repeat'] == 'daily' or (r['repeat'] == 'weekdays' and cand.weekday() < 5) or \
                (r['repeat'] == 'weekly' and cand.weekday() == base.weekday()):
            return cand
        cand += dt.timedelta(days=1)
    return None


def reminders_on(day):
    out = []
    start = dt.datetime.combine(day, dt.time.min) - dt.timedelta(seconds=1)
    for r in db.query('SELECT * FROM reminders WHERE active=1'):
        n = next_occurrence(r, start)
        if n and n.date() == day:
            out.append({**r, 'time': n.strftime('%H:%M')})
    return sorted(out, key=lambda r: r['time'])


# ---------------- notifier loop ----------------
def _once(key):
    if db.one('SELECT 1 FROM sent WHERE key=?', (key,)):
        return False
    db.execute('INSERT INTO sent VALUES (?, ?)', (key, dt.datetime.now().isoformat(timespec='seconds')))
    return True


def _hm(s):
    h, m = (s or '00:00').split(':')
    return int(h) * 60 + int(m)


def tick(now=None):
    now = now or dt.datetime.now()
    if db.get_setting('notifications') != '1':
        return
    day = now.date()
    mins = now.hour * 60 + now.minute
    lead = int(db.get_setting('lead_minutes') or 10)

    # habit / routine sessions
    for s in sessions_for(day):
        if not s['notify'] or s['done']:
            continue
        start = _hm(s['start'])
        if start - lead <= mins <= start + 5 and _once(f"habit:{s['id']}:{day}"):
            notify.toast(f"{s['name']} at {s['start']}", f"{s['minutes']} min session. {s['details'] or ''}"[:200])

    # one-off / repeating reminders
    for r in db.query('SELECT * FROM reminders WHERE active=1'):
        last = dt.datetime.fromisoformat(r['last_fired']) if r['last_fired'] else \
            dt.datetime.fromisoformat(r['due_at']) - dt.timedelta(seconds=1)
        n = next_occurrence(r, last)
        if n and n <= now and (now - n) < dt.timedelta(hours=12):
            notify.toast('Reminder', r['title'])
            db.execute('UPDATE reminders SET last_fired=?, active=? WHERE id=?',
                       (n.isoformat(timespec='seconds'), 0 if r['repeat'] == 'none' else 1, r['id']))
        elif n and n <= now:  # missed while the laptop was off - skip forward silently
            db.execute('UPDATE reminders SET last_fired=?, active=? WHERE id=?',
                       (now.isoformat(timespec='seconds'), 0 if r['repeat'] == 'none' else 1, r['id']))

    # GRE class reminder
    try:
        from . import gre
        gre.tick(now, _once, notify.toast)
    except Exception as e:
        print('gre tick error:', e)

    # daily database backup
    try:
        db.backup_daily()
    except Exception as e:
        print('backup error:', e)

    # morning digest
    if mins >= _hm(db.get_setting('digest_time')) and mins < 12 * 60 and _once(f'digest:{day}'):
        summ = today_summary(day)
        habits = [s for s in summ['sessions'] if s['kind'] == 'habit']
        msg = f"{len(habits)} sessions today"
        if summ['overdue']:
            msg += f" | {len(summ['overdue'])} overdue"
        due_today = [t for t in summ['due_soon'] if t['days_left'] == 0]
        if due_today:
            msg += f" | due today: {due_today[0]['title'][:60]}"
        soon = [e for e in summ['upcoming'] if (dt.date.fromisoformat(e['date']) - day).days <= 7]
        if soon:
            msg += f" | this week: {soon[0]['title'][:50]}"
        g = summ.get('gre')
        if g and not g.get('finished') and g.get('study_today'):
            msg += f" | GRE Day {g['day']}: {g['title'][:40]}"
        notify.toast('Good morning - your plan for today', msg)

    # evening check
    if mins >= _hm(db.get_setting('evening_time')) and _once(f'evening:{day}'):
        left = [s for s in sessions_for(day) if s['kind'] == 'habit' and not s['done']]
        if left:
            notify.toast('Still open today', ', '.join(s['name'] for s in left)[:200])


def loop(stop_event):
    while not stop_event.is_set():
        try:
            tick()
        except Exception as e:  # never let the loop die
            print('notifier error:', e)
        stop_event.wait(30)


def start_background():
    ev = threading.Event()
    threading.Thread(target=loop, args=(ev,), daemon=True).start()
    return ev
