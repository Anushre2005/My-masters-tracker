'use strict';
// GRE courses (quant + verbal): a tutor-style path. Each chapter = lesson (concept → worked example step by step → "your turn")
// → timed chapter test → combined unit test, plus GRE-timed section simulations, weak-spot drills, a score predictor,
// per-question pacing and a GRE-style on-screen calculator for quant.
// Uses helpers from app.js ($, esc, api, post, toast, fmtDate) and gre.js (gre, body, views, greOpen, greReplan).

const course = { view: 'home', subject: 'quant', state: null, lesson: null, test: null, result: null, timer: null, onlyWrong: false };
const STATE_PILL = { mastered: ['ok', 'Mastered'], relearn: ['bad', 'Re-learn'], tested: ['warn', 'Below 80%'], learning: ['acc', 'Learning'], due: ['warn', 'Due now'], later: ['', 'Coming up'] };
const pctPill = (p) => (p === null || p === undefined) ? '' : `<span class="pill ${p >= 80 ? 'ok' : p >= 60 ? 'warn' : 'bad'}">${p}%</span>`;
const mmss = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
const DIFF = { 1: 'Easy', 2: 'Medium', 3: 'Hard' };
const SUBJ = { quant: 'Quant', verbal: 'Verbal' };
const VERBAL_CH = ['tc_basic', 'tc_shift', 'tc_double', 'tc_triple', 'se', 'rc', 'cr', 'cr2'];
const READING_CH = ['rc', 'cr', 'cr2'];
// seconds after which a question counts as slow (same limits as the server)
const slowLimit = (ch) => ch === 'vocab' ? 60 : VERBAL_CH.includes(ch) ? (READING_CH.includes(ch) ? 150 : 90) : 120;

// ---------------------------------------------------------------- answers
function parseNum(s) {
  s = String(s ?? '').replace(/[,\s$%°]/g, '').replace(/−/g, '-');
  if (!s) return null;
  if (s.includes('/')) { const [a, b] = s.split('/').map(Number); return b && Number.isFinite(a) ? a / b : null; }
  const v = Number(s);
  return Number.isFinite(v) ? v : null;
}
function isRight(q, r) {
  if (q.kind === 'ne') { const v = parseNum(r); const t = q.v[0] / q.v[1]; return v !== null && Math.abs(v - t) <= 1e-6 * Math.max(1, Math.abs(t)); }
  if (q.kind === 'tc') return Array.isArray(r) && q.a.every((x, i) => r[i] === x);
  if (!Array.isArray(r) || !r.length) return false;
  const want = Array.isArray(q.a) ? q.a : [q.a];
  return r.length === want.length && want.every((x) => r.includes(x));
}
const hasAnswer = (r) => r !== null && r !== undefined && r !== '' && !(Array.isArray(r) && !r.length);
// fully answered: every blank of a multi-blank text completion filled
const answered = (q, r) => q.kind === 'tc' ? Array.isArray(r) && q.c.every((_, i) => r[i] !== null && r[i] !== undefined) : hasAnswer(r);
const partly = (q, r) => q.kind === 'tc' && Array.isArray(r) && r.some((x) => x !== null && x !== undefined) && !answered(q, r);
const answerText = (q, r) => q.kind === 'ne' ? String(r ?? '')
  : q.kind === 'tc' ? (answered(q, r) || partly(q, r) ? q.c.map((col, i) => (r || [])[i] !== null && (r || [])[i] !== undefined ? col[r[i]] : '—').join(' / ') : '')
    : (r || []).map((j) => q.c[j]).join(' + ');
const rightText = (q) => q.kind === 'ne' ? q.a : q.kind === 'tc' ? q.a.map((j, i) => q.c[i][j]).join(' / ') : (Array.isArray(q.a) ? q.a : [q.a]).map((j) => q.c[j]).join(' + ');

function qBody(q, r, { locked = false, reveal = false } = {}) {
  let ans;
  if (q.kind === 'ne') {
    const cls = reveal ? (isRight(q, r) ? 'right' : 'wrong') : '';
    ans = `<div class="row"><input id="ne-in" class="ne ${cls}" value="${esc(r ?? '')}" placeholder="Type your answer" autocomplete="off" ${locked ? 'disabled' : ''}>
      ${reveal && !isRight(q, r) ? `<span>Correct answer: <b>${esc(q.a)}</b></span>` : ''}</div>`;
  } else if (q.kind === 'tc') {
    const names = ['Blank (i)', 'Blank (ii)', 'Blank (iii)'];
    ans = `<div class="tc-cols">${q.c.map((col, b) => `<div class="col"><h4>${names[b]}</h4><div class="choices">${col.map((c, j) => {
      const on = (r || [])[b] === j;
      let cls = on ? 'picked' : '';
      if (reveal) cls = q.a[b] === j ? 'right' : (on ? 'wrong' : '');
      return `<button class="choice ${cls}" data-b="${b}" data-c="${j}" ${locked ? 'disabled' : ''}>${esc(c)}</button>`;
    }).join('')}</div></div>`).join('')}</div>`;
  } else {
    const right = Array.isArray(q.a) ? q.a : [q.a];
    ans = `<div class="choices">${q.c.map((c, j) => {
      const on = (r || []).includes(j);
      let cls = on ? 'picked' : '';
      if (reveal) cls = right.includes(j) ? 'right' : (on ? 'wrong' : '');
      return `<button class="choice ${cls}" data-c="${j}" ${locked ? 'disabled' : ''}>${q.kind === 'ma' ? (on ? '☑' : '☐') : String.fromCharCode(65 + j)}&nbsp; ${esc(c)}</button>`;
    }).join('')}</div>`;
  }
  const tip = q.kind === 'ma' ? `<div class="meta" style="margin-bottom:6px">${q.chapter === 'se' ? 'Select exactly TWO answers.' : 'Select ALL correct answers - there may be one or several.'}</div>`
    : q.kind === 'ne' ? '<div class="meta" style="margin-bottom:6px">Numeric entry: type the number (fractions like 7/3 are fine).</div>'
      : q.kind === 'tc' ? '<div class="meta" style="margin-bottom:6px">Pick one word for each blank. Both / all blanks must be right.</div>' : '';
  const psg = q.passage ? `<div class="passage"><div class="ptitle">Passage${q.ptitle ? ' · ' + esc(q.ptitle) : ''}</div>${esc(q.passage)}</div>` : '';
  return `${psg}<div class="qtext">${esc(q.q)}</div>${tip}${ans}`;
}
// wire up choice buttons / numeric input; choices redraw, the text input does not (keeps focus)
function bindQ(box, q, get, set, redraw) {
  box.querySelectorAll('[data-c]').forEach((b) => b.onclick = () => {
    const j = +b.dataset.c;
    if (q.kind === 'tc') { const r = [...(get() || q.c.map(() => null))]; r[+b.dataset.b] = j; set(r); return redraw(); }
    const r = get() || [];
    set(q.kind === 'ma' ? (r.includes(j) ? r.filter((x) => x !== j) : [...r, j]) : [j]);
    redraw();
  });
  const ne = box.querySelector('#ne-in');
  if (ne) { ne.oninput = () => set(ne.value); if (!ne.disabled) ne.focus(); }
}

// ---------------------------------------------------------------- score predictor card
function predictCard(p, compact = false) {
  const name = SUBJ[p.subject];
  if (!p.ready) return `<div class="card predict"><h2>Predicted ${name} score</h2><div class="meta">Appears after ${p.need} test questions in the last 45 days (you have ${p.n}). Chapter, unit and section tests all count.</div>
    ${p.last_mock ? `<div style="margin-top:8px">Last practice test: <b>${p.last_mock.score}</b> <span class="meta">(${esc(p.last_mock.name || '')}, ${fmtDate(p.last_mock.date)})</span></div>` : ''}</div>`;
  const pos = (v) => `${Math.round(100 * (v - 130) / 40)}%`;
  const gap = p.target ? p.target - p.score : 0;
  return `<div class="card predict"><div class="row" style="justify-content:space-between;align-items:flex-start"><div><h2 style="margin-bottom:2px">Predicted ${name}</h2>
      <div class="big">${p.score}</div><div class="range">likely ${p.lo}–${p.hi} · target ${p.target || '–'}</div></div>
      <div style="text-align:right">${gap > 0 ? `<span class="pill warn">${gap} below target</span>` : p.target ? '<span class="pill ok">At or above target</span>' : ''}</div></div>
    <div class="gauge"><span class="rng" style="left:${pos(p.lo)};width:${Math.max(1, Math.round(100 * (p.hi - p.lo) / 40))}%"></span>
      ${p.target ? `<span class="tg" style="left:${pos(p.target)}" title="Target ${p.target}"></span>` : ''}<span class="pt" style="left:${pos(p.score)}"></span></div>
    <div class="gauge-scale"><span>130</span><span>150</span><span>170</span></div>
    ${compact ? '' : `<div class="meta" style="margin-top:8px">From ${p.n} questions (${p.accuracy}% right, weighted by difficulty).${p.pace ? ` Pace ${p.pace} s/question vs GRE ${p.pace_target} s.` : ''}${p.penalty ? ` −${p.penalty} for slow pacing.` : ''}
      A rough estimate from this app's questions - your POWERPREP scores are the real benchmark.${p.last_mock ? ` Last practice test: <b>${p.last_mock.score}</b>.` : ''}</div>`}</div>`;
}

