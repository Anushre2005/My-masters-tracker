'use strict';
// GRE "Test results" tab: add screenshots of a practice-test result (ETS mini quiz, POWERPREP, Magoosh, Manhattan…),
// the app reads them (offline OCR + local AI), you check and correct the results, then they feed the score list,
// predictor, weak topics, Error log and tutor. Uses helpers from app.js and gre.js (gre, body, views, esc, api, post, del, toast).

const res = { meta: null, draft: null, files: [], prefill: {} };

// open the tab with some fields filled in (from a class day or a mock step)
function greAddResult(prefill = {}) { res.prefill = prefill; res.draft = null; res.files = []; gre.tab = 'results'; if (current !== 'gre') go('gre'); else views.gre(); }

async function greResults() {
  const m = res.meta = await api('/api/gre/results');
  if (res.draft) return drawResultReview();
  const p = res.prefill;
  const dayN = p.day ?? (gre.ov && gre.ov.status.current);
  const accPill = (s) => { if (!s) return ''; const [c, t] = s.split('/').map(Number); const pc = Math.round(100 * c / t); return `<span class="pill ${pc >= 80 ? 'ok' : pc >= 60 ? 'warn' : 'bad'}">${s}</span>`; };
  const topics = Object.entries(m.topics).map(([k, v]) => ({ key: k, ...v })).sort((a, b) => a.pct - b.pct);
  body().innerHTML = `<div class="grid g2"><div class="card"><h2>Add a test result</h2>
      <div class="meta" style="margin-bottom:8px">Screenshot the score / analysis page of any practice test or quiz (ETS mini quiz, POWERPREP, Magoosh, Manhattan, a book set…).
        Add every page of the analysis. The app reads them on your laptop - nothing is uploaded anywhere.</div>
      <div id="drop" class="drop">Drop screenshots here, <b>paste</b> one with Ctrl+V, or <label class="linkish">choose files<input type="file" id="r-files" accept="image/*" multiple hidden></label></div>
      <div id="r-thumbs" class="thumbs"></div>
      <div class="form-grid" style="margin-top:10px;max-width:none">
        <span>Test name</span><input id="r-name" value="${esc(p.name || '')}" placeholder="e.g. ETS mini quiz, POWERPREP 1, Magoosh mock 2">
        <span>From</span>${select(['', ...m.sources], p.source || '', 'id="r-source"')}
        <span>Type</span>${select(['', ...m.kinds], p.kind || '', 'id="r-kind"')}
        <span>Plan day</span><input id="r-day" type="number" min="1" max="${gre.ov ? gre.ov.status.total : 100}" value="${esc(dayN ?? '')}" style="width:90px">
        <span></span><div class="row"><button id="r-scan" disabled>Read the screenshots</button><button class="ghost small" id="r-manual">Enter results by hand instead</button></div></div>
      <div id="r-status"></div></div>
    <div class="card"><h2>How results are used</h2><ul class="notes">
      <li><b>Scores</b> (Quant / Verbal / AWA) go to your practice-test list on the Progress tab.</li>
      <li><b>Every question</b> counts in the score predictor - official ETS questions count 1.5×.</li>
      <li><b>Topics</b> you miss show up as weak spots in the Quant / Verbal course, and the AI tutor is told about them.</li>
      <li><b>Wrong questions</b> go to the Error log with a redo date, so you revisit them from the test's review screen.</li>
      <li>Reading takes ~1-3 minutes (OCR + your local AI). Always check the numbers before saving - OCR can misread.</li></ul></div></div>
    <div class="card" style="margin-top:16px"><h2>Your test results</h2>
      ${m.results.length ? `<table><thead><tr><th>Date</th><th>Test</th><th>Q</th><th>V</th><th>AWA</th><th>Quant right</th><th>Verbal right</th><th></th></tr></thead><tbody>
        ${m.results.map((r) => `<tr><td style="white-space:nowrap">${fmtDate(r.date)}</td><td><b>${esc(r.name)}</b><div class="meta">${esc([r.source, r.kind, r.day ? 'day ' + r.day : ''].filter(Boolean).join(' · '))}</div></td>
          <td><b>${r.quant ?? ''}</b></td><td><b>${r.verbal ?? ''}</b></td><td>${r.awa ?? ''}</td><td>${accPill(r.quant_acc)}</td><td>${accPill(r.verbal_acc)}</td>
          <td style="white-space:nowrap">${r.images.map((im) => `<a class="ext" href="/api/gre/results/${r.id}/img/${im}" target="_blank" rel="noopener">📷</a>`).join(' ')}
            <button class="ghost small" data-edit="${r.id}">Edit</button> <button class="danger small" data-rdel="${r.id}">×</button></td></tr>`).join('')}</tbody></table>`
        : '<div class="empty">No results yet. Start with the ETS mini quiz from Day 1.</div>'}</div>
    ${topics.length ? `<div class="card" style="margin-top:16px"><h2>Accuracy by topic in your tests <span class="meta">(weakest first)</span></h2><table><tbody>${topics.map((t) => `<tr>
        <td>${esc(t.title)} <span class="pill">${t.subject === 'quant' ? 'Q' : 'V'}</span></td><td style="width:40%"><div class="bar"><i style="width:${t.pct}%;background:${t.pct >= 80 ? 'var(--ok)' : t.pct >= 60 ? 'var(--warn)' : 'var(--bad)'}"></i></div></td>
        <td style="text-align:right">${t.correct}/${t.total}</td><td><button class="ghost small" data-learn="${t.key}">Learn</button></td></tr>`).join('')}</tbody></table></div>` : ''}`;
  const addFiles = (fs) => {
    for (const f of fs) if (f.type.startsWith('image/')) res.files.push(f);
    drawThumbs();
  };
  $('#r-files').onchange = (e) => addFiles(e.target.files);
  const drop = $('#drop');
  drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('on'); };
  drop.ondragleave = () => drop.classList.remove('on');
  drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove('on'); addFiles(e.dataTransfer.files); };
  document.onpaste = (e) => {
    if (gre.tab !== 'results' || current !== 'gre' || res.draft) return;
    const fs = [...(e.clipboardData || {}).items || []].filter((i) => i.type.startsWith('image/')).map((i) => {
      const f = i.getAsFile(); return new File([f], `pasted-${Date.now()}.png`, { type: f.type });
    });
    if (fs.length) { e.preventDefault(); addFiles(fs); toast('Screenshot pasted'); }
  };
  drawThumbs();
  $('#r-scan').onclick = scanResult;
  $('#r-manual').onclick = () => {
    res.draft = { id: null, images: [], name: $('#r-name').value, source: $('#r-source').value, kind: $('#r-kind').value, day: +$('#r-day').value || null,
      date: isoToday(), quant: null, verbal: null, awa: null, sections: [], questions: [], manual: true };
    drawResultReview();
  };
  body().querySelectorAll('[data-edit]').forEach((b) => b.onclick = async () => { res.draft = await api('/api/gre/results/' + b.dataset.edit); drawResultReview(); window.scrollTo(0, 0); });
  body().querySelectorAll('[data-rdel]').forEach((b) => b.onclick = async () => {
    if (!confirm('Delete this result? Its scores and its open Error-log entries are removed too.')) return;
    await del('/api/gre/results/' + b.dataset.rdel); greResults();
  });
  body().querySelectorAll('[data-learn]').forEach((b) => b.onclick = () => openLesson(b.dataset.learn));
}
function drawThumbs() {
  const el = $('#r-thumbs'); if (!el) return;
  el.innerHTML = res.files.map((f, i) => `<div class="thumb"><img src="${URL.createObjectURL(f)}" alt="Screenshot ${i + 1}"><button class="danger small" data-rm="${i}">×</button></div>`).join('');
  el.querySelectorAll('[data-rm]').forEach((b) => b.onclick = () => { res.files.splice(+b.dataset.rm, 1); drawThumbs(); });
  const sc = $('#r-scan'); if (sc) { sc.disabled = !res.files.length; sc.textContent = res.files.length ? `Read ${res.files.length} screenshot${res.files.length > 1 ? 's' : ''}` : 'Read the screenshots'; }
}
async function scanResult() {
  const fd = new FormData();
  res.files.forEach((f) => fd.append('images', f, f.name || 'screenshot.png'));
  fd.append('name', $('#r-name').value); fd.append('source', $('#r-source').value); fd.append('kind', $('#r-kind').value); fd.append('day', $('#r-day').value);
  $('#r-scan').disabled = true;
  $('#r-status').innerHTML = '<div class="explain warn" style="margin-top:10px">Reading the screenshots (text recognition, then your local AI) - this takes 1-3 minutes…</div>';
  try {
    const r = await fetch('/api/gre/results/scan', { method: 'POST', body: fd });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || 'Upload failed');
    res.draft = d; res.files = [];
    if (current === 'gre' && gre.tab === 'results') { drawResultReview(); window.scrollTo(0, 0); } else toast('Results read - open GRE Prep → Test results to check them');
  } catch (e) {
    $('#r-status').innerHTML = `<div class="explain bad" style="margin-top:10px">${esc(e.message)}</div>`; $('#r-scan').disabled = false;
  }
}

