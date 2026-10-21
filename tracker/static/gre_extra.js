'use strict';
// Extras: guided "today's session", formula & rule cards, weekly report, smart revision, "report a bad question",
// and pronunciation (Windows voices via speechSynthesis - works offline).
// Uses helpers from app.js ($, esc, api, post, toast, fmtDate) and gre.js / gre_course.js (gre, body, views, greOpen, startTest).

// ---------------------------------------------------------------- pronunciation
function say(word) {
  try {
    const u = new SpeechSynthesisUtterance(word);
    const v = speechSynthesis.getVoices().find((x) => /en[-_](US|GB|IN)/i.test(x.lang));
    if (v) u.voice = v;
    u.lang = v ? v.lang : 'en-US'; u.rate = 0.9;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  } catch (e) { /* no voices - ignore */ }
}
const sayBtn = (w) => `<button class="say-btn" data-say="${esc(w)}" title="Hear it">🔊</button>`;

// ---------------------------------------------------------------- report a bad question
const flagBtn = (info) => `<button class="ghost small flag-btn" data-flag="${esc(JSON.stringify(info))}" title="Wrong answer, typo or confusing? Report it and it will not be shown again">⚑ Report problem</button>`;
function flagInfo(it) {
  if (it.chapter === 'vocab' || it.topic === 'vocab') return { kind: (it.q || '').includes('______') ? 'vocab_sentence' : 'other', ref: it.word || '', text: it.q };
  if (!it.gen || it.gen === 'bank') return { kind: 'bank', ref: '', text: it.q };
  return { kind: VERBAL_CH.includes(it.chapter) ? 'verbal' : 'quant', ref: it.gen, text: it.q };
}
document.addEventListener('click', async (e) => {
  const s = e.target.closest('[data-say]'); if (s) { e.preventDefault(); e.stopPropagation(); return say(s.dataset.say); }
  const f = e.target.closest('[data-flag]'); if (!f || f.disabled) return;
  e.preventDefault();
  const note = prompt('What is wrong with this question? (optional - e.g. "answer B is also right", "typo")', '');
  if (note === null) return;
  await post('/api/gre/flag', { ...JSON.parse(f.dataset.flag), note });
  f.disabled = true; f.textContent = '⚑ Reported';
  toast('Thanks - this question will not be shown again.');
});

// ---------------------------------------------------------------- guided "today's session"
const SESSION_SKIP = ['read', 'watch'];  // optional steps are not part of the guided session
function stepMinutes(k, d) {
  if (k === 'notes') return ((d.study && d.study.notes) || []).reduce((a, x) => a + x.minutes, 0) + (d.study && d.study.sheet ? d.study.sheet.minutes : 0) || 10;
  if (k === 'practice') return Math.round(d.practice.reduce((a, p) => a + p.items.length, 0) * 1.5) + (d.books.length ? 10 : 0);
  return { tutor: 25, vocab: 15, quiz: 20, essay: 35, mock: 150, homework: 15, eod: 5 }[k] || 10;
}
function renderSession(d, n) {
  const parts = d.progress.parts || {};
  const steps = [...body().querySelectorAll('.steps > .step[id^="step-"]')].map((el) => ({ k: el.id.slice(5), el,
    title: (el.querySelector('h2') || {}).innerText.replace(/^\s*\d+\s*/, '').split('—')[0].trim() })).filter((s) => !SESSION_SKIP.includes(s.k));
  if (!steps.length) return;
  const todo = steps.filter((s) => !parts[s.k]);
  const warm = d.vocab_warmup || 0;
  const mins = todo.reduce((a, s) => a + stepMinutes(s.k, d), 0) + (warm ? Math.ceil(warm * 0.3) : 0);
  const next = warm ? { k: 'warmup', title: `Warm-up (${warm} missed words)` } : todo[0];
  const started = steps.some((s) => parts[s.k]);
  const bar = document.createElement('div');
  bar.className = 'card session-bar';
  bar.innerHTML = `<div class="row"><b>Today's session</b><span class="meta">${steps.length - todo.length}/${steps.length} steps done${todo.length ? ` · about ${mins} min left` : ''}</span>
      <span style="flex:1"></span>${next ? `<button id="ss-go">${started ? 'Continue' : "Start today's session"} → ${esc(next.title)}</button>` : '<span class="pill ok">All steps done - mark the day complete below</span>'}</div>
    <div class="row ss-chips">${warm ? `<button class="chip" data-ss="warmup">Warm-up (${warm})</button>` : ''}${steps.map((s) => `<button class="chip ${parts[s.k] ? 'on' : ''}" data-ss="${s.k}">${parts[s.k] ? '✓ ' : ''}${esc(s.title)}</button>`).join('')}</div>`;
  const stepsEl = body().querySelector('.steps'); stepsEl.parentNode.insertBefore(bar, stepsEl);
  const goTo = (k) => {
    if (k === 'warmup') return greOpen(n, 'vocab');
    const el = $('#step-' + k); if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    el.classList.add('focus'); setTimeout(() => el.classList.remove('focus'), 1800);
  };
  bar.querySelectorAll('[data-ss]').forEach((b) => b.onclick = () => goTo(b.dataset.ss));
  const go = $('#ss-go'); if (go) go.onclick = () => goTo(next.k);
  // "done - next step" at the bottom of each step of the session
  steps.forEach((s, i) => {
    if (parts[s.k]) return;
    const f = document.createElement('div'); f.className = 'row step-foot';
    const after = steps.slice(i + 1).find((x) => !parts[x.k]);
    f.innerHTML = `<span style="flex:1"></span><button class="small ghost">✓ Done${after ? ` - next: ${esc(after.title)}` : ''}</button>`;
    f.querySelector('button').onclick = async () => {
      await post('/api/gre/day/' + n, { parts: { [s.k]: true } });
      gre.scrollAfter = after ? after.k : null; greClass();
    };
    s.el.appendChild(f);
  });
  if (gre.scrollAfter) { const k = gre.scrollAfter; gre.scrollAfter = null; setTimeout(() => goTo(k), 60); }
}