// ---------------------------------------------------------------- home
async function greCourse() {
  if (course.view === 'lesson' && course.lesson) return drawLesson();
  if (course.view === 'test' && course.test) return drawTest();
  if (course.view === 'result' && course.result) return drawResult();
  course.view = 'home';
  const subj = course.subject;
  const s = course.state = await api('/api/gre/course?subject=' + subj);
  const nx = s.next; const sp = s.spec;
  const mastered = s.chapters.filter((c) => c.state === 'mastered').length;
  const learnt = s.chapters.filter((c) => c.learnt >= c.concepts).length;
  const chRow = (c) => {
    const [cls, lab] = STATE_PILL[c.state];
    return `<li class="${c.taught ? '' : 'later'}"><span class="time">Day ${c.day}<div class="meta">${fmtDate(c.date, { day: 'numeric', month: 'short' })}</div></span>
      <div class="grow"><b>${esc(c.title)}</b> <span class="pill ${cls}">${lab}</span>
        <div class="meta">Lesson ${c.learnt}/${c.concepts} concepts${c.attempts ? ` · ${c.attempts} test${c.attempts > 1 ? 's' : ''} · last ${c.last}%` : ''}</div></div>
      ${pctPill(c.best)}<button class="ghost small" data-learn="${c.key}">Learn</button><button class="small" data-test="chapter:${c.key}">Test</button></li>`;
  };
  const unitCard = (u) => `<div class="card" style="margin-bottom:16px"><div class="row" style="justify-content:space-between">
      <div><h2 style="margin:0">${esc(u.title)}</h2><div class="meta">Combined test planned for day ${u.day} (${fmtDate(u.date, { day: 'numeric', month: 'short' })})${u.attempts ? ` · ${u.attempts} attempt${u.attempts > 1 ? 's' : ''}` : ''}</div></div>
      <div class="row">${pctPill(u.best)}<button class="${u.ready ? '' : 'ghost'} small" data-test="unit:${u.key}" title="${u.ready ? '' : 'Best taken after every chapter test in this unit'}">Unit test · ${sp.unit.n} Q</button></div></div>
    <ul class="list">${s.chapters.filter((c) => c.unit === u.key).map(chRow).join('')}</ul></div>`;
  const goLabel = { lesson: 'Start lesson', class: 'Open class' }[nx.type] || 'Start test';
  body().innerHTML = `
    ${s.behind > 1 && s.class ? `<div class="card banner" style="margin-bottom:12px"><div class="grow"><b>You are ${s.behind} classes behind your plan.</b>
        <span class="meta">The next class is Day ${s.class.day} (${esc(s.class.title)}), planned for ${fmtDate(s.class.date, { day: 'numeric', month: 'short' })}.</span></div>
        <button class="ghost small" onclick="greOpen(${s.class.day})">Open Day ${s.class.day}</button><button class="small" onclick="greReplan()">Re-plan from today</button></div>` : ''}
    <div class="card tutor-next"><div class="row" style="justify-content:space-between;align-items:flex-start;flex-wrap:nowrap">
      <div><div class="meta" style="letter-spacing:.06em">YOUR ${SUBJ[subj].toUpperCase()} TUTOR SAYS</div><h2 style="margin:4px 0 6px">${esc(nx.label)}</h2><div>${esc(nx.why)}</div></div>
      <button id="nx-go" style="white-space:nowrap">${goLabel}</button></div></div>
    <div class="grid g4" style="margin:16px 0">
      <div class="card stat"><div class="l">Chapters mastered (80%+)</div><div class="n">${mastered}/${s.chapters.length}</div></div>
      <div class="card stat"><div class="l">Lessons finished</div><div class="n">${learnt}/${s.chapters.length}</div></div>
      <div class="card stat"><div class="l">Tests taken</div><div class="n">${s.tests_taken}</div></div>
      <div class="card stat"><div class="l">Weak spots</div><div class="n">${s.weak.length}</div><div class="x">concepts under 70%</div></div></div>
    <div class="course-grid"><div>${s.units.map(unitCard).join('')}</div>
      <div class="grid" style="align-content:start">
        ${predictCard(s.predict, true)}
        <div class="card"><h2>How your tutor works</h2><ol class="notes">
          <li><b>Learn</b> one chapter at a time: each concept is explained, then a worked example is revealed step by step, then you solve one yourself.</li>
          <li><b>Chapter test</b>: ${sp.chapter.n} questions, ${sp.chapter.minutes} minutes, no hints. 80% = mastered; under 60% = re-learn.</li>
          <li><b>Unit test</b>: ${sp.unit.n} questions mixing the unit's chapters - you must spot what each question needs.</li>
          <li><b>Section simulation</b>: real GRE timing; section 2 gets harder if you do well on section 1.</li>
          <li>${subj === 'quant' ? 'Every test has new numbers, so retakes never repeat.' : 'A question you have answered is never served again; when the hand-written ones run out, tests use new sentences on your words.'} Mistakes go to your Error log and come back until you get them right 3 times.</li></ol></div>
        <div class="card"><h2>Weak spots</h2>${s.weak.length ? `<ul class="list">${s.weak.map((w) => `<li><div class="grow"><b>${esc(w.name)}</b><div class="meta">${esc(w.title)} · ${w.correct}/${w.total} right</div></div>
            ${pctPill(w.pct)}<button class="ghost small" data-relearn="${w.chapter}:${w.concept}">Re-learn</button></li>`).join('')}</ul>
          <button style="margin-top:10px" data-test="drill:">Weak-spot drill · ${sp.drill.n} Q</button>` : '<div class="empty">Concepts you get wrong in tests show up here.</div>'}
          ${(s.test_weak || []).length ? `<div class="meta" style="margin:12px 0 4px">FROM YOUR UPLOADED TEST RESULTS</div><ul class="list">${s.test_weak.map((w) => `<li><div class="grow"><b>${esc(w.title)}</b>
            <div class="meta">${w.correct}/${w.total} right in practice tests</div></div>${pctPill(w.pct)}<button class="ghost small" data-learn="${w.chapter}">Learn</button></li>`).join('')}</ul>` : ''}</div>
        <div class="card"><h2>Section simulation</h2><div>Section 1: ${sp.section1.n} questions in ${sp.section1.minutes} minutes from every chapter you have reached. Then section 2 (${sp.section2.n} questions, ${sp.section2.minutes} minutes) - harder if you scored well, like the real adaptive GRE.${subj === 'quant' ? ' The on-screen calculator is available, as on test day.' : ''}</div>
          <button style="margin-top:10px" data-test="section1:">Start section 1</button></div>
        <div class="card"><h2>Recent tests</h2><ul class="list">${s.recent.map((t) => `<li><span class="time">${fmtDate(t.at.slice(0, 10), { day: 'numeric', month: 'short' })}</span>
            <div class="grow">${esc(t.title)}<div class="meta">${t.seconds ? mmss(t.seconds) + ' used' : ''}</div></div>${pctPill(Math.round(100 * t.score / t.total))}
            <button class="ghost small" data-review="${t.id}">Review</button></li>`).join('') || '<li class="empty">No tests yet.</li>'}</ul></div></div></div>`;
  $('#nx-go').onclick = () => nx.type === 'lesson' ? openLesson(nx.key) : nx.type === 'class' ? greOpen(nx.key)
    : startTest(nx.type === 'section' ? 'section1' : nx.type, nx.key || '');
  body().querySelectorAll('[data-learn]').forEach((b) => b.onclick = () => openLesson(b.dataset.learn));
  body().querySelectorAll('[data-test]').forEach((b) => b.onclick = () => { const [k, key] = b.dataset.test.split(':'); startTest(k, key); });
  body().querySelectorAll('[data-relearn]').forEach((b) => b.onclick = () => { const [ch, c] = b.dataset.relearn.split(':'); openLesson(ch, +c); });
  body().querySelectorAll('[data-review]').forEach((b) => b.onclick = async () => {
    const t = await api('/api/gre/course/test/' + b.dataset.review);
    course.result = { ...t, fresh: false }; course.view = 'result'; course.onlyWrong = false; drawResult(); window.scrollTo(0, 0);
  });
}
function courseHome() { course.view = 'home'; course.lesson = null; course.result = null; showCourse(); }

