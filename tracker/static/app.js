'use strict';
const $ = (s, el = document) => el.querySelector(s);
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const api = async (url, opts = {}) => {
  const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts,
    body: opts.body && typeof opts.body !== 'string' ? JSON.stringify(opts.body) : opts.body });
  return r.json();
};
const patch = (url, body) => api(url, { method: 'PATCH', body });
const post = (url, body) => api(url, { method: 'POST', body });
const del = (url) => api(url, { method: 'DELETE' });

const STATUSES = ['Not started', 'In progress', 'Waiting', 'Done', 'N/A'];
const APP_STATUSES = ['Not started', 'Drafting', 'Submitted', 'Interview', 'Admit', 'Waitlist', 'Reject', 'Withdrawn', 'Not applying'];
const RQ_STATUSES = ['Not started', 'In progress', 'Verified - add to Programs', 'Dropped', 'Not eligible'];

function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2600); }
function fmtDate(s, opts = { day: '2-digit', month: 'short', year: 'numeric' }) { if (!s) return ''; const d = new Date(s + 'T00:00'); return d.toLocaleDateString('en-GB', opts); }
function isoToday() { const d = new Date(); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); }
function addDays(iso, n) { const d = new Date(iso + 'T00:00'); d.setDate(d.getDate() + n); return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); }
function daysPill(n) {
  if (n === null || n === undefined) return '';
  if (n < 0) return `<span class="pill bad">${-n} d overdue</span>`;
  if (n === 0) return '<span class="pill warn">today</span>';
  if (n <= 14) return `<span class="pill warn">${n} d</span>`;
  return `<span class="pill">${n} d</span>`;
}
const prioPill = (p) => p === 'High' ? '<span class="pill bad">High</span>' : p === 'Medium' ? '<span class="pill warn">Med</span>' : `<span class="pill">${esc(p || 'Low')}</span>`;
const select = (opts, val, attrs = '') => `<select ${attrs}>${opts.map((o) => `<option ${o === val ? 'selected' : ''}>${esc(o)}</option>`).join('')}</select>`;

// ---------------------------------------------------------------- router
const views = {};
let current = 'today';
function go(v) {
  current = v;
  document.querySelectorAll('nav a').forEach((a) => a.classList.toggle('active', a.dataset.view === v));
  location.hash = v;
  views[v]();
}
document.querySelectorAll('nav a').forEach((a) => a.addEventListener('click', () => go(a.dataset.view)));
$('#brand-date').textContent = new Date().toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
$('#sync-btn').addEventListener('click', async () => {
  toast('Syncing to Excel...');
  const r = await post('/api/sync_excel', {});
  toast(r.ok ? `Excel updated (${r.rows_written} rows). Backup saved.` : r.error);
});

