"""Flask API + static UI, bound to 127.0.0.1 only."""
import datetime as dt
import os
import re
import threading

from flask import Flask, Response, jsonify, request, send_file, send_from_directory, stream_with_context

from . import ai, db, engine, excel_sync, funding, gre, importer, mobile, notify, results, sitewatch

STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, static_folder=STATIC)
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024  # screenshot uploads

TASK_FIELDS = {'status', 'notes', 'due_date', 'days_before', 'priority', 'title', 'details', 'category'}
PROGRAM_FIELDS = {'planned_submit', 'status', 'notes', 'deadline'}
HABIT_FIELDS = {'name', 'kind', 'hours_per_week', 'active_from', 'active_until', 'days', 'start_time',
                'minutes', 'notify', 'details'}
REMINDER_FIELDS = {'title', 'due_at', 'repeat', 'active', 'notes'}
SETTING_KEYS = {'excel_path', 'digest_time', 'evening_time', 'lead_minutes', 'notifications',
                'ollama_url', 'ollama_model', 'fee_uplift',
                'fx_USD', 'fx_GBP', 'fx_EUR', 'fx_SGD', 'fx_AUD', 'fx_CAD', 'fx_CHF',
                'watch_enabled', 'watch_hours', 'watch_notify'}


show_window = None  # set by main.py: brings the desktop window to the front


@app.get('/api/show')
def api_show():
    if show_window:
        show_window()
    return jsonify(ok=True)


@app.get('/')
def index():
    return send_from_directory(STATIC, 'index.html')


@app.get('/api/today')
def api_today():
    day = engine.pdate(request.args.get('date')) or engine.today()
    return jsonify(engine.today_summary(day))


@app.post('/api/habit_log')
def api_habit_log():
    b = request.json
    db.execute('INSERT OR REPLACE INTO habit_log VALUES (?,?,?)', (b['habit_id'], b['date'], 1 if b.get('done') else 0))
    return jsonify(ok=True)


# ---- tasks ----
@app.get('/api/tasks')
def api_tasks():
    return jsonify(engine.all_tasks())


@app.post('/api/tasks')
def api_task_create():
    b = request.json
    nums = [int(m.group(1)) for t in db.query("SELECT id FROM tasks WHERE scope='common'")
            if (m := re.match(r'C(\d+)$', t['id']))]
    tid = f'C{(max(nums) if nums else 0) + 1:02d}'
    db.execute('INSERT INTO tasks(id,scope,category,title,details,due_date,priority,status,notes,created_in_app,sort) '
               'VALUES (?,?,?,?,?,?,?,?,?,1,9999)',
               (tid, 'common', b.get('category') or 'Personal', b['title'], b.get('details'), b.get('due_date'),
                b.get('priority') or 'Medium', 'Not started', b.get('notes')))
    return jsonify(ok=True, id=tid)


@app.patch('/api/tasks/<tid>')
def api_task_update(tid):
    b = dict(request.json)
    if 'status' in b:
        b['completed_date'] = engine.today().isoformat() if b['status'] == 'Done' else None
        TASK_FIELDS_X = TASK_FIELDS | {'completed_date'}
    else:
        TASK_FIELDS_X = TASK_FIELDS
    db.update_row('tasks', 'id', tid, b, TASK_FIELDS_X)
    return jsonify(ok=True)


@app.delete('/api/tasks/<tid>')
def api_task_delete(tid):
    db.execute('DELETE FROM tasks WHERE id=? AND created_in_app=1', (tid,))
    return jsonify(ok=True)


# ---- programs ----
@app.get('/api/programs')
def api_programs():
    tasks = engine.all_tasks()
    t0 = engine.today()
    out = []
    for p in db.query('SELECT * FROM programs ORDER BY sort'):
        mine = [t for t in tasks if t['program_id'] == p['id']]
        counted = [t for t in mine if t['status'] != 'N/A']
        done = sum(t['status'] == 'Done' for t in counted)
        ps = engine.pdate(p['planned_submit'])
        out.append({**p, 'tasks': len(counted), 'done': done,
                    'overdue': sum(t['open'] and t['days_left'] is not None and t['days_left'] < 0 for t in mine),
                    'days_to_submit': (ps - t0).days if ps else None, 'cost': engine.program_cost(p)})
    return jsonify(out)