// switch the GRE screen to the right course tab (if needed) and draw the current course view
function quizMode() {
  return (course.view === 'test' && course.test && course.test.quiz) || (course.view === 'result' && course.result && course.result.quiz) || course.view === 'quizbreak' || course.view === 'mockessay';
}
function drawQuizView() { return course.view === 'test' ? drawTest() : course.view === 'quizbreak' ? drawQuizBreak() : course.view === 'mockessay' ? drawMockEssay() : drawResult(); }
function showCourse() {
  if (quizMode()) {
    if (current !== 'gre' || gre.tab !== 'class') { gre.tab = 'class'; if (current !== 'gre') return go('gre'); return views.gre(); }
    drawQuizView(); window.scrollTo(0, 0); return;
  }
  const tab = course.subject === 'verbal' ? 'vcourse' : 'course';
  if (current !== 'gre' || gre.tab !== tab) { gre.tab = tab; if (current !== 'gre') return go('gre'); return views.gre(); }
  greCourse(); window.scrollTo(0, 0);
}

// ---------------------------------------------------------------- lesson
async function openLesson(ch, ci = null) {
  const L = await api('/api/gre/course/lesson/' + ch);
  const done = new Set(L.done);
  const first = ci ?? L.concepts.findIndex((c) => !done.has(c.i));
  course.subject = L.subject || (VERBAL_CH.includes(ch) ? 'verbal' : 'quant');
  course.lesson = { ...L, done, finished: ci === null && first < 0, ci: first < 0 ? 0 : first };
  resetConcept();
  course.view = 'lesson';
  showCourse();
}
function resetConcept() { Object.assign(course.lesson, { shown: 0, q: null, r: null, tries: 0, solved: false, revealed: false, set: null }); }

function drawLesson() {
  const L = course.lesson;
  const c = L.concepts[L.ci]; const ex = c.example;
  const allShown = L.shown >= ex.steps.length;
  const best = L.tests.length ? Math.max(...L.tests) : null;
  body().innerHTML = `<div class="row" style="margin-bottom:12px"><button class="ghost small" id="ls-back">← ${SUBJ[course.subject]} course</button>
      <h2 style="margin:0">${esc(L.title)}</h2><span class="meta">Day ${L.day} · ${L.done.size}/${L.concepts.length} concepts learnt${best !== null ? ` · best chapter test ${best}%` : ''}</span>
      <span style="flex:1"></span>${course.subject === 'quant' ? '<button class="ghost small" onclick="calcToggle()">Calculator</button>' : ''}</div>
    <div class="lesson-grid">
      <div class="card"><div class="meta" style="margin-bottom:6px">CONCEPTS</div><ol class="outline">${L.concepts.map((k) => `<li class="${k.i === L.ci && !L.finished ? 'cur' : ''}" data-ci="${k.i}">
          <span class="tick">${L.done.has(k.i) ? '✓' : ''}</span>${esc(k.title)}</li>`).join('')}
        <li class="${L.finished ? 'cur' : ''}" data-ci="end"><span class="tick"></span>Chapter test</li></ol></div>
      <div>${L.finished ? lessonEnd(L) : `
        <div class="card"><div class="meta">CONCEPT ${L.ci + 1} OF ${L.concepts.length}</div><h2 style="margin:4px 0 8px">${esc(c.title)}</h2>
          <ul class="notes">${c.teach.map((t) => `<li>${esc(t)}</li>`).join('')}</ul></div>
        <div class="card" style="margin-top:12px"><h3>Worked example</h3><div class="qtext">${esc(ex.q)}</div>
          <ol class="ex-steps">${ex.steps.slice(0, L.shown).map((x) => `<li>${esc(x)}</li>`).join('')}</ol>
          ${allShown ? `<div class="explain ok"><b>Answer:</b> ${esc(ex.a)}</div>`
            : `<div class="row"><button class="small" id="ls-step">${L.shown ? 'Next step' : 'Show the first step'}</button>
               <span class="meta">Try each step yourself before you reveal it.</span><span style="flex:1"></span><button class="ghost small" id="ls-all">Show all steps</button></div>`}</div>
        ${allShown ? practiceCard(L, c) : ''}`}</div></div>`;
  $('#ls-back').onclick = courseHome;
  body().querySelectorAll('[data-ci]').forEach((li) => li.onclick = () => {
    if (li.dataset.ci === 'end') L.finished = true; else { L.finished = false; L.ci = +li.dataset.ci; }
    resetConcept(); drawLesson(); window.scrollTo(0, 0);
  });
  if (L.finished) { $('#ls-test').onclick = () => startTest('chapter', L.chapter); return; }
  const st = $('#ls-step'); if (st) st.onclick = () => { L.shown++; drawLesson(); };
  const sa = $('#ls-all'); if (sa) sa.onclick = () => { L.shown = ex.steps.length; drawLesson(); };
  const nx = $('#ls-next'); if (nx) nx.onclick = () => {
    if (L.ci + 1 < L.concepts.length) L.ci++; else L.finished = true;
    resetConcept(); drawLesson(); window.scrollTo(0, 0);
  };
  const again = $('#ls-again'); if (again) again.onclick = loadSet;
  if (allShown && !L.set) return loadSet();
  if (!L.q || !L.set || L.set.over) return;
  bindQ($('#ls-q'), L.q, () => L.r, (v) => { L.r = v; const ck = $('#ls-check'); if (ck) ck.disabled = !answered(L.q, v); }, drawLesson);
  const ck = $('#ls-check'); if (ck) ck.onclick = async () => {
    const right = isRight(L.q, L.r);
    if (right) L.solved = true; else if (++L.tries >= 2) L.revealed = true;
    if (L.solved || L.revealed) await recordPractice(L, right);
    drawLesson();
  };
  const ne = $('#ne-in'); if (ne && ck) ne.onkeydown = (e) => { if (e.key === 'Enter' && hasAnswer(ne.value)) ck.click(); };
  const nq = $('#ls-nextq'); if (nq) nq.onclick = () => nextPractice(L);
  const fl = $('#ls-flag'); if (fl) fl.onclick = async () => {
    if (L.q.flagged) return;
    await post('/api/gre/vocab/sentence/flag', { word: L.q.word, sentence: L.q.q });
    L.q.flagged = true; toast('Thanks - that sentence will not be used again.'); drawLesson();
  };
}
// ---------------------------------------------------------------- 10-question practice set for each concept
const PASS = 0.7; // share of the set answered right that ticks the concept as learnt
function practiceNote(S) {
  const a = S.vocab ? `${S.vocab} of these use words from your earlier sessions${S.style ? ', with the kind of clue this concept teaches' : ''}.` : '';
  const b = S.missing ? ` ${S.missing} more of your words are being written into new sentences in the background - press "New set" later to get them.` : '';
  return a + b;
}
function practiceCard(L, c) {
  const S = L.set;
  if (!S) return `<div class="card" style="margin-top:12px"><h3>Practice</h3><div class="meta">Building your practice set…</div></div>`;
  const n = S.qs.length; const right = S.res.filter(Boolean).length;
  const dots = S.qs.map((_, i) => `<span class="pdot ${S.res[i] === true ? 'ok' : S.res[i] === false ? 'bad' : i === S.i && !S.over ? 'cur' : ''}"></span>`).join('');
  const note = practiceNote(S);
  const nextConcept = L.ci + 1 >= L.concepts.length ? 'Finish lesson →' : 'Next concept →';
  if (S.over) {
    const pass = n && right / n >= PASS;
    return `<div class="card" style="margin-top:12px"><h3>Practice result: ${right} / ${n}</h3>
      <div class="pdots">${dots}</div>
      <div class="explain ${pass ? 'ok' : 'warn'}" style="margin-top:10px">${pass ? 'Concept learnt ✓ - well done.'
        : `Below ${Math.round(PASS * 100)}% - re-read the concept and the worked example above, then try a new set.`}
        ${S.res.some((x) => x === false) ? ' Course questions you got wrong are in your Error log, and missed words joined your missed-words queue.' : ''}</div>
      ${note ? `<div class="meta" style="margin-top:6px">${esc(note)}</div>` : ''}
      <div class="row" style="margin-top:10px"><button class="ghost small" id="ls-again">New set</button><span style="flex:1"></span>
        <button class="small" id="ls-next">${nextConcept}</button></div></div>`;
  }
  const q = L.q;
  return `<div class="card" style="margin-top:12px"><div class="row"><h3 style="margin:0">Practice · question ${S.i + 1} of ${n}</h3><span style="flex:1"></span>
      <span class="meta">${q.word ? 'Word from an earlier session · ' : ''}${DIFF[q.diff] || ''}</span></div>
    <div class="pdots" style="margin:6px 0 10px">${dots}</div>
    <div id="ls-q">${qBody(q, L.r, { locked: L.solved || L.revealed, reveal: L.solved || L.revealed })}</div>
    ${practiceFeedback(L, c)}
    ${S.i === 0 && note ? `<div class="meta" style="margin-top:8px">${esc(note)}</div>` : ''}</div>`;
}
function practiceFeedback(L, c) {
  const S = L.set; const last = S.i + 1 >= S.qs.length;
  const nextQ = `<button class="small" id="ls-nextq">${last ? 'See my result' : 'Next question →'}</button>`;
  const skip = `<button class="ghost small" id="ls-next">${L.ci + 1 >= L.concepts.length ? 'Finish lesson' : 'Skip to next concept'}</button>`
    + (L.q.word ? ` <button class="ghost small" id="ls-flag" title="The sentence is wrong, unclear or has two possible answers">${L.q.flagged ? 'Reported ✓' : 'Report sentence'}</button>` : '');
  if (L.solved) return `<div class="explain ok"><b>Correct!</b> ${esc(L.q.x)}</div><div class="row" style="margin-top:10px">${skip}<span style="flex:1"></span>${nextQ}</div>`;
  if (L.revealed) return `<div class="explain bad"><b>Here is how to do it.</b> The answer is <b>${esc(rightText(L.q))}</b>. ${esc(L.q.x)}</div>
    <div class="row" style="margin-top:10px">${skip}<span style="flex:1"></span>${nextQ}</div>`;
  const hint = L.q.word ? 'Find the clue in the sentence, predict your own word, then match it to a word you learnt earlier.' : c.hint;
  return `${L.tries ? `<div class="explain warn"><b>Not quite - try once more.</b> Hint: ${esc(hint)}</div>` : ''}
    <div class="row" style="margin-top:10px"><button id="ls-check" ${answered(L.q, L.r) ? '' : 'disabled'}>Check answer</button>
    <span class="meta">${L.tries ? 'Second try - after this I will show you the solution.' : 'Two tries, with a hint after the first.'}</span></div>`;
}
async function loadSet() {
  const L = course.lesson;
  const s = await api(`/api/gre/course/practice/${L.chapter}/${L.ci}`);
  if (!s || s.error || !s.questions || !s.questions.length) { toast((s && s.error) || 'No practice questions for this concept.'); return; }
  L.set = { qs: s.questions, i: 0, res: [], vocab: s.vocab, missing: s.missing, style: s.style, over: false };
  Object.assign(L, { q: s.questions[0], r: null, tries: 0, solved: false, revealed: false });
  drawLesson();
}
async function recordPractice(L, right) {
  const S = L.set; const q = L.q;
  if (S.res[S.i] !== undefined) return;
  S.res[S.i] = right;
  await post(`/api/gre/course/practice/${L.chapter}/${L.ci}`, { correct: right, word: q.word || null, gen: q.gen || null,
    q: q.passage ? `${q.ptitle || 'Passage'}: ${q.q}` : q.q, answer: rightText(q), x: q.x,
    item: { kind: q.kind, q: q.q, c: q.c, a: q.a, v: q.v, x: q.x, passage: q.passage, ptitle: q.ptitle, diff: q.diff, gen: q.gen } });
}
async function nextPractice(L) {
  const S = L.set;
  if (S.i + 1 < S.qs.length) {
    S.i++;
    Object.assign(L, { q: S.qs[S.i], r: null, tries: 0, solved: false, revealed: false });
    drawLesson(); window.scrollTo(0, document.body.scrollHeight);
    return;
  }
  S.over = true;
  if (S.res.filter(Boolean).length / S.qs.length >= PASS) {
    L.done.add(L.ci);
    await post('/api/gre/course/lesson/' + L.chapter, { concept: L.ci });
  }
  drawLesson();
}
function lessonEnd(L) {
  const n = L.concepts.length; const k = L.done.size;
  return `<div class="card"><h2>${k >= n ? 'Lesson complete 🎉' : 'End of the lesson'}</h2>
    <div>${k >= n ? `You solved a "your turn" question for all ${n} concepts.` : `You have solved ${k} of ${n} concepts. Concepts without a ✓ are worth one more look - click them on the left.`}</div>
    <div class="meta" style="margin:10px 0">The chapter test has 10 questions in 15 minutes, from easy to hard, with no hints - just like a tutor's class test.
      80%+ means you have mastered the chapter; below 60% means re-learn the weak concepts first.</div>
    <button id="ls-test">Take the chapter test · 10 Q · 15 min</button></div>`;
}