// ---------------------------------------------------------------- Today
let todayDate = isoToday();
views.today = async () => {
  const s = await api('/api/today?date=' + todayDate);
  const isToday = todayDate === isoToday();
  const items = [
    ...s.sessions.map((x) => ({ t: x.start, html: sessionRow(x) })),
    ...s.reminders.map((r) => ({ t: r.time, html: `<li><span class="time">${esc(r.time)}</span><span class="pill acc">Reminder</span><div class="grow">${esc(r.title)}</div></li>` })),
  ].sort((a, b) => a.t.localeCompare(b.t));
  const ph = s.phase; const fd = s.first_deadline; const w = s.week;
  $('#view').innerHTML = `
    <div class="row" style="justify-content:space-between">
      <div><h1>${isToday ? 'Today' : fmtDate(todayDate, { weekday: 'long', day: 'numeric', month: 'long' })}</h1>
      <div class="sub">${fmtDate(todayDate, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}</div></div>
      <div class="row"><button class="ghost small" data-d="-1">&larr; Prev</button>
      ${isToday ? '' : '<button class="ghost small" data-d="0">Today</button>'}
      <button class="ghost small" data-d="1">Next &rarr;</button></div>
    </div>
    <div class="grid g4" style="margin-bottom:16px">
      <div class="card stat"><div class="l">Current phase</div><div class="n" style="font-size:18px">${esc(ph ? ph.name : '—')}</div><div class="x">${ph ? ph.days_left + ' days left in phase' : ''}</div></div>
      <div class="card stat"><div class="l">First application date</div><div class="n">${fd ? fd.days : '—'}<span style="font-size:13px;font-weight:400"> days</span></div><div class="x">${fd ? esc(fd.program) + ' · ' + fmtDate(fd.date) : ''}</div></div>
      <div class="card stat"><div class="l">Overdue tasks</div><div class="n" style="color:${s.overdue.length ? 'var(--bad)' : 'inherit'}">${s.overdue.length}</div><div class="x">${s.due_soon.length} due in next 14 days</div></div>
      <div class="card stat"><div class="l">Habits this week</div><div class="n">${w.done}/${w.planned}</div><div class="bar" style="margin-top:6px"><i style="width:${w.planned ? Math.round(100 * w.done / w.planned) : 0}%"></i></div></div>
    </div>
    <div class="grid g2">
      <div class="card"><h2>Schedule</h2>
        <ul class="list">${items.map((i) => i.html).join('') || '<li class="empty">Nothing scheduled.</li>'}</ul>
        ${ph ? `<details style="margin-top:10px"><summary>Phase milestones</summary><p>${esc(ph.milestones)}</p></details>` : ''}
      </div>
      <div class="grid" style="align-content:start">
        ${typeof greTodayCard === 'function' ? greTodayCard(s.gre) : ''}
        <div class="card"><h2>Tasks to work on</h2>
          <ul class="list">${s.next_tasks.map(taskRow).join('') || '<li class="empty">All clear.</li>'}</ul>
          <button class="ghost small" onclick="go('tasks')" style="margin-top:8px">All tasks</button></div>
        <div class="card"><h2>Coming up</h2>
          <ul class="list">${s.upcoming.map((e) => `<li><span class="time">${fmtDate(e.date)}</span><div class="grow">${esc(e.title)}<div class="meta">${esc(e.type)}</div></div>${daysPill(Math.round((new Date(e.date) - new Date(isoToday())) / 864e5))}</li>`).join('')}</ul></div>
      </div>
    </div>`;
  $('#view').querySelectorAll('[data-d]').forEach((b) => b.onclick = () => { todayDate = b.dataset.d === '0' ? isoToday() : addDays(todayDate, +b.dataset.d); views.today(); });
  bindChecks(views.today);
};
function sessionRow(x) {
  const routine = x.kind === 'routine';
  return `<li class="${routine ? 'routine' : ''}">
    <span class="time">${esc(x.start)}–${esc(x.end)}</span>
    ${routine ? '<span class="pill">Routine</span>' : `<button class="check ${x.done ? 'on' : ''}" data-habit="${esc(x.id)}" data-date="${esc(x.date)}" data-done="${x.done ? 1 : 0}" title="Mark done">${x.done ? '✓' : ''}</button>`}
    <div class="grow"><span class="${x.done ? 'done-text' : ''}">${esc(x.name)}</span><div class="meta">${esc(x.details || '')}</div></div></li>`;
}
function taskRow(t) {
  return `<li><button class="check" data-task="${esc(t.id)}" title="Mark done"></button>
    <div class="grow">${esc(t.title)}<div class="meta">${esc(t.program || t.category || '')} · due ${fmtDate(t.due)} · ${esc(t.status)}</div></div>
    ${prioPill(t.priority)} ${daysPill(t.days_left)}</li>`;
}
function bindChecks(refresh) {
  document.querySelectorAll('[data-habit]').forEach((b) => b.onclick = async () => {
    await post('/api/habit_log', { habit_id: b.dataset.habit, date: b.dataset.date, done: b.dataset.done !== '1' });
    refresh();
  });
  document.querySelectorAll('[data-task]').forEach((b) => b.onclick = async () => {
    await patch('/api/tasks/' + b.dataset.task, { status: 'Done' }); toast('Marked done'); refresh();
  });
}

// ---------------------------------------------------------------- Upcoming
let calRange = 120, calType = 'All';
views.calendar = async () => {
  const ev = await api('/api/calendar?days=' + calRange);
  const types = ['All', ...new Set(ev.map((e) => e.type))];
  const list = ev.filter((e) => calType === 'All' || e.type === calType);
  let html = '', month = '';
  for (const e of list) {
    const m = fmtDate(e.date, { month: 'long', year: 'numeric' });
    if (m !== month) { if (month) html += '</ul></div>'; html += `<div class="month">${m}</div><div class="card"><ul class="list">`; month = m; }
    const days = Math.round((new Date(e.date) - new Date(isoToday())) / 864e5);
    html += `<li><span class="time">${fmtDate(e.date, { weekday: 'short', day: '2-digit', month: 'short' })}</span>
      <div class="grow">${esc(e.title)}<div class="meta">${esc(e.type)}${e.program ? ' · ' + esc(e.program) : ''}</div></div>
      ${e.kind === 'key_date' ? `<button class="ghost small" data-kd="${e.id}">Done</button>` : ''}
      ${e.link ? `<a class="ext" href="${esc(e.link)}" target="_blank" rel="noopener">Open</a>` : ''} ${daysPill(days)}</li>`;
  }
  if (month) html += '</ul></div>';
  $('#view').innerHTML = `<h1>Upcoming</h1><div class="sub">Key dates, programme deadlines, planned submissions and task due dates.</div>
    <div class="toolbar">Range ${select(['30', '60', '120', '365', '1000'], String(calRange), 'id="cal-range"')} days
    &nbsp; Type ${select(types, calType, 'id="cal-type"')}</div>${html || '<div class="empty">Nothing in this range.</div>'}`;
  $('#cal-range').onchange = (e) => { calRange = +e.target.value; views.calendar(); };
  $('#cal-type').onchange = (e) => { calType = e.target.value; views.calendar(); };
  document.querySelectorAll('[data-kd]').forEach((b) => b.onclick = async () => { await patch('/api/key_dates/' + b.dataset.kd, { done: 1 }); views.calendar(); });
};