@app.get('/api/programs/<pid>')
def api_program_detail(pid):
    p = db.one('SELECT * FROM programs WHERE id=?', (pid,))
    if not p:
        return jsonify(error='not found'), 404
    ps = engine.pdate(p['planned_submit'])
    tasks = sorted([t for t in engine.all_tasks() if t['program_id'] == pid], key=lambda t: t['due'] or '9999')
    return jsonify({**p, 'cost': engine.program_cost(p), 'tasks': tasks,
                    'days_to_submit': (ps - engine.today()).days if ps else None,
                    'curriculum': db.one('SELECT * FROM curriculum WHERE program_id=?', (pid,)),
                    'official_pages': sitewatch.pages_for(pid), 'page_changes': sitewatch.changes(pid, limit=50),
                    'funding': funding.for_program(pid), 'funding_statuses': funding.STATUSES, 'funding_checked': funding.CHECKED,
                    'watch_hours': db.get_setting('watch_hours'),
                    'work_exp_at_submit': round((ps - dt.date(2027, 1, 1)).days / 30.4375, 1) if ps else None})


@app.patch('/api/curriculum/<pid>')
def api_curriculum_update(pid):
    db.execute('INSERT OR IGNORE INTO curriculum(program_id) VALUES (?)', (pid,))
    db.update_row('curriculum', 'program_id', pid, request.json,
                  {'overview', 'structure', 'core', 'electives', 'capstone', 'source', 'checked'})
    return jsonify(ok=True)


@app.patch('/api/programs/<pid>/costs')
def api_program_costs(pid):
    db.update_row('programs', 'id', pid, request.json, {'tuition', 'living_cost', 'living_note'})
    return jsonify(ok=True)


@app.patch('/api/programs/<pid>')
def api_program_update(pid):
    db.update_row('programs', 'id', pid, request.json, PROGRAM_FIELDS)
    return jsonify(ok=True)


# ---- official-page watcher + funding ----
@app.get('/api/watch/status')
def api_watch_status():
    return jsonify(unseen=sitewatch.unseen_count(), running=sitewatch._running.locked())


@app.get('/api/watch/changes')
def api_watch_changes():
    return jsonify(sitewatch.changes(request.args.get('program_id'), unseen_only=request.args.get('unseen') == '1'))


@app.post('/api/watch/seen')
def api_watch_seen():
    b = request.json or {}
    sitewatch.mark_seen(b.get('id'), b.get('program_id'))
    return jsonify(ok=True, unseen=sitewatch.unseen_count())


@app.post('/api/watch/check')
def api_watch_check():
    b = request.json or {}
    if sitewatch._running.locked():
        return jsonify(ok=False, error='A check is already running')
    threading.Thread(target=sitewatch.check_due, kwargs=dict(force=True, program_id=b.get('program_id'), pause=1.0),
                     daemon=True).start()
    return jsonify(ok=True)


@app.patch('/api/funding/<pid>/<aid>')
def api_funding_update(pid, aid):
    b = request.json or {}
    funding.set_status(pid, aid, b.get('status'), b.get('note'))
    return jsonify(ok=True)


# ---- habits ----
@app.get('/api/habits')
def api_habits():
    return jsonify(db.query('SELECT * FROM habits ORDER BY kind, sort, id'))


@app.get('/api/habits/week')
def api_habits_week():
    start = engine.week_start(engine.pdate(request.args.get('start')) or engine.today())
    days = [start + dt.timedelta(days=k) for k in range(7)]
    grid = []
    for h in db.query("SELECT * FROM habits WHERE kind='habit' ORDER BY sort"):
        cells = []
        for d in days:
            if engine.scheduled_on(h, d):
                r = db.one('SELECT done FROM habit_log WHERE habit_id=? AND date=?', (h['id'], d.isoformat()))
                cells.append({'date': d.isoformat(), 'scheduled': True, 'done': bool(r and r['done'])})
            else:
                cells.append({'date': d.isoformat(), 'scheduled': False, 'done': False})
        if any(c['scheduled'] for c in cells):
            grid.append({'habit': h, 'cells': cells})
    return jsonify({'start': start.isoformat(), 'days': [d.isoformat() for d in days], 'grid': grid})


