"""Phone flashcards over Wi-Fi: a tiny second web server that serves ONLY the GRE vocab trainer.

Off by default. When switched on (GRE → Settings) it listens on the local network (0.0.0.0, port
`gre_phone_port`) so a phone on the same Wi-Fi can open it. Every URL needs a random secret token, and the
only things it can do are list due vocab cards and record "knew it / didn't know". The main app stays on
127.0.0.1 and is never exposed.
"""
import hmac
import secrets
import socket
import threading

from flask import Flask, abort, jsonify, request

from . import db, gre

app = Flask(__name__)
_server = None
_lock = threading.Lock()


def token():
    t = db.get_setting('gre_phone_token')
    if not t:
        t = secrets.token_urlsafe(6)
        db.set_setting('gre_phone_token', t)
    return t


def port():
    try:
        return int(db.get_setting('gre_phone_port') or 8766)
    except ValueError:
        return 8766


def _check(t):
    if not hmac.compare_digest(str(t), token()):
        abort(404)


def lan_ips():
    ips = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.255.255.255', 1))  # no packet is sent; this just picks the outgoing interface
            ips.append(s.getsockname()[0])
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if ip not in ips and not ip.startswith('127.'):
                ips.append(ip)
    except OSError:
        pass
    return ips


def urls():
    return [f'http://{ip}:{port()}/v/{token()}' for ip in lan_ips()]


def running():
    return _server is not None


def start():
    global _server
    with _lock:
        if _server:
            return True
        from werkzeug.serving import make_server
        srv = make_server('0.0.0.0', port(), app, threaded=True)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        _server = srv
        return True


def stop():
    global _server
    with _lock:
        if _server:
            _server.shutdown()
            _server = None


def start_if_enabled():
    if db.get_setting('gre_phone') == '1':
        try:
            start()
        except Exception as e:
            print('phone server failed to start:', e)


def status():
    out = {'enabled': db.get_setting('gre_phone') == '1', 'running': running(), 'port': port(), 'urls': urls() if running() else []}
    if out['urls']:
        try:
            import segno
            out['qr'] = segno.make(out['urls'][0], error='m').svg_data_uri(scale=5, dark='#1f3864')
        except Exception:
            out['qr'] = None
    return out


def set_enabled(on):
    db.set_setting('gre_phone', '1' if on else '0')
    if on:
        start()
    else:
        stop()
    return status()


def new_token():
    db.set_setting('gre_phone_token', secrets.token_urlsafe(6))
    return status()


# ---------------------------------------------------------------- routes (token-protected)
@app.after_request
def _headers(r):
    r.headers['Cache-Control'] = 'no-store'
    r.headers['X-Content-Type-Options'] = 'nosniff'
    r.headers['Referrer-Policy'] = 'no-referrer'
    return r


@app.get('/v/<t>')
def page(t):
    _check(t)
    return PAGE.replace('__TOKEN__', t)


@app.get('/v/<t>/due')
def due(t):
    _check(t)
    v = gre.vocab_state()
    return jsonify({'due': v['due'][:200], 'boxes': v['boxes']})


@app.post('/v/<t>/answer')
def answer(t):
    _check(t)
    b = request.get_json(silent=True) or {}
    word = str(b.get('word', ''))[:60]
    gre.vocab_answer(word, bool(b.get('correct')))
    return jsonify(ok=True)


@app.get('/v/<t>/warmup')
def warmup(t):
    _check(t)
    return jsonify({'questions': gre.queue_state()['warmup']})


@app.post('/v/<t>/warmup')
def warmup_answer(t):
    _check(t)
    b = request.get_json(silent=True) or {}
    return jsonify(gre.queue_answer(str(b.get('word', ''))[:60], bool(b.get('correct'))))


@app.get('/v/<t>/eod')
def eod(t):
    _check(t)
    return jsonify({'questions': gre.eod_state()['questions']})