// ---------------------------------------------------------------- Tasks
const tf = { scope: 'open', program: 'All', status: 'All', q: '' };
views.tasks = async () => {
  const all = await api('/api/tasks');
  const programs = ['All', 'Common tasks', ...new Set(all.filter((t) => t.program).map((t) => t.program))];
  $('#view').innerHTML = `<h1>Tasks</h1><div class="sub">${all.length} tasks · programme task dates move automatically when you change a planned submit date.</div>
    <div class="toolbar">
      ${select(['open', 'all', 'overdue', 'next 30 days'], tf.scope, 'id="f-scope"')}
      ${select(programs, tf.program, 'id="f-prog"')}
      ${select(['All', ...STATUSES], tf.status, 'id="f-status"')}
      <input id="f-q" placeholder="Search…" value="${esc(tf.q)}">
      <span style="flex:1"></span>
      <details><summary><b>+ Add task</b></summary>
        <div class="row" style="margin-top:8px"><input id="n-title" placeholder="Task" size="34"><input id="n-due" type="date">
        ${select(['High', 'Medium', 'Low'], 'Medium', 'id="n-prio"')}<input id="n-cat" placeholder="Category" size="10" value="Personal"><button id="n-add">Add</button></div></details>
    </div>
    <div class="card tablewrap"><table><thead><tr><th>ID</th><th>For</th><th>Task</th><th>Due</th><th></th><th>Priority</th><th>Status</th><th>Notes</th></tr></thead><tbody id="tbody"></tbody></table></div>`;
  const render = () => {
    const q = tf.q.toLowerCase();
    const rows = all.filter((t) => {
      if (tf.scope === 'open' && !t.open) return false;
      if (tf.scope === 'overdue' && !(t.open && t.days_left < 0)) return false;
      if (tf.scope === 'next 30 days' && !(t.open && t.days_left !== null && t.days_left <= 30)) return false;
      if (tf.program === 'Common tasks' && t.scope !== 'common') return false;
      if (!['All', 'Common tasks'].includes(tf.program) && t.program !== tf.program) return false;
      if (tf.status !== 'All' && t.status !== tf.status) return false;
      if (q && !(`${t.title} ${t.details || ''} ${t.category || ''} ${t.program || ''}`.toLowerCase().includes(q))) return false;
      return true;
    }).sort((a, b) => (a.due || '9999').localeCompare(b.due || '9999'));
    $('#tbody').innerHTML = rows.map((t) => `<tr class="${t.open ? '' : 'is-done'}" data-id="${esc(t.id)}">
      <td>${esc(t.id)}</td><td>${esc(t.program || t.category || '')}</td>
      <td style="max-width:420px">${esc(t.title)}${t.details ? `<div class="meta">${esc(t.details)}</div>` : ''}${t.link ? ` <a class="ext" target="_blank" rel="noopener" href="${esc(t.link)}">link</a>` : ''}</td>
      <td>${t.scope === 'common' ? `<input type="date" class="t-due" value="${esc(t.due_date || '')}">` : `${fmtDate(t.due)}<div class="meta">${t.days_before} d before submit</div>`}</td>
      <td>${t.open ? daysPill(t.days_left) : ''}</td><td>${prioPill(t.priority)}</td>
      <td>${select(STATUSES, t.status, 'class="t-status"')}</td>
      <td><input class="t-notes" value="${esc(t.notes || '')}" size="18"></td></tr>`).join('') || '<tr><td colspan="8" class="empty">No tasks match.</td></tr>';
    $('#tbody').querySelectorAll('tr[data-id]').forEach((tr) => {
      const id = tr.dataset.id, t = all.find((x) => x.id === id);
      tr.querySelector('.t-status').onchange = async (e) => { await patch('/api/tasks/' + id, { status: e.target.value }); t.status = e.target.value; t.open = !['Done', 'N/A'].includes(t.status); toast('Saved'); };
      tr.querySelector('.t-notes').onchange = async (e) => { await patch('/api/tasks/' + id, { notes: e.target.value }); toast('Saved'); };
      const due = tr.querySelector('.t-due');
      if (due) due.onchange = async (e) => { await patch('/api/tasks/' + id, { due_date: e.target.value || null }); toast('Saved'); views.tasks(); };
    });
  };
  render();
  $('#f-scope').onchange = (e) => { tf.scope = e.target.value; render(); };
  $('#f-prog').onchange = (e) => { tf.program = e.target.value; render(); };
  $('#f-status').onchange = (e) => { tf.status = e.target.value; render(); };
  $('#f-q').oninput = (e) => { tf.q = e.target.value; render(); };
  $('#n-add').onclick = async () => {
    const title = $('#n-title').value.trim(); if (!title) return;
    await post('/api/tasks', { title, due_date: $('#n-due').value || null, priority: $('#n-prio').value, category: $('#n-cat').value });
    toast('Task added'); views.tasks();
  };
};

