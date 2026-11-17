'use strict';
// Programme page extras: official pages being watched (+ change history) and scholarships & funding.
// Also the "Site updates" view and its unread badge in the sidebar.

const FIT = { likely: ['ok', 'Likely eligible'], check: ['warn', 'Check eligibility'], unlikely: ['bad', 'Unlikely / not open to you'] };
const KIND_PILL = { 'University merit': 'acc', 'Need-based': '', Assistantship: 'ok', 'External award': 'acc', 'Loan scholarship': 'warn' };
const shortUrl = (u) => (u || '').replace(/^https?:\/\/(www\.)?/, '').slice(0, 60);
const fmtWhen = (s) => (s ? new Date(s).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : 'never');
const checkText = (s) => esc(s || '').replace(/\bcheck\b/gi, '<span class="pill warn">check</span>');

function changeItem(c, withProg) {
  const lines = (t, cls) => (t || '').split('\n').filter(Boolean).slice(0, 12).map((l) => `<div class="diff ${cls}">${cls === 'add' ? '+' : '−'} ${esc(l)}</div>`).join('');
  return `<li class="chg ${c.seen ? '' : 'unseen'}" data-chg="${c.id}"><div class="grow">
      <div>${c.seen ? '' : '<span class="pill bad">new</span> '}${withProg ? `<a href="#" data-prog="${esc(c.program_id)}"><b>${esc(c.short_name || c.program_id)}</b></a> · ` : ''}<b>${esc(c.label)}</b>
        ${c.change_type === 'error' ? '<span class="pill warn">link problem</span>' : c.change_type === 'minor' ? '<span class="pill">minor</span>' : ''}
        <span class="meta">${fmtWhen(c.at)}</span></div>
      <div class="meta" style="margin:2px 0 4px">${esc(c.summary)}</div>
      ${(c.added || c.removed) ? `<details><summary class="meta">What changed</summary>${lines(c.added, 'add')}${lines(c.removed, 'del')}</details>` : ''}
    </div>
    <div class="row" style="flex-direction:column;align-items:flex-end;gap:4px">
      <a class="btnlink" href="${esc(c.url)}" target="_blank" rel="noopener">Open page</a>
      ${c.seen ? '' : `<button class="ghost small" data-seen="${c.id}">Mark seen</button>`}</div></li>`;
}

function bindChanges(root, refresh) {
  root.querySelectorAll('[data-seen]').forEach((b) => b.onclick = async () => { const r = await post('/api/watch/seen', { id: +b.dataset.seen }); setBadge(r.unseen); refresh(); });
  root.querySelectorAll('[data-prog]').forEach((a) => a.onclick = (e) => { e.preventDefault(); openProgram(a.dataset.prog); });
}

function awardCard(a, pid, statuses) {
  const fit = FIT[a.fit] || FIT.check;
  const li = (xs) => (xs || []).map((x) => `<li>${checkText(x)}</li>`).join('');
  return `<div class="award" data-aid="${esc(a.id)}">
    <div class="row" style="justify-content:space-between;align-items:flex-start">
      <div class="grow"><b>${esc(a.name)}</b> <span class="pill ${KIND_PILL[a.kind] ?? ''}">${esc(a.kind)}</span>
        <span class="pill ${fit[0]}" title="${esc(a.fit_note || '')}">${fit[1]}</span>
        <div class="meta">${esc(a.by)}${a.scope === 'external' ? ' · external award' : ''}</div></div>
      ${select(statuses, a.status, 'class="f-status" title="Your status"')}
    </div>
    <table class="kv">
      <tr><td>Amount</td><td>${checkText(a.amount)}</td></tr>
      <tr><td>Deadline</td><td>${checkText(a.deadline)}</td></tr>
      <tr><td>Who can get it</td><td>${checkText(a.eligibility)}</td></tr>
      ${a.fit_note ? `<tr><td>For you</td><td>${checkText(a.fit_note)}</td></tr>` : ''}
    </table>
    ${(a.steps || []).length || (a.prepare || []).length ? `<details><summary>How to apply &amp; what to prepare</summary>
      ${(a.steps || []).length ? `<b>Steps</b><ol>${li(a.steps)}</ol>` : ''}
      ${(a.prepare || []).length ? `<b>Prepare</b><ul>${li(a.prepare)}</ul>` : ''}</details>` : ''}
    <div class="row" style="justify-content:space-between;margin-top:6px">
      <a class="ext" href="${esc(a.link)}" target="_blank" rel="noopener">Official page: ${esc(shortUrl(a.link))}</a>
      <input class="f-note" placeholder="My note" value="${esc(a.note || '')}" size="28"></div>
  </div>`;
}