@app.post('/api/habits')
def api_habit_create():
    b = request.json
    hid = f"U{db.one('SELECT COUNT(*) n FROM habits')['n'] + 1}"
    while db.one('SELECT 1 FROM habits WHERE id=?', (hid,)):
        hid += 'x'
    db.execute('INSERT INTO habits(id,name,kind,hours_per_week,active_from,active_until,days,start_time,minutes,notify,details,sort) '
               'VALUES (?,?,?,?,?,?,?,?,?,?,?,500)',
               (hid, b['name'], b.get('kind', 'habit'), b.get('hours_per_week'), b.get('active_from') or engine.today().isoformat(),
                b.get('active_until') or '2029-08-31', b.get('days') or 'Daily', b.get('start_time') or '20:00',
                int(b.get('minutes') or 30), 1 if b.get('notify', True) else 0, b.get('details')))
    return jsonify(ok=True, id=hid)


@app.patch('/api/habits/<hid>')
def api_habit_update(hid):
    db.update_row('habits', 'id', hid, request.json, HABIT_FIELDS)
    return jsonify(ok=True)


@app.delete('/api/habits/<hid>')
def api_habit_delete(hid):
    db.execute('DELETE FROM habits WHERE id=?', (hid,))
    db.execute('DELETE FROM habit_log WHERE habit_id=?', (hid,))
    return jsonify(ok=True)


# ---- calendar / key dates ----
@app.get('/api/calendar')
def api_calendar():
    days = int(request.args.get('days', 120))
    t0 = engine.today()
    return jsonify(engine.events(t0 - dt.timedelta(days=int(request.args.get('past', 0))), t0 + dt.timedelta(days=days)))


@app.patch('/api/key_dates/<int:kid>')
def api_key_date(kid):
    db.update_row('key_dates', 'id', kid, request.json, {'done', 'date', 'title'})
    return jsonify(ok=True)


# ---- reminders ----
@app.get('/api/reminders')
def api_reminders():
    now = dt.datetime.now()
    out = []
    for r in db.query('SELECT * FROM reminders ORDER BY active DESC, due_at'):
        n = engine.next_occurrence(r, now) if r['active'] else None
        out.append({**r, 'next': n.isoformat(timespec='minutes') if n else None})
    return jsonify(out)


@app.post('/api/reminders')
def api_reminder_create():
    b = request.json
    rid = db.execute('INSERT INTO reminders(title,due_at,repeat,active,notes) VALUES (?,?,?,1,?)',
                     (b['title'], b['due_at'], b.get('repeat') or 'none', b.get('notes')))
    return jsonify(ok=True, id=rid)


@app.patch('/api/reminders/<int:rid>')
def api_reminder_update(rid):
    db.update_row('reminders', 'id', rid, request.json, REMINDER_FIELDS | {'last_fired'})
    return jsonify(ok=True)


@app.delete('/api/reminders/<int:rid>')
def api_reminder_delete(rid):
    db.execute('DELETE FROM reminders WHERE id=?', (rid,))
    return jsonify(ok=True)


# ---- research queue ----
@app.get('/api/research')
def api_research():
    return jsonify(db.query('SELECT * FROM research ORDER BY priority, id'))


@app.patch('/api/research/<int:rid>')
def api_research_update(rid):
    db.update_row('research', 'id', rid, request.json, {'status', 'notes'})
    return jsonify(ok=True)


# ---- settings / sync ----
@app.get('/api/settings')
def api_settings():
    return jsonify({r['key']: r['value'] for r in db.query('SELECT * FROM settings')})


@app.post('/api/settings')
def api_settings_save():
    for k, v in request.json.items():
        if k in SETTING_KEYS:
            db.set_setting(k, v)
    return jsonify(ok=True)


@app.post('/api/sync_excel')
def api_sync():
    return jsonify(excel_sync.run())


@app.post('/api/import_excel')
def api_import():
    try:
        return jsonify(ok=True, **importer.run())
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@app.post('/api/notify_test')
def api_notify_test():
    notify.toast('Masters Tracker', 'Notifications are working.')
    return jsonify(ok=True)


# ---- GRE prep ----
@app.get('/api/gre/overview')
def api_gre_overview():
    return jsonify(gre.overview())


@app.get('/api/gre/day/<int:n>')
def api_gre_day(n):
    if not 1 <= n <= len(gre.gre_plan.PLAN):
        return jsonify(error='not found'), 404
    return jsonify(gre.day_payload(n))


@app.post('/api/gre/day/<int:n>')
def api_gre_day_save(n):
    return jsonify(gre.save_progress(n, request.json))


@app.get('/api/gre/quiz/<int:n>')
def api_gre_quiz(n):
    return jsonify(gre.build_quiz(n))