@app.post('/v/<t>/eod')
def eod_answer(t):
    _check(t)
    b = request.get_json(silent=True) or {}
    return jsonify(gre.eod_answer(str(b.get('word', ''))[:60], bool(b.get('correct'))))


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#1f3864"><title>GRE vocab</title>
<style>
:root{--bg:#f6f7fb;--card:#fff;--ink:#1c2333;--muted:#6b7385;--acc:#1f3864;--ok:#1e8e5a;--bad:#c0392b;--line:#e3e6ee;--okbg:#dff3e8;--badbg:#fbe4e2}
@media (prefers-color-scheme:dark){:root{--bg:#12151c;--card:#1b2030;--ink:#e8ebf3;--muted:#9aa3b5;--acc:#8fb0ff;--line:#2a3145;--okbg:#173326;--badbg:#3d1f1d}}
*{box-sizing:border-box}html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:520px;margin:0 auto;padding:12px 16px calc(16px + env(safe-area-inset-bottom))}
.tabs{display:flex;gap:6px;margin-bottom:12px}.tabs button{flex:1;padding:10px 4px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);font:inherit;font-size:14px;font-weight:600;min-height:44px}
.tabs button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.meta{color:var(--muted);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px 18px;min-height:220px;display:flex;flex-direction:column;justify-content:center;gap:12px}
.center{text-align:center;align-items:center}
.w{font-size:32px;font-weight:700;word-break:break-word}.d{font-size:18px}.q{font-size:18px;font-weight:600}
.row{display:flex;gap:12px;margin-top:14px}button{font:inherit;font-weight:600;border:0;border-radius:12px;padding:14px;min-height:52px;cursor:pointer}
.row button{flex:1}.show{background:var(--acc);color:#fff}.no{background:var(--bad);color:#fff}.yes{background:var(--ok);color:#fff}
.ch{display:block;width:100%;text-align:left;background:var(--card);color:var(--ink);border:1px solid var(--line);margin-top:8px;font-weight:500}
.ch.right{background:var(--okbg);border-color:var(--ok)}.ch.wrong{background:var(--badbg);border-color:var(--bad)}
.say{background:transparent;border:1px solid var(--line);color:var(--ink);min-height:40px;padding:6px 12px;font-size:15px}
.bar{height:6px;background:var(--line);border-radius:3px;overflow:hidden;margin:8px 0 12px}.bar i{display:block;height:100%;background:var(--acc)}
.exp{padding:10px 12px;border-radius:10px;background:var(--okbg)}.exp.bad{background:var(--badbg)}
</style></head><body><main>
<div class="tabs"><button data-m="warmup">Warm-up</button><button data-m="cards">Flashcards</button><button data-m="eod">Missed today</button></div>
<div class="meta" id="info">Loading...</div><div class="bar"><i id="pg" style="width:0"></i></div>
<div id="box"></div>
<p class="meta">Warm-up = missed words from earlier days (5 correct answers clear a word). Missed today = one last review before bed. Everything syncs to Masters Tracker on your laptop.</p>
</main><script>
const T='__TOKEN__';let mode='warmup',items=[],i=0,shown=false,picked=null,total=0;
const $=s=>document.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function say(w){try{const u=new SpeechSynthesisUtterance(w);u.lang='en-US';u.rate=0.9;speechSynthesis.cancel();speechSynthesis.speak(u);}catch(e){}}
const FMT={meaning:'pick the meaning',word:'pick the word',sentence:'fill the blank'};
async function load(m){mode=m;document.querySelectorAll('[data-m]').forEach(b=>b.classList.toggle('on',b.dataset.m===m));
 $('#info').textContent='Loading...';
 try{const r=await fetch('/v/'+T+'/'+(m==='cards'?'due':m));const j=await r.json();items=m==='cards'?j.due:j.questions;total=items.length;i=0;shown=false;picked=null;draw();}
 catch(e){$('#info').textContent='Cannot reach the laptop. Is Masters Tracker open and on the same Wi-Fi?';}}
function draw(){$('#pg').style.width=(total?Math.round(100*i/total):100)+'%';
 if(i>=items.length){$('#info').textContent=total?'All done for now.':'Nothing here right now.';
  $('#box').innerHTML='<div class="card center"><div class="w">Done</div><div class="meta">'+(mode==='warmup'?'Missed words come back here tomorrow.':'Come back later.')+'</div><button class="show" id="again">Check again</button></div>';
  $('#again').onclick=()=>load(mode);return;}
 if(mode==='cards')return drawCard();
 const q=items[i];$('#info').textContent=(i+1)+' of '+total+' - '+FMT[q.format];
 let h='<div class="card"><div class="q">'+esc(q.q)+'</div>'+q.c.map((c,j)=>{let cls='';if(picked!==null)cls=j===q.a?'right':(j===picked?'wrong':'');
  return '<button class="ch '+cls+'" data-c="'+j+'" '+(picked!==null?'disabled':'')+'>'+esc(c)+'</button>';}).join('');
 if(picked!==null)h+='<div class="exp '+(picked===q.a?'':'bad')+'"><b>'+esc(q.word)+'</b>: '+esc(q.def)+'</div><div class="row"><button class="say" id="sy">&#128266; say it</button><button class="show" id="nx">Next</button></div>';
 $('#box').innerHTML=h+'</div>';
 document.querySelectorAll('[data-c]').forEach(b=>b.onclick=()=>pick(+b.dataset.c));
 const nx=$('#nx');if(nx){nx.onclick=()=>{i++;picked=null;draw();};$('#sy').onclick=()=>say(q.word);}}
async function pick(j){if(picked!==null)return;picked=j;const q=items[i];draw();
 try{await fetch('/v/'+T+'/'+mode,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({word:q.word,correct:j===q.a})});}
 catch(e){$('#info').textContent='Lost connection - that answer was not saved.';}}
function drawCard(){const w=items[i];$('#info').textContent=(i+1)+' of '+total+' - group '+w.group+' - '+(w.box?'box '+w.box:'new word');
 $('#box').innerHTML='<div class="card center" id="fc"><div class="w">'+esc(w.word)+'</div><button class="say" id="sy">&#128266; say it</button>'+(shown?'<div class="d">'+esc(w.def)+'</div>':'<div class="meta">Tap to reveal</div>')+'</div><div class="row">'+(shown?'<button class="no" id="no">Didn&#39;t know</button><button class="yes" id="yes">Knew it</button>':'<button class="show" id="sh">Reveal meaning</button>')+'</div>';
 $('#sy').onclick=e=>{e.stopPropagation();say(w.word);};
 if(shown){$('#no').onclick=()=>ans(false);$('#yes').onclick=()=>ans(true);}else{$('#sh').onclick=()=>{shown=true;drawCard();};$('#fc').onclick=()=>{shown=true;drawCard();};}}
async function ans(ok){const w=items[i];i++;shown=false;draw();
 try{await fetch('/v/'+T+'/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({word:w.word,correct:ok})});}
 catch(e){$('#info').textContent='Lost connection - that answer was not saved.';}}
document.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>load(b.dataset.m));
load('warmup');
</script></body></html>"""
