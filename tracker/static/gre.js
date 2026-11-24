'use strict';
// GRE Prep: daily class (notes, videos, reading, practice, vocab, quiz, essay, tutor), quant + verbal courses, plan,
// vocab trainer, progress (score predictor, pacing, mistake trends), error log with redo, essays with AI feedback,
// library and settings (schedule, re-plan, targets, phone flashcards, backups).
// Uses helpers from app.js ($, esc, api, post, patch, del, toast, fmtDate) and gre_course.js (course, qBody, bindQ, …).

const GRE_TABS = [['class', "Today's class"], ['course', 'Quant course'], ['vcourse', 'Verbal course'], ['plan', 'Plan'], ['vocab', 'Vocab trainer'], ['cards', 'Formula cards'],
  ['progress', 'Progress'], ['results', 'Test results'], ['errors', 'Error log'], ['essays', 'Essays'], ['library', 'Library'], ['gsettings', 'Settings']];
const gre = { tab: 'class', day: null, quiz: null, tutor: [], essayTimer: null };
const SECTION_PILL = { Quant: 'acc', Verbal: 'ok', Writing: 'warn', Review: '', Mock: 'bad', Orientation: '' };
const secPill = (s) => `<span class="pill ${SECTION_PILL[s] ?? ''}">${esc(s)}</span>`;
const ext = (url, label) => `<a class="ext" href="${esc(url)}" target="_blank" rel="noopener">${label}</a>`;

// ---------------------------------------------------------------- Today-screen card (used by app.js)
function greTodayCard(g) {
  if (!g) return '';
  if (g.finished) return `<div class="card"><h2>GRE prep</h2><div>All ${g.total} classes done. Good luck on test day!</div></div>`;
  const when = g.study_today ? `today at ${esc(g.time)}` : (g.started ? 'no class scheduled today' : `plan starts ${fmtDate(g.start, { weekday: 'short', day: 'numeric', month: 'short' })}`);
  return `<div class="card gre-card"><div class="row" style="justify-content:space-between"><h2 style="margin:0">GRE class</h2>
      <span class="meta">${when}</span></div>
    <div style="margin:8px 0 6px"><b>Day ${g.day}</b> of ${g.total} · ${secPill(g.section)} ${esc(g.title)}</div>
    <div class="row">${g.behind ? `<span class="pill bad">${g.behind} day${g.behind > 1 ? 's' : ''} behind</span>` : '<span class="pill ok">On track</span>'}
      ${g.vocab_due ? `<span class="pill warn">${g.vocab_due} vocab cards due</span>` : ''}${g.errors_due ? `<span class="pill warn">${g.errors_due} mistakes to redo</span>` : ''}<span class="meta">~${g.minutes} min</span>
      <span style="flex:1"></span><button class="small" onclick="greOpen(${g.day})">Open class</button></div></div>`;
}
function greOpen(n, tab = 'class') { gre.day = n; gre.tab = tab; go('gre'); }

// move the plan so the next unfinished class lands on today
async function greReplan() {
  const st = gre.ov ? gre.ov.status : null;
  const msg = st && st.current ? `Move Day ${st.current} to today (or your next study day) and shift every later class to match?\n\nCompleted classes stay completed. The plan currently ends ${fmtDate(st.end)}.`
    : 'Re-plan from today?';
  if (!confirm(msg)) return;
  const r = await post('/api/gre/replan', {});
  if (!r.ok) return toast(r.error || 'Could not re-plan');
  toast(`Day ${r.day} is now on ${fmtDate(r.day_date, { weekday: 'short', day: 'numeric', month: 'short' })}. New end date: ${fmtDate(r.end)}.`);
  gre.day = r.day; views.gre();
}

// ---------------------------------------------------------------- shell
views.gre = async () => {
  const o = await api('/api/gre/overview');
  gre.ov = o;
  if (!gre.day) gre.day = o.status.current || o.status.total;
  const st = o.status;
  $('#view').innerHTML = `<div class="row" style="justify-content:space-between;align-items:flex-start">
      <div><h1>GRE Prep</h1><div class="sub">${st.total}-day plan · ${fmtDate(st.start)} → ${fmtDate(st.end)} · material from your shared GRE Drive folder</div></div>
      <div class="row">${st.behind ? `<span class="pill bad">${st.behind} behind plan</span><button class="ghost small" onclick="greReplan()" title="Shift the remaining classes so the next one is today">Re-plan from today</button>` : '<span class="pill ok">On track</span>'}
        <span class="pill acc">${st.done}/${st.total} classes</span><span class="pill">${o.vocab.unlocked}/${o.vocab.total_groups} vocab groups</span>
        ${o.errors_due ? `<span class="pill warn">${o.errors_due} mistakes to redo</span>` : o.errors_open ? `<span class="pill">${o.errors_open} open errors</span>` : ''}</div></div>
    <div class="bar" style="margin:-8px 0 14px"><i style="width:${Math.round(100 * st.done / st.total)}%"></i></div>
    <div class="tabs">${GRE_TABS.map(([k, l]) => `<button class="tab ${gre.tab === k ? 'on' : ''}" data-tab="${k}">${l}${k === 'vocab' && o.vocab.due ? ` <span class="count">${o.vocab.due}</span>` : ''}${k === 'errors' && o.errors_due ? ` <span class="count">${o.errors_due}</span>` : ''}</button>`).join('')}</div>
    <div id="gre-body"></div>`;
  $('#view').querySelectorAll('[data-tab]').forEach((b) => b.onclick = () => {
    const t = b.dataset.tab;
    if ((t === 'course' || t === 'vcourse') && !course.test) {
      const subj = t === 'vcourse' ? 'verbal' : 'quant';
      if (gre.tab === t || course.subject !== subj) { course.view = 'home'; course.lesson = null; course.result = null; }  // clicking the tab again returns to the course map
    }
    gre.tab = t; if (t === 'class' && !gre.day) gre.day = st.current; views.gre();
  });
  const courseTab = (subj) => () => { if (!course.test) course.subject = subj; greCourse(); };
  ({ class: greClass, course: courseTab('quant'), vcourse: courseTab('verbal'), plan: grePlan, vocab: greVocab, cards: greCards, progress: greProgress,
    results: greResults, errors: greErrors, essays: greEssays, library: greLibrary, gsettings: greSettings })[gre.tab]();
};
const body = () => $('#gre-body');