@app.post('/api/gre/quiz')
def api_gre_quiz_save():
    return jsonify(gre.record_quiz(request.json))


@app.get('/api/gre/vocab')
def api_gre_vocab():
    return jsonify(gre.vocab_state())


@app.get('/api/gre/vocab/queue')
def api_gre_vocab_queue():
    return jsonify(gre.queue_state())


@app.post('/api/gre/vocab/queue')
def api_gre_vocab_queue_answer():
    b = request.json or {}
    return jsonify(gre.queue_answer(str(b.get('word', '')), bool(b.get('correct'))))


@app.get('/api/gre/vocab/eod')
def api_gre_vocab_eod():
    return jsonify(gre.eod_state())


@app.post('/api/gre/vocab/eod')
def api_gre_vocab_eod_answer():
    b = request.json or {}
    return jsonify(gre.eod_answer(str(b.get('word', '')), bool(b.get('correct'))))


@app.post('/api/gre/vocab')
def api_gre_vocab_answer():
    b = request.json
    gre.vocab_answer(b['word'], bool(b.get('correct')), card=True)
    return jsonify(ok=True)


@app.get('/api/gre/errors')
def api_gre_errors():
    return jsonify(gre.errors())


@app.get('/api/gre/errors/summary')
def api_gre_errors_summary():
    return jsonify(gre.errors_summary())


@app.post('/api/gre/errors')
def api_gre_error_add():
    b = request.json
    kind = b.get('kind') or gre.REASON_KIND.get(b.get('answer') or '', 'Unsorted')
    eid = gre.add_error(b.get('day'), b.get('topic'), b.get('source') or 'Manual', b.get('question'), b.get('answer'), b.get('note'), kind=kind)
    return jsonify(ok=True, id=eid)


@app.patch('/api/gre/errors/<int:eid>')
def api_gre_error_update(eid):
    b = dict(request.json or {})
    if 'kind' in b and b['kind'] not in gre.ERROR_KINDS:
        b.pop('kind')
    db.update_row('gre_errors', 'id', eid, b, {'status', 'note', 'topic', 'question', 'answer', 'kind', 'redo_on'})
    return jsonify(ok=True)


@app.post('/api/gre/errors/<int:eid>/redo')
def api_gre_error_redo(eid):
    return jsonify(gre.redo_error(eid, bool((request.json or {}).get('correct'))))


@app.delete('/api/gre/errors/<int:eid>')
def api_gre_error_delete(eid):
    db.execute('DELETE FROM gre_errors WHERE id=?', (eid,))
    return jsonify(ok=True)


@app.get('/api/gre/essays')
def api_gre_essays():
    return jsonify(gre.essays())


@app.post('/api/gre/essays/<int:eid>/feedback')
def api_gre_essay_feedback(eid):
    return jsonify(gre.essay_feedback(eid))


@app.post('/api/gre/essays')
def api_gre_essay_save():
    gre.ensure()
    b = request.json
    eid = db.execute('INSERT INTO gre_essays(day,at,prompt,body,words,minutes,self_score) VALUES (?,?,?,?,?,?,?)',
                     (b.get('day'), dt.datetime.now().isoformat(timespec='seconds'), b.get('prompt'), b.get('body'),
                      len((b.get('body') or '').split()), b.get('minutes'), b.get('self_score')))
    return jsonify(ok=True, id=eid)


@app.post('/api/gre/scores')
def api_gre_score_add():
    gre.ensure()
    b = request.json
    db.execute('INSERT INTO gre_scores(date,name,quant,verbal,awa,notes) VALUES (?,?,?,?,?,?)',
               (b.get('date') or engine.today().isoformat(), b.get('name'), b.get('quant') or None, b.get('verbal') or None,
                b.get('awa') or None, b.get('notes')))
    return jsonify(ok=True)


@app.delete('/api/gre/scores/<int:sid>')
def api_gre_score_delete(sid):
    db.execute('DELETE FROM gre_scores WHERE id=?', (sid,))
    return jsonify(ok=True)


@app.post('/api/gre/settings')
def api_gre_settings():
    for k, v in request.json.items():
        if k in gre.SETTING_KEYS:
            db.set_setting(k, v)
    return jsonify(ok=True)


@app.get('/api/gre/library')
def api_gre_library():
    return jsonify(gre.library())