window.renderProgramExtras = (p) => {
  const box = $('#p-extras'); if (!box) return;
  const pages = p.official_pages || []; const chg = p.page_changes || []; const fund = p.funding || [];
  const uni = fund.filter((a) => a.scope === 'programme'); const ext = fund.filter((a) => a.scope === 'external');
  box.innerHTML = `
    <div class="card" style="margin-top:16px"><div class="row" style="justify-content:space-between">
        <h2>Official pages &amp; updates</h2><button class="ghost small" id="w-check">Check these pages now</button></div>
      <p class="meta">The app re-reads these pages every ${esc(p.watch_hours || '12')} h while it runs (and at start-up) and tells you when the main text changes - menus, date stamps and tracking bits are ignored. Change the interval in Settings.</p>
      <table>${pages.map((g) => `<tr><td style="width:190px"><b>${esc(g.label)}</b></td>
          <td><a class="ext" href="${esc(g.url)}" target="_blank" rel="noopener">${esc(shortUrl(g.url))}</a>
          <div class="meta">${g.active ? `checked ${fmtWhen(g.last_checked)} · ${esc(g.last_status || 'not checked yet')}` : esc(g.last_status || '')}</div></td></tr>`).join('')
        || '<tr><td class="empty">No official pages saved for this programme.</td></tr>'}</table>
      <h3 style="margin-top:14px">Change history</h3>
      ${chg.length ? `<div class="row" style="justify-content:flex-end"><button class="ghost small" id="w-seen-all">Mark all seen</button></div><ul class="list">${chg.map((c) => changeItem(c, false)).join('')}</ul>`
        : '<p class="empty">No changes recorded yet. The first check only saves a baseline.</p>'}
    </div>
    <div class="card" style="margin-top:16px">
      <h2>Scholarships &amp; funding</h2>
      <p class="meta">From official pages, checked ${fmtDate(p.funding_checked)}. Amounts and dates are the current cycle - you apply for Fall 2029, so confirm each one when the next cycle opens. <span class="pill warn">check</span> = not confirmed on an official page. Funding tasks with projected dates are in Tasks.</p>
      <h3>From the university</h3>${uni.length ? uni.map((a) => awardCard(a, p.id, p.funding_statuses)).join('') : '<p class="empty">Nothing programme-specific found.</p>'}
      <h3 style="margin-top:14px">External scholarships &amp; loan scholarships for Indian students</h3>${ext.map((a) => awardCard(a, p.id, p.funding_statuses)).join('')}
    </div>`;
  const reload = () => views.program(p.id);
  bindChanges(box, reload);
  const sa = $('#w-seen-all'); if (sa) sa.onclick = async () => { const r = await post('/api/watch/seen', { program_id: p.id }); setBadge(r.unseen); reload(); };
  $('#w-check').onclick = async () => {
    const r = await post('/api/watch/check', { program_id: p.id });
    toast(r.ok ? 'Checking pages… refresh in a minute' : r.error);
    if (r.ok) setTimeout(() => { if (location.hash === '#programme/' + p.id) reload(); }, 45000);
  };
  box.querySelectorAll('.award').forEach((el) => {
    const aid = el.dataset.aid;
    el.querySelector('.f-status').onchange = async (e) => { await patch(`/api/funding/${p.id}/${aid}`, { status: e.target.value }); toast('Saved'); };
    el.querySelector('.f-note').onchange = async (e) => { await patch(`/api/funding/${p.id}/${aid}`, { note: e.target.value }); toast('Saved'); };
  });
};

// ---------------------------------------------------------------- Site updates view
views.updates = async () => {
  const [all, st] = await Promise.all([api('/api/watch/changes'), api('/api/watch/status')]);
  setBadge(st.unseen);
  $('#view').innerHTML = `<h1>Site updates</h1>
    <div class="sub">Changes the app found on your programmes' official pages (programme, admissions, funding, international). Click "Open page" to see it on the university site.</div>
    <div class="row" style="margin-bottom:12px"><button id="u-check">Check all pages now</button>
      <button class="ghost" id="u-seen">Mark all seen</button><span class="meta">${st.running ? 'A check is running…' : ''}</span></div>
    <div class="card">${all.length ? `<ul class="list">${all.map((c) => changeItem(c, true)).join('')}</ul>` : '<p class="empty">No changes yet. The first check of each page saves a baseline; changes show up from the next check.</p>'}</div>`;
  bindChanges($('#view'), views.updates);
  $('#u-seen').onclick = async () => { const r = await post('/api/watch/seen', {}); setBadge(r.unseen); views.updates(); };
  $('#u-check').onclick = async () => { const r = await post('/api/watch/check', {}); toast(r.ok ? 'Checking all pages - takes a few minutes' : r.error); };
};

function setBadge(n) {
  const b = $('#upd-badge'); if (!b) return;
  b.textContent = n; b.style.display = n ? 'inline-block' : 'none';
}
async function pollBadge() { try { const s = await api('/api/watch/status'); setBadge(s.unseen); } catch (e) { /* server restarting */ } }
pollBadge();
setInterval(pollBadge, 60 * 1000);
