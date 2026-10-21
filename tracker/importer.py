"""One-time import of the Excel tracker into SQLite.

Formula results are read from a LibreOffice-recalculated temp copy when LibreOffice is
installed (openpyxl cannot evaluate formulas); otherwise from Excel's cached values.
"""
import datetime as dt
import os
import shutil
import subprocess
import tempfile

import openpyxl

from . import db

# Default day-to-day slots for the Weekly Plan habits (edit later in the app).
HABIT_SLOTS = {
    'H1': ('Mon,Wed,Fri', '19:00', 60),
    'H2': ('Mon,Tue,Wed,Thu,Fri,Sat', '21:00', 20),
    'H3': ('Sat', '10:00', 120),
    'H4': ('Sun', '18:00', 30),
    'H5': ('Fri', '18:30', 30),
    'H6': ('Fri', '18:15', 15),
    'H7': ('Monthly-Sat', '16:00', 30),
    'H8': ('Mon,Tue,Wed,Thu,Fri,Sat', '21:00', 60),
}

ROUTINES = [
    ('R1', 'College / final-semester study (edit times)', 'Mon,Tue,Wed,Thu,Fri', '09:00', 480,
     '2026-10-05', '2026-12-31'),
    ('R2', 'ZS work (edit times)', 'Mon,Tue,Wed,Thu,Fri', '09:00', 540, '2027-01-04', '2029-07-15'),
]


def find_soffice():
    for p in (shutil.which('soffice'), r'C:\Program Files\LibreOffice\program\soffice.exe',
              r'C:\Program Files (x86)\LibreOffice\program\soffice.exe'):
        if p and os.path.exists(p):
            return p
    return None


