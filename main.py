"""Masters Tracker desktop app.

Runs the local server + reminder loop, shows the UI in its own window (Edge WebView2),
and keeps a tray icon. Closing the window hides it to the tray so reminders keep running;
quit from the tray menu. `--hidden` starts in the tray only (used for autostart).
"""
import os
import socket
import sys
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tracker import db  # noqa: E402

# pythonw / frozen exe has no console: send prints to a log file
if sys.stdout is None or sys.stderr is None:
    os.makedirs(db.DATA_DIR, exist_ok=True)
    _log = open(os.path.join(db.DATA_DIR, 'app.log'), 'a', buffering=1, encoding='utf-8')
    sys.stdout = sys.stderr = _log

from tracker import engine, excel_sync, importer, mobile, notify, server  # noqa: E402


def port_in_use(port):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(('127.0.0.1', port)) == 0


def make_icon():
    from PIL import Image, ImageDraw
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((4, 4, 60, 60), 14, fill=(31, 56, 100, 255))
    d.line((18, 34, 28, 44, 46, 22), fill=(255, 255, 255, 255), width=7)
    return img


def main():
    port = int(db.get_setting('port'))
    url = f'http://127.0.0.1:{port}/'
    hidden = '--hidden' in sys.argv

    if port_in_use(port):  # already running: bring that window forward and exit
        try:
            urllib.request.urlopen(url + 'api/show', timeout=3)
        except Exception:
            pass
        return

    if db.is_empty():
        print('First run - importing Excel tracker...')
        try:
            print(importer.run())
        except Exception as e:
            print('import failed:', e)
    if db.get_setting('details_imported') != '2':
        try:
            importer.import_details()
        except Exception as e:
            print('details import failed:', e)
    try:  # programmes added in the app (US biotech + business + AI options)
        from tracker import extra_programs
        extra_programs.ensure()
    except Exception as e:
        print('extra programmes failed:', e)

    # database health check + daily backup before anything writes
    try:
        health = db.health()
        if health != 'ok':
            print('database check failed:', health)
            notify.toast('Masters Tracker: database problem',
                         f'SQLite reported "{health[:80]}". Backups are in {db.BACKUP_DIR} - see GRE Prep > Settings.')
        else:
            db.backup_daily()
    except Exception as e:
        print('startup backup failed:', e)

    stop = engine.start_background()
    mobile.start_if_enabled()
    threading.Thread(target=lambda: server.app.run(host='127.0.0.1', port=port, threaded=True, use_reloader=False),
                     daemon=True).start()
    for _ in range(50):
        if port_in_use(port):
            break
        time.sleep(0.1)

    import webview
    state = {'quitting': False, 'hint_shown': False}
    window = webview.create_window('Masters Tracker', url, width=1320, height=860, min_size=(900, 600),
                                   hidden=hidden, background_color='#f6f7fb')

    def show():
        window.show()
        window.restore()

    server.show_window = show

    def on_closing():
        if state['quitting']:
            return True
        window.hide()
        if not state['hint_shown']:
            state['hint_shown'] = True
            notify.toast('Masters Tracker is still running',
                         'Reminders keep working. Open it again from the tray icon or the Start Menu.')
        return False

    window.events.closing += on_closing

    def tray():
        try:
            import pystray
        except ImportError:
            return

        def sync(icon, item):
            r = excel_sync.run()
            notify.toast('Sync to Excel', 'Done.' if r.get('ok') else r.get('error', 'Failed'))

        def quit_(icon, item):
            state['quitting'] = True
            stop.set()
            icon.stop()
            window.destroy()

        icon = pystray.Icon('masters_tracker', make_icon(), 'Masters Tracker', menu=pystray.Menu(
            pystray.MenuItem('Open Masters Tracker', lambda i, it: show(), default=True),
            pystray.MenuItem('Sync to Excel', sync),
            pystray.MenuItem('Quit', quit_)))
        icon.run()

    threading.Thread(target=tray, daemon=True).start()
    webview.start(private_mode=False, storage_path=os.path.join(db.DATA_DIR, 'webview'))
    os._exit(0)


if __name__ == '__main__':
    main()
