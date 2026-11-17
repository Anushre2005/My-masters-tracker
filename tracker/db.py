"""SQLite storage for the Masters tracker."""
import os
import sqlite3
import threading

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Per-user data folder, shared by the installed .exe and by running from source.
DATA_DIR = os.path.join(os.environ.get('LOCALAPPDATA') or os.path.expanduser('~'), 'MastersTracker', 'data')
DB_PATH = os.path.join(DATA_DIR, 'tracker.db')
_OLD_DB = os.path.join(BASE_DIR, 'data', 'tracker.db')  # location used before the desktop build

DEFAULT_SETTINGS = {
    'excel_path': os.path.join(os.path.expanduser('~'), 'Downloads', 'Masters_Abroad_2029_Tracker.xlsx'),
    'digest_time': '08:00',        # morning summary toast
    'evening_time': '21:45',       # evening "what's left today" toast
    'lead_minutes': '10',          # habit reminder this many minutes before start
    'notifications': '1',
    'ollama_url': 'http://localhost:11434',
    'ollama_model': 'llama3.1:8b',
    'port': '8765',
    # planning FX (INR per 1 unit) + fee uplift, from the Excel Budget tab; editable in Settings
    'fx_USD': '90', 'fx_GBP': '120', 'fx_EUR': '105', 'fx_SGD': '70', 'fx_AUD': '60', 'fx_CAD': '65', 'fx_CHF': '112',
    'fee_uplift': '0.075',
    # official-page watcher (sitewatch.py)
    'watch_enabled': '1', 'watch_hours': '12', 'watch_notify': '1',
}

# columns added after the first release (programme details / costs)
PROGRAM_EXTRA_COLS = ['fee_basis', 'gre', 'english', 'work_exp', 'recs', 'essays', 'interview', 'app_fee',
                      'special', 'living_cost', 'living_note']

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS programs (
    id TEXT PRIMARY KEY, short_name TEXT, tier TEXT, country TEXT, university TEXT, programme TEXT,
    duration TEXT, intake TEXT, tuition TEXT, currency TEXT, deadline TEXT, deadline_notes TEXT,
    planned_submit TEXT, confidence TEXT, link TEXT, status TEXT, notes TEXT, post_study TEXT,
    scholarship_notes TEXT, sort INTEGER);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY, scope TEXT, program_id TEXT, category TEXT, title TEXT, details TEXT,
    due_date TEXT, days_before INTEGER, priority TEXT, status TEXT, completed_date TEXT,
    notes TEXT, link TEXT, created_in_app INTEGER DEFAULT 0, sort INTEGER);
CREATE TABLE IF NOT EXISTS key_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, title TEXT, type TEXT, program TEXT,
    confidence TEXT, link TEXT, done INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS habits (
    id TEXT PRIMARY KEY, name TEXT, kind TEXT DEFAULT 'habit', hours_per_week REAL,
    active_from TEXT, active_until TEXT, days TEXT, start_time TEXT, minutes INTEGER,
    notify INTEGER DEFAULT 1, details TEXT, sort INTEGER);
CREATE TABLE IF NOT EXISTS habit_log (
    habit_id TEXT, date TEXT, done INTEGER, PRIMARY KEY (habit_id, date));
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, due_at TEXT, repeat TEXT DEFAULT 'none',
    active INTEGER DEFAULT 1, last_fired TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, start TEXT, end TEXT, milestones TEXT);