// ---------------------------------------------------------------- test runner
async function startTest(kind, key = '', level = 'mixed', fromDay = null, subject = null) {
  subject = subject || course.subject || 'quant';
  if (course.test && !confirm('A test is already running. Abandon it and start this one?')) return;
  const t = await api(`/api/gre/course/test?kind=${kind}&key=${encodeURIComponent(key || '')}&level=${level}&subject=${subject}`);
  if (t.error) return toast(t.error);
  if (t.fresh_note) toast(t.fresh_note);
  clearInterval(course.timer); course.timer = null;
  course.subject = subject;
  course.test = { ...t, subject, i: 0, resp: t.questions.map(() => null), marked: new Set(), secs: t.questions.map(() => 0),
    start: Date.now(), qStart: Date.now(), review: false, fromDay, level };
  course.view = 'test';
  showCourse();
}
// ---------------------------------------------------------------- daily quiz in GRE format (sections on the day's topics + vocab)
async function startQuiz(n) {
  if (course.test && !confirm('A test is already running. Abandon it and start the quiz?')) return;
  const qz = await api('/api/gre/quiz/' + n);
  if (!qz.sections || !qz.sections.length) return toast('No quiz for this day.');
  clearInterval(course.timer); course.timer = null;
  course.quiz = { day: n, title: qz.title, sections: qz.sections, idx: 0, items: [], seconds: 0, minutes: 0 };
  startQuizSection();
}
async function startWeekTest(week, day) {
  if (course.test && !confirm('A test is already running. Abandon it and start the weekly test?')) return;
  const wt = await api('/api/gre/weektest/' + week);
  if (!wt.sections || !wt.sections.length) return toast('Nothing to test for this week yet.');
  const c = wt.counts;
  if (!confirm(`Week ${week} summary test: ${c.quant} Quant, ${c.verbal} Verbal and ${c.words} vocabulary questions in ${wt.sections.length} timed sections (about ${wt.sections.reduce((a, s) => a + s.minutes, 0)} min). Start?`)) return;
  clearInterval(course.timer); course.timer = null;
  course.quiz = { weekly: true, week, day, title: wt.title, sections: wt.sections, idx: 0, items: [], seconds: 0, minutes: 0 };
  startQuizSection();
}
async function startMock(day = null) {
  if (course.test && !confirm('A test is already running. Abandon it and start the full practice test?')) return;
  if (!confirm('Start a full practice test? Essay (30 min), then Verbal and Quant sections with real GRE timing - about 2 hours. Find a quiet place first.')) return;
  const m = await api('/api/gre/mock/start');
  clearInterval(course.timer); course.timer = null;
  course.quiz = { mock: true, day: day, title: 'Full practice test (in the app)', prompt: m.prompt, idx: 0, items: [], seconds: 0, minutes: 0, done: [], s1: {},
    sections: m.plan.map((p) => p.type === 'essay' ? { ...p, subject: 'essay', questions: [] }
      : { ...p, title: `${SUBJ[p.subject]} section ${p.kind === 'section1' ? 1 : 2}${p.kind === 'section2' ? ' (adaptive)' : ''}`, questions: null }) };
  startQuizSection();
}
function drawMockEssay() {
  const Q = course.quiz;
  body().innerHTML = `<div class="card test-bar"><div class="row"><b>${esc(Q.title)} · Analytical Writing</b><span style="flex:1"></span>
      <span class="meta" id="me-words">0 words</span><span class="timer" id="me-timer">30:00</span><button class="small" id="me-submit">Submit essay</button></div></div>
    <div class="card test-q"><div class="prompt">${esc(Q.prompt)}</div>
      <div class="meta" style="margin:6px 0">Write a response in which you discuss the extent to which you agree or disagree with the statement and explain your reasoning.</div>
      <textarea id="me-body" rows="18" placeholder="Plan 5 minutes, write 22, proofread 3."></textarea></div>`;
  const ta = $('#me-body'); const t0 = Q.essayStart || (Q.essayStart = Date.now());
  ta.value = Q.essayText || ''; ta.focus();
  ta.oninput = () => { Q.essayText = ta.value; $('#me-words').textContent = (ta.value.trim() ? ta.value.trim().split(/\s+/).length : 0) + ' words'; };
  ta.oninput();
  const submit = async () => {
    clearInterval(course.timer); course.timer = null;
    if ((Q.essayText || '').trim()) {
      const r = await post('/api/gre/essays', { day: Q.day, prompt: Q.prompt, body: Q.essayText, minutes: Math.round((Date.now() - t0) / 600) / 100 });
      Q.essayId = r.id;
    }
    Q.idx++; course.view = 'quizbreak'; showCourse();
  };
  clearInterval(course.timer);
  course.timer = setInterval(() => {
    const left = Math.max(0, 1800 - Math.floor((Date.now() - t0) / 1000)); const el = $('#me-timer');
    if (el) { el.textContent = mmss(left); el.classList.toggle('late', left < 180); }
    if (!left) { toast('Time is up - essay submitted.'); submit(); }
  }, 1000);
  $('#me-submit').onclick = () => { if (confirm('Submit the essay and go on to the next section?')) submit(); };
}
async function startQuizSection() {
  const Q = course.quiz; const s = Q.sections[Q.idx];
  if (Q.mock && s.type === 'essay') { course.view = 'mockessay'; return showCourse(); }
  if (Q.mock && !s.questions) {  // section 2 difficulty depends on how section 1 of that subject went
    const p = Q.s1[s.subject]; const level = s.kind === 'section2' ? (p >= 60 ? 'hard' : p < 40 ? 'easy' : 'mixed') : 'mixed';
    const t = await api(`/api/gre/course/test?kind=${s.kind}&subject=${s.subject}&level=${level}`);
    Object.assign(s, { questions: t.questions, minutes: t.minutes, title: t.title, level, key: t.key });
  }
  course.test = { kind: 'quiz', key: '', quiz: true, title: Q.sections.length > 1 ? `${s.title} (section ${Q.idx + 1} of ${Q.sections.length})` : s.title,
    minutes: s.minutes, questions: s.questions, subject: s.subject, i: 0, resp: s.questions.map(() => null), marked: new Set(),
    secs: s.questions.map(() => 0), start: Date.now(), qStart: Date.now(), review: false, fromDay: Q.day, level: 'mixed' };
  course.view = 'test';
  showCourse();
}
function drawQuizBreak() {
  const Q = course.quiz; const s = Q.sections[Q.idx]; const prev = Q.sections[Q.idx - 1];
  body().innerHTML = `<div class="card test-q" style="max-width:640px;margin:20px auto"><div class="meta">${esc(Q.title)}</div>
      <h2 style="margin:6px 0">Section ${Q.idx} complete</h2>
      <div>You finished <b>${esc(prev.title)}</b>. Like the real GRE, your score comes at the end.</div>
      <div class="card" style="margin:14px 0;background:var(--grey-soft)"><b>Next: ${esc(s.title)}</b>
        <div class="meta">${s.questions ? `${s.questions.length} questions · ${s.minutes} minutes` : (s.kind === 'section2' ? 'difficulty set by your section 1 - like the real test' : 'GRE timing')}${s.subject === 'quant' ? ' · calculator available' : ''}</div></div>
      <div class="meta" style="margin-bottom:12px">On test day you get a 1-minute break between sections - stretch, then go.</div>
      <button id="qb-go">Start section ${Q.idx + 1}</button></div>`;
  $('#qb-go').onclick = startQuizSection;
}

