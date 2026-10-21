"""Windows toast notifications (falls back to console print)."""
try:
    from winotify import Notification, audio
except ImportError:  # non-Windows / missing package
    Notification = None


def toast(title, msg):
    if Notification is None:
        print(f'[toast] {title}: {msg}')
        return
    try:
        n = Notification(app_id='Masters Tracker', title=title, msg=msg or ' ', duration='long')
        n.set_audio(audio.Default, loop=False)
        n.show()
    except Exception as e:
        print('toast failed:', e)
