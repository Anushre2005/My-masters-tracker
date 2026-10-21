'use strict';
// Study notes ("tuition handouts"): topic-wise reading shown first in each class - rules, worked examples revealed step
// by step, traps and quick checks - plus revision sheets on review days, a notes library and printable pages.
// Uses helpers from app.js ($, esc, api, toast) and gre.js (gre, body, ext).

const notesState = { open: null };

function blockHtml(b, key) {
  switch (b.t) {
    case 'h': return `<h3 class="sn-h">${esc(b.text)}</h3>`;
    case 'h2': return `<h4 class="sn-h2">${esc(b.text)}</h4>`;
    case 'p': return `<p class="sn-p">${esc(b.text)}</p>`;
    case 'rule': return `<div class="sn-rule">${esc(b.text)}</div>`;
    case 'tip': return `<div class="sn-tip"><b>Tip</b> ${esc(b.text)}</div>`;
    case 'trap': return `<div class="sn-trap"><b>Trap</b> ${esc(b.text)}</div>`;
    case 'list': return `<ul class="sn-list">${b.items.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`;
    case 'table': return `<div class="tablewrap"><table class="sn-table"><thead><tr>${b.head.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead>
      <tbody>${b.rows.map((r) => `<tr>${r.map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    case 'ex': return `<div class="sn-ex" data-ex="${key}"><div class="lab">Worked example - try it yourself first</div><div class="q">${esc(b.q)}</div>
      <ol class="ex-steps">${b.steps.map((s, i) => `<li data-st="${i}" hidden>${esc(s)}</li>`).join('')}</ol>
      <div class="ans" hidden><b>Answer:</b> ${esc(b.a)}</div>
      <div class="row"><button class="small ghost" data-next>Show the first step</button><button class="small ghost" data-all>Show all</button></div></div>`;
    case 'check': return `<details class="sn-check"><summary><b>Check yourself:</b> ${esc(b.q)}</summary><div class="ans">${esc(b.a)}</div></details>`;
    default: return '';
  }
}
function blocksHtml(blocks, prefix) { return blocks.map((b, i) => blockHtml(b, `${prefix}-${i}`)).join(''); }

function noteHtml(n, open = true) {
  return `<details class="sn-note" ${open ? 'open' : ''}><summary><b>${esc(n.title)}</b> <span class="meta">· about ${n.minutes} min</span></summary>
    <div class="sn-body">${blocksHtml(n.blocks, n.id)}</div></details>`;
}
function sheetHtml(s) {
  return `<div class="sn-sheet"><div class="meta" style="margin-bottom:6px">${esc(s.title)} - the rules, traps and quick checks from the topics you are revising. Answer the checks before you open them.</div>
    ${s.sections.map((x) => `<details class="sn-note"><summary><b>${esc(x.title)}</b> <a class="ext small-link" href="#" data-note="${x.id}">full notes</a></summary>
      <div class="sn-body">${blocksHtml(x.blocks, 's-' + x.id)}</div></details>`).join('')}</div>`;
}

// the first step of a class: today's study material
function studyHtml(d) {
  const s = d.study || {};
  const key = d.notes.length ? `<div class="sn-key"><div class="meta" style="margin-bottom:4px">TODAY'S KEY POINTS</div><ul class="notes">${d.notes.map((x) => `<li>${esc(x)}</li>`).join('')}</ul></div>` : '';
  const mins = (s.notes || []).reduce((a, n) => a + n.minutes, 0) + (s.sheet ? s.sheet.minutes : 0);
  return `<div class="meta" style="margin-bottom:8px">Read this first (${mins ? `about ${mins} minutes` : 'short'}). Try every worked example before revealing its steps, and answer the
      "Check yourself" questions in your head before opening them. Then do the tutor session and solve the sums below.</div>
    ${(s.notes || []).map((n, i) => noteHtml(n, i === 0)).join('')}${s.sheet ? sheetHtml(s.sheet) : ''}${key}`;
}

// worked examples reveal one step at a time; links inside sheets open the full note
function bindStudy(root) {
  root.querySelectorAll('[data-ex]').forEach((ex) => {
    const steps = [...ex.querySelectorAll('[data-st]')]; const ans = ex.querySelector('.ans');
    const nb = ex.querySelector('[data-next]'); const ab = ex.querySelector('[data-all]');
    const done = () => { ans.hidden = false; nb.hidden = true; ab.hidden = true; };
    nb.onclick = () => {
      const next = steps.find((s) => s.hidden);
      if (next) { next.hidden = false; nb.textContent = steps.some((s) => s.hidden) ? 'Next step' : 'Show the answer'; } else done();
      if (!steps.length) done();
    };
    ab.onclick = () => { steps.forEach((s) => { s.hidden = false; }); done(); };
  });
  root.querySelectorAll('[data-note]').forEach((a) => a.onclick = (e) => { e.preventDefault(); openNote(a.dataset.note); });
}

// ---------------------------------------------------------------- notes library (Library tab) and single-note view
async function openNote(id) {
  notesState.open = id;
  if (current !== 'gre' || gre.tab !== 'library') { gre.tab = 'library'; return current !== 'gre' ? go('gre') : views.gre(); }
  drawNote();
}
async function drawNote() {
  const n = await api('/api/gre/notes/' + notesState.open);
  body().innerHTML = `<div class="row" style="margin-bottom:12px"><button class="ghost small" id="nt-back">← Library</button><h2 style="margin:0">${esc(n.title)}</h2>
      <span class="meta">about ${n.minutes} min</span><span style="flex:1"></span>${ext('/gre/notes/' + n.id, 'Print / save as PDF')}</div>
    <div class="card sn-single">${blocksHtml(n.blocks, n.id)}</div>`;
  $('#nt-back').onclick = () => { notesState.open = null; greLibrary(); window.scrollTo(0, 0); };
  bindStudy(body()); window.scrollTo(0, 0);
}
function notesLibraryCard(list) {
  const group = (s, title) => {
    const xs = list.filter((x) => x.subject === s);
    return xs.length ? `<div class="meta" style="margin:10px 0 4px">${title.toUpperCase()}</div><ul class="list">${xs.map((x) => `<li><div class="grow"><a href="#" class="linkish" data-note="${x.id}">${esc(x.title)}</a>
      <div class="meta">${x.days.length ? 'Day ' + x.days.join(', ') : 'Revision'} · about ${x.minutes} min</div></div>${ext('/gre/notes/' + x.id, 'PDF')}</li>`).join('')}</ul>` : '';
  };
  return `<div class="card" style="margin-bottom:16px"><div class="row"><h2 style="margin:0">Study notes <span class="meta">(${list.length} topics - written for this course)</span></h2><span style="flex:1"></span>
      ${ext('/gre/notes/all?subject=quant', 'All quant notes as one PDF')} · ${ext('/gre/notes/all?subject=verbal', 'All verbal notes as one PDF')}</div>
    <div class="grid g2">${'<div>' + group('quant', 'Quant') + '</div><div>' + group('verbal', 'Verbal') + group('writing', 'Analytical Writing') + group('strategy', 'Strategy & test day') + '</div>'}</div></div>`;
}