def _subject():
    s = request.args.get('subject', 'quant')
    return s if s in gre.SUBJECTS else 'quant'


def _known_chapter(ch):
    return ch in gre.gre_course.LESSONS or ch in gre.gre_verbal.LESSONS


@app.get('/api/gre/course')
def api_gre_course():
    return jsonify(gre.course_state(_subject()))


@app.get('/api/gre/course/lesson/<ch>')
def api_gre_course_lesson(ch):
    if not _known_chapter(ch):
        return jsonify({'error': 'unknown chapter'}), 404
    return jsonify(gre.course_lesson(ch))


@app.post('/api/gre/course/lesson/<ch>')
def api_gre_course_lesson_save(ch):
    if not _known_chapter(ch):
        return jsonify({'error': 'unknown chapter'}), 404
    return jsonify(gre.save_lesson(ch, request.json.get('concept', 0)))


@app.get('/api/gre/course/try/<ch>/<int:c>')
def api_gre_course_try(ch, c):
    if not _known_chapter(ch):
        return jsonify({'error': 'unknown chapter'}), 404
    return jsonify(gre.try_question(ch, c))


@app.get('/api/gre/course/practice/<ch>/<int:c>')
def api_gre_course_practice(ch, c):
    if not _known_chapter(ch):
        return jsonify({'error': 'unknown chapter'}), 404
    return jsonify(gre.practice_set(ch, c))


@app.post('/api/gre/course/practice/<ch>/<int:c>')
def api_gre_course_practice_answer(ch, c):
    if not _known_chapter(ch):
        return jsonify({'error': 'unknown chapter'}), 404
    return jsonify(gre.practice_answer(ch, c, request.json or {}))


@app.post('/api/gre/vocab/sentence/flag')
def api_gre_vocab_sentence_flag():
    b = request.json or {}
    return jsonify(gre.flag_sentence(str(b.get('word', '')), str(b.get('sentence', ''))))


@app.get('/api/gre/course/test')
def api_gre_course_test():
    a = request.args
    try:
        return jsonify(gre.course_test(a.get('kind', 'chapter'), a.get('key'), a.get('level', 'mixed'), _subject()))
    except (KeyError, ValueError):
        return jsonify({'error': 'unknown test'}), 400


@app.get('/api/gre/results')
def api_gre_results():
    return jsonify(results=results.listing(), chapters=results.chapters(), sources=results.SOURCES, kinds=results.KINDS, types=results.QTYPES,
                   topics=results.topic_stats())


@app.post('/api/gre/results/scan')
def api_gre_results_scan():
    files = [f for f in request.files.getlist('images') if f and f.filename]
    if not files:
        return jsonify(error='Add at least one screenshot'), 400
    f = request.form
    day = int(f['day']) if (f.get('day') or '').isdigit() else None
    return jsonify(results.scan(files, f.get('name', ''), day, f.get('kind', ''), f.get('source', '')))


@app.post('/api/gre/results/manual')
def api_gre_results_manual():
    b = request.json or {}
    return jsonify(results.create_manual(b.get('name', ''), b.get('day'), b.get('kind', ''), b.get('source', '')))


@app.get('/api/gre/results/<int:rid>')
def api_gre_result(rid):
    r = results.get(rid)
    return (jsonify(r), 200) if r else (jsonify(error='not found'), 404)


@app.post('/api/gre/results/<int:rid>')
def api_gre_result_save(rid):
    return jsonify(results.save(rid, request.json or {}))


@app.delete('/api/gre/results/<int:rid>')
def api_gre_result_delete(rid):
    return jsonify(results.delete(rid))


@app.get('/api/gre/results/<int:rid>/img/<name>')
def api_gre_result_img(rid, name):
    p = results.image_path(rid, name)
    return send_file(p) if p else ('', 404)


@app.get('/api/gre/notes')
def api_gre_notes():
    return jsonify(gre.gre_notes.library())


@app.get('/api/gre/notes/<key>')
def api_gre_note(key):
    if key not in gre.gre_notes.NOTES:
        return jsonify(error='not found'), 404
    return jsonify(gre.gre_notes.get(key))


@app.get('/gre/notes/day/<int:n>')
def gre_notes_day_page(n):
    if not 1 <= n <= len(gre.gre_plan.PLAN):
        return 'not found', 404
    return Response(gre.gre_notes.day_page(n), mimetype='text/html')


