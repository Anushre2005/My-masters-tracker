"""Windows toast notifications (falls back to console print)."""
from xml.sax.saxutils import escape

try:
    from winotify import Notification, audio
except ImportError:  # non-Windows / missing package
    Notification = None


def toast(title, msg, url=None, button=None):
    """Show a toast. With `url`, clicking the toast (or the optional `button`) opens that page in the browser."""
    if Notification is None:
        print(f'[toast] {title}: {msg}' + (f' -> {url}' if url else ''))
        return
    try:
        # winotify pastes everything into an expandable PowerShell here-string: escape ` and $ (else "$20,000"
        # becomes an empty variable) and keep it on one line; the URL and button also sit in XML attributes.
        def ps(s):
            return ' '.join(str(s).replace('`', '``').replace('$', '`$').replace(']]>', ']] >').split())
        link = ps(escape(url, {'"': '&quot;'})) if url else ''
        n = Notification(app_id='Masters Tracker', title=ps(title), msg=ps(msg or ' '), duration='long', launch=link)
        n.set_audio(audio.Default, loop=False)
        if url and button:
            n.add_actions(label=ps(escape(button, {'"': '&quot;'})), launch=link)
        n.show()
    except Exception as e:
        print('toast failed:', e)