// ---------------------------------------------------------------- smart revision
async function smartCardHtml(day) {
  const s = await api('/api/gre/smart');
  const row = (n, label, btn) => n ? `<li><div class="grow"><b>${n}</b> ${label}</div>${btn}</li>` : '';
  const weak = ['quant', 'verbal'].map((subj) => s.weak[subj].length ? `<li><div class="grow"><b>${SUBJ[subj]} weak spots:</b> ${s.weak[subj].map((w) => `${esc(w.name)} (${w.pct}%)`).join(', ')}</div>
      <button class="small" data-smart-drill="${subj}">Weak-spot drill</button></li>` : '').join('');
  const tw = s.test_weak.length ? `<li><div class="grow"><b>From your practice tests:</b> ${s.test_weak.map((w) => `${esc(w.title)} (${w.correct}/${w.total})`).join(', ')}</div>
      ${s.test_weak.slice(0, 1).map((w) => `<button class="ghost small" data-smart-learn="${w.chapter}">Learn ${esc(w.title)}</button>`).join('')}</li>` : '';
  const items = row(s.warmup, 'missed words in the warm-up', `<button class="small" onclick="greOpen(${day || 'gre.day'}, 'vocab')">Warm-up</button>`)
    + row(s.errors_due, 'mistakes due for a redo', `<button class="small" onclick="gre.tab='errors';views.gre()">Error log</button>`)
    + row(s.cards, 'formula / rule cards due', `<button class="small" onclick="gre.tab='cards';views.gre()">Formula cards</button>`)
    + weak + tw
    + row(s.eod, 'words missed today (end-of-day review)', `<button class="ghost small" onclick="greOpen(${day || 'gre.day'}, 'vocab')">Review</button>`);
  return `<div class="card smart"><h2>Smart revision <span class="meta">- built from your own mistakes, in this order</span></h2>
    ${items ? `<ul class="list">${items}</ul>` : '<div class="empty">Nothing to revise right now - well done. Do a section simulation instead.</div>'}</div>`;
}
function bindSmart(root, day) {
  root.querySelectorAll('[data-smart-drill]').forEach((b) => b.onclick = () => startTest('drill', '', 'mixed', day || null, b.dataset.smartDrill));
  root.querySelectorAll('[data-smart-learn]').forEach((b) => b.onclick = () => openLesson(b.dataset.smartLearn));
}