// ---------------------------------------------------------------- Programmes
views.programs = async () => {
  const ps = await api('/api/programs');
  $('#view').innerHTML = `<h1>Programmes</h1><div class="sub">Click a programme for its details, syllabus, requirements and cost in ₹. Change a planned submit date and every task for that programme moves with it.</div>
    <div class="card tablewrap"><table><thead><tr><th>Programme</th><th>Tier</th><th>Country</th><th>Total cost</th><th>Deadline (expected)</th><th>Planned submit</th><th></th><th>Tasks</th><th>Status</th><th>Notes</th></tr></thead>
    <tbody>${ps.map((p) => `<tr data-id="${esc(p.id)}">
      <td><a class="ext" href="#" data-open="${esc(p.id)}"><b>${esc(p.short_name)}</b></a><div class="meta">${esc(p.programme)}</div></td>
      <td><span class="pill ${p.tier === 'Ambitious' ? 'bad' : p.tier === 'Target' ? 'warn' : p.tier === 'Safe' ? 'ok' : ''}">${esc(p.tier)}</span></td>
      <td>${esc(p.country)}</td><td style="white-space:nowrap">${p.cost && p.cost.total_lakh ? `<b>₹${p.cost.total_lakh} L</b><div class="meta">tuition + living</div>` : '—'}</td>
      <td>${fmtDate(p.deadline)}<div class="meta">${esc(p.confidence || '')}</div></td>
      <td><input type="date" class="p-date" value="${esc(p.planned_submit || '')}"></td><td>${daysPill(p.days_to_submit)}</td>
      <td style="min-width:110px">${p.done}/${p.tasks}${p.overdue ? ` <span class="pill bad">${p.overdue} late</span>` : ''}<div class="bar"><i style="width:${p.tasks ? Math.round(100 * p.done / p.tasks) : 0}%"></i></div></td>
      <td>${select(APP_STATUSES, p.status, 'class="p-status"')}</td>
      <td><input class="p-notes" value="${esc(p.notes || '')}" size="16"></td></tr>`).join('')}</tbody></table></div>`;
  $('#view').querySelectorAll('tr[data-id]').forEach((tr) => {
    const id = tr.dataset.id;
    tr.querySelector('.p-date').onchange = async (e) => { await patch('/api/programs/' + id, { planned_submit: e.target.value || null }); toast('Saved - task dates updated'); views.programs(); };
    tr.querySelector('.p-status').onchange = async (e) => { await patch('/api/programs/' + id, { status: e.target.value }); toast('Saved'); };
    tr.querySelector('.p-notes').onchange = async (e) => { await patch('/api/programs/' + id, { notes: e.target.value }); toast('Saved'); };
  });
  $('#view').querySelectorAll('[data-open]').forEach((a) => a.onclick = (e) => { e.preventDefault(); openProgram(a.dataset.open); });
};