function tickTest() {
  const t = course.test; if (!t) { clearInterval(course.timer); course.timer = null; return; }
  const left = t.minutes * 60 - Math.floor((Date.now() - t.start) / 1000);
  const el = $('#tt-timer'); if (el) { el.textContent = mmss(Math.max(0, left)); el.classList.toggle('late', left < 120); }
  if (left <= 0) { toast('Time is up - your test has been submitted.'); submitTest(); }
}
function drawTest() {
  const t = course.test; const n = t.questions.length; const q = t.questions[t.i];
  if (!course.timer) course.timer = setInterval(tickTest, 1000);
  const done = t.questions.filter((qq, i) => answered(qq, t.resp[i])).length;
  const statusOf = (i) => answered(t.questions[i], t.resp[i]) ? 'Answered' : partly(t.questions[i], t.resp[i]) ? 'Incomplete' : 'Not answered';
  body().innerHTML = `<div class="card test-bar"><div class="row">
      <b>${esc(t.title)}</b><span style="flex:1"></span><span class="meta">${done}/${n} answered</span>
      ${t.subject === 'quant' ? '<button class="ghost small" onclick="calcToggle()">Calculator</button>' : ''}
      <button class="ghost small" id="tt-review">${t.review ? 'Return to question' : 'Review'}</button>
      <span class="timer" id="tt-timer" title="Time left"></span><button class="small" id="tt-submit">Submit</button></div></div>
    ${t.review ? `<div class="card test-q"><h2>Review</h2><div class="meta" style="margin-bottom:10px">Like the GRE review screen: click a row to go to that question. Marked questions have an amber edge.</div>
        <table class="review-table"><thead><tr><th>#</th><th>Status</th><th>Marked</th><th></th></tr></thead><tbody>
        ${t.questions.map((qq, i) => `<tr class="${t.marked.has(i) ? 'mk' : ''}"><td>Question ${i + 1}</td>
          <td>${statusOf(i) === 'Answered' ? 'Answered' : `<span class="pill ${statusOf(i) === 'Incomplete' ? 'warn' : 'bad'}">${statusOf(i)}</span>`}</td>
          <td>${t.marked.has(i) ? '★' : ''}</td><td><button class="ghost small" data-go="${i}">Go to question</button></td></tr>`).join('')}</tbody></table>
        <div class="meta" style="margin-top:12px">${n - done ? `${n - done} not fully answered - there is no penalty for guessing, so answer everything.` : 'All questions answered.'}</div></div>`
      : `<div class="card test-q"><div class="row" style="margin-bottom:4px"><span class="meta">Question ${t.i + 1} of ${n}</span><span style="flex:1"></span>
          <button class="ghost small ${t.marked.has(t.i) ? 'on' : ''}" id="tt-mark">${t.marked.has(t.i) ? '★ Marked' : '☆ Mark for review'}</button></div>
        <div id="tt-q">${qBody(q, t.resp[t.i])}</div>
        <div class="row" style="margin-top:16px"><button class="ghost" id="tt-prev" ${t.i ? '' : 'disabled'}>← Previous</button><span style="flex:1"></span>
          <button id="tt-next">${t.i + 1 < n ? 'Next →' : 'Review & submit'}</button></div></div>`}
    <div class="row" style="margin-top:8px"><button class="ghost small" id="tt-quit">Quit test</button>
      <span class="meta">No hints during a test. Mark questions you want to revisit; skip anything taking over 2 minutes and come back.</span></div>`;
  tickTest();
  const goTo = (i) => { t.secs[t.i] += (Date.now() - t.qStart) / 1000; t.qStart = Date.now(); t.i = i; t.review = false; drawTest(); };
  if (!t.review) {
    bindQ($('#tt-q'), q, () => t.resp[t.i], (v) => { t.resp[t.i] = v; }, drawTest);
    $('#tt-mark').onclick = () => { t.marked.has(t.i) ? t.marked.delete(t.i) : t.marked.add(t.i); drawTest(); };
    $('#tt-prev').onclick = () => goTo(t.i - 1);
    $('#tt-next').onclick = () => { if (t.i + 1 < n) goTo(t.i + 1); else { t.secs[t.i] += (Date.now() - t.qStart) / 1000; t.qStart = Date.now(); t.review = true; drawTest(); } };
    const ne = $('#ne-in'); if (ne) ne.onkeydown = (e) => { if (e.key === 'Enter') $('#tt-next').click(); };
  } else body().querySelectorAll('[data-go]').forEach((b) => b.onclick = () => { t.qStart = Date.now(); t.i = +b.dataset.go; t.review = false; drawTest(); });
  $('#tt-review').onclick = () => { if (t.review) { t.qStart = Date.now(); t.review = false; drawTest(); } else { t.secs[t.i] += (Date.now() - t.qStart) / 1000; t.qStart = Date.now(); t.review = true; drawTest(); } };
  $('#tt-submit').onclick = () => {
    const left = n - t.questions.filter((qq, i) => answered(qq, t.resp[i])).length;
    if (!confirm(left ? `${left} question${left > 1 ? 's are' : ' is'} not fully answered. Submit anyway?` : 'Submit the test?')) return;
    submitTest();
  };
  $('#tt-quit').onclick = () => {
    if (!confirm('Quit this test? Nothing will be saved.')) return;
    clearInterval(course.timer); course.timer = null; calcClose();
    if (t.quiz) { const wasMock = course.quiz && course.quiz.mock; course.test = null; course.quiz = null; course.view = 'home'; if (wasMock && !gre.day) { gre.tab = 'progress'; return views.gre(); } return greClass(); }
    course.test = null; courseHome();
  };
}
async function submitTest() {
  const t = course.test; if (!t || t.submitting) return;
  t.submitting = true;
  clearInterval(course.timer); course.timer = null;
  if (!t.review) t.secs[t.i] += (Date.now() - t.qStart) / 1000;
  const seconds = Math.min(t.minutes * 60, Math.round((Date.now() - t.start) / 1000));
  const items = t.questions.map((q, i) => ({ chapter: q.chapter, concept: q.concept, diff: q.diff, ctitle: q.ctitle, cname: q.cname, kind: q.kind, gen: q.gen,
    q: q.q, c: q.c, a: q.a, v: q.v, x: q.x, passage: q.passage, ptitle: q.ptitle, resp: t.resp[i], correct: isRight(q, t.resp[i]),
    yours: answerText(q, t.resp[i]), right: rightText(q), secs: Math.round(t.secs[i]), topic: q.topic, word: q.word, section: t.subject }));
  if (t.quiz) return finishQuizSection(t, items, seconds);
  const res = await post('/api/gre/course/test', { kind: t.kind, key: t.key, title: t.title, minutes: t.minutes, seconds, items, day: t.fromDay, subject: t.subject });
  if (t.fromDay) await post('/api/gre/day/' + t.fromDay, { parts: { tutor: true } });
  course.result = { id: res.id, kind: t.kind, key: t.key, title: t.title, minutes: t.minutes, seconds, items, fresh: true, fromDay: t.fromDay, level: t.level, subject: t.subject };
  course.test = null; course.view = 'result'; course.onlyWrong = false; calcClose();
  const tab = t.subject === 'verbal' ? 'vcourse' : 'course';
  if (current === 'gre' && gre.tab === tab) { drawResult(); window.scrollTo(0, 0); } else toast(`Test saved - open the ${SUBJ[t.subject]} course tab to see your results.`);
}