// ---------------------------------------------------------------- class
const PARTS = [['notes', 'Study notes'], ['watch', 'Watch'], ['tutor', 'Tutor'], ['practice', 'Solve sums'], ['vocab', 'Vocab'], ['quiz', 'Quiz'], ['homework', 'Homework'], ['eod', 'Missed-words review'], ['read', 'Go deeper']];
async function greClass() {
  if (quizMode()) return drawQuizView();
  const n = gre.day;
  const d = await api('/api/gre/day/' + n);
  gre.d = d;
  const parts = d.progress.parts || {};
  const st = gre.ov.status;
  const isCurrent = n === st.current;
  const shown = PARTS.filter(([k]) => !((k === 'watch' && !d.videos.length) || (k === 'read' && !d.read.length) || (k === 'practice' && !d.practice.length && !d.books.length)
    || (k === 'quiz' && !d.has_quiz) || (k === 'tutor' && !(d.course || []).length) || (k === 'homework' && !d.homework) || (k === 'eod' && !d.vocab_words.length && !d.review_groups.length) || (k === 'vocab' && !d.vocab_words.length && !d.review_groups.length) || (k === 'notes' && !d.notes.length && !(d.study && (d.study.notes.length || d.study.sheet)))));
  if (d.essay) shown.push(['essay', 'Essay']);
  if (d.mock) shown.push(['mock', 'Mock test']);
  const chip = ([k, l]) => `<button class="chip ${parts[k] ? 'on' : ''}" data-part="${k}" title="Tick when done">${parts[k] ? '✓ ' : ''}${l}</button>`;
  const tick = (k) => `<button class="check ${parts[k] ? 'on' : ''}" data-part="${k}" title="Mark this step done">${parts[k] ? '✓' : ''}</button>`;
  const step = (k, num, title, inner, extra = '') => `<div class="card step" id="step-${k}"><div class="row step-h">${tick(k)}<h2><span class="num">${num}</span>${title}</h2><span style="flex:1"></span>${extra}</div>${inner}</div>`;
  let i = 0;
  const S = [];
  const study = d.study || {};
  const revisionDay = d.section === 'Review' || /^(Revision|Weak-area|Review)/.test(d.title);
  if (d.notes.length || (study.notes || []).length || study.sheet) S.push(step('notes', ++i, study.sheet && !(study.notes || []).length ? 'Revision sheet — read this first' : 'Study notes — read this first',
    studyHtml(d), ext('/gre/notes/day/' + n, 'Print / save as PDF')));
  if (revisionDay) S.push('<div id="smart-box"></div>');
  if (d.videos.length) S.push(step('watch', ++i, 'Watch (optional, if you like videos)', d.videos.map((v) => `<div class="meta" style="margin:4px 0">Magoosh · ${esc(v.folder.replace('Adbanced', 'Advanced').replace('Inqualities', 'Inequalities'))} · ${ext(v.folder_url, 'folder')}</div>
      <ol class="vids">${v.videos.map((x) => `<li>${ext(x.url, esc(x.title))}</li>`).join('')}</ol>`).join(''), `<span class="meta">${d.videos.reduce((a, v) => a + v.videos.length, 0)} videos</span>`));
  if ((d.course || []).length) S.push(step('tutor', ++i, 'Tutor session — worked examples, then you try', courseDayBox(d)));
  if (d.practice.length || d.books.length) S.push(step('practice', ++i, 'Solve sums', `
      <div class="meta" style="margin-bottom:8px">Do every question first (timed, no peeking), then watch the video solution for anything you missed or guessed.
        Got one wrong (or guessed)? Tap its <b>✗</b> - it is saved to your Error log to redo in a week.</div>
      ${d.practice.map((p) => `<div class="pset"><div class="row"><b>${esc(p.name)}</b><span class="meta">${p.items.length} questions · Magoosh</span><span style="flex:1"></span>${ext(p.folder, 'folder')}</div>
        <div class="qgrid">${p.items.map((it) => { const st = (d.practice_marks || {})[`${p.code}:${it.n}`];
          return `<span class="q ${st === 'Open' ? 'wrong' : st === 'Fixed' ? 'fixed' : ''}">${it.q.map((u, j) => ext(u, j ? `p${j + 1}` : `Q${it.n}`)).join(' ')}${it.s ? ` · ${ext(it.s, '▶')}` : ''}
            <button class="qx" data-mk="${p.code}:${it.n}" title="${st === 'Open' ? 'Marked wrong - in your Error log. Click to undo.' : st === 'Fixed' ? 'You got this wrong before and fixed it. Click to mark it wrong again.' : 'I got this wrong - save it to redo'}">${st === 'Fixed' ? '✓' : '✗'}</button></span>`; }).join('')}</div></div>`).join('')}
      ${d.books.length ? `<div style="margin-top:8px"><b>Book exercises</b><ul class="list">${d.books.map((r) => `<li><div class="grow">${ext(r.url, esc(prettyName(r.name)))}<div class="meta">${esc(r.note)}</div></div></li>`).join('')}</ul></div>` : ''}
      <details style="margin-top:6px"><summary>+ Log a mistake from a book or anywhere else</summary>${errorForm(d)}</details>`));
  const warmup = d.vocab_warmup ? `<div class="explain warn" style="margin-bottom:8px"><b>First: warm-up on ${d.vocab_warmup} missed word${d.vocab_warmup > 1 ? 's' : ''}</b> from earlier days
      <button class="small" onclick="greOpen(${n}, 'vocab')">Start warm-up</button></div>` : '';
  if (d.vocab_words.length) S.push(step('vocab', ++i, `Vocab — GregMat group ${d.vocab_group} (30 words)`, `${warmup}
      <div class="meta" style="margin-bottom:6px">Say each word, guess its meaning, then hover or tap to reveal. Use it in a sentence of your own.</div>
      <div class="words">${d.vocab_words.map((w) => `<div class="word"><b>${esc(w.word)}</b> ${sayBtn(w.word)}<span class="def">${esc(w.def)}</span></div>`).join('')}</div>`,
    `<button class="ghost small" id="reveal">Reveal all</button><button class="ghost small" onclick="greOpen(${n}, 'vocab')">Flashcards</button>`));
  else if (d.review_groups.length) S.push(step('vocab', ++i, 'Vocab review', `${warmup}<div>Review day — no new words. Clear your due flashcards (groups ${d.review_groups[0]}–${d.review_groups[d.review_groups.length - 1]}).</div>`,
    `<button class="small" onclick="greOpen(${n}, 'vocab')">Open flashcards</button>`));
  if (d.has_quiz) S.push(step('quiz', ++i, 'Quiz', `<div id="quiz-box">${quizIntro(d)}</div>`));
  if (d.essay) S.push(step('essay', ++i, 'Essay — Analyze an Issue (30 minutes)', essayBox(d)));
  if (d.mock) S.push(step('mock', ++i, 'Full-length practice test', `<div>${ext(d.mock.url, esc(d.mock.name))}</div>
      <div class="meta" style="margin:6px 0">When you finish, add a screenshot of the score report - the app reads the scores and per-question results.
        <button class="small" onclick="greAddResult({ day: ${n}, name: ${esc(JSON.stringify(d.mock.name.split(' - ')[0]))}, source: ${esc(JSON.stringify(/POWERPREP|ETS|Official/i.test(d.mock.name) ? 'ETS' : ''))}, kind: 'Full practice test' })">Add result screenshot</button>
        Or just type the scores:</div>
      <div class="row" style="margin:4px 0 8px"><span class="meta">No test today or want extra practice?</span>
        <button class="ghost small" onclick="startMock(${n})">Take a full practice test inside the app (about 2 h)</button></div>
      <div class="row"><input id="m-q" type="number" placeholder="Quant" style="width:80px"><input id="m-v" type="number" placeholder="Verbal" style="width:80px">
      <input id="m-a" type="number" step="0.5" placeholder="AWA" style="width:70px"><button class="small" id="m-save">Save scores</button></div>`));
  if (d.homework) S.push(step('homework', ++i, 'Homework', `<div>${esc(d.homework)}</div>`));
  if (d.vocab_words.length || d.review_groups.length) {
    const e = d.vocab_eod || {};
    S.push(step('eod', ++i, "End-of-day review — today's missed words", `<div id="eod-box">${e.pending
      ? `<div>You missed <b>${e.pending} word${e.pending > 1 ? 's' : ''}</b> today (flashcards, quiz or warm-up). One last quick quiz on them before you finish the day.</div>
         <div class="row" style="margin-top:8px"><button class="small" id="eod-start">Start review (${e.pending})</button></div>`
      : e.reviewed ? `<div class="explain ok">Done - you reviewed ${e.reviewed} missed word${e.reviewed > 1 ? 's' : ''} today. They come back in tomorrow's warm-up.</div>`
        : '<div class="meta">Nothing missed yet today. After the vocab flashcards and the quiz, any word you got wrong appears here for one last review.</div>'}</div>`));
  }
  const habit = d.read.filter((r) => /^Daily reading habit/.test(r.note)); const deeper = d.read.filter((r) => !/^Daily reading habit/.test(r.note));
  if (d.read.length) S.push(step('read', ++i, 'Go deeper (optional)', `${habit.map((r) => `<div class="row" style="margin-bottom:8px"><span class="pill">Reading habit · 15 min</span>
        ${ext(r.url, esc(prettyName(r.name)))}<span class="meta">read ONE piece and write its main point in one sentence</span></div>`).join('')}
      ${deeper.length ? `<details><summary>Books and notes for extra practice (${deeper.length}) - only if you want more after the study notes</summary><ul class="list">${deeper.map((r) => `<li><div class="grow">${ext(r.url, esc(prettyName(r.name)))}<div class="meta">${esc(r.note)}</div></div></li>`).join('')}</ul></details>` : ''}`));
  S.push(`<div class="card step"><div class="row step-h"><h2><span class="num">?</span>Ask the tutor</h2><span style="flex:1"></span><span class="meta" id="t-status"></span></div>${tutorBox()}</div>`);

  body().innerHTML = `
    <div class="row" style="justify-content:space-between;margin-bottom:12px">
      <button class="ghost small" ${n <= 1 ? 'disabled' : ''} data-go="${n - 1}">&larr; Day ${n - 1}</button>
      <div class="row">${isCurrent ? '' : `<button class="ghost small" data-go="${st.current || st.total}">Jump to current class (Day ${st.current || st.total})</button>`}</div>
      <button class="ghost small" ${n >= st.total ? 'disabled' : ''} data-go="${n + 1}">Day ${n + 1} &rarr;</button></div>
    <div class="card hero">
      <div class="row" style="justify-content:space-between"><div class="meta">Day ${n} of ${st.total} · Week ${d.week} · planned for ${fmtDate(d.date, { weekday: 'long', day: 'numeric', month: 'short', year: 'numeric' })}</div>
        <div>${d.progress.done ? `<span class="pill ok">Completed ${fmtDate(d.progress.done_on)}</span>` : (d.date < isoToday() ? '<span class="pill bad">Overdue</span> <button class="ghost small" onclick="greReplan()">Re-plan from today</button>' : d.date === isoToday() ? '<span class="pill warn">Today</span>' : '')}</div></div>
      <h1 style="margin:6px 0">${secPill(d.section)} ${esc(d.title)}</h1>
      <div class="row">${shown.map(chip).join('')}<span style="flex:1"></span><span class="meta">≈ ${d.minutes} min</span></div></div>
    <div class="steps">${S.join('')}</div>
    <div class="card" style="margin-top:16px"><h2>Finish the class</h2>
      <div class="row"><label>Minutes studied <input id="f-min" type="number" value="${esc(d.progress.minutes ?? d.minutes)}" style="width:80px"></label>
      <input id="f-notes" placeholder="Notes for yourself (what was hard, what to revisit)" value="${esc(d.progress.notes || '')}" style="flex:1;min-width:240px">
      ${d.progress.done ? '<button class="ghost" id="f-undo">Mark not done</button>' : `<button id="f-done">Mark Day ${n} complete</button>`}</div>
      <div class="row" style="margin-top:8px"><span class="meta">Took a quiz or test today (e.g. the ETS mini quiz)?</span>
        <button class="ghost small" onclick="greAddResult({ day: ${n}, name: ${esc(JSON.stringify(n === 1 ? 'ETS mini quiz' : ''))}, source: ${esc(JSON.stringify(n === 1 ? 'ETS' : ''))}, kind: ${esc(JSON.stringify(n === 1 ? 'Quiz / question set' : ''))} })">Add a test result (screenshot)</button></div></div>`;

  body().querySelectorAll('[data-go]').forEach((b) => b.onclick = () => { gre.day = +b.dataset.go; gre.quiz = null; greClass(); window.scrollTo(0, 0); });
  body().querySelectorAll('[data-part]').forEach((b) => b.onclick = async () => {
    await post('/api/gre/day/' + n, { parts: { [b.dataset.part]: !parts[b.dataset.part] } }); greClass();
  });
  body().querySelectorAll('[data-mk]').forEach((b) => b.onclick = async () => {
    const [code, qn] = b.dataset.mk.split(':'); const chip = b.closest('.q');
    const wrong = !chip.classList.contains('wrong');
    const r = await post('/api/gre/practice/mark', { day: n, code, n: +qn, wrong });
    if (!r.ok) return toast(r.error || 'Could not save');
    d.practice_marks = { ...(d.practice_marks || {}), [b.dataset.mk]: r.status };
    chip.classList.toggle('wrong', wrong); chip.classList.remove('fixed'); b.textContent = '✗';
    b.title = wrong ? 'Marked wrong - in your Error log. Click to undo.' : 'I got this wrong - save it to redo';
    toast(wrong ? `Q${qn} saved to your Error log - redo it in a week` : `Q${qn} removed from your Error log`);
  });
  const rv = $('#reveal'); if (rv) rv.onclick = () => body().querySelectorAll('.words').forEach((w) => w.classList.toggle('show'));
  const qs = $('#q-start'); if (qs) qs.onclick = () => startQuiz(n);
  bindErrorForm(d);
  bindEssay(d);
  bindTutor(n);
  bindCourseDay(d);
  bindStudy(body());
  renderSession(d, n);
  const sm = $('#smart-box'); if (sm) smartCardHtml(n).then((h) => { sm.innerHTML = h; bindSmart(sm, n); });
  const es = $('#eod-start'); if (es) es.onclick = async () => {
    const e = await api('/api/gre/vocab/eod');
    runWordDrill($('#eod-box'), e.questions, '/api/gre/vocab/eod', {
      label: "Today's missed words",
      onDone: async (res) => { await post('/api/gre/day/' + n, { parts: { eod: true } }); toast(`Review done: ${res.filter((r) => r.ok).length}/${res.length} right`); greClass(); },
    });
  };
  const ms = $('#m-save'); if (ms) ms.onclick = async () => {
    await post('/api/gre/scores', { name: `Day ${n}: ${d.mock.name}`.slice(0, 120), quant: +$('#m-q').value || null, verbal: +$('#m-v').value || null, awa: +$('#m-a').value || null });
    await post('/api/gre/day/' + n, { parts: { mock: true } }); toast('Scores saved'); greClass();
  };
  const fd = $('#f-done'); if (fd) fd.onclick = async () => {
    const pend = (await api('/api/gre/vocab/eod')).pending;
    if (pend && confirm(`You have ${pend} missed word${pend > 1 ? 's' : ''} from today to review. Do the end-of-day review first?`)) {
      return $('#step-eod').scrollIntoView({ behavior: 'smooth' });
    }
    await post('/api/gre/day/' + n, { done: true, minutes: +$('#f-min').value || null, notes: $('#f-notes').value });
    toast(`Day ${n} complete — nice work!`); gre.day = Math.min(st.total, n + 1); gre.quiz = null; views.gre(); window.scrollTo(0, 0);
  };
  const fu = $('#f-undo'); if (fu) fu.onclick = async () => { await post('/api/gre/day/' + n, { done: false }); views.gre(); };
}
function prettyName(n) {
  return n.replace(/\[Manhattan_Prep\]_GRE_/, 'Manhattan GRE – ').replace(/\(superingenious\.com\)/, '').replace(/\.(pdf|docx|epub|PDF)$/, '')
    .replace(/_/g, ' ').replace(/\s+/g, ' ').trim();
}

// ---------------------------------------------------------------- quiz (GRE format - run by gre_course.js startQuiz)
function quizIntro(d) {
  const best = d.quizzes.length ? Math.max(...d.quizzes.map((q) => Math.round(100 * q.score / q.total))) : null;
  const qt = d.topics.filter((t) => !VERBAL_CH.includes(t.key)); const vt = d.topics.filter((t) => VERBAL_CH.includes(t.key));
  const vs = d.vocab_ctx || {}; const hasVocab = d.vocab_words.length || d.review_groups.length;
  return `<div class="meta" style="margin-bottom:8px">Like the real GRE: timed sections, one question at a time, Mark & Review, no answers until you submit - then a full review with explanations.</div>
    <ul class="list">
      ${qt.length ? `<li><div class="grow"><b>Section 1 · Quant</b> <span class="meta">(calculator available)</span><div class="meta">${qt.map((t) => esc(t.name)).join(' · ')}</div></div></li>` : ''}
      ${vt.length || hasVocab ? `<li><div class="grow"><b>Section ${qt.length ? 2 : 1} · Verbal</b><div class="meta">${[hasVocab ? (d.vocab_words.length ? `8 of today's words (group ${d.vocab_group}) in sentences` : '8 of your weakest words in sentences') : '', ...vt.map((t) => esc(t.name))].filter(Boolean).join(' · ')}</div>
        ${hasVocab && vs.total ? `<div class="meta">${vs.ready >= vs.total ? 'All of today\'s word sentences are ready.' : `GRE-style sentences ready for ${vs.ready} of ${vs.total} words${vs.running ? ' - your local AI is writing the rest' : ''}; until then a word is tested by its meaning.`}</div>` : ''}</div></li>` : ''}</ul>
    <div class="row" style="margin-top:10px"><button id="q-start">${d.quizzes.length ? 'Retake quiz (new questions)' : 'Start quiz'}</button>
    ${best !== null ? `<span class="meta">Best so far: <b>${best}%</b> · ${d.quizzes.length} attempt${d.quizzes.length > 1 ? 's' : ''}</span>` : '<span class="meta">Wrong answers go to your Error log; missed words go back to flashcard box 1.</span>'}</div>`;
}

// ---------------------------------------------------------------- essay
function essayBox(d) {
  return `<div class="prompt">${esc(d.essay_prompt)}</div>
    <div class="meta" style="margin:6px 0">Write a response in which you discuss the extent to which you agree or disagree with the statement and explain your reasoning. Consider ways the statement might or might not hold true.</div>
    <div class="row" style="margin-bottom:6px"><button class="ghost small" id="e-start">Start 30:00 timer</button><span id="e-timer" class="timer">30:00</span><span style="flex:1"></span><span class="meta" id="e-words">0 words</span></div>
    <textarea id="e-body" rows="14" placeholder="Plan for 5 minutes (thesis + 2-3 examples), write for 22, proofread for 3."></textarea>
    <details style="margin:8px 0"><summary>Scoring rubric</summary><ul class="notes">
      <li>6 – clear, insightful position; compelling, specific examples; well organised; precise language; minor errors only.</li>
      <li>5 – clear position; well-chosen examples; organised; mostly fluent.</li><li>4 – a position with relevant but general support; adequate organisation; some errors.</li>
      <li>3 – limited or vague support; weak organisation; noticeable errors.</li><li>1–2 – little or no position or support; serious language problems.</li></ul></details>
    <div class="row"><label>Self score ${select(['', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5', '5.5', '6'], '', 'id="e-score"')}</label><button class="small" id="e-save">Save essay</button>
      <button class="small" id="e-ai">Save &amp; get AI score</button><button class="ghost small" id="e-tutor">Discuss with tutor</button>
      ${d.essays.length ? `<span class="meta">${d.essays.length} saved for this day (see Essays tab)</span>` : ''}</div>
    <div id="e-fb"></div>`;
}
function bindEssay(d) {
  const ta = $('#e-body'); if (!ta) return;
  let started = null;
  ta.oninput = () => { $('#e-words').textContent = (ta.value.trim() ? ta.value.trim().split(/\s+/).length : 0) + ' words'; };
  $('#e-start').onclick = () => {
    clearInterval(gre.essayTimer); started = Date.now(); ta.focus();
    gre.essayTimer = setInterval(() => {
      const el = $('#e-timer'); if (!el) return clearInterval(gre.essayTimer);
      const left = Math.max(0, 1800 - Math.floor((Date.now() - started) / 1000));
      el.textContent = `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`;
      el.classList.toggle('late', left < 180);
      if (!left) { clearInterval(gre.essayTimer); toast('Time is up — stop writing and proofread.'); }
    }, 1000);
  };
  const save = async () => {
    const r = await post('/api/gre/essays', { day: d.day, prompt: d.essay_prompt, body: ta.value, minutes: started ? Math.round((Date.now() - started) / 600) / 100 : null, self_score: +$('#e-score').value || null });
    await post('/api/gre/day/' + d.day, { parts: { essay: true } }); clearInterval(gre.essayTimer);
    return r.id;
  };
  $('#e-save').onclick = async () => {
    if (!ta.value.trim()) return toast('Write something first');
    await save(); toast('Essay saved'); greClass();
  };
  $('#e-ai').onclick = async () => {
    if (!ta.value.trim()) return toast('Write something first');
    const id = await save();
    ['#e-save', '#e-ai'].forEach((s) => { $(s).disabled = true; });
    $('#e-fb').innerHTML = '<div class="explain warn" style="margin-top:10px">Essay saved. Your local AI is grading it against the ETS rubric - this usually takes 1–3 minutes…</div>';
    const r = await post(`/api/gre/essays/${id}/feedback`, {});
    const fb = $('#e-fb'); if (!fb) return toast('AI feedback ready - see the Essays tab.');
    fb.innerHTML = feedbackHtml(r.feedback, r.ai_score, r.error);
    ['#e-save', '#e-ai'].forEach((s) => { $(s).disabled = false; });
  };
  $('#e-tutor').onclick = () => {
    if (!ta.value.trim()) return toast('Write the essay first');
    tutorSend(`Here is my GRE Issue essay. Point out the weakest argument and help me improve it.\n\nPROMPT: ${d.essay_prompt}\n\nESSAY:\n${ta.value}`, d.day);
    $('#t-status').scrollIntoView({ behavior: 'smooth' });
  };
}
function feedbackHtml(fb, score, error) {
  if (!fb) return '';
  const st = fb.stats || {};
  return `<div class="card" style="margin-top:10px"><div class="row" style="justify-content:space-between"><h3 style="margin:0">AI feedback ${score !== null && score !== undefined ? `<span class="pill ${score >= 4.5 ? 'ok' : score >= 3.5 ? 'warn' : 'bad'}">${score} / 6</span>` : ''}</h3>
      <span class="meta">${esc(fb.model || '')} · ${st.words ?? '?'} words · ${st.paragraphs ?? '?'} paragraphs</span></div>
    ${error ? `<div class="explain bad">${esc(error)}</div>` : ''}
    ${fb.summary ? `<div style="margin:6px 0"><b>${esc(fb.summary)}</b></div>` : ''}
    ${(fb.strengths || []).length ? `<div class="meta" style="margin-top:6px">STRENGTHS</div><ul class="fb-list">${fb.strengths.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
    ${(fb.improvements || []).length ? `<div class="meta">TO IMPROVE</div><ul class="fb-list">${fb.improvements.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
    ${(fb.notes || []).length ? `<div class="meta">STRUCTURE CHECKS</div><ul class="fb-list">${fb.notes.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
    ${fb.rewrite ? `<details><summary>Your weakest paragraph, rewritten</summary><div style="white-space:pre-wrap;margin-top:6px">${esc(fb.rewrite)}</div></details>` : ''}
    <div class="meta" style="margin-top:8px">A small local model is only a rough grader - use the score as a trend, and compare with ETS's scored POWERPREP essays.</div></div>`;
}

// ---------------------------------------------------------------- tutor (local Ollama)
function tutorBox() {
  return `<div class="meta" style="margin-bottom:6px">Your local AI tutor (Ollama) knows today's class. It can explain, set extra questions and review essays — double-check its maths against the answer keys.</div>
    <div class="row" style="margin-bottom:6px">
      <button class="ghost small" data-tq="Explain today's topic to me simply, with one worked example, then give me one question to try.">Explain today's topic</button>
      <button class="ghost small" data-tq="Give me 5 new GRE-style practice questions on today's topic, from easy to hard. Do not show the answers until I reply with mine.">5 more questions</button>
      <button class="ghost small" data-tq="What are the most common traps and mistakes students make on today's topic?">Common traps</button>
      <button class="ghost small" data-tq="Make a 10-minute revision summary of today's class I can read before bed.">Revision summary</button>
      <button class="ghost small" id="t-clear">Clear</button></div>
    <div class="chat" id="t-chat" style="min-height:80px;max-height:420px"></div>
    <div class="row" style="margin-top:8px"><textarea id="t-in" rows="2" placeholder="Ask a doubt, paste a question you got wrong, or send your answers…"></textarea><button id="t-send">Ask</button></div>`;
}
function drawTutor() {
  const box = $('#t-chat'); if (!box) return;
  box.innerHTML = gre.tutor.map((c) => `<div class="msg ${c.role}">${esc(c.content)}</div>`).join('') || '<div class="empty">Stuck on something? Ask here.</div>';
  box.scrollTop = box.scrollHeight;
}
function bindTutor(n) {
  if (gre.tutorDay !== n) { gre.tutor = []; gre.tutorDay = n; }
  drawTutor();
  api('/api/ai/models').then((m) => { const s = $('#t-status'); if (s) s.innerHTML = m.ok ? '<span class="pill ok">Ollama connected</span>' : '<span class="pill bad">Ollama not running</span>'; });
  body().querySelectorAll('[data-tq]').forEach((b) => b.onclick = () => tutorSend(b.dataset.tq, n));
  $('#t-send').onclick = () => { const v = $('#t-in').value; $('#t-in').value = ''; tutorSend(v, n); };
  $('#t-in').onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#t-send').click(); } };
  $('#t-clear').onclick = () => { gre.tutor = []; drawTutor(); };
}
async function tutorSend(text, n) {
  if (!text.trim()) return;
  gre.tutor.push({ role: 'user', content: text }); const ans = { role: 'assistant', content: '…' }; gre.tutor.push(ans); drawTutor();
  const r = await fetch('/api/gre/tutor', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ day: n, messages: gre.tutor.slice(0, -1) }) });
  const reader = r.body.getReader(); const dec = new TextDecoder(); ans.content = '';
  for (;;) { const { done, value } = await reader.read(); if (done) break; ans.content += dec.decode(value, { stream: true }); drawTutor(); }
}

// ---------------------------------------------------------------- error log
const KIND_HELP = { Unsorted: 'not sorted yet', Concept: "didn't know how", Careless: 'knew it, slipped', Timing: 'ran out of time / too slow',
  Vocab: "didn't know a word", Misread: 'misread the question' };
function errorForm(d) {
  return `<div class="form-grid" style="margin-top:8px;max-width:none"><span>Topic</span><input id="er-topic" value="${esc(d ? d.title : '')}">
    <span>Question / where</span><input id="er-q" placeholder="e.g. Magoosh MC Q42, or paste the question">
    <span>Why I missed it</span>${select(['Concept gap', 'Careless mistake', 'Ran out of time', 'Did not know the word', 'Misread the question'], 'Concept gap', 'id="er-why"')}
    <span>Rule for next time</span><input id="er-note" placeholder="The takeaway in one line"><span></span><div><button class="small" id="er-add">Add to Error log</button></div></div>`;
}
function bindErrorForm(d) {
  const b = $('#er-add'); if (!b) return;
  b.onclick = async () => {
    if (!$('#er-q').value.trim()) return toast('Describe the question first');
    await post('/api/gre/errors', { day: d ? d.day : null, topic: $('#er-topic').value, source: d ? `Practice - day ${d.day}` : 'Manual',
      question: $('#er-q').value, answer: $('#er-why').value, note: $('#er-note').value });
    toast('Logged - due for a redo in a week'); $('#er-q').value = ''; $('#er-note').value = '';
  };
}
const errView = { filter: 'Due', kind: 'All', redo: null };
async function greErrors() {
  const [rows, sum] = await Promise.all([api('/api/gre/errors'), api('/api/gre/errors/summary')]);
  gre.errRows = rows;
  const t0 = isoToday();
  const list = rows.filter((r) => (errView.filter === 'All' || (errView.filter === 'Due' ? r.due : r.status === errView.filter))
    && (errView.kind === 'All' || (r.kind || 'Unsorted') === errView.kind));
  const maxT = Math.max(1, ...Object.values(sum.trend).flat());
  const redo = errView.redo && rows.find((r) => r.id === errView.redo.id);
  body().innerHTML = `${redo ? redoBox(redo) : ''}
    <div class="grid g2" style="margin-bottom:16px"><div class="card"><h2>Why you miss questions <span class="meta">(open mistakes - click to filter)</span></h2>
      <div class="kinds"><button class="k ${errView.kind === 'All' ? 'on' : ''}" data-kind="All"><b>${Object.values(sum.open).reduce((a, b) => a + b, 0)}</b>All</button>
        ${sum.kinds.map((k) => `<button class="k ${errView.kind === k ? 'on' : ''}" data-kind="${k}" title="${esc(KIND_HELP[k])}"><b>${sum.open[k]}</b>${k}</button>`).join('')}</div>
      <div class="meta" style="margin-top:8px">${sum.open.Unsorted ? `Sort the ${sum.open.Unsorted} unsorted mistakes - knowing WHY you miss questions is the fastest way to stop missing them.` : 'All open mistakes are sorted.'}
        ${sum.open.Careless > sum.open.Concept && sum.open.Careless >= 3 ? ' Careless errors are your biggest group: slow down on the first read and re-check what the question asks.' : ''}
        ${sum.open.Timing >= 3 ? ' Timing is costing you: guess, mark and move on after 2 minutes.' : ''}</div></div>
      <div class="card"><h2>Mistakes per week</h2><table class="trend"><thead><tr><th></th>${sum.weeks.map((w) => `<th>${fmtDate(w, { day: 'numeric', month: 'short' })}</th>`).join('')}</tr></thead>
        <tbody>${sum.kinds.filter((k) => sum.trend[k].some((x) => x)).map((k) => `<tr><td style="text-align:left">${k}</td>${sum.trend[k].map((x) => `<td class="${x && x >= maxT * 0.6 ? 'hot' : ''}">${x || '·'}</td>`).join('')}</tr>`).join('')
          || '<tr><td colspan="7" class="empty">No mistakes logged in the last 6 weeks.</td></tr>'}</tbody></table>
        <div class="meta" style="margin-top:6px">A falling row means that kind of mistake is going away.</div></div></div>
    <div class="card"><div class="toolbar"><b>Error log</b><span class="meta">Each mistake comes back for a redo after a week. Solve it cold: right → Fixed, wrong → back in 3 days.</span>
      <span style="flex:1"></span>${select(['Due', 'Open', 'Fixed', 'All'], errView.filter, 'id="er-f"')}</div>
    ${errView.filter === 'Due' && !list.length ? `<div class="empty">Nothing due for a redo today.${rows.some((r) => r.status === 'Open') ? ' Switch the filter to "Open" to see everything still open.' : ''}</div>` : ''}
    <div class="tablewrap"><table><thead><tr><th>Date</th><th>Topic</th><th>Question</th><th>Answer</th><th>Why</th><th>Rule for next time</th><th>Status</th><th></th></tr></thead>
    <tbody>${list.map((r) => `<tr data-id="${r.id}"><td style="white-space:nowrap">${fmtDate(r.created)}<div class="meta">${esc(r.source || '')}</div>
        ${r.status === 'Open' ? `<div class="meta">${r.due ? '<span class="pill warn">redo due</span>' : `redo ${fmtDate(r.redo_on, { day: 'numeric', month: 'short' })}`}${r.redo_count ? ` · ${r.redo_count} tr${r.redo_count > 1 ? 'ies' : 'y'}` : ''}</div>` : ''}</td>
      <td>${esc(r.topic || '')}</td>
      <td style="max-width:340px;white-space:pre-wrap">${esc((r.question || '').length > 220 ? r.question.slice(0, 220) + '…' : r.question)}${r.detail && r.detail.links ? `<div class="meta">${r.detail.links.map((l) => ext(l.url, esc(l.label))).join(' · ')}</div>` : ''}</td><td style="max-width:200px">${esc(r.answer || '')}${r.secs ? `<div class="meta">${r.secs} s</div>` : ''}</td>
      <td>${select(sum.kinds, r.kind || 'Unsorted', 'class="er-kind"')}</td>
      <td><textarea class="er-note" rows="2" style="min-width:180px">${esc(r.note || '')}</textarea></td><td>${select(['Open', 'Fixed'], r.status, 'class="er-st"')}</td>
      <td style="white-space:nowrap">${r.status === 'Open' ? '<button class="small er-redo">Redo</button> ' : ''}<button class="danger small er-del">×</button></td></tr>`).join('')
      || (errView.filter === 'Due' ? '' : '<tr><td colspan="8" class="empty">Nothing here.</td></tr>')}</tbody></table></div></div>
    <div class="card" style="margin-top:16px"><h2>Add an entry</h2>${errorForm(null)}</div>`;
  $('#er-f').onchange = (e) => { errView.filter = e.target.value; greErrors(); };
  body().querySelectorAll('[data-kind]').forEach((b) => b.onclick = () => { errView.kind = b.dataset.kind; if (errView.filter === 'Due' && b.dataset.kind !== 'All') errView.filter = 'Open'; greErrors(); });
  body().querySelectorAll('tr[data-id]').forEach((tr) => {
    const id = +tr.dataset.id;
    tr.querySelector('.er-note').onchange = async (e) => { await patch('/api/gre/errors/' + id, { note: e.target.value }); toast('Saved'); };
    tr.querySelector('.er-kind').onchange = async (e) => { await patch('/api/gre/errors/' + id, { kind: e.target.value }); greErrors(); };
    tr.querySelector('.er-st').onchange = async (e) => { await patch('/api/gre/errors/' + id, { status: e.target.value }); greErrors(); };
    tr.querySelector('.er-del').onclick = async () => { if (confirm('Delete this entry?')) { await del('/api/gre/errors/' + id); greErrors(); } };
    const rd = tr.querySelector('.er-redo'); if (rd) rd.onclick = () => { errView.redo = { id, r: null, checked: false, revealed: false }; greErrors(); window.scrollTo(0, 0); };
  });
  if (redo) bindRedo(redo);
  bindErrorForm(null);
  const b = $('#er-add'); const orig = b.onclick; b.onclick = async () => { await orig(); greErrors(); };
}
function redoBox(r) {
  const R = errView.redo; const q = r.detail;
  const canAnswer = q && (q.c || q.kind === 'ne');
  let inner;
  if (canAnswer) {
    inner = `<div id="rd-q">${qBody(q, R.r, { locked: R.checked, reveal: R.checked })}</div>
      ${R.checked ? `<div class="explain ${R.ok ? 'ok' : 'bad'}"><b>${R.ok ? 'Right - marked Fixed.' : 'Still wrong - it comes back in 3 days.'}</b> ${esc(q.x || r.note || '')}</div>`
        : `<div class="row" style="margin-top:10px"><button id="rd-check" ${answered(q, R.r) ? '' : 'disabled'}>Check</button><span class="meta">Solve it cold, without looking at your notes.</span></div>`}`;
  } else {
    const links = q && q.links ? q.links.filter((l) => R.revealed || !/solution/i.test(l.label)) : [];
    inner = `<div class="qtext">${esc(r.question || '')}</div>
      ${links.length ? `<div class="row" style="margin-bottom:6px">${links.map((l) => ext(l.url, esc(l.label))).join(' · ')}</div>` : ''}
      ${R.revealed ? `<div class="explain">${esc(r.answer || '')}${r.note ? `<div style="margin-top:4px"><b>Rule:</b> ${esc(r.note)}</div>` : ''}</div>
        ${R.checked ? '' : '<div class="row" style="margin-top:10px"><button id="rd-yes">I got it right</button><button class="ghost" id="rd-no">Still wrong</button></div>'}`
        : '<div class="row" style="margin-top:10px"><button id="rd-show">I have solved it - show the answer</button><span class="meta">Redo it on paper first.</span></div>'}`;
  }
  return `<div class="card redo-box" style="margin-bottom:16px"><div class="row"><h2 style="margin:0">Redo: ${esc(r.topic || '')}</h2><span class="pill">${esc(r.kind || 'Unsorted')}</span>
      <span style="flex:1"></span>${R.checked ? '<button class="small" id="rd-next">Next due mistake →</button>' : ''}<button class="ghost small" id="rd-close">Close</button></div>${inner}</div>`;
}
function bindRedo(r) {
  const R = errView.redo; const q = r.detail;
  const finish = async (ok) => { R.checked = true; R.ok = ok; await post(`/api/gre/errors/${r.id}/redo`, { correct: ok }); greErrors(); };
  $('#rd-close').onclick = () => { errView.redo = null; greErrors(); };
  const nx = $('#rd-next'); if (nx) nx.onclick = () => {
    const next = (gre.errRows || []).find((x) => x.due && x.id !== r.id);
    errView.redo = next ? { id: next.id, r: null, checked: false, revealed: false } : null;
    if (!next) toast('No more mistakes due today.');
    greErrors();
  };
  if (q && (q.c || q.kind === 'ne') && !R.checked) {
    bindQ($('#rd-q'), q, () => R.r, (v) => { R.r = v; const ck = $('#rd-check'); if (ck) ck.disabled = !answered(q, v); }, () => greErrors());
    $('#rd-check').onclick = () => finish(isRight(q, R.r));
  } else if (R.checked) body().querySelectorAll('#ne-in').forEach((x) => x.removeAttribute('id'));
  const sh = $('#rd-show'); if (sh) sh.onclick = () => { R.revealed = true; greErrors(); };
  const y = $('#rd-yes'); if (y) y.onclick = () => finish(true);
  const no = $('#rd-no'); if (no) no.onclick = () => finish(false);
}

// ---------------------------------------------------------------- plan
async function grePlan() {
  const o = gre.ov; const today = isoToday();
  let html = '';
  for (let w = 1; w <= o.weeks; w++) {
    const ds = o.days.filter((d) => d.week === w);
    const done = ds.filter((d) => d.done).length;
    html += `<div class="month">Week ${w} <span class="meta" style="font-weight:400">· ${fmtDate(ds[0].date, { day: 'numeric', month: 'short' })} – ${fmtDate(ds[ds.length - 1].date, { day: 'numeric', month: 'short' })} · ${done}/${ds.length} done</span></div>
      <div class="card"><ul class="list">${ds.map((d) => `<li class="plan-row ${d.day === o.status.current ? 'cur' : ''}" data-open="${d.day}">
        <span class="time">${fmtDate(d.date, { weekday: 'short', day: '2-digit', month: 'short' })}</span>
        <button class="check ${d.done ? 'on' : ''}" tabindex="-1">${d.done ? '✓' : ''}</button>
        <div class="grow"><b>Day ${d.day}</b> · ${secPill(d.section)} ${esc(d.title)}${d.vocab_group ? `<span class="meta"> · vocab group ${d.vocab_group}</span>` : ''}</div>
        ${d.quiz_pct !== null ? `<span class="pill ${d.quiz_pct >= 80 ? 'ok' : d.quiz_pct >= 60 ? 'warn' : 'bad'}">quiz ${d.quiz_pct}%</span>` : ''}
        ${!d.done && d.date < today ? '<span class="pill bad">overdue</span>' : ''}${d.date === today ? '<span class="pill warn">today</span>' : ''}</li>`).join('')}</ul></div>`;
  }
  body().innerHTML = `<div class="row" style="margin-bottom:6px"><div class="meta grow">Click any day to open its class. Dates follow your start date and study days (Settings tab). The next class is always the first one not done.</div>
      ${o.status.behind ? `<button class="small" onclick="greReplan()">Re-plan from today (${o.status.behind} behind)</button>` : ''}</div>${html}`;
  body().querySelectorAll('[data-open]').forEach((li) => li.onclick = () => { gre.day = +li.dataset.open; gre.tab = 'class'; views.gre(); });
}

// ---------------------------------------------------------------- vocab trainer
async function greVocab() {
  const [v, qu, eod] = await Promise.all([api('/api/gre/vocab'), api('/api/gre/vocab/queue'), api('/api/gre/vocab/eod')]);
  gre.v = v; gre.vi = 0; gre.vshow = false; gre.qu = qu;
  const wu = gre.warm && gre.warm.date === isoToday() ? gre.warm : (gre.warm = { date: isoToday(), i: 0, picked: null, results: [], skipped: false, qs: qu.warmup });
  const warming = wu.qs.length && !wu.skipped && wu.i < wu.qs.length;
  const boxes = [1, 2, 3, 4, 5].map((b) => `<div class="card stat"><div class="l">Box ${b}${b === 1 ? ' (daily)' : b === 5 ? ' (mastered)' : ''}</div><div class="n">${v.boxes[b] || 0}</div></div>`).join('');
  const dots = (h) => `<span class="dots">${[...Array(qu.target)].map((_, k) => `<i class="${k < h ? 'on' : ''}"></i>`).join('')}</span>`;
  const done = wu.results.length ? `<div class="explain ok" style="margin-bottom:10px">Warm-up done: ${wu.results.filter((r) => r.ok).length}/${wu.results.length} right${wu.results.some((r) => r.cleared) ? ` · cleared: ${wu.results.filter((r) => r.cleared).map((r) => esc(r.word)).join(', ')}` : ''}.</div>` : '';
  const status = (w) => w.today ? "missed today - in tomorrow's warm-up" : w.done_today ? 'done today' : "in today's warm-up";
  body().innerHTML = `<div class="grid g2"><div class="card">${warming
      ? `<h2>Warm-up: missed words <span class="pill bad">${wu.qs.length - wu.i} left</span></h2><div id="wu"></div>`
      : `<h2>Flashcards due <span class="pill warn">${v.due.length}</span></h2>${done}
        ${v.budget && v.budget.daily_cap ? `<div class="meta" style="margin-bottom:8px">Today's limit: ${v.budget.daily_cap} cards (${v.budget.done_today} done so far) - about half reviews, half new words.${v.budget.waiting ? ` ${v.budget.waiting} more cards wait for the next days.` : ''}${v.budget.cap < 30 ? ` Fewer new words while your missed-words queue has ${v.budget.queue} words.` : ''}</div>` : ''}
        ${wu.results.length && gre.day ? `<div style="margin-bottom:8px"><button class="ghost small" onclick="greOpen(${gre.day})">← Back to Day ${gre.day} class</button></div>` : ''}<div id="fc"></div>`}</div>
    <div class="card"><h2>How it works</h2><ul class="notes">
      <li><b>Missed-words queue:</b> every word you get wrong (flashcards, phone, quiz) joins the queue. From the next day it comes back in a mixed warm-up before your flashcards - meaning, word or sentence questions. <b>${qu.target} correct answers</b> remove it.</li>
      <li>Words unlock with your classes (one GregMat group per weekday).</li>
      <li>"Knew it" moves a word up a box; "Didn't know" sends it back to box 1 and into the queue.</li><li>Box 1 is shown daily, box 2 after 1 day, box 3 after 3, box 4 after a week, box 5 after 15 days.</li>
      <li>Want them on your phone? Turn on <a href="#" onclick="gre.tab='gsettings';views.gre();return false">phone flashcards</a> in Settings.</li></ul></div></div>
    <div class="card" style="margin-top:16px"><div class="row"><h2 style="margin:0">Missed-words queue <span class="pill">${qu.queue.length}</span></h2>
        <span class="meta">${qu.cleared} cleared so far · ${qu.target} correct answers clear a word${qu.warmup_waiting ? ` · ${qu.warmup_waiting} more wait for the next warm-ups (max ${qu.cap} a day)` : ''}</span><span style="flex:1"></span>
        ${!warming && wu.qs.length > wu.i ? '<button class="small" id="wu-resume">Do the warm-up</button>' : ''}
        ${!warming && eod.pending ? `<button class="small" id="eod-v">End-of-day review (${eod.pending})</button>` : ''}</div>
      ${qu.queue.length ? `<details class="qlist" style="margin-top:8px"><summary class="meta">Show the ${qu.queue.length} words in the queue</summary>
        <div class="words show qwords" style="margin-top:8px">${qu.queue.map((w) => `<div class="word"><b>${esc(w.word)}</b> ${dots(w.hits)}
          <span class="meta">${status(w)}${w.misses ? ` · missed ${w.misses}x in warm-ups` : ''}</span><span class="def">${esc(w.def)}</span></div>`).join('')}</div></details>`
        : '<div class="empty">Empty - words you miss will appear here.</div>'}</div>
    <div class="grid g5" style="margin:16px 0">${boxes}</div>
    <div class="card"><div class="toolbar"><h2 style="margin:0">All 37 GregMat groups</h2><span style="flex:1"></span><input id="v-q" placeholder="Search a word…"></div><div id="v-groups"></div></div>`;
  if (warming) drawWarmup(); else drawCard();
  const rs = $('#wu-resume'); if (rs) rs.onclick = () => { wu.skipped = false; greVocab(); };
  const ev = $('#eod-v'); if (ev) ev.onclick = () => {
    const card = body().querySelector('.grid.g2 > .card');
    card.innerHTML = "<h2>End-of-day review - today's missed words</h2><div id='eod-v-box'></div>"; card.scrollIntoView({ behavior: 'smooth' });
    runWordDrill($('#eod-v-box'), eod.questions, '/api/gre/vocab/eod', { label: "Today's missed words", onDone: (res) => { toast(`Review done: ${res.filter((r) => r.ok).length}/${res.length} right`); greVocab(); } });
  };
  const drawGroups = (q = '') => {
    $('#v-groups').innerHTML = v.groups.map((g) => {
      const ws = g.words.filter((w) => !q || w.word.toLowerCase().includes(q) || w.def.toLowerCase().includes(q));
      if (q && !ws.length) return '';
      return `<details ${q ? 'open' : ''} class="vg"><summary><b>Group ${g.group}</b> ${g.unlocked ? '' : '<span class="pill">locked</span>'}
        <span class="meta">${g.seen}/30 seen · ${g.mastered} mastered</span><span class="bar" style="display:inline-block;width:120px;vertical-align:middle;margin-left:8px"><i style="width:${Math.round(100 * g.mastered / 30)}%"></i></span></summary>
        <div class="words show">${ws.map((w) => `<div class="word"><b>${esc(w.word)}</b> <span class="pill">${w.box ? 'box ' + w.box : 'new'}</span><span class="def">${esc(w.def)}</span></div>`).join('')}</div></details>`;
    }).join('');
  };
  drawGroups();
  $('#v-q').oninput = (e) => drawGroups(e.target.value.trim().toLowerCase());
}
// quick word drill used by the end-of-day review: questions from the server, answers posted to `endpoint`
function runWordDrill(el, qs, endpoint, { label = 'Word review', onDone = () => {} } = {}) {
  const st = { i: 0, picked: null, res: [] };
  const draw = () => {
    if (st.i >= qs.length) return onDone(st.res);
    const q = qs[st.i];
    const fmt = { meaning: 'Pick the meaning', word: 'Pick the word', sentence: 'Fill the blank' }[q.format];
    el.innerHTML = `<div class="meta">${esc(label)} · ${fmt} · ${st.i + 1} of ${qs.length}</div>
      <div class="qtext" style="font-size:17px">${esc(q.q)}</div>
      <div class="choices">${q.c.map((c, j) => {
        let cls = ''; if (st.picked !== null) cls = j === q.a ? 'right' : (j === st.picked ? 'wrong' : '');
        return `<button class="choice ${cls}" data-dc="${j}" ${st.picked !== null ? 'disabled' : ''}>${String.fromCharCode(65 + j)}&nbsp; ${esc(c)}</button>`;
      }).join('')}</div>
      ${st.picked !== null ? `<div class="explain ${st.picked === q.a ? 'ok' : 'bad'}"><b>${esc(q.word)}</b> ${sayBtn(q.word)}: ${esc(q.def)}
        <div style="margin-top:4px">${flagBtn({ kind: q.format === 'sentence' ? 'vocab_sentence' : 'other', ref: q.word, text: q.q })}</div></div>
        <div class="row" style="margin-top:10px"><button data-dnext>${st.i + 1 < qs.length ? 'Next' : 'Finish'} (Enter)</button></div>`
      : `<div class="meta" style="margin-top:8px">Keys 1-${q.c.length} to answer.</div>`}`;
    el.querySelectorAll('[data-dc]').forEach((b) => b.onclick = () => answer(+b.dataset.dc));
    const nx = el.querySelector('[data-dnext]'); if (nx) nx.onclick = next;
  };
  const answer = async (j) => {
    if (st.picked !== null) return;
    const q = qs[st.i]; st.picked = j;
    st.res.push({ word: q.word, ok: j === q.a });
    draw();
    await post(endpoint, { word: q.word, correct: j === q.a });
  };
  const next = () => { st.i++; st.picked = null; draw(); };
  document.onkeydown = (e) => {
    if (!document.body.contains(el) || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) || st.i >= qs.length) return;
    const q = qs[st.i];
    if (st.picked === null && /^[1-5]$/.test(e.key) && +e.key <= q.c.length) answer(+e.key - 1);
    else if (st.picked !== null && e.key === 'Enter') { e.preventDefault(); next(); }
  };
  if (!qs.length) { el.innerHTML = '<div class="meta">Nothing to review.</div>'; return; }
  draw();
}

// one warm-up question at a time, with the meaning shown after each answer
function drawWarmup() {
  const wu = gre.warm; const el = $('#wu'); if (!el) return;
  const q = wu.qs[wu.i]; const target = gre.qu.target;
  const fmt = { meaning: 'Pick the meaning', word: 'Pick the word', sentence: 'Fill the blank' }[q.format];
  const after = wu.last && wu.last.cleared ? ' - <b>cleared from the queue!</b>' : wu.picked === q.a ? ` (${wu.last ? wu.last.hits : q.hits + 1}/${target})` : ' - it stays in the queue.';
  el.innerHTML = `<div class="meta">${fmt} · ${wu.i + 1} of ${wu.qs.length} · ${q.hits}/${target} correct so far for this word</div>
    <div class="qtext" style="font-size:17px">${esc(q.q)}</div>
    <div class="choices">${q.c.map((c, j) => {
      let cls = ''; if (wu.picked !== null) cls = j === q.a ? 'right' : (j === wu.picked ? 'wrong' : '');
      return `<button class="choice ${cls}" data-c="${j}" ${wu.picked !== null ? 'disabled' : ''}>${String.fromCharCode(65 + j)}&nbsp; ${esc(c)}</button>`;
    }).join('')}</div>
    ${wu.picked !== null ? `<div class="explain ${wu.picked === q.a ? 'ok' : 'bad'}"><b>${esc(q.word)}</b> ${sayBtn(q.word)}: ${esc(q.def)}${after}
        <div style="margin-top:4px">${flagBtn({ kind: q.format === 'sentence' ? 'vocab_sentence' : 'other', ref: q.word, text: q.q })}</div></div>
      <div class="row" style="margin-top:10px"><button id="wu-next">${wu.i + 1 < wu.qs.length ? 'Next' : 'Finish warm-up'} (Enter)</button></div>`
    : `<div class="row" style="margin-top:10px"><span class="meta">Keys 1-${q.c.length} to answer.</span><span style="flex:1"></span><button class="ghost small" id="wu-skip">Skip warm-up for now</button></div>`}`;
  const answer = async (j) => {
    if (wu.picked !== null) return;
    wu.picked = j; const ok = j === q.a;
    wu.last = await post('/api/gre/vocab/queue', { word: q.word, correct: ok });
    wu.results.push({ word: q.word, ok, cleared: wu.last.cleared });
    drawWarmup();
  };
  const next = () => { wu.i++; wu.picked = null; wu.last = null; if (wu.i >= wu.qs.length) greVocab(); else drawWarmup(); };
  el.querySelectorAll('[data-c]').forEach((b) => b.onclick = () => answer(+b.dataset.c));
  const nx = $('#wu-next'); if (nx) nx.onclick = next;
  const sk = $('#wu-skip'); if (sk) sk.onclick = () => { wu.skipped = true; greVocab(); };
  document.onkeydown = (e) => {
    if (gre.tab !== 'vocab' || current !== 'gre' || !$('#wu') || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    if (wu.picked === null && /^[1-5]$/.test(e.key) && +e.key <= q.c.length) answer(+e.key - 1);
    else if (wu.picked !== null && e.key === 'Enter') { e.preventDefault(); next(); }
  };
}
function drawCard() {
  const v = gre.v; const el = $('#fc'); if (!el) return;
  if (gre.vi >= v.due.length) {
    el.innerHTML = `<div class="empty">${v.due.length ? 'All due cards done for today. 🎉' : (v.unlocked.length ? 'Nothing due — come back tomorrow.' : 'Words unlock when you open your first class.')}</div>`; return;
  }
  const w = v.due[gre.vi];
  el.innerHTML = `<div class="flash" id="fc-card"><div class="meta">Group ${w.group} · ${w.box ? 'box ' + w.box : 'new word'} · ${gre.vi + 1} of ${v.due.length}</div>
      <div class="fw">${esc(w.word)} ${sayBtn(w.word)}</div><div class="fd">${gre.vshow ? esc(w.def) : '<span class="meta">Say the meaning out loud, then reveal (Space)</span>'}</div></div>
    <div class="row" style="justify-content:center;margin-top:10px">${gre.vshow
      ? '<button class="danger" id="fc-no">Didn\'t know (1)</button><button id="fc-yes">Knew it (2)</button>'
      : '<button id="fc-show">Reveal meaning</button>'}</div>`;
  const ans = async (ok) => { await post('/api/gre/vocab', { word: w.word, correct: ok }); gre.vi++; gre.vshow = false; drawCard(); };
  if ($('#fc-show')) $('#fc-show').onclick = () => { gre.vshow = true; drawCard(); };
  if ($('#fc-yes')) { $('#fc-yes').onclick = () => ans(true); $('#fc-no').onclick = () => ans(false); }
  document.onkeydown = (e) => {
    if (gre.tab !== 'vocab' || current !== 'gre' || ['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;
    if (e.code === 'Space' && !gre.vshow) { e.preventDefault(); gre.vshow = true; drawCard(); }
    else if (gre.vshow && e.key === '1') ans(false);
    else if (gre.vshow && e.key === '2') ans(true);
  };
}

// ---------------------------------------------------------------- progress
async function greProgress() {
  const o = gre.ov;
  const ins = await api('/api/gre/insights');
  gre.progressExtra = true;
  const mastered = (o.vocab.boxes[4] || 0) + (o.vocab.boxes[5] || 0);
  const sp = ins.speed;
  body().innerHTML = `<div id="weekly-box" style="margin-bottom:16px"></div>
    <div class="grid g2" style="margin-bottom:16px"><div id="smart-p"></div>
      <div class="card"><h2>Full practice test in the app</h2><div>Essay (30 min) + Verbal + Quant sections with real GRE timing and section-adaptive difficulty - about 2 hours.
        Sections are saved like course tests (they feed the predictor and the Error log) and you get estimated scores at the end.</div>
        <button style="margin-top:10px" onclick="startMock()">Start a full practice test</button></div></div>
    <div class="grid g2" style="margin-bottom:16px">${predictCard(ins.predict.quant)}${predictCard(ins.predict.verbal)}</div>
    <div class="grid g4" style="margin-bottom:16px">
      <div class="card stat"><div class="l">Classes done</div><div class="n">${o.status.done}/${o.status.total}</div><div class="x">${o.status.behind ? o.status.behind + ' behind plan' : 'on track'}</div></div>
      <div class="card stat"><div class="l">Hours studied</div><div class="n">${(o.minutes / 60).toFixed(1)}</div><div class="x">from completed classes</div></div>
      <div class="card stat"><div class="l">Words mastered (box 4-5)</div><div class="n">${mastered}</div><div class="x">of 1,112 GregMat words</div></div>
      <div class="card stat"><div class="l">Quizzes taken</div><div class="n">${o.quizzes.length}</div><div class="x">${o.errors_open} open errors · ${o.errors_due} due</div></div></div>
    <div class="grid g2"><div class="grid" style="align-content:start">
      <div class="card"><h2>Pacing by chapter <span class="meta">(slowest first, from course tests)</span></h2>
        ${sp.length ? `<table><thead><tr><th>Chapter</th><th style="text-align:right">Avg</th><th style="text-align:right">Slow</th><th style="text-align:right">Right when fast</th><th style="text-align:right">Right when slow</th></tr></thead>
          <tbody>${sp.map((r) => `<tr><td>${esc(r.title)} <span class="pill">${r.subject === 'quant' ? 'Q' : 'V'}</span></td>
            <td style="text-align:right">${r.avg} s${r.avg > r.limit ? ' <span class="pill slow">slow</span>' : ''}</td><td style="text-align:right">${r.slow_pct}%</td>
            <td style="text-align:right">${r.acc_fast ?? '–'}${r.acc_fast !== null ? '%' : ''}</td><td style="text-align:right">${r.acc_slow ?? '–'}${r.acc_slow !== null ? '%' : ''}</td></tr>`).join('')}</tbody></table>
          <div class="meta" style="margin-top:8px">GRE pace is about ${ins.pace.quant} s per quant question and ${ins.pace.verbal} s per verbal question. "Slow" = over 2 min (quant), 90 s (TC/SE) or 2½ min (reading).
            If you rarely get slow questions right, guess and move on sooner - that time is worth more on the next question.</div>`
          : '<div class="empty">Take course tests to see your pace per chapter.</div>'}</div>
      <div class="card"><h2>Accuracy by quiz topic <span class="meta">(weakest first)</span></h2>
      ${o.topics.length ? `<table><tbody>${o.topics.map((t) => `<tr><td>${esc(t.name)}</td><td style="width:40%"><div class="bar"><i style="width:${t.pct}%;background:${t.pct >= 80 ? 'var(--ok)' : t.pct >= 60 ? 'var(--warn)' : 'var(--bad)'}"></i></div></td>
        <td style="text-align:right;white-space:nowrap">${t.pct}% <span class="meta">(${t.correct}/${t.total})</span></td></tr>`).join('')}</tbody></table>` : '<div class="empty">Take a quiz to see your strengths and weaknesses.</div>'}</div></div>
      <div class="grid" style="align-content:start"><div class="card"><div class="row"><h2 style="margin:0">Practice-test scores</h2><span style="flex:1"></span>
        <button class="ghost small" onclick="greAddResult()">Add result screenshot</button></div><div style="height:8px"></div>
        ${o.scores.length ? `<table><thead><tr><th>Date</th><th>Test</th><th>Q</th><th>V</th><th>AWA</th><th></th></tr></thead><tbody>${o.scores.map((s) => `<tr><td>${fmtDate(s.date)}</td><td>${esc(s.name || '')}</td>
          <td><b>${s.quant ?? ''}</b></td><td><b>${s.verbal ?? ''}</b></td><td>${s.awa ?? ''}</td><td><button class="danger small" data-sdel="${s.id}">×</button></td></tr>`).join('')}</tbody></table>` : '<div class="empty">Scores from mock tests appear here.</div>'}
        <details style="margin-top:8px"><summary>+ Add a score</summary><div class="row" style="margin-top:6px"><input id="s-d" type="date" value="${isoToday()}"><input id="s-n" placeholder="Test name" size="18">
          <input id="s-q" type="number" placeholder="Q" style="width:64px"><input id="s-v" type="number" placeholder="V" style="width:64px"><input id="s-a" type="number" step="0.5" placeholder="AWA" style="width:64px"><button class="small" id="s-add">Add</button></div></details></div>
      <div class="card"><h2>Open mistakes by type</h2><div class="kinds">${ins.errors.kinds.map((k) => `<div class="k"><b>${ins.errors.open[k]}</b>${k}</div>`).join('')}</div>
        <div class="row" style="margin-top:10px"><span class="meta grow">${ins.errors.due} due for a redo today.</span><button class="ghost small" onclick="gre.tab='errors';views.gre()">Open Error log</button></div></div>
      <div class="card"><h2>Recent quizzes</h2><ul class="list">${o.quizzes.slice(0, 12).map((q) => `<li><span class="time">${fmtDate(q.at.slice(0, 10))}</span><div class="grow">Day ${q.day}</div>
        <span class="pill ${q.score / q.total >= 0.8 ? 'ok' : q.score / q.total >= 0.6 ? 'warn' : 'bad'}">${q.score}/${q.total}</span></li>`).join('') || '<li class="empty">None yet.</li>'}</ul></div></div></div>`;
  drawWeekly($('#weekly-box'));
  smartCardHtml(null).then((h) => { const el = $('#smart-p'); if (el) { el.innerHTML = h; bindSmart(el, null); } });
  $('#s-add').onclick = async () => { await post('/api/gre/scores', { date: $('#s-d').value, name: $('#s-n').value, quant: +$('#s-q').value || null, verbal: +$('#s-v').value || null, awa: +$('#s-a').value || null }); toast('Saved'); views.gre(); };
  body().querySelectorAll('[data-sdel]').forEach((b) => b.onclick = async () => { await del('/api/gre/scores/' + b.dataset.sdel); views.gre(); });
}

// ---------------------------------------------------------------- essays
async function greEssays() {
  const es = await api('/api/gre/essays');
  const scored = es.filter((e) => e.ai_score !== null && e.ai_score !== undefined);
  body().innerHTML = `<div class="card"><h2>Your essays</h2><div class="meta" style="margin-bottom:8px">Essay days are in the plan (days ${gre.ov.days.filter((d) => d.essay).map((d) => d.day).join(', ')}). Reread old essays before writing a new one.
      ${scored.length > 1 ? ` AI scores so far: ${scored.slice().reverse().map((e) => `<b>${e.ai_score}</b>`).join(' → ')}.` : ''}</div>
    ${es.map((e) => `<details class="vg" data-eid="${e.id}"><summary><b>${fmtDate(e.at.slice(0, 10))}</b> · Day ${e.day ?? '–'} · ${e.words} words${e.minutes ? ` · ${Math.round(e.minutes)} min` : ''}${e.self_score ? ` · self-score <b>${e.self_score}</b>` : ''}
        ${e.ai_score !== null && e.ai_score !== undefined ? ` · <span class="pill ${e.ai_score >= 4.5 ? 'ok' : e.ai_score >= 3.5 ? 'warn' : 'bad'}">AI ${e.ai_score}</span>` : ''}</summary>
      <div class="prompt" style="margin:8px 0">${esc(e.prompt || '')}</div><div style="white-space:pre-wrap">${esc(e.body || '')}</div>
      <div class="fb">${e.ai_feedback ? feedbackHtml(e.ai_feedback, e.ai_score, e.ai_feedback.error) : ''}</div>
      <div class="row" style="margin-top:8px"><button class="small" data-grade="${e.id}">${e.ai_feedback ? 'Grade again' : 'Get AI feedback'}</button><span class="meta">Takes 1–3 minutes on your laptop.</span></div></details>`).join('') || '<div class="empty">No essays yet.</div>'}
    <div style="margin-top:10px"><a class="ext" href="https://www.ets.org/gre/test-takers/general-test/prepare/content/analytical-writing.html" target="_blank" rel="noopener">Official ETS writing page (prompt pools, scoring guide)</a></div></div>`;
  body().querySelectorAll('[data-grade]').forEach((b) => b.onclick = async () => {
    const id = b.dataset.grade; const box = body().querySelector(`[data-eid="${id}"] .fb`);
    b.disabled = true; box.innerHTML = '<div class="explain warn" style="margin-top:10px">Grading with your local AI…</div>';
    const r = await post(`/api/gre/essays/${id}/feedback`, {});
    if (gre.tab === 'essays') greEssays(); else toast('AI feedback ready');
    if (!r.ok) toast(r.error || 'Could not grade');
  });
}

// ---------------------------------------------------------------- library
let libQ = '';
async function greLibrary() {
  if (notesState.open) return drawNote();
  const lib = gre.lib || (gre.lib = await api('/api/gre/library'));
  const notesList = gre.notesList || (gre.notesList = await api('/api/gre/notes'));
  const draw = () => {
    const q = libQ.toLowerCase();
    const files = lib.files.filter((f) => !q || (f.path + ' ' + f.name).toLowerCase().includes(q));
    const byPath = {};
    files.forEach((f) => (byPath[f.path] = byPath[f.path] || []).push(f));
    $('#lib-files').innerHTML = Object.entries(byPath).map(([p, fs]) => `<details class="vg" ${q ? 'open' : ''}><summary><b>${esc(p)}</b> <span class="meta">${fs.length}</span></summary>
      <ul class="list">${fs.map((f) => `<li>${ext(f.url, esc(prettyName(f.name)))}</li>`).join('')}</ul></details>`).join('') || '<div class="empty">No match.</div>';
  };
  body().innerHTML = `${notesLibraryCard(notesList)}<div class="grid g2" style="margin-bottom:16px"><div class="card"><h2>Official ETS material <span class="meta">(not in the Drive folder)</span></h2>
      <ul class="list">${lib.official.map((o) => `<li><div class="grow">${ext(o.url, esc(o.name))}<div class="meta">${esc(o.note)}</div></div>
        <span class="pill ${o.kind === 'Free' ? 'ok' : 'warn'}">${o.kind}</span></li>`).join('')}</ul>
      <div class="meta" style="margin-top:8px">Official questions are the closest to the real test. The three books are sold separately or together as the "Super Power Pack" on the ETS page.</div></div>
    <div class="card"><h2>Book order that works</h2><div class="meta" style="margin-bottom:6px">From ${esc(lib.order.who)} - ${ext(lib.order.source, 'their notes')}. The plan follows this order.</div>
      <ol class="notes">${lib.order.steps.map((x) => `<li>${esc(x)}</li>`).join('')}</ol></div></div>
    <div class="grid g2"><div class="card"><h2>Magoosh video lessons</h2><ul class="list">${lib.lessons.map((l) => `<li><div class="grow">${ext(l.url, esc(l.name))}</div><span class="meta">${l.count} videos</span></li>`).join('')}</ul></div>
    <div class="grid" style="align-content:start"><div class="card"><h2>Magoosh practice questions (with video solutions)</h2><ul class="list">${lib.practice.map((p) => `<li><div class="grow">${ext(p.url, esc(p.name))}</div>
      <span class="meta">${p.used} in plan · ${p.count - p.used} spare</span></li>`).join('')}</ul></div>
      <div class="card"><h2>Drive folders</h2><div class="row">${lib.folders.map((f) => ext(f.url, esc(f.name))).join(' · ')}</div>
      <div style="margin-top:8px">${ext(lib.root, 'Open the whole GRE folder in Drive')}</div></div></div></div>
    <div class="card" style="margin-top:16px"><div class="toolbar"><h2 style="margin:0">Books, notes and assignments</h2><span style="flex:1"></span><input id="lib-q" placeholder="Search e.g. probability, Manhattan, vocab" value="${esc(libQ)}" size="34"></div><div id="lib-files"></div></div>`;
  draw();
  bindStudy(body());
  $('#lib-q').oninput = (e) => { libQ = e.target.value; draw(); };
}

// ---------------------------------------------------------------- settings
async function greSettings() {
  const s = gre.ov.settings; const days = s.gre_days.split(',');
  const DN = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const st = gre.ov.status;
  body().innerHTML = `<div class="grid g2"><div class="grid" style="align-content:start">
    <div class="card"><h2>Study schedule</h2><div class="form-grid">
    <span>Start date</span><div><input type="date" id="g-start" value="${esc(s.gre_start)}"> <span class="meta">Day 1 lands on the first study day on or after this date.</span></div>
    <span>Study days</span><div class="row">${DN.map((d) => `<label><input type="checkbox" class="g-day" value="${d}" ${days.includes(d) ? 'checked' : ''}> ${d}</label>`).join('')}</div>
    <span>Class time</span><div><input type="time" id="g-time" value="${esc(s.gre_time)}"> <span class="meta">A Windows reminder pops up shortly before.</span></div>
    <span>Reminder</span><label><input type="checkbox" id="g-notify" ${s.gre_notify === '1' ? 'checked' : ''}> Remind me about each class</label>
    <span>Target scores</span><div class="row"><label>Quant <input type="number" id="g-tq" min="130" max="170" value="${esc(s.gre_target_q)}" style="width:72px"></label>
      <label>Verbal <input type="number" id="g-tv" min="130" max="170" value="${esc(s.gre_target_v)}" style="width:72px"></label><span class="meta">Used by the score predictor.</span></div>
    <span></span><div><button id="g-save">Save</button> <span class="meta">Plan currently ends ${fmtDate(st.end)}.</span></div></div></div>
    <div class="card"><h2>Fell behind?</h2><div>${st.behind ? `You are <b>${st.behind}</b> class${st.behind > 1 ? 'es' : ''} behind. Re-planning moves Day ${st.current} to today (or your next study day) and shifts every later class to match. Completed classes stay completed.`
      : 'You are on track. If you miss classes later, this button moves the next unfinished class to today and shifts the rest of the plan.'}</div>
      <button style="margin-top:10px" ${st.current ? '' : 'disabled'} onclick="greReplan()">Re-plan from today</button></div>
    <div class="card"><h2>Tips</h2><ul class="notes">
      <li>The plan is 100 classes. At 6 days a week it takes about 17 weeks; tick Sunday too and it takes about 14 weeks - handy if you want to test before you join ZS in January.</li>
      <li>Planning to test in April 2028 instead? Set the start date to 1 Nov 2027 — your progress stays as it is.</li>
      <li>Your existing "Light GRE/GMAT practice" habit (21:00) overlaps with these classes — you can pause it in Habits &amp; schedule.</li></ul></div></div>
    <div class="grid" style="align-content:start">
    <div class="card"><h2>Phone flashcards (same Wi-Fi)</h2><div id="phone"><div class="meta">Loading…</div></div></div>
    <div class="card"><h2>Your data</h2><div id="data"><div class="meta">Loading…</div></div></div></div></div>`;
  $('#g-save').onclick = async () => {
    const ds = [...document.querySelectorAll('.g-day:checked')].map((x) => x.value);
    if (!ds.length) return toast('Pick at least one study day');
    await post('/api/gre/settings', { gre_start: $('#g-start').value, gre_days: ds.join(','), gre_time: $('#g-time').value || '20:00', gre_notify: $('#g-notify').checked ? '1' : '0',
      gre_target_q: $('#g-tq').value || '165', gre_target_v: $('#g-tv').value || '155' });
    toast('Schedule saved'); views.gre();
  };
  drawPhone(await api('/api/gre/phone'));
  drawData(await api('/api/data/status'));
}
function drawPhone(p) {
  const el = $('#phone'); if (!el) return;
  el.innerHTML = `<label><input type="checkbox" id="ph-on" ${p.enabled ? 'checked' : ''}> Let my phone open the vocab flashcards over Wi-Fi</label>
    ${p.error ? `<div class="explain bad" style="margin-top:8px">${esc(p.error)}</div>` : ''}
    ${p.running && p.urls.length ? `<div class="row" style="margin-top:10px;align-items:flex-start">${p.qr ? `<img class="qr" src="${p.qr}" alt="QR code for the flashcard link">` : ''}
        <div class="grow"><div>Scan the code with your phone camera, or open:</div>${p.urls.map((u) => `<div class="mono" style="margin:4px 0"><b>${esc(u)}</b></div>`).join('')}
          <div class="meta" style="margin-top:6px">Works while this app is running and your phone is on the same Wi-Fi. Only the flashcards are shared - nothing else in the tracker.
            If Windows asks whether to allow Masters Tracker on the network, choose <b>Private networks</b> only.</div>
          <button class="ghost small" id="ph-new" style="margin-top:8px">Make a new link (old one stops working)</button></div></div>`
      : p.enabled ? '<div class="meta" style="margin-top:8px">Starting…</div>' : '<div class="meta" style="margin-top:8px">Off. When on, a QR code appears here for your phone. The link contains a secret code, so only someone with the link can open it.</div>'}`;
  $('#ph-on').onchange = async (e) => drawPhone(await post('/api/gre/phone', { enabled: e.target.checked }));
  const nw = $('#ph-new'); if (nw) nw.onclick = async () => drawPhone(await post('/api/gre/phone/token', {}));
}
function drawData(d) {
  const el = $('#data'); if (!el) return;
  const kb = (n) => `${Math.round(n / 1024)} KB`;
  el.innerHTML = `<div>Database check: ${d.health === 'ok' ? '<span class="pill ok">OK</span>' : `<span class="pill bad">${esc(d.health)}</span> - restore the latest backup below.`}</div>
    <div class="meta" style="margin:8px 0">A backup is made automatically every day (the last ${d.keep} are kept).</div>
    <ul class="list">${d.backups.map((b) => `<li><div class="grow mono">${esc(b.name)}</div><span class="meta">${kb(b.size)}</span></li>`).join('') || '<li class="empty">No backups yet.</li>'}</ul>
    ${d.onedrive ? `<label style="display:block;margin-top:8px"><input type="checkbox" id="od-on" ${d.onedrive_on ? 'checked' : ''}> Also keep a copy in OneDrive (syncs to the cloud, so a broken laptop does not lose your progress)</label>
      <div class="meta mono">${esc(d.onedrive)}</div>` : '<div class="meta" style="margin-top:8px">OneDrive is not set up on this PC, so backups stay on this laptop only.</div>'}
    <div class="row" style="margin-top:8px"><button class="small" id="bk-now">Back up now</button><button class="ghost small" id="bk-open">Open backups folder</button></div>
    <div class="meta" style="margin-top:8px">To restore: quit Masters Tracker from the tray, copy a backup over <span class="mono">tracker.db</span> in the folder above the backups, then start the app.</div>`;
  $('#bk-now').onclick = async () => { const r = await post('/api/data/backup', {}); toast(r.ok ? 'Backup saved' : (r.error || 'Backup failed')); drawData(await api('/api/data/status')); };
  $('#bk-open').onclick = () => post('/api/data/open', {});
  const od = $('#od-on'); if (od) od.onchange = async (e) => drawData(await post('/api/data/onedrive', { enabled: e.target.checked }));
}