// ---------------------------------------------------------------- review & correct, then save
function drawResultReview() {
  const d = res.draft; const m = res.meta;
  const chOpts = (sec, val) => `<select class="q-ch"><option value="">(topic)</option>${m.chapters.filter((c) => !sec || c.subject === sec.toLowerCase()).map((c) =>
    `<option value="${c.key}" ${c.key === val ? 'selected' : ''}>${esc(c.title)}</option>`).join('')}</select>`;
  const resSel = (v) => `<select class="q-ok"><option value="1" ${v === true ? 'selected' : ''}>Right</option><option value="0" ${v === false ? 'selected' : ''}>Wrong</option><option value="" ${v === null || v === undefined ? 'selected' : ''}>Not answered / unknown</option></select>`;
  const right = d.questions.filter((q) => q.correct === true).length; const wrong = d.questions.filter((q) => q.correct === false).length;
  body().innerHTML = `<div class="row" style="margin-bottom:12px"><button class="ghost small" id="rv-back">← Test results</button>
      <h2 style="margin:0">${d.manual ? 'Enter the results' : 'Check what was read'}</h2><span class="meta">Fix anything wrong, then save.</span></div>
    ${(d.errors || []).map((e) => `<div class="explain bad">${esc(e)}</div>`).join('')}${d.ai_error ? `<div class="explain warn">${esc(d.ai_error)}</div>` : ''}
    <div class="grid g2"><div class="card"><h2>Test and scores</h2><div class="form-grid" style="max-width:none">
        <span>Test name</span><input id="v-name" value="${esc(d.name || '')}">
        <span>Date taken</span><input id="v-date" type="date" value="${esc(d.date || isoToday())}">
        <span>From</span>${select(['', ...m.sources], d.source || '', 'id="v-source"')}
        <span>Type</span>${select(['', ...m.kinds], d.kind || '', 'id="v-kind"')}
        <span>Plan day</span><input id="v-day" type="number" value="${esc(d.day ?? '')}" style="width:90px">
        <span>Scaled scores</span><div class="row"><label>Quant <input id="v-q" type="number" min="130" max="170" value="${esc(d.quant ?? '')}" style="width:76px"></label>
          <label>Verbal <input id="v-v" type="number" min="130" max="170" value="${esc(d.verbal ?? '')}" style="width:76px"></label>
          <label>AWA <input id="v-a" type="number" step="0.5" min="0" max="6" value="${esc(d.awa ?? '')}" style="width:64px"></label></div>
        <span></span><span class="meta">Leave scores empty for quizzes and question sets that do not give a 130-170 score.</span>
        <span>Notes</span><input id="v-notes" value="${esc(d.notes || '')}" placeholder="How it felt, timing problems, what to fix"></div></div>
      <div class="card"><h2>Screenshots</h2>${d.images.length && d.id ? `<div class="thumbs">${d.images.map((im) => `<a href="/api/gre/results/${d.id}/img/${im}" target="_blank" rel="noopener" class="thumb"><img src="/api/gre/results/${d.id}/img/${im}" alt="${esc(im)}"></a>`).join('')}</div>` : '<div class="meta">None - entered by hand.</div>'}
        ${d.ocr ? `<details style="margin-top:8px"><summary>Text read from the screenshots</summary><pre class="ocr">${esc(d.ocr)}</pre></details>` : ''}</div></div>
    <div class="card" style="margin-top:16px"><div class="row"><h2 style="margin:0">Questions</h2><span class="meta">${d.questions.length} questions · ${right} right · ${wrong} wrong</span><span style="flex:1"></span>
        <label class="meta">Add <input id="v-addn" type="number" min="1" max="60" value="${d.questions.length ? 1 : 10}" style="width:56px"></label>
        ${select(['Quant', 'Verbal'], 'Quant', 'id="v-addsec"')}<button class="ghost small" id="v-add">Add questions</button></div>
      <div class="meta" style="margin:6px 0 10px">One row per question. "Right / Wrong" is what matters most; topic and time make the analysis better. Wrong questions go to your Error log.</div>
      ${d.questions.length ? `<div class="tablewrap"><table id="v-qs"><thead><tr><th>#</th><th>Section</th><th>Type</th><th>Topic</th><th>Result</th><th>Seconds</th><th></th></tr></thead><tbody>
        ${d.questions.map((q, i) => `<tr data-i="${i}"><td><input class="q-n" type="number" value="${esc(q.n)}" style="width:56px"></td>
          <td>${select(['Quant', 'Verbal'], q.section || 'Quant', 'class="q-sec"')}</td><td>${select(['', ...m.types], q.type || '', 'class="q-type"')}</td>
          <td>${chOpts(q.section, q.chapter)}</td><td>${resSel(q.correct)}</td><td><input class="q-s" type="number" min="0" value="${esc(q.seconds ?? '')}" style="width:72px"></td>
          <td><button class="danger small" data-qrm="${i}">×</button></td></tr>`).join('')}</tbody></table></div>`
        : '<div class="empty">No questions read. If the page lists questions, add them here (or just save the scores).</div>'}</div>
    <div class="row" style="margin-top:12px"><button id="v-save">Save results</button><button class="ghost" id="v-cancel">Cancel</button>
      <span class="meta">${d.id ? 'Saving replaces this result\'s earlier scores and open Error-log entries.' : ''}</span></div>`;
  const collect = () => {
    const rows = [...body().querySelectorAll('#v-qs tbody tr')];
    d.questions = rows.map((tr) => {
      const ok = tr.querySelector('.q-ok').value;
      return { n: +tr.querySelector('.q-n').value || null, section: tr.querySelector('.q-sec').value, type: tr.querySelector('.q-type').value,
        chapter: tr.querySelector('.q-ch').value, correct: ok === '' ? null : ok === '1', seconds: tr.querySelector('.q-s').value === '' ? null : +tr.querySelector('.q-s').value,
        difficulty: d.questions[+tr.dataset.i] ? d.questions[+tr.dataset.i].difficulty : null };
    });
    Object.assign(d, { name: $('#v-name').value, date: $('#v-date').value, source: $('#v-source').value, kind: $('#v-kind').value, day: +$('#v-day').value || null,
      quant: $('#v-q').value || null, verbal: $('#v-v').value || null, awa: $('#v-a').value === '' ? null : $('#v-a').value, notes: $('#v-notes').value });
  };
  const leave = () => { res.draft = null; res.prefill = {}; greResults(); window.scrollTo(0, 0); };
  $('#rv-back').onclick = leave; $('#v-cancel').onclick = leave;
  // a section change re-filters the topic list
  body().querySelectorAll('.q-sec').forEach((s) => s.onchange = () => { collect(); drawResultReview(); });
  body().querySelectorAll('.q-ok').forEach((s) => s.onchange = () => { collect(); drawResultReview(); });
  body().querySelectorAll('[data-qrm]').forEach((b) => b.onclick = () => { collect(); d.questions.splice(+b.dataset.qrm, 1); drawResultReview(); });
  $('#v-add').onclick = () => {
    collect();
    const k = Math.max(1, Math.min(60, +$('#v-addn').value || 1)); const sec = $('#v-addsec').value;
    let n = d.questions.reduce((a, q) => Math.max(a, q.n || 0), 0);
    for (let j = 0; j < k; j++) d.questions.push({ n: ++n, section: sec, type: '', chapter: '', correct: true, seconds: null, difficulty: null });
    drawResultReview();
  };
  $('#v-save').onclick = async () => {
    collect();
    if (!d.name.trim()) return toast('Give the test a name');
    $('#v-save').disabled = true;
    if (!d.id) {  // entered by hand: create the record first (no screenshots)
      d.id = (await post('/api/gre/results/manual', { name: d.name, source: d.source, kind: d.kind, day: d.day })).id;
    }
    const r = await post('/api/gre/results/' + d.id, d);
    if (!r.ok) { $('#v-save').disabled = false; return toast(r.error || 'Could not save'); }
    toast(`Saved${r.errors_added ? ` - ${r.errors_added} wrong question${r.errors_added > 1 ? 's' : ''} added to the Error log` : ''}`);
    const pd = d.day && gre.ov ? gre.ov.days.find((x) => x.day === d.day) : null;
    if (pd && pd.mock) await post('/api/gre/day/' + d.day, { parts: { mock: true } });  // the mock step is done once its result is in
    leave();
  };
}