async function finishQuizSection(t, items, seconds) {
  const Q = course.quiz;
  Q.items.push(...items); Q.seconds += seconds; Q.minutes += t.minutes;
  calcClose(); course.test = null;
  if (Q.mock) {  // each mock section is saved like a course section test (predictor, pacing, Error log)
    const s = Q.sections[Q.idx];
    await post('/api/gre/course/test', { kind: s.kind, key: s.key || s.level || 'mixed', title: `Full test · ${s.title}`, minutes: t.minutes, seconds, items, subject: s.subject, day: Q.day });
    Q.done.push({ subject: s.subject, kind: s.kind, items });
    if (s.kind === 'section1') Q.s1[s.subject] = Math.round(100 * items.filter((x) => x.correct).length / Math.max(1, items.length));
    if (Q.idx + 1 < Q.sections.length) { Q.idx++; course.view = 'quizbreak'; return showCourse(); }
    const res = await post('/api/gre/mock/finish', { sections: Q.done });
    if (Q.day) await post('/api/gre/day/' + Q.day, { parts: { mock: true } });
    course.result = { kind: 'mock', quiz: true, key: '', title: Q.title, minutes: Q.minutes, seconds: Q.seconds, items: Q.items, fresh: true, fromDay: Q.day, subject: 'mixed', mockScores: res.scores };
    course.quiz = null; course.view = 'result'; course.onlyWrong = false;
    return showCourse();
  }
  if (Q.weekly) {  // each section is saved as a test (Error log, missed-words queue, predictor)
    const s = Q.sections[Q.idx];
    await post('/api/gre/course/test', { kind: 'week', key: String(Q.week), title: s.title, minutes: t.minutes, seconds, items, subject: s.subject, day: Q.day });
    if (Q.idx + 1 < Q.sections.length) { Q.idx++; course.view = 'quizbreak'; return showCourse(); }
    await post('/api/gre/day/' + Q.day, { parts: { weekly: true } });
    course.result = { kind: 'week', quiz: true, key: '', title: Q.title, minutes: Q.minutes, seconds: Q.seconds, items: Q.items, fresh: true, fromDay: Q.day, subject: 'mixed' };
    course.quiz = null; course.view = 'result'; course.onlyWrong = false;
    return showCourse();
  }
  if (Q.idx + 1 < Q.sections.length) { Q.idx++; course.view = 'quizbreak'; return showCourse(); }
  const score = Q.items.filter((i) => i.correct).length;
  await post('/api/gre/quiz', { day: Q.day, score, total: Q.items.length, items: Q.items });
  await post('/api/gre/day/' + Q.day, { parts: { quiz: true } });
  course.result = { kind: 'quiz', quiz: true, key: '', title: Q.title, minutes: Q.minutes, seconds: Q.seconds, items: Q.items, fresh: true, fromDay: Q.day, subject: 'mixed' };
  course.quiz = null; course.view = 'result'; course.onlyWrong = false;
  showCourse();
}