@app.get('/gre/notes/all')
def gre_notes_all_page():
    s = request.args.get('subject')
    return Response(gre.gre_notes.all_page(s if s in ('quant', 'verbal', 'writing', 'strategy') else None), mimetype='text/html')


@app.get('/gre/notes/<key>')
def gre_note_page(key):
    if key not in gre.gre_notes.NOTES:
        return 'not found', 404
    return Response(gre.gre_notes.note_page(key), mimetype='text/html')


@app.post('/api/gre/practice/mark')
def api_gre_practice_mark():
    try:
        return jsonify(gre.mark_practice(request.json or {}))
    except (KeyError, ValueError, IndexError):
        return jsonify(ok=False, error='bad request'), 400


@app.get('/api/gre/cards')
def api_gre_cards():
    return jsonify(gre.cards_state())


@app.post('/api/gre/cards')
def api_gre_card_answer():
    b = request.json or {}
    return jsonify(gre.card_answer(str(b.get('id', '')), bool(b.get('correct'))))


@app.post('/api/gre/flag')
def api_gre_flag():
    return jsonify(gre.flag_question(request.json or {}))


@app.get('/api/gre/report')
def api_gre_report():
    d = engine.pdate(request.args.get('end'))
    return jsonify(gre.weekly_report(d))


@app.get('/api/gre/smart')
def api_gre_smart():
    return jsonify(gre.smart_revision())


@app.get('/api/gre/mock/start')
def api_gre_mock_start():
    return jsonify(gre.mock_start())


@app.post('/api/gre/mock/finish')
def api_gre_mock_finish():
    return jsonify(gre.mock_finish(request.json or {}))


@app.post('/api/data/onedrive')
def api_data_onedrive():
    db.set_setting('backup_onedrive', '1' if (request.json or {}).get('enabled') else '0')
    return api_data_status()


@app.post('/api/gre/replan')
def api_gre_replan():
    return jsonify(gre.replan())


@app.get('/api/gre/insights')
def api_gre_insights():
    return jsonify(gre.insights())


@app.get('/api/gre/phone')
def api_gre_phone():
    return jsonify(mobile.status())


@app.post('/api/gre/phone')
def api_gre_phone_set():
    try:
        return jsonify(mobile.set_enabled(bool((request.json or {}).get('enabled'))))
    except OSError as e:
        db.set_setting('gre_phone', '0')
        return jsonify({**mobile.status(), 'error': f'Could not open port {mobile.port()}: {e}'})


@app.post('/api/gre/phone/token')
def api_gre_phone_token():
    return jsonify(mobile.new_token())


@app.get('/api/data/status')
def api_data_status():
    try:
        health = db.health()
    except Exception as e:
        health = str(e)
    return jsonify(health=health, backups=db.list_backups()[:5], folder=db.BACKUP_DIR, keep=db.KEEP_BACKUPS,
                   onedrive=db.onedrive_dir(), onedrive_on=db.get_setting('backup_onedrive') != '0')


@app.post('/api/data/backup')
def api_data_backup():
    try:
        path = db.backup()
        return jsonify(ok=True, path=path)
    except Exception as e:
        return jsonify(ok=False, error=str(e))


@app.post('/api/data/open')
def api_data_open():
    os.makedirs(db.BACKUP_DIR, exist_ok=True)
    os.startfile(db.BACKUP_DIR)
    return jsonify(ok=True)


@app.post('/api/gre/course/test')
def api_gre_course_test_save():
    return jsonify(gre.save_test(request.json))


@app.get('/api/gre/course/test/<int:tid>')
def api_gre_course_test_detail(tid):
    t = gre.test_detail(tid)
    return (jsonify(t), 200) if t else (jsonify({'error': 'not found'}), 404)


@app.post('/api/gre/tutor')
def api_gre_tutor():
    b = request.json
    return Response(stream_with_context(ai.chat_stream(b.get('messages', []), b.get('model'), system=gre.tutor_system(b.get('day')))),
                    mimetype='text/plain; charset=utf-8')


# ---- AI ----
@app.get('/api/ai/models')
def api_models():
    return jsonify(ai.models())


@app.post('/api/ai/chat')
def api_chat():
    b = request.json
    return Response(stream_with_context(ai.chat_stream(b.get('messages', []), b.get('model'))),
                    mimetype='text/plain; charset=utf-8')


@app.get('/api/ai/context')
def api_ai_context():
    return Response(ai.context_text(), mimetype='text/plain; charset=utf-8')