CREATE TABLE IF NOT EXISTS research (
    id INTEGER PRIMARY KEY AUTOINCREMENT, priority TEXT, country TEXT, programme TEXT, why TEXT,
    verify TEXT, info TEXT, status TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS sent (key TEXT PRIMARY KEY, at TEXT);
CREATE TABLE IF NOT EXISTS curriculum (
    program_id TEXT PRIMARY KEY, overview TEXT, structure TEXT, core TEXT, electives TEXT, capstone TEXT,
    source TEXT, checked TEXT);
"""

_lock = threading.RLock()


def connect():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH) and os.path.exists(_OLD_DB):
        src = sqlite3.connect(_OLD_DB)
        dst = sqlite3.connect(DB_PATH)
        src.backup(dst)
        src.close(); dst.close()
    con = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    return con


_con = None


def con():
    global _con
    if _con is None:
        _con = connect()
        _con.executescript(SCHEMA)
        have = {r[1] for r in _con.execute('PRAGMA table_info(programs)')}
        for c in PROGRAM_EXTRA_COLS:
            if c not in have:
                _con.execute(f'ALTER TABLE programs ADD COLUMN {c} TEXT')
        have = {r[1] for r in _con.execute('PRAGMA table_info(curriculum)')}
        for c in ('req_source', 'req_kind'):
            if c not in have:
                _con.execute(f'ALTER TABLE curriculum ADD COLUMN {c} TEXT')
        for k, v in DEFAULT_SETTINGS.items():
            _con.execute('INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)', (k, v))
        _con.commit()
    return _con


def query(sql, args=()):
    with _lock:
        return [dict(r) for r in con().execute(sql, args).fetchall()]


def one(sql, args=()):
    rows = query(sql, args)
    return rows[0] if rows else None


def execute(sql, args=()):
    with _lock:
        cur = con().execute(sql, args)
        con().commit()
        return cur.lastrowid


def executemany(sql, rows):
    with _lock:
        con().executemany(sql, rows)
        con().commit()


# ---- backups: one copy per day in DATA_DIR/backups, the last KEEP_BACKUPS kept
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')
KEEP_BACKUPS = 14


def backup(path=None):
    """Consistent copy of the live database (SQLite online backup, safe while the app is running)."""
    import datetime as _dt
    os.makedirs(BACKUP_DIR, exist_ok=True)
    path = path or os.path.join(BACKUP_DIR, f'tracker-{_dt.date.today().isoformat()}.db')
    tmp = path + '.tmp'
    with _lock:
        dst = sqlite3.connect(tmp)
        try:
            con().backup(dst)
        finally:
            dst.close()
    os.replace(tmp, path)
    for old in list_backups()[KEEP_BACKUPS:]:
        try:
            os.remove(os.path.join(BACKUP_DIR, old['name']))
        except OSError:
            pass
    try:
        copy_to_onedrive(path)
    except Exception as e:  # a cloud-folder problem must never break the local backup
        print('OneDrive backup copy failed:', e)
    return path


def onedrive_dir():
    """Backup folder inside OneDrive (synced to the cloud), or None if OneDrive is not set up."""
    root = os.environ.get('OneDrive') or os.environ.get('OneDriveConsumer')
    return os.path.join(root, 'MastersTracker backups') if root and os.path.isdir(root) else None


def copy_to_onedrive(path):
    import shutil
    d = onedrive_dir()
    if not d or get_setting('backup_onedrive') == '0':
        return None
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.basename(path))
    shutil.copy2(path, dst)
    olds = sorted([f for f in os.listdir(d) if f.startswith('tracker-') and f.endswith('.db')], reverse=True)
    for f in olds[KEEP_BACKUPS:]:
        try:
            os.remove(os.path.join(d, f))
        except OSError:
            pass
    return dst


def backup_daily():
    """Make today's backup if it does not exist yet. Called at startup and from the background loop."""
    import datetime as _dt
    if not os.path.exists(os.path.join(BACKUP_DIR, f'tracker-{_dt.date.today().isoformat()}.db')):
        return backup()
    return None


def list_backups():
    if not os.path.isdir(BACKUP_DIR):
        return []
    files = [f for f in os.listdir(BACKUP_DIR) if f.startswith('tracker-') and f.endswith('.db')]
    return [{'name': f, 'size': os.path.getsize(os.path.join(BACKUP_DIR, f))} for f in sorted(files, reverse=True)]


def health():
    """'ok' or the first problem SQLite reports (quick_check)."""
    with _lock:
        r = con().execute('PRAGMA quick_check').fetchone()
    return r[0] if r else 'unknown'


def get_setting(key):
    r = one('SELECT value FROM settings WHERE key=?', (key,))
    return r['value'] if r else DEFAULT_SETTINGS.get(key)


def set_setting(key, value):
    execute('INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
            (key, str(value)))


def is_empty():
    return one('SELECT COUNT(*) AS n FROM tasks')['n'] == 0


def update_row(table, key_col, key, fields, allowed):
    fields = {k: v for k, v in fields.items() if k in allowed}
    if not fields:
        return
    cols = ', '.join(f'{k}=?' for k in fields)
    execute(f'UPDATE {table} SET {cols} WHERE {key_col}=?', (*fields.values(), key))