// ---------------------------------------------------------------- formula & rule cards
async function greCards() {
  const c = gre.cards = await api('/api/gre/cards'); gre.ci = 0; gre.cshow = false;
  const boxes = [1, 2, 3, 4, 5].map((b) => `<div class="card stat"><div class="l">Box ${b}${b === 5 ? ' (mastered)' : ''}</div><div class="n">${c.boxes[b] || 0}</div></div>`).join('');
  body().innerHTML = `<div class="grid g2"><div class="card"><h2>Formula & rule cards due <span class="pill warn">${c.due.length}</span></h2><div id="cc"></div></div>
    <div class="card"><h2>How it works</h2><ul class="notes">
      <li>Every rule box in your study notes becomes a card (${c.total} in all). Cards unlock when you reach that topic in the plan - ${c.unlocked} so far.</li>
      <li>Read the front, say the full rule or formula out loud, then reveal. Be strict: "Knew it" only if you had it exactly.</li>
      <li>Up to 15 new cards a day${c.new_waiting ? ` (${c.new_waiting} more unlocked cards wait for the next days)` : ''}. Same boxes as vocab: box 1 daily … box 5 after 15 days.</li>
      <li>5 minutes a day keeps every formula fresh for the revision weeks and test day.</li></ul></div></div>
    <div class="grid g5" style="margin-top:16px">${boxes}</div>`;
  drawFormulaCard();
}
function drawFormulaCard() {
  const c = gre.cards; const el = $('#cc'); if (!el) return;
  if (gre.ci >= c.due.length) { el.innerHTML = `<div class="empty">${c.due.length ? 'All due cards done for today.' : 'Nothing due - cards unlock as you reach new topics.'}</div>`; return; }
  const k = c.due[gre.ci];
  el.innerHTML = `<div class="flash"><div class="meta">${esc(k.topic)} · ${k.box ? 'box ' + k.box : 'new card'} · ${gre.ci + 1} of ${c.due.length}</div>
      <div class="fcard-front">${esc(k.front)}</div>${gre.cshow ? `<div class="fcard-back">${esc(k.back)}</div>` : '<div class="meta">Say the full rule, then reveal (Space)</div>'}</div>
    <div class="row" style="justify-content:center;margin-top:10px">${gre.cshow
      ? '<button class="danger" id="cc-no">Didn\'t know (1)</button><button id="cc-yes">Knew it (2)</button>'
      : '<button id="cc-show">Reveal</button>'}<a href="#" class="linkish small-link" data-note="${k.note}">open the note</a></div>`;
  const ans = async (ok) => { await post('/api/gre/cards', { id: k.id, correct: ok }); gre.ci++; gre.cshow = false; drawFormulaCard(); };
  if ($('#cc-show')) $('#cc-show').onclick = () => { gre.cshow = true; drawFormulaCard(); };
  if ($('#cc-yes')) { $('#cc-yes').onclick = () => ans(true); $('#cc-no').onclick = () => ans(false); }
  el.querySelectorAll('[data-note]').forEach((a) => a.onclick = (e) => { e.preventDefault(); openNote(a.dataset.note); });
  document.onkeydown = (e) => {
    if (gre.tab !== 'cards' || current !== 'gre' || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    if (e.code === 'Space' && !gre.cshow) { e.preventDefault(); gre.cshow = true; drawFormulaCard(); }
    else if (gre.cshow && e.key === '1') ans(false);
    else if (gre.cshow && e.key === '2') ans(true);
  };
}

// ---------------------------------------------------------------- weekly report
function shiftIso(iso, days) { const d = new Date(iso + 'T00:00'); d.setDate(d.getDate() + days); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); }
async function weeklyCardHtml(end) {
  const r = await api('/api/gre/report' + (end ? '?end=' + end : ''));
  const p = (x) => x.ready ? `<b>${x.score}</b> <span class="meta">(${x.lo}-${x.hi}, target ${x.target})</span>` : `<span class="meta">needs ${x.need - x.n} more test questions</span>`;
  return `<div class="card weekly"><div class="row"><h2 style="margin:0">Weekly report</h2><span class="meta">${fmtDate(r.start, { day: 'numeric', month: 'short' })} – ${fmtDate(r.end, { day: 'numeric', month: 'short' })}</span>
      <span style="flex:1"></span><button class="ghost small" data-week="${shiftIso(r.end, -7)}">← Previous week</button>${end ? `<button class="ghost small" data-week="">This week</button>` : ''}</div>
    <div class="grid g4" style="margin:10px 0">
      <div class="stat"><div class="l">Classes done</div><div class="n">${r.classes}</div><div class="x">${(r.minutes / 60).toFixed(1)} h · ${r.behind ? r.behind + ' behind plan' : 'on track'}</div></div>
      <div class="stat"><div class="l">Quizzes</div><div class="n">${r.quizzes}</div><div class="x">${r.quiz_pct !== null ? r.quiz_pct + '% right' : '-'}</div></div>
      <div class="stat"><div class="l">Course tests</div><div class="n">${r.tests.quant.n + r.tests.verbal.n}</div><div class="x">Q ${r.tests.quant.pct ?? '-'}% · V ${r.tests.verbal.pct ?? '-'}%</div></div>
      <div class="stat"><div class="l">Words</div><div class="n">${r.new_words}</div><div class="x">new · ${r.words_cleared} cleared · ${r.queue_open} in queue</div></div></div>
    <div class="grid g2"><div><div class="meta">PREDICTED SCORES NOW</div><div>Quant ${p(r.predict.quant)}</div><div>Verbal ${p(r.predict.verbal)}</div>
        <div class="meta" style="margin-top:8px">${r.mistakes} mistakes logged this week · ${r.errors_open} open in the Error log</div>
        ${r.weak.length ? `<div class="meta" style="margin-top:8px">FOCUS ON</div><ul class="notes">${r.weak.map((w) => `<li>${esc(w.title)} <span class="meta">(${esc(w.topic)}, ${w.pct}%)</span></li>`).join('')}</ul>` : ''}</div>
      <div><div class="meta">NEXT 7 DAYS</div><ul class="notes">${r.next.map((x) => `<li>${fmtDate(x.date, { weekday: 'short', day: 'numeric' })} · Day ${x.day} · ${esc(x.title)}</li>`).join('') || '<li>Plan finished</li>'}</ul></div></div></div>`;
}
async function drawWeekly(holder, end) {
  holder.innerHTML = await weeklyCardHtml(end);
  holder.querySelectorAll('[data-week]').forEach((b) => b.onclick = () => drawWeekly(holder, b.dataset.week));
}