// ---------------------------------------------------------------- Programme detail
const inr = (n) => (n === null || n === undefined) ? '—' : '₹' + Math.round(n).toLocaleString('en-IN');
const lakh = (n) => (n === null || n === undefined) ? '' : `₹${(n / 1e5).toFixed(1)} lakh`;
const loc = (n, c) => (n === null || n === undefined) ? '—' : `${c} ${Math.round(n).toLocaleString('en-US')}`;
function openProgram(id) { current = 'programs'; location.hash = 'programme/' + id; views.program(id); }
views.program = async (id) => {
  const p = await api('/api/programs/' + id);
  const c = p.cost || {}; const cu = p.curriculum || {};
  const req = [['GRE / GMAT', p.gre], ['English test', p.english], ['Work experience', p.work_exp], ['Recommendations', p.recs],
    ['Essays / SOP', p.essays], ['Interview', p.interview], ['Application fee', p.app_fee], ['Special assessments / notes', p.special]];
  const verify = (v) => /VERIFY/i.test(v || '') ? `<span class="pill warn">verify</span> ${esc(v)}` : esc(v || '—');
  const items = (s) => (s || '').split(/;\s*/).filter(Boolean).map((x) => `<li>${esc(x)}</li>`).join('');
  $('#view').innerHTML = `
    <button class="ghost small" id="back">&larr; All programmes</button>
    <h1 style="margin-top:12px">${esc(p.short_name)}</h1>
    <div class="sub">${esc(p.programme)} · ${esc(p.university)} · ${esc(p.country)} &nbsp;
      <span class="pill ${p.tier === 'Ambitious' ? 'bad' : p.tier === 'Target' ? 'warn' : p.tier === 'Safe' ? 'ok' : ''}">${esc(p.tier)}</span>
      ${p.link ? ` · <a class="ext" href="${esc(p.link)}" target="_blank" rel="noopener">Official page</a>` : ''}</div>
    <div class="grid g4" style="margin-bottom:16px">
      <div class="card stat"><div class="l">Total cost (est. 2029)</div><div class="n">${c.total_lakh ? '₹' + c.total_lakh + ' L' : '—'}</div><div class="x">${inr(c.total_inr)}</div></div>
      <div class="card stat"><div class="l">Duration</div><div class="n" style="font-size:15px">${esc(p.duration || '—')}</div><div class="x">${esc(p.intake || '')}</div></div>
      <div class="card stat"><div class="l">Expected deadline</div><div class="n" style="font-size:18px">${fmtDate(p.deadline) || '—'}</div><div class="x">${esc(p.confidence || '')}</div></div>
      <div class="card stat"><div class="l">My planned submit</div><div class="n" style="font-size:18px">${fmtDate(p.planned_submit) || '—'}</div><div class="x">${p.days_to_submit !== null ? p.days_to_submit + ' days · ' : ''}~${p.work_exp_at_submit ?? '—'} months at ZS by then</div></div>
    </div>
    <div class="grid g2">
      <div class="grid" style="align-content:start">
        <div class="card"><div class="row" style="justify-content:space-between"><h2>Syllabus / curriculum</h2><button class="ghost small" id="cu-edit">Edit</button></div>
          <div id="cu-view">
            <p>${esc(cu.overview || 'No curriculum saved yet - click Edit to add it.')}</p>
            ${cu.structure ? `<p><b>Structure.</b> ${esc(cu.structure)}</p>` : ''}
            ${cu.core ? `<b>Core courses</b><ul>${items(cu.core)}</ul>` : ''}
            ${cu.electives ? `<b>Electives</b><ul>${items(cu.electives)}</ul>` : ''}
            ${cu.capstone ? `<p><b>Capstone / project.</b> ${esc(cu.capstone)}</p>` : ''}
            ${cu.source ? `<div class="meta">Source: <a class="ext" href="${esc(cu.source)}" target="_blank" rel="noopener">${esc(cu.source.replace(/^https?:\/\//, '').slice(0, 70))}</a> · checked ${fmtDate(cu.checked)}. Course names change yearly - confirm before applying.</div>` : ''}
          </div>
          <div id="cu-form" style="display:none">
            ${['overview', 'structure', 'core', 'electives', 'capstone', 'source'].map((k) => `<label class="meta">${k}${['core', 'electives'].includes(k) ? ' (separate with ;)' : ''}</label><textarea data-cu="${k}" rows="${['core', 'electives'].includes(k) ? 4 : 2}">${esc(cu[k] || '')}</textarea>`).join('')}
            <button id="cu-save" style="margin-top:8px">Save</button></div>
        </div>
        <div class="card"><h2>Requirements</h2>
          <table>${req.map(([k, v]) => `<tr><td style="width:170px;color:var(--muted)">${k}</td><td>${verify(v)}</td></tr>`).join('')}</table>
          ${cu.req_source ? `<div class="meta" style="margin-top:8px">Checked 7 Oct 2026 for the 2026-27 cycle (${esc(cu.req_kind)} source: <a class="ext" href="${esc(cu.req_source)}" target="_blank" rel="noopener">${esc(cu.req_source.replace(/^https?:\/\//, '').slice(0, 60))}</a>). Requirements change - recheck in mid-2028.</div>` : ''}</div>
      </div>
      <div class="grid" style="align-content:start">
        <div class="card"><h2>Cost in Indian rupees</h2>
          ${c.fx ? `<table>
            <tr><td style="color:var(--muted)">Tuition (latest published)</td><td>${loc(c.tuition_local, c.currency)}</td><td><b>${inr(c.tuition_inr)}</b></td></tr>
            <tr><td style="color:var(--muted)">Tuition est. for 2029 (+${Math.round(c.uplift * 1000) / 10}%)</td><td>${loc(c.tuition_2029_local, c.currency)}</td><td><b>${inr(c.tuition_2029_inr)}</b></td></tr>
            <tr><td style="color:var(--muted)">Living cost (whole programme)</td><td>${loc(c.living_local, c.currency)}</td><td><b>${inr(c.living_inr)}</b></td></tr>
            <tr><td><b>Total</b></td><td>${loc(c.total_local, c.currency)}</td><td><b>${inr(c.total_inr)}</b><div class="meta">${lakh(c.total_inr)}</div></td></tr></table>
            <p class="meta">Fee basis: ${esc(p.fee_basis || '—')}<br>Living cost: ${esc(p.living_note || '—')}<br>
            Rate used: 1 ${esc(c.currency)} = ₹${c.fx} (planning rate - change in Settings). Excludes flights, visa, insurance and deposits.</p>
            <details><summary>Edit tuition / living cost</summary><div class="row" style="margin-top:8px">
              Tuition (${esc(c.currency)}) <input id="c-t" type="number" value="${c.tuition_local ?? ''}" style="width:110px">
              Living (${esc(c.currency)}) <input id="c-l" type="number" value="${c.living_local ?? ''}" style="width:110px"><button id="c-save" class="small">Save</button></div></details>`
          : `<p class="empty">No exchange rate for ${esc(p.currency || 'this currency')} - add it in Settings.</p>`}
        </div>
        <div class="card"><h2>After graduating</h2>
          <p><b>Post-study work:</b> ${esc(p.post_study || '—')}</p><p><b>Scholarships:</b> ${esc(p.scholarship_notes || '—')}</p>
          ${p.deadline_notes ? `<p class="meta">Deadline notes: ${esc(p.deadline_notes)}</p>` : ''}</div>
        <div class="card"><h2>My tasks for this programme</h2>
          <ul class="list">${p.tasks.map((t) => `<li><div class="grow ${t.open ? '' : 'done-text'}">${esc(t.title)}<div class="meta">due ${fmtDate(t.due)} · ${esc(t.status)}</div></div>${t.open ? daysPill(t.days_left) : '<span class="pill ok">Done</span>'}</li>`).join('')}</ul></div>
      </div>
    </div>
    <div id="p-extras"></div>`;
  $('#back').onclick = () => go('programs');
  if (window.renderProgramExtras) renderProgramExtras(p);
  $('#cu-edit').onclick = () => { $('#cu-view').style.display = 'none'; $('#cu-form').style.display = 'block'; };
  $('#cu-save').onclick = async () => {
    const body = { checked: isoToday() }; document.querySelectorAll('[data-cu]').forEach((t) => body[t.dataset.cu] = t.value);
    await patch('/api/curriculum/' + id, body); toast('Curriculum saved'); views.program(id);
  };
  const cs = $('#c-save');
  if (cs) cs.onclick = async () => { await patch(`/api/programs/${id}/costs`, { tuition: $('#c-t').value, living_cost: $('#c-l').value }); toast('Saved'); views.program(id); };
};

// ---------------------------------------------------------------- Habits
let weekStart = null;
views.habits = async () => {
  const wk = await api('/api/habits/week' + (weekStart ? '?start=' + weekStart : ''));
  weekStart = wk.start;
  const habits = await api('/api/habits');
  const t = isoToday();
  $('#view').innerHTML = `<h1>Habits &amp; schedule</h1><div class="sub">Tick sessions as you do them. Habits switch on and off by their active dates; you get a reminder before each one.</div>
    <div class="card" style="margin-bottom:16px">
      <div class="row" style="justify-content:space-between"><h2>Week of ${fmtDate(wk.start)}</h2>
      <div class="row"><button class="ghost small" data-w="-7">&larr;</button><button class="ghost small" data-w="0">This week</button><button class="ghost small" data-w="7">&rarr;</button></div></div>
      <table class="week-grid"><thead><tr><th>Habit</th>${wk.days.map((d) => `<th style="${d === t ? 'color:var(--accent)' : ''}">${fmtDate(d, { weekday: 'short', day: 'numeric' })}</th>`).join('')}<th>Done</th></tr></thead>
      <tbody>${wk.grid.map((g) => `<tr><td>${esc(g.habit.name)}<div class="meta">${esc(g.habit.start_time)} · ${g.habit.minutes} min</div></td>
        ${g.cells.map((c) => c.scheduled ? `<td><button class="check ${c.done ? 'on' : ''}" data-habit="${esc(g.habit.id)}" data-date="${c.date}" data-done="${c.done ? 1 : 0}">${c.done ? '✓' : ''}</button></td>` : '<td class="cell-off">·</td>').join('')}
        <td>${g.cells.filter((c) => c.done).length}/${g.cells.filter((c) => c.scheduled).length}</td></tr>`).join('') || '<tr><td colspan="9" class="empty">No habits scheduled this week.</td></tr>'}</tbody></table>
    </div>
    <div class="card"><h2>Edit habits &amp; fixed routine</h2>
      <div class="meta" style="margin-bottom:8px">Days: <code>Daily</code>, <code>Weekdays</code>, <code>Mon,Wed,Fri</code>, or <code>Monthly-Sat</code> (first Saturday). Routine = fixed blocks like college/work (shown on Today, not tracked).</div>
      <div class="tablewrap"><table><thead><tr><th>Name</th><th>Type</th><th>Days</th><th>Start</th><th>Min</th><th>Active from</th><th>Until</th><th>Remind</th><th></th></tr></thead>
      <tbody>${habits.map((h) => `<tr data-id="${esc(h.id)}">
        <td><input data-f="name" value="${esc(h.name)}" size="26"></td>
        <td>${select(['habit', 'routine'], h.kind, 'data-f="kind"')}</td>
        <td><input data-f="days" value="${esc(h.days)}" size="16"></td>
        <td><input data-f="start_time" type="time" value="${esc(h.start_time)}"></td>
        <td><input data-f="minutes" type="number" min="5" step="5" value="${h.minutes}" style="width:64px"></td>
        <td><input data-f="active_from" type="date" value="${esc(h.active_from || '')}"></td>
        <td><input data-f="active_until" type="date" value="${esc(h.active_until || '')}"></td>
        <td><input data-f="notify" type="checkbox" ${h.notify ? 'checked' : ''}></td>
        <td><button class="danger small" data-del="${esc(h.id)}">Delete</button></td></tr>`).join('')}
      </tbody></table></div>
      <div class="row" style="margin-top:12px"><input id="h-name" placeholder="New habit or routine" size="26">${select(['habit', 'routine'], 'habit', 'id="h-kind"')}
        <input id="h-days" value="Daily" size="14"><input id="h-time" type="time" value="20:00"><input id="h-min" type="number" value="30" style="width:64px"><button id="h-add">Add</button></div>
    </div>`;
  $('#view').querySelectorAll('[data-w]').forEach((b) => b.onclick = () => { weekStart = b.dataset.w === '0' ? null : addDays(weekStart, +b.dataset.w); views.habits(); });
  bindChecks(views.habits);
  $('#view').querySelectorAll('tr[data-id] [data-f]').forEach((inp) => inp.onchange = async () => {
    const id = inp.closest('tr').dataset.id, f = inp.dataset.f;
    const v = inp.type === 'checkbox' ? (inp.checked ? 1 : 0) : inp.type === 'number' ? +inp.value : inp.value;
    await patch('/api/habits/' + id, { [f]: v }); toast('Saved');
  });
  $('#view').querySelectorAll('[data-del]').forEach((b) => b.onclick = async () => { if (confirm('Delete this habit and its history?')) { await del('/api/habits/' + b.dataset.del); views.habits(); } });
  $('#h-add').onclick = async () => {
    const name = $('#h-name').value.trim(); if (!name) return;
    await post('/api/habits', { name, kind: $('#h-kind').value, days: $('#h-days').value, start_time: $('#h-time').value, minutes: +$('#h-min').value });
    views.habits();
  };
};

// ---------------------------------------------------------------- Reminders
views.reminders = async () => {
  const rs = await api('/api/reminders');
  const now = new Date(Date.now() - new Date().getTimezoneOffset() * 60000 + 3600e3).toISOString().slice(0, 16);
  $('#view').innerHTML = `<h1>Reminders</h1><div class="sub">Pop-up notifications on this laptop. Habit reminders are automatic; add anything else here.</div>
    <div class="card" style="margin-bottom:16px"><div class="row"><input id="r-title" placeholder="Remind me to…" size="40"><input id="r-at" type="datetime-local" value="${now}">
      ${select(['none', 'daily', 'weekdays', 'weekly'], 'none', 'id="r-rep"')}<button id="r-add">Add reminder</button></div></div>
    <div class="card"><ul class="list">${rs.map((r) => `<li><div class="grow ${r.active ? '' : 'done-text'}">${esc(r.title)}<div class="meta">${r.repeat === 'none' ? 'Once' : 'Repeats ' + esc(r.repeat)} · ${r.next ? 'next ' + new Date(r.next).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' }) : 'finished'}</div></div>
      <button class="ghost small" data-tog="${r.id}" data-a="${r.active}">${r.active ? 'Pause' : 'Resume'}</button><button class="danger small" data-rdel="${r.id}">Delete</button></li>`).join('') || '<li class="empty">No reminders yet.</li>'}</ul></div>`;
  $('#r-add').onclick = async () => {
    const title = $('#r-title').value.trim(); if (!title || !$('#r-at').value) return;
    await post('/api/reminders', { title, due_at: $('#r-at').value + ':00', repeat: $('#r-rep').value }); toast('Reminder set'); views.reminders();
  };
  $('#view').querySelectorAll('[data-tog]').forEach((b) => b.onclick = async () => { await patch('/api/reminders/' + b.dataset.tog, { active: b.dataset.a === '1' ? 0 : 1 }); views.reminders(); });
  $('#view').querySelectorAll('[data-rdel]').forEach((b) => b.onclick = async () => { await del('/api/reminders/' + b.dataset.rdel); views.reminders(); });
};

// ---------------------------------------------------------------- Assistant
const chat = [];
views.assistant = async () => {
  $('#view').innerHTML = `<h1>Assistant</h1><div class="sub">Runs on your local Ollama - your tracker data stays on this laptop.</div>
    <div class="card"><div class="toolbar"><span id="ai-status" class="meta">Checking Ollama…</span><select id="ai-model"></select><span style="flex:1"></span>
      <button class="ghost small" data-q="Plan my day: lay out today as time blocks around my schedule, and tell me the 3 most important things to do.">Plan my day</button>
      <button class="ghost small" data-q="What should I focus on this week, and what is at risk of slipping?">This week</button>
      <button class="ghost small" data-q="Review my overdue and upcoming tasks and suggest which to do first, which to reschedule, and why.">Triage tasks</button>
      <button class="ghost small" id="ai-clear">Clear</button></div>
      <div class="chat" id="chat"></div>
      <div class="row" style="margin-top:10px"><textarea id="ai-in" rows="2" placeholder="Ask anything about your plan… (Enter to send, Shift+Enter for new line)"></textarea><button id="ai-send">Send</button></div></div>`;
  const m = await api('/api/ai/models');
  $('#ai-status').innerHTML = m.ok ? '<span class="pill ok">Ollama connected</span>' : '<span class="pill bad">Ollama not reachable - start Ollama</span>';
  $('#ai-model').innerHTML = (m.models.length ? m.models : [m.selected]).map((x) => `<option ${x === m.selected ? 'selected' : ''}>${esc(x)}</option>`).join('');
  $('#ai-model').onchange = (e) => post('/api/settings', { ollama_model: e.target.value });
  const box = $('#chat');
  const draw = () => { box.innerHTML = chat.map((c) => `<div class="msg ${c.role}">${esc(c.content)}</div>`).join('') || '<div class="empty">Try “Plan my day”.</div>'; box.scrollTop = box.scrollHeight; };
  draw();
  const send = async (text) => {
    if (!text.trim()) return;
    chat.push({ role: 'user', content: text }); const ans = { role: 'assistant', content: '…' }; chat.push(ans); draw();
    $('#ai-send').disabled = true;
    const r = await fetch('/api/ai/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: chat.slice(0, -1), model: $('#ai-model').value }) });
    const reader = r.body.getReader(); const dec = new TextDecoder(); ans.content = '';
    for (;;) { const { done, value } = await reader.read(); if (done) break; ans.content += dec.decode(value, { stream: true }); if (current === 'assistant') draw(); }
    $('#ai-send') && ($('#ai-send').disabled = false);
  };
  $('#ai-send').onclick = () => { const v = $('#ai-in').value; $('#ai-in').value = ''; send(v); };
  $('#ai-in').onkeydown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); $('#ai-send').click(); } };
  $('#view').querySelectorAll('[data-q]').forEach((b) => b.onclick = () => send(b.dataset.q));
  $('#ai-clear').onclick = () => { chat.length = 0; draw(); };
};

// ---------------------------------------------------------------- Research
views.research = async () => {
  const rs = await api('/api/research');
  $('#view').innerHTML = `<h1>Research queue</h1><div class="sub">Programmes to verify before adding to your list.</div>
    <div class="card tablewrap"><table><thead><tr><th>P</th><th>Country</th><th>Programme</th><th>Why</th><th>Verify</th><th>Status</th><th>Notes</th></tr></thead>
    <tbody>${rs.map((r) => `<tr data-id="${r.id}"><td>${esc(r.priority)}</td><td>${esc(r.country)}</td><td><b>${esc(r.programme)}</b>${r.info ? `<div class="meta">${esc(r.info)}</div>` : ''}</td>
      <td>${esc(r.why)}</td><td class="meta">${esc(r.verify)}</td><td>${select(RQ_STATUSES, r.status, 'class="r-status"')}</td>
      <td><input class="r-notes" value="${esc(r.notes || '')}" size="18"></td></tr>`).join('')}</tbody></table></div>`;
  $('#view').querySelectorAll('tr[data-id]').forEach((tr) => {
    tr.querySelector('.r-status').onchange = async (e) => { await patch('/api/research/' + tr.dataset.id, { status: e.target.value }); toast('Saved'); };
    tr.querySelector('.r-notes').onchange = async (e) => { await patch('/api/research/' + tr.dataset.id, { notes: e.target.value }); toast('Saved'); };
  });
};

// ---------------------------------------------------------------- Settings
views.settings = async () => {
  const s = await api('/api/settings');
  const f = (k, label, type = 'text', extra = '') => `<label>${label}</label><input data-k="${k}" type="${type}" value="${esc(s[k] || '')}" ${extra}>`;
  $('#view').innerHTML = `<h1>Settings</h1><div class="sub">Last import: ${esc(s.last_import || '—')} · Last sync to Excel: ${esc(s.last_sync || 'never')}</div>
    <div class="card"><div class="form-grid">
      <label>Notifications</label><div><input data-k="notifications" type="checkbox" ${s.notifications === '1' ? 'checked' : ''}> on <button class="ghost small" id="s-test">Send test</button></div>
      ${f('digest_time', 'Morning summary at', 'time')}
      ${f('evening_time', 'Evening check at', 'time')}
      ${f('lead_minutes', 'Habit reminder (min before)', 'number', 'min="0" max="120"')}
      ${f('ollama_url', 'Ollama URL')}
      ${f('ollama_model', 'Ollama model')}
      ${f('excel_path', 'Excel tracker path', 'text', 'size="70"')}
      <label>Watch official pages</label><div><input data-k="watch_enabled" type="checkbox" ${s.watch_enabled !== '0' ? 'checked' : ''}> on &nbsp;
        <input data-k="watch_notify" type="checkbox" ${s.watch_notify !== '0' ? 'checked' : ''}> toast when a page changes</div>
      ${f('watch_hours', 'Re-check pages every (hours)', 'number', 'min="1" max="168"')}
    </div></div>
    <div class="card" style="margin-top:16px"><h2>Exchange rates for ₹ costs</h2>
      <p class="meta">₹ per 1 unit of each currency (planning rates from your Excel Budget tab, Oct 2026). Update them with live rates when you compare offers.</p>
      <div class="row">${['USD', 'GBP', 'EUR', 'SGD', 'CAD', 'AUD', 'CHF'].map((c) => `<label>${c} <input data-k="fx_${c}" type="number" step="0.1" value="${esc(s['fx_' + c] || '')}" style="width:80px"></label>`).join('')}</div>
      <div class="row" style="margin-top:8px"><label>Fee increase to 2029 (decimal, 0.075 = 7.5%) <input data-k="fee_uplift" type="number" step="0.005" value="${esc(s.fee_uplift || '')}" style="width:80px"></label></div></div>
    <div class="card" style="margin-top:16px"><h2>Excel</h2>
      <p class="meta">Sync writes statuses, dates, notes and the weekly habit log back into the Excel file (close it in Excel first). A backup is saved in a <code>tracker_backups</code> folder next to it.</p>
      <div class="row"><button id="s-sync">Sync to Excel now</button>
      <button class="danger" id="s-import">Re-import from Excel (replaces app data)</button></div></div>
    <div class="card" style="margin-top:16px"><h2>Run all the time</h2>
      <p class="meta">Closing this window hides it to the tray - reminders keep running. Reopen from the tray icon or the Start Menu; quit from the tray icon (right-click → Quit).
      To start at login (in the tray), run <code>Start at login - ON</code> from the Masters Tracker folder in the Start Menu.</p></div>`;
  $('#view').querySelectorAll('[data-k]').forEach((i) => i.onchange = async () => {
    await post('/api/settings', { [i.dataset.k]: i.type === 'checkbox' ? (i.checked ? '1' : '0') : i.value }); toast('Saved');
  });
  $('#s-test').onclick = () => post('/api/notify_test', {});
  $('#s-sync').onclick = async () => { const r = await post('/api/sync_excel', {}); toast(r.ok ? 'Excel updated' : r.error); views.settings(); };
  $('#s-import').onclick = async () => {
    if (!confirm('Replace all app data with the Excel file? Changes not synced to Excel will be lost. Reminders are kept.')) return;
    toast('Importing… (can take a minute)'); const r = await post('/api/import_excel', {}); toast(r.ok ? `Imported ${r.tasks} tasks` : r.error); views.settings();
  };
};

// route after every script (e.g. gre.js) has registered its views
window.addEventListener('DOMContentLoaded', () => {
  if (location.hash.startsWith('#programme/')) openProgram(location.hash.split('/')[1]);
  else go(views[location.hash.slice(1)] ? location.hash.slice(1) : 'today');
});
setInterval(() => { if (current === 'today' && document.visibilityState === 'visible') views.today(); }, 5 * 60 * 1000);
