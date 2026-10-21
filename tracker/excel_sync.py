"""Write app changes back into the Excel tracker (statuses, dates, notes, weekly habit log).

Only input cells are touched; formulas stay intact. A timestamped backup is written first.
"""
import datetime as dt
import math
import os
import shutil

import openpyxl
from copy import copy

from . import db, engine


def _dt(s):
    d = engine.pdate(s)
    return dt.datetime(d.year, d.month, d.day) if d else None


def _copy_style(dst, src):
    dst.font = copy(src.font); dst.fill = copy(src.fill); dst.border = copy(src.border)
    dst.alignment = copy(src.alignment); dst.number_format = src.number_format


def run():
    path = db.get_setting('excel_path')
    if not os.path.exists(path):
        return {'ok': False, 'error': f'Excel file not found: {path}'}
    bdir = os.path.join(os.path.dirname(path), 'tracker_backups')
    os.makedirs(bdir, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(path, os.path.join(bdir, f'{os.path.splitext(os.path.basename(path))[0]}_{stamp}.xlsx'))

    wb = openpyxl.load_workbook(path)
    changed = 0

    # Programs
    ws = wb['Programs']
    rows = {ws[f'A{r}'].value: r for r in range(5, ws.max_row + 1) if ws[f'A{r}'].value}
    for p in db.query('SELECT * FROM programs'):
        r = rows.get(p['id'])
        if r:
            ws[f'V{r}'] = _dt(p['planned_submit']); ws[f'AC{r}'] = p['status']; ws[f'AD{r}'] = p['notes']
            changed += 1

    # Program tasks
    ws = wb['Program Tasks']
    rows = {ws[f'A{r}'].value: r for r in range(6, ws.max_row + 1) if ws[f'A{r}'].value}
    for t in db.query("SELECT * FROM tasks WHERE scope='program'"):
        r = rows.get(t['id'])
        if r:
            ws[f'H{r}'] = t['days_before']; ws[f'K{r}'] = t['status']
            ws[f'L{r}'] = _dt(t['completed_date']); ws[f'O{r}'] = t['notes']
            changed += 1

    # Common tasks (append rows created in the app)
    ws = wb['Common Tasks']
    rows = {ws[f'A{r}'].value: r for r in range(6, ws.max_row + 1) if ws[f'A{r}'].value}
    last = max(rows.values()) if rows else 5
    for t in db.query("SELECT * FROM tasks WHERE scope='common' ORDER BY sort, id"):
        r = rows.get(t['id'])
        if not r:
            last += 1
            r = last
            for col in 'ABCDEFGHIJKL':
                _copy_style(ws[f'{col}{r}'], ws[f'{col}{r - 1}'])
            ws[f'A{r}'] = t['id']; ws[f'B{r}'] = t['category']; ws[f'C{r}'] = t['title']; ws[f'D{r}'] = t['details']
            ws[f'F{r}'] = t['priority']
            ws[f'I{r}'] = f'=IF(OR($E{r}="",$G{r}="Done",$G{r}="N/A"),"",$E{r}-TODAY())'
            ws[f'L{r}'] = f'=IF(OR(NOT(ISNUMBER($E{r})),$G{r}="Done",$G{r}="N/A"),"",$E{r}+ROW()/100000)'
        ws[f'E{r}'] = _dt(t['due_date']); ws[f'G{r}'] = t['status']
        ws[f'H{r}'] = _dt(t['completed_date']); ws[f'K{r}'] = t['notes']
        changed += 1
    if ws.auto_filter.ref:
        ws.auto_filter.ref = f'A5:L{last}'

    # Research queue status
    ws = wb['Research Queue']
    rows = {ws[f'C{r}'].value: r for r in range(5, ws.max_row + 1) if ws[f'C{r}'].value}
    for q in db.query('SELECT * FROM research'):
        r = rows.get(q['programme'])
        if r:
            ws[f'G{r}'] = q['status']; ws[f'H{r}'] = q['notes']

    # Weekly plan: habit dates + weekly Y/N log
    if 'Weekly Plan' in wb.sheetnames:
        ws = wb['Weekly Plan']
        hrow = {ws[f'A{r}'].value: r for r in range(6, 14) if ws[f'A{r}'].value}
        for h in db.query("SELECT * FROM habits WHERE kind='habit'"):
            r = hrow.get(h['id'])
            if r:
                ws[f'C{r}'] = h['hours_per_week']; ws[f'D{r}'] = _dt(h['active_from']); ws[f'E{r}'] = _dt(h['active_until'])
        col_of = {ws.cell(row=18, column=c).value: c for c in range(3, 11)}
        habits = {h['id']: h for h in db.query("SELECT * FROM habits WHERE kind='habit'")}
        t0 = engine.today()
        for r in range(19, ws.max_row + 1):
            wk = ws[f'A{r}'].value
            if not isinstance(wk, dt.datetime) or wk.date() > t0:
                continue
            for hid, c in col_of.items():
                h = habits.get(hid)
                if not h:
                    continue
                days = [wk.date() + dt.timedelta(days=k) for k in range(7)]
                planned = [d for d in days if engine.scheduled_on(h, d)]
                if not planned:
                    continue
                done = sum(1 for d in planned if db.one('SELECT done FROM habit_log WHERE habit_id=? AND date=? AND done=1',
                                                         (hid, d.isoformat())))
                week_over = days[-1] < t0
                if done >= math.ceil(len(planned) / 2):
                    ws.cell(row=r, column=c, value='Y')
                elif week_over:
                    ws.cell(row=r, column=c, value='N')

    wb.calculation.fullCalcOnLoad = True
    try:
        wb.save(path)
    except PermissionError:
        return {'ok': False, 'error': 'The Excel file is open - close it in Excel and try again.'}
    db.set_setting('last_sync', dt.datetime.now().isoformat(timespec='seconds'))
    return {'ok': True, 'rows_written': changed, 'backup_dir': bdir}