// ---------------------------------------------------------------- results
function drawResult() {
  const R = course.result; const items = R.items; const subj = R.subject || 'quant';
  const score = items.filter((i) => i.correct).length; const pct = Math.round(100 * score / items.length);
  const byConcept = R.kind === 'chapter';
  const groups = {};
  items.forEach((it) => {
    const k = byConcept ? `${it.chapter}:${it.concept ?? 'x'}` : it.chapter;
    const g = groups[k] = groups[k] || { c: 0, n: 0, chapter: it.chapter, concept: it.concept, name: byConcept ? (it.cname || 'Mixed practice') : (it.ctitle || it.chapter) };
    g.n++; if (it.correct) g.c++;
  });
  const diff = [1, 2, 3].map((d) => { const xs = items.filter((i) => i.diff === d); return { d, n: xs.length, c: xs.filter((i) => i.correct).length }; }).filter((x) => x.n);
  const verdict = R.kind === 'mock' ? [pct >= 75 ? 'ok' : pct >= 55 ? 'warn' : 'bad', 'Full test done.', 'Now review every question below - wrong ones and lucky guesses. That review is worth as much as the test itself.']
    : pct >= 80 ? ['ok', 'Mastered.', R.kind === 'chapter' ? 'Move on to the next chapter - this one will come back in the unit test.' : 'Strong work - keep this level under time pressure.']
    : pct >= 60 ? ['warn', 'Getting there.', 'Read the explanation of every miss below, re-learn any concept under 70%, then retake (the questions will be new).']
      : ['bad', 'Re-learn first.', 'Go back through the lesson for the concepts marked below, do the "your turn" questions until they feel easy, then retake.'];
  const s1Next = R.kind === 'section1' ? (pct >= 60 ? 'hard' : pct < 40 ? 'easy' : 'mixed') : null;
  const avg = R.seconds && items.length ? R.seconds / items.length : null;
  const target = R.minutes * 60 / items.length;
  const slow = items.filter((it) => it.secs && it.secs > slowLimit(it.chapter));
  const slowRight = slow.filter((it) => it.correct).length;
  const list = items.map((it, i) => ({ it, i })).filter(({ it }) => !course.onlyWrong || !it.correct);
  let lastPassage = null;
  body().innerHTML = `<div class="row" style="margin-bottom:12px"><button class="ghost small" id="rs-back">← ${R.quiz ? (R.fromDay ? 'Day ' + R.fromDay + ' class' : 'GRE Prep') : SUBJ[subj] + ' course'}</button><h2 style="margin:0">${esc(R.title)}</h2></div>
    <div class="card hero"><div class="row" style="justify-content:space-between;align-items:flex-start">
      <div><div class="score ${verdict[0]}">${score} / ${items.length} · ${pct}%</div>
        <div style="margin-top:4px"><b>${verdict[1]}</b> ${verdict[2]}</div>
        <div class="meta" style="margin-top:6px">${R.seconds ? `Time used ${mmss(R.seconds)} of ${R.minutes}:00` : ''}${avg ? ` · ${Math.round(avg)} s per question (target ≤ ${Math.round(target)} s)` : ''}${R.fresh && score < items.length ? ' · wrong answers were added to your Error log' : ''}</div></div>
      <div class="row">${s1Next ? `<button id="rs-s2">Continue to section 2 (${s1Next === 'hard' ? 'harder' : s1Next === 'easy' ? 'easier' : 'medium'})</button>` : ''}
        ${['chapter', 'unit', 'drill', 'quiz'].includes(R.kind) ? '<button class="ghost" id="rs-again">Retake with new questions</button>' : ''}</div></div></div>
    ${R.mockScores ? `<div class="card" style="margin-top:12px;background:var(--grey-soft)"><b>Estimated scores</b> - Quant <b>${R.mockScores.quant.score ?? '-'}</b> (${R.mockScores.quant.right}/${R.mockScores.quant.total} right)
        · Verbal <b>${R.mockScores.verbal.score ?? '-'}</b> (${R.mockScores.verbal.right}/${R.mockScores.verbal.total} right)
        <div class="meta">A rough estimate from this app's questions; saved to your practice-test scores. Your essay is in the Essays tab - press "Get AI feedback" there for a score.</div></div>` : ''}
    ${R.quiz && R.fresh ? `<div class="meta" style="margin-top:8px">${items.some((i) => i.topic === 'vocab' && !i.correct) ? 'Words you missed joined the missed-words queue (warm-ups from tomorrow, 3 right answers clear them). ' : ''}Other mistakes are in your Error log.</div>` : ''}
    <div class="grid g3" style="margin:16px 0">
      <div class="card"><h2>${byConcept ? 'By concept' : 'By chapter'}</h2><table><tbody>${Object.values(groups).map((g) => {
        const p = Math.round(100 * g.c / g.n);
        const relearn = p < 70 && g.chapter && !['vocab', 'qc'].includes(g.chapter) ? `<button class="ghost small" data-relearn="${g.chapter}:${g.concept ?? ''}">Re-learn</button>` : '';
        return `<tr><td>${esc(g.name)}</td><td style="width:35%"><div class="bar"><i style="width:${p}%;background:${p >= 80 ? 'var(--ok)' : p >= 60 ? 'var(--warn)' : 'var(--bad)'}"></i></div></td>
          <td style="white-space:nowrap;text-align:right">${g.c}/${g.n}</td><td>${relearn}</td></tr>`;
      }).join('')}</tbody></table></div>
      <div class="card"><h2>By difficulty</h2><table><tbody>${diff.map((x) => `<tr><td>${DIFF[x.d]}</td><td style="width:45%"><div class="bar"><i style="width:${Math.round(100 * x.c / x.n)}%"></i></div></td>
        <td style="text-align:right">${x.c}/${x.n}</td></tr>`).join('')}</tbody></table>
        <div class="meta" style="margin-top:10px">${diff.find((x) => x.d === 1 && x.c < x.n) ? 'You missed easy questions - those are usually careless errors or a concept gap. Slow down on the first read.' : 'Easy questions all right - good foundation.'}</div></div>
      <div class="card"><h2>Pacing</h2>${items.some((it) => it.secs) ? `
        <div><b>${slow.length}</b> question${slow.length === 1 ? '' : 's'} took longer than the limit${slow.length ? ` - you got <b>${slowRight}</b> of them right` : ''}.</div>
        <div class="meta" style="margin-top:6px">Limits: ${subj === 'quant' ? '2 min per quant question' : '90 s for TC/SE, 2½ min for reading questions'}.
          ${slow.length && slowRight / slow.length < 0.5 ? 'Slow questions are mostly wrong anyway: next time, guess, mark and move on after the limit.' : avg && avg > target * 1.15 ? 'Overall you were slower than GRE pace; practise estimating and skipping.' : 'Pace looks fine.'}</div>`
        : '<div class="meta">No timing recorded for this test.</div>'}</div></div>
    <div class="card"><div class="row"><h2 style="margin:0">Review every question</h2><span style="flex:1"></span>
      <label><input type="checkbox" id="rs-wrong" ${course.onlyWrong ? 'checked' : ''}> Only mistakes</label></div>
      ${list.map(({ it, i }) => {
        const showP = it.passage && it.passage !== lastPassage; lastPassage = it.passage || lastPassage;
        const qq = showP ? it : { ...it, passage: null };
        const isSlow = it.secs && it.secs > slowLimit(it.chapter);
        return `<div class="rv-item"><div class="row"><b>${it.correct ? '<span style="color:var(--ok)">✓</span>' : '<span style="color:var(--bad)">✗</span>'} Question ${i + 1}</b>
          <span class="meta">${esc(it.ctitle || '')}${it.cname ? ' · ' + esc(it.cname) : ''} · ${DIFF[it.diff] || ''}${it.secs ? ` · ${it.secs} s` : ''}</span>${isSlow ? '<span class="pill slow">slow</span>' : ''}</div>
        ${qBody(qq, it.resp, { locked: true, reveal: true })}
        ${!it.correct && !answered(it, it.resp) ? '<div class="meta">You left this blank or incomplete.</div>' : ''}
        <div class="explain ${it.correct ? 'ok' : 'bad'}">${esc(it.x)}</div><div class="row" style="margin-top:4px"><span style="flex:1"></span>${flagBtn(flagInfo(it))}</div></div>`;
      }).join('') || '<div class="empty">No mistakes - nice.</div>'}</div>`;
  $('#rs-back').onclick = R.quiz ? () => { course.result = null; course.view = 'home'; greClass(); window.scrollTo(0, 0); } : courseHome;
  $('#rs-wrong').onchange = (e) => { course.onlyWrong = e.target.checked; drawResult(); };
  body().querySelectorAll('[data-relearn]').forEach((b) => b.onclick = () => { const [ch, c] = b.dataset.relearn.split(':'); openLesson(ch, c === '' ? null : +c); });
  const s2 = $('#rs-s2'); if (s2) s2.onclick = () => startTest('section2', '', s1Next, R.fromDay, subj);
  const ag = $('#rs-again'); if (ag) ag.onclick = () => R.kind === 'week' ? startWeekTest(gre.d && gre.d.weekly ? gre.d.weekly.week : 1, R.fromDay) : R.quiz ? startQuiz(R.fromDay) : startTest(R.kind, R.kind === 'drill' ? '' : R.key, 'mixed', R.fromDay, subj);
  // the review list has inputs from qBody; make sure none of them grab focus
  body().querySelectorAll('#ne-in').forEach((x) => x.removeAttribute('id'));
}

// ---------------------------------------------------------------- Today's class integration
function courseDayBox(d) {
  return `<div class="meta" style="margin-bottom:8px">Learn the chapter with the tutor first, then take its test. Tests are timed and marked, and mistakes go to your Error log.</div>
    <ul class="list">${d.course.map((c) => c.type === 'chapter'
      ? `<li><div class="grow"><b>${esc(c.title)}</b> <span class="pill">${SUBJ[c.subject]}</span><div class="meta">Lesson ${c.learnt}/${c.concepts} concepts${c.best !== null && c.best !== undefined ? ` · best test ${c.best}%` : ''}</div></div>
         <button class="ghost small" data-cl="${c.key}">${c.learnt ? (c.learnt >= c.concepts ? 'Revise lesson' : 'Continue lesson') : 'Start lesson'}</button><button class="small" data-ct="chapter:${c.key}:${c.subject}">Chapter test</button></li>`
      : c.type === 'unit'
        ? `<li><div class="grow"><b>${esc(c.title)}</b><div class="meta">${c.retest ? 'Revision retest' : 'Combined test of the unit'} · 20 Q${c.best !== null && c.best !== undefined ? ` · best ${c.best}%` : ''}</div></div>
           <button class="small" data-ct="unit:${c.key}:${c.subject}">Unit test</button></li>`
        : `<li><div class="grow"><b>${esc(c.title)}</b></div><button class="small" data-ct="section1::${c.subject}">Start section 1</button></li>`).join('')}</ul>`;
}
function bindCourseDay(d) {
  body().querySelectorAll('[data-cl]').forEach((b) => b.onclick = () => openLesson(b.dataset.cl));
  body().querySelectorAll('[data-ct]').forEach((b) => b.onclick = () => { const [k, key, subj] = b.dataset.ct.split(':'); startTest(k, key, 'mixed', d.day, subj || 'quant'); });
}

// ---------------------------------------------------------------- GRE-style on-screen calculator
// Like the test-day calculator: + − × ÷ with order of operations, parentheses, √, ±, memory (MR / MC / M+)
// and "Transfer display" into a numeric-entry box. Up to 8 digits.
const calc = { tokens: [], cur: '0', fresh: true, entry: false, mem: 0, err: false };
function calcFmt(v) {
  if (!Number.isFinite(v) || Math.abs(v) >= 1e8) { calc.err = true; return 'Error'; }
  if (Math.abs(v) < 1e-8) return '0';
  let s = String(parseFloat(v.toPrecision(8)));
  if (s.includes('e')) s = v.toFixed(8).replace(/\.?0+$/, '');
  return s;
}
function calcEval(tokens) {
  let i = 0;
  const peek = () => tokens[i];
  const factor = () => {
    const t = tokens[i++];
    if (t === '(') { const v = expr(); if (peek() === ')') i++; return v; }
    if (t === '−u') return -factor();
    return typeof t === 'number' ? t : NaN;
  };
  const term = () => { let v = factor(); while (peek() === '×' || peek() === '÷') { const op = tokens[i++]; const w = factor(); v = op === '×' ? v * w : (w === 0 ? NaN : v / w); } return v; };
  const expr = () => { let v = term(); while (peek() === '+' || peek() === '−') { const op = tokens[i++]; const w = term(); v = op === '+' ? v + w : v - w; } return v; };
  return expr();
}
function calcPress(k) {
  const c = calc;
  if (c.err && k !== 'C') return;
  const last = c.tokens[c.tokens.length - 1];
  const isOp = (x) => ['+', '−', '×', '÷'].includes(x);
  if (/^[0-9]$/.test(k)) {
    if (c.fresh) { c.cur = k; c.fresh = false; } else if (c.cur.replace(/[-.]/g, '').length < 8) c.cur = c.cur === '0' ? k : (c.cur === '-0' ? '-' + k : c.cur + k);
    c.entry = true;
  } else if (k === '.') {
    if (c.fresh) { c.cur = '0.'; c.fresh = false; } else if (!c.cur.includes('.')) c.cur += '.';
    c.entry = true;
  } else if (k === '±') {
    c.cur = c.cur.startsWith('-') ? c.cur.slice(1) : '-' + c.cur; c.entry = true;
  } else if (isOp(k)) {
    if (c.entry) c.tokens.push(Number(c.cur));
    else if (isOp(last)) c.tokens.pop();
    else if (!c.tokens.length || last === '(') c.tokens.push(Number(c.cur));
    c.tokens.push(k); c.fresh = true; c.entry = false;
  } else if (k === '(') {
    if (c.entry && c.tokens.length && !isOp(last) && last !== '(') return;
    c.tokens.push('('); c.cur = '0'; c.fresh = true; c.entry = false;
  } else if (k === ')') {
    const open = c.tokens.filter((x) => x === '(').length - c.tokens.filter((x) => x === ')').length;
    if (!open) return;
    if (c.entry || isOp(last) || last === '(') c.tokens.push(Number(c.cur));
    c.tokens.push(')');
    let depth = 0, j = c.tokens.length - 1;
    for (; j >= 0; j--) { if (c.tokens[j] === ')') depth++; else if (c.tokens[j] === '(' && --depth === 0) break; }
    c.cur = calcFmt(calcEval(c.tokens.slice(j))); c.fresh = true; c.entry = false;
  } else if (k === '=') {
    if (c.entry || isOp(last) || last === '(' || !c.tokens.length) c.tokens.push(Number(c.cur));
    let open = c.tokens.filter((x) => x === '(').length - c.tokens.filter((x) => x === ')').length;
    while (open-- > 0) c.tokens.push(')');
    c.cur = calcFmt(calcEval(c.tokens)); c.tokens = []; c.fresh = true; c.entry = true;
  } else if (k === '√') {
    const v = Number(c.cur);
    c.cur = v < 0 ? (c.err = true, 'Error') : calcFmt(Math.sqrt(v)); c.fresh = true; c.entry = true;
  } else if (k === 'CE') { c.cur = '0'; c.fresh = true; c.entry = false; }
  else if (k === 'C') Object.assign(c, { tokens: [], cur: '0', fresh: true, entry: false, err: false });
  else if (k === 'MR') { c.cur = calcFmt(c.mem); c.fresh = true; c.entry = true; }
  else if (k === 'MC') c.mem = 0;
  else if (k === 'M+') { c.mem += Number(c.cur) || 0; c.fresh = true; }
  else if (k === 'T') {
    const ne = document.getElementById('ne-in');
    if (!ne || ne.disabled) return toast('Transfer works on numeric-entry questions.');
    ne.value = c.err ? '' : c.cur; ne.dispatchEvent(new Event('input'));
  }
  calcDraw();
}
function calcDraw() {
  const el = document.getElementById('calc'); if (!el) return;
  const show = (t) => typeof t === 'number' ? calcFmt(t) : t;
  el.querySelector('.expr').textContent = calc.tokens.map(show).join(' ');
  el.querySelector('.val').textContent = calc.cur;
  el.querySelector('.m').textContent = calc.mem ? 'M' : '';
}
function calcClose() { const el = document.getElementById('calc'); if (el) el.remove(); }
function calcToggle() {
  if (document.getElementById('calc')) return calcClose();
  const keys = [['MR', 'MC', 'M+', 'C'], ['(', ')', '√', 'CE'], ['7', '8', '9', '÷'], ['4', '5', '6', '×'], ['1', '2', '3', '−'], ['0', '.', '±', '+'], ['=']];
  const el = document.createElement('div'); el.id = 'calc';
  el.innerHTML = `<div class="ch">Calculator<button title="Close">×</button></div>
    <div class="disp"><span class="m"></span><div class="expr"></div><div class="val">0</div></div>
    <div class="keys">${keys.flat().map((k) => `<button class="${['+', '−', '×', '÷', '='].includes(k) ? 'op' : ''} ${k === '=' ? 'wide' : ''}" data-k="${k}">${k}</button>`).join('')}
      <button class="wide" data-k="T">Transfer display</button></div>`;
  document.body.appendChild(el);
  el.querySelector('.ch button').onclick = calcClose;
  el.querySelectorAll('[data-k]').forEach((b) => b.onclick = () => calcPress(b.dataset.k));
  // drag by the title bar
  const head = el.querySelector('.ch');
  head.onmousedown = (e) => {
    if (e.target.tagName === 'BUTTON') return;
    const r = el.getBoundingClientRect(); const dx = e.clientX - r.left; const dy = e.clientY - r.top;
    const move = (ev) => { el.style.left = Math.max(0, ev.clientX - dx) + 'px'; el.style.top = Math.max(0, ev.clientY - dy) + 'px'; el.style.right = 'auto'; };
    const up = () => { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); };
    document.addEventListener('mousemove', move); document.addEventListener('mouseup', up);
  };
  calcDraw();
}
document.addEventListener('keydown', (e) => {
  if (!document.getElementById('calc') || ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
  const map = { '*': '×', '/': '÷', '-': '−', '+': '+', Enter: '=', '=': '=', Escape: 'C', Backspace: 'CE', '(': '(', ')': ')', '.': '.' };
  const k = /^[0-9]$/.test(e.key) ? e.key : map[e.key];
  if (k) { e.preventDefault(); calcPress(k); }
});