def recalculated_copy(path):
    soffice = find_soffice()
    if not soffice:
        return None
    out = tempfile.mkdtemp(prefix='mt_')
    try:
        subprocess.run([soffice, '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', out, path],
                       timeout=240, capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        p = os.path.join(out, os.path.basename(path))
        return p if os.path.exists(p) else None
    except Exception:
        return None


def d(v):
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    if isinstance(v, dt.date):
        return v.isoformat()
    return None


def s(v):
    if v is None:
        return None
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def link(cell):
    return cell.hyperlink.target if cell.hyperlink is not None and cell.hyperlink.target else None


def import_details(wb=None):
    """Requirements, living costs, FX and curriculum. Only touches detail fields, never your statuses/dates."""
    if wb is None:
        path = db.get_setting('excel_path')
        if not os.path.exists(path):
            return False
        wb = openpyxl.load_workbook(path)
    ps = wb['Programs']
    for r in range(5, ps.max_row + 1):
        pid = s(ps[f'A{r}'].value)
        if not pid or not pid.startswith('P'):
            continue
        g = lambda c: s(ps[f'{c}{r}'].value)
        db.execute('UPDATE programs SET fee_basis=?, gre=?, english=?, work_exp=?, recs=?, essays=?, interview=?, app_fee=?, '
                   'special=? WHERE id=?', (g('K'), g('L'), g('M'), g('N'), g('O'), g('P'), g('Q'), g('R'), g('S'), pid))
    if 'Budget' in wb.sheetnames:
        b = wb['Budget']
        for r in range(5, 12):
            cur, rate = s(b[f'A{r}'].value), b[f'B{r}'].value
            if cur and isinstance(rate, (int, float)):
                db.set_setting(f'fx_{cur}', rate)
        if isinstance(b['E5'].value, (int, float)):
            db.set_setting('fee_uplift', b['E5'].value)
        for r in range(15, 36):  # A15 = '=Programs!A5' -> programme row r-10
            pid = s(ps[f'A{r - 10}'].value)
            living = b[f'G{r}'].value
            if pid and isinstance(living, (int, float)):
                db.execute('UPDATE programs SET living_cost=?, living_note=? WHERE id=?', (living, s(b[f'H{r}'].value), pid))
    from .curriculum import CHECKED, DATA, REQUIREMENTS
    for pid, c in DATA.items():
        db.execute('INSERT OR IGNORE INTO curriculum(program_id,overview,structure,core,electives,capstone,source,checked) '
                   'VALUES (?,?,?,?,?,?,?,?)',
                   (pid, c['overview'], c['structure'], c['core'], c['electives'], c['capstone'], c['source'], CHECKED))
    # researched requirements fill only fields the Excel tracker still marks VERIFY (or leaves empty)
    for pid, req in REQUIREMENTS.items():
        p = db.one('SELECT * FROM programs WHERE id=?', (pid,))
        if not p:
            continue
        for field, val in req.items():
            if field in ('src', 'kind', 'force'):
                continue
            cur = p.get(field) or ''
            if not cur or 'VERIFY' in cur.upper() or field in req.get('force', []):
                db.execute(f'UPDATE programs SET {field}=? WHERE id=?', (val, pid))
        db.execute('INSERT OR IGNORE INTO curriculum(program_id) VALUES (?)', (pid,))
        db.execute('UPDATE curriculum SET req_source=?, req_kind=? WHERE program_id=?', (req['src'], req['kind'], pid))
    db.set_setting('details_imported', '2')
    return True


def run(path=None):
    path = path or db.get_setting('excel_path')
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    wf = openpyxl.load_workbook(path)                         # formulas + hyperlinks
    calc = recalculated_copy(path)
    wv = openpyxl.load_workbook(calc or path, data_only=True)  # values

    for t in ('programs', 'tasks', 'key_dates', 'habits', 'habit_log', 'phases', 'research'):
        db.execute(f'DELETE FROM {t}')

    # Programs
    pv, pf = wv['Programs'], wf['Programs']
    rows = []
    for r in range(5, pv.max_row + 1):
        pid = s(pv[f'A{r}'].value)
        if not pid or not pid.startswith('P'):
            continue
        g = lambda c: pv[f'{c}{r}'].value
        rows.append((pid, s(g('B')), s(g('C')), s(g('D')), s(g('E')), s(g('F')), s(g('G')), s(g('H')),
                     s(g('I')), s(g('J')), d(g('T')), s(g('U')), d(g('V')), s(g('X')), link(pf[f'Y{r}']),
                     s(g('AC')) or 'Not started', s(g('AD')), s(g('AA')), s(g('AB')), r))
    db.executemany('INSERT INTO programs(id,short_name,tier,country,university,programme,duration,intake,tuition,currency,'
                   'deadline,deadline_notes,planned_submit,confidence,link,status,notes,post_study,scholarship_notes,sort) '
                   'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)
    import_details(wf)

    # Program tasks
    tv = wv['Program Tasks']
    rows = []
    for r in range(6, tv.max_row + 1):
        tid = s(tv[f'A{r}'].value)
        if not tid:
            continue
        g = lambda c: tv[f'{c}{r}'].value
        db_ = g('H')
        rows.append((tid, 'program', s(g('B')), s(g('E')), s(g('F')), s(g('G')), None,
                     int(db_) if isinstance(db_, (int, float)) else 0, s(g('J')), s(g('K')) or 'Not started',
                     d(g('L')), s(g('O')), None, 0, r))
    db.executemany('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)

    # Common tasks
    cv, cf = wv['Common Tasks'], wf['Common Tasks']
    rows = []
    for r in range(6, cv.max_row + 1):
        tid = s(cv[f'A{r}'].value)
        if not tid:
            continue
        g = lambda c: cv[f'{c}{r}'].value
        rows.append((tid, 'common', None, s(g('B')), s(g('C')), s(g('D')), d(g('E')), None, s(g('F')),
                     s(g('G')) or 'Not started', d(g('H')), s(g('K')), link(cf[f'J{r}']), 0, r))
    db.executemany('INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', rows)

    # Key dates (programme dates are computed live from the programs table, so skip those rows)
    dv, dfm = wv['Deadlines'], wf['Deadlines']
    rows = []
    for r in range(5, dv.max_row + 1):
        f = dfm[f'A{r}'].value
        if isinstance(f, str) and 'Programs!' in f:
            continue
        date = d(dv[f'A{r}'].value)
        if not date:
            continue
        rows.append((date, s(dv[f'B{r}'].value), s(dv[f'C{r}'].value), s(dv[f'D{r}'].value),
                     s(dv[f'F{r}'].value), link(dfm[f'G{r}']), 1 if s(dv[f'H{r}'].value) == 'Yes' else 0))
    db.executemany('INSERT INTO key_dates(date,title,type,program,confidence,link,done) VALUES (?,?,?,?,?,?,?)', rows)

    # Habits + routines
    if 'Weekly Plan' in wv.sheetnames:
        hv = wv['Weekly Plan']
        rows = []
        for i, r in enumerate(range(6, 14)):
            hid = s(hv[f'A{r}'].value)
            if not hid:
                continue
            days, start, mins = HABIT_SLOTS.get(hid, ('Sun', '10:00', 30))
            rows.append((hid, s(hv[f'B{r}'].value), 'habit', hv[f'C{r}'].value, d(hv[f'D{r}'].value),
                         d(hv[f'E{r}'].value), days, start, mins, 1, s(hv[f'G{r}'].value), i))
        db.executemany('INSERT INTO habits VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', rows)
        # weekly log: a "Y" marks that week's scheduled sessions done
        from . import engine
        habit_cols = {chr(ord('C') + j): s(hv.cell(row=18, column=3 + j).value) for j in range(8)}
        for r in range(19, hv.max_row + 1):
            wk = hv[f'A{r}'].value
            if not isinstance(wk, dt.datetime):
                continue
            for col, hid in habit_cols.items():
                if s(hv[f'{col}{r}'].value) == 'Y':
                    h = db.one('SELECT * FROM habits WHERE id=?', (hid,))
                    for k in range(7):
                        day = wk.date() + dt.timedelta(days=k)
                        if h and engine.scheduled_on(h, day):
                            db.execute('INSERT OR REPLACE INTO habit_log VALUES (?,?,1)', (hid, day.isoformat()))
    for i, (rid, name, days, start, mins, a, b) in enumerate(ROUTINES):
        db.execute('INSERT INTO habits VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   (rid, name, 'routine', None, a, b, days, start, mins, 0, 'Fixed block - not tracked.', 100 + i))

    # Timeline phases
    tl = wv['Timeline']
    rows = []
    for r in range(5, 20):
        if tl[f'A{r}'].value:
            rows.append((s(tl[f'A{r}'].value), d(tl[f'B{r}'].value), d(tl[f'C{r}'].value), s(tl[f'D{r}'].value)))
    db.executemany('INSERT INTO phases(name,start,end,milestones) VALUES (?,?,?,?)', rows)

    # Research queue
    rq = wv['Research Queue']
    rows = []
    for r in range(5, rq.max_row + 1):
        if rq[f'C{r}'].value:
            rows.append(tuple(s(rq[f'{c}{r}'].value) for c in 'ABCDEFGH'))
    db.executemany('INSERT INTO research(priority,country,programme,why,verify,info,status,notes) '
                   'VALUES (?,?,?,?,?,?,?,?)', rows)

    db.set_setting('last_import', dt.datetime.now().isoformat(timespec='seconds'))
    if calc:
        shutil.rmtree(os.path.dirname(calc), ignore_errors=True)
    return {
        'programs': db.one('SELECT COUNT(*) n FROM programs')['n'],
        'tasks': db.one('SELECT COUNT(*) n FROM tasks')['n'],
        'key_dates': db.one('SELECT COUNT(*) n FROM key_dates')['n'],
        'habits': db.one('SELECT COUNT(*) n FROM habits')['n'],
        'recalculated_with_libreoffice': bool(calc),
    }
