// Acader Room demo. State is in localStorage; the server only proxies grounded LLM calls.
const KEY = 'acader-room-demo-v1';
const $ = (id) => document.getElementById(id);
const h = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) k === 'class' ? (e.className = v) : e.setAttribute(k, v);
  for (const c of kids.flat()) if (c != null) e.append(c.nodeType ? c : document.createTextNode(String(c)));
  return e;
};
const blankProc = () => ({ typed_chars: 0, paste_attempts: 0, bursts: 0, assisted_input: false, active_ms: 0 });
const fresh = (s) => ({ draft: '', coachLog: [], pending: null, helper: [], process: blankProc(), cite: [], cov: null, lastCoachLen: 0, ...s });

let S;
try { S = JSON.parse(localStorage.getItem(KEY)); } catch { S = null; }
if (!S || !S.spaces) S = { active: 'econ', spaces: window.SEED.map(fresh) };
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch {} };
const sp = () => S.spaces.find((x) => x.id === S.active) || S.spaces[0];
const ctx = () => ({ space_title: sp().title, prompt: sp().prompt, sources: sp().sources, draft: sp().draft });

function toast(msg) { const t = h('div', { class: 'toast' }, msg); document.body.append(t); setTimeout(() => t.remove(), 3200); }
async function api(path, body) {
  const r = await fetch(path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.message || d.detail || `request failed (${r.status})`);
  return d;
}
async function busy(btn, fn) {
  const t = btn.textContent; btn.disabled = true; btn.textContent = '...';
  try { return await fn(); } catch (e) { toast('Error: ' + e.message); } finally { btn.disabled = false; btn.textContent = t; }
}

// ---- rendering -------------------------------------------------------------------------
function renderSpaces() {
  $('spaces').replaceChildren(...S.spaces.map((x) => h('button', { class: 'space' + (x.id === S.active ? ' on' : '') }, x.title)));
  [...$('spaces').children].forEach((b, i) => (b.onclick = () => { S.active = S.spaces[i].id; save(); renderAll(); }));
}
function renderHead() {
  $('head').replaceChildren(h('h2', {}, 'Task'), h('div', { class: 'card' }, h('b', {}, sp().title), h('div', { class: 'mut' }, sp().prompt)));
}
function renderSources() {
  $('sources').replaceChildren(...sp().sources.map((s) => {
    const body = h('div', { class: 'src-text' }, s.text); body.hidden = true;
    const head = h('div', {}, h('span', { class: 'kind ' + s.kind }, s.kind), h('b', {}, `[${s.id}] ${s.title}`), ' ',
      h('button', { class: 'sm' }, 'view'), ' ', h('button', { class: 'sm' }, 'remove'));
    const [view, rm] = head.querySelectorAll('button');
    view.onclick = () => { body.hidden = !body.hidden; };
    rm.onclick = () => { if (confirm(`Remove [${s.id}]?`)) { sp().sources = sp().sources.filter((x) => x.id !== s.id); save(); renderSources(); } };
    return h('div', { class: 'card' }, head, body);
  }));
}
function renderStats() {
  const p = sp().process, w = sp().draft.trim() ? sp().draft.trim().split(/\s+/).length : 0;
  $('stats').textContent = `${w} words · typed ${p.typed_chars} chars · paste attempts blocked ${p.paste_attempts} · large inputs ${p.bursts}`;
}
function renderHelper() {
  $('hLog').replaceChildren(...sp().helper.map((m) => h('div', { class: 'msg ' + (m.role === 'user' ? 'u' : 'a') }, m.text)));
}
function renderCoach() {
  const s = sp(), box = $('cBox');
  if (!s.pending) { box.replaceChildren(h('div', { class: 'mut' }, 'The Coach asks you questions about your own draft. It never answers them. Use "Ask me a question", or keep writing and it will check in.')); }
  else {
    const ta = h('textarea', { rows: '4', placeholder: 'Answer in your own words...' });
    const send = h('button', { class: 'pri sm' }, 'Answer'), unsure = h('button', { class: 'sm' }, "I'm not sure");
    const submit = (txt) => busy(send, async () => {
      const g = await api('/api/coach/grade', { ctx: ctx(), question: s.pending.question, answer: txt });
      s.coachLog.push({ q: s.pending.question, a: txt, anchor: s.pending.anchor, level: g.level, note: g.note });
      s.pending = null; save(); renderCoach();
    });
    send.onclick = () => submit(ta.value); unsure.onclick = () => submit('');
    box.replaceChildren(h('div', { class: 'card q' }, h('b', {}, s.pending.question),
      s.pending.anchor ? h('div', { class: 'anchor' }, '"' + s.pending.anchor + '"') : null,
      s.pending.escalated ? h('div', { class: 'mut' }, 'Large input was detected, so this one is a bit tougher.') : null, ta,
      h('div', { class: 'bar' }, send, unsure)));
  }
  const labels = { strong: '✔ strong', partial: '◐ partial', needs_oral: '? a short oral check would help' };
  $('cLog').replaceChildren(...[...s.coachLog].reverse().map((c) => h('div', { class: 'card' }, h('div', { class: 'mut' }, 'Q: ' + c.q),
    h('div', {}, 'A: ' + (c.a || '(no answer)')), h('div', { class: 'mut' }, (labels[c.level] || c.level) + (c.note ? ' · ' + c.note : '')))));
}
function renderOut() {
  const s = sp(), out = $('out'), parts = [];
  if (s.cov) {
    parts.push(h('h2', {}, 'Coverage map'));
    s.cov.claims.forEach((c) => parts.push(h('div', { class: 'card' }, h('div', { class: 'anchor' }, '"' + c.quote + '"'),
      c.source_ids.length ? c.source_ids.map((i) => h('span', { class: 'chip' }, i)) : h('span', { class: 'mut' }, 'no sources yet'))));
    s.cov.questions.forEach((q) => parts.push(h('div', { class: 'card q' }, q)));
  }
  if (s.cite.length) {
    parts.push(h('h2', {}, 'Citation check (this room\'s sources only)'));
    const sym = { supported: '✔ supported', partial: '◐ partly supported', unsupported: '✘ not supported', not_found: '✘ not found in this room', unverified: '? could not verify' };
    s.cite.forEach((c) => parts.push(h('div', { class: 'card' }, h('span', { class: 'v-' + c.verdict }, `[${c.source_id}] ${sym[c.verdict] || c.verdict}`),
      c.sentence ? h('div', { class: 'anchor' }, '"' + c.sentence + '"') : null, c.evidence ? h('div', { class: 'mut' }, 'Source says: "' + c.evidence + '"') : null,
      c.note ? h('div', { class: 'mut' }, c.note) : null)));
  }
  out.replaceChildren(...parts);
}
function renderAll() {
  renderSpaces(); renderHead(); renderSources(); $('draft').value = sp().draft; prevLen = sp().draft.length;
  renderStats(); renderHelper(); renderCoach(); renderOut(); $('assist').checked = sp().process.assisted_input;
}

// ---- writing sandbox: typing only, process signals ---------------------------------------
let prevLen = 0, idleTimer = null, lastTs = 0;
const PASTE_TYPES = new Set(['insertFromPaste', 'insertFromDrop', 'insertFromPasteAsQuotation', 'insertFromYank']);
$('draft').addEventListener('beforeinput', (e) => {
  const p = sp().process;
  if (PASTE_TYPES.has(e.inputType)) {
    if (!p.assisted_input) { e.preventDefault(); p.paste_attempts++; save(); renderStats(); toast('Typing only in the sandbox. Bring ideas in as sources instead, or ask your instructor about assisted input.'); }
    else { p.bursts++; p.pendingEscalate = true; }
  }
});
$('draft').addEventListener('input', () => {
  const s = sp(), p = s.process, now = Date.now();
  const delta = $('draft').value.length - prevLen; prevLen = $('draft').value.length;
  if (lastTs && now - lastTs < 15000) p.active_ms += now - lastTs; lastTs = now;
  if (delta > 40 && !p.pendingEscalate) { p.bursts++; p.pendingEscalate = true; }  // autocomplete / bulk insert
  if (delta > 0) p.typed_chars += Math.min(delta, 40);
  s.draft = $('draft').value; save(); renderStats();
  if (p.pendingEscalate) { p.pendingEscalate = false; save(); askCoach(true); return; }
  clearTimeout(idleTimer);
  const freq = $('freq').value, need = freq === 'high' ? 120 : 320;
  if (freq !== 'off') idleTimer = setTimeout(() => { if (!sp().pending && sp().draft.length - sp().lastCoachLen >= need) askCoach(false); }, 20000);
});
$('assist').onchange = () => { sp().process.assisted_input = $('assist').checked; save(); toast($('assist').checked ? 'Assisted input on: pasted text is allowed, but expect more Coach questions and an oral-check recommendation.' : 'Typing only.'); };

// ---- Coach / Helper -------------------------------------------------------------------
async function askCoach(escalate) {
  const s = sp(); if (s.pending) { showTab('C'); return; }
  try {
    const d = await api('/api/coach', { ctx: ctx(), history: s.coachLog.map((c) => ({ q: c.q, a: c.a })), escalate });
    s.pending = { ...d, escalated: escalate }; s.lastCoachLen = s.draft.length; save(); showTab('C'); renderCoach();
    if (escalate) toast('Your Coach has a question.');
  } catch (e) { toast('Coach error: ' + e.message); }
}
$('coachNow').onclick = (e) => busy(e.target, () => askCoach(false));
$('hSend').onclick = (e) => busy(e.target, async () => {
  const q = $('hIn').value.trim(); if (!q) return;
  sp().helper.push({ role: 'user', text: q }); $('hIn').value = ''; renderHelper();
  const d = await api('/api/helper', { ctx: ctx(), question: q });
  sp().helper.push({ role: 'ai', text: d.answer }); save(); renderHelper();
});
function showTab(t) { $('pH').hidden = t !== 'H'; $('pC').hidden = t !== 'C'; $('tH').className = t === 'H' ? 'on' : ''; $('tC').className = t === 'C' ? 'on' : ''; }
$('tH').onclick = () => showTab('H'); $('tC').onclick = () => showTab('C');

// ---- coverage / citations ----------------------------------------------------------------
$('cov').onclick = (e) => busy(e.target, async () => { sp().cov = await api('/api/coverage', ctx()); save(); renderOut(); });
const runCite = async () => { const d = await api('/api/cite-check', ctx()); sp().cite = d.checks; save(); renderOut(); return d; };
$('cite').onclick = (e) => busy(e.target, async () => {
  if (!/\[S\d+\]/.test(sp().draft)) { toast('Add citations like [S1] to your draft first.'); return; }
  await runCite();
});

$('sample').onclick = () => {
  const s = sp(), txt = { econ: 'A binding minimum wage is a price floor, so it can leave more people seeking work than there are jobs [S1]. However, a border-county comparison found employment changed by less than one percent [S2], while a large, fast increase cut hours at small firms [S3]. So the size and speed of the increase decide the outcome.',
    cs: 'A constant learning rate makes gradient descent bounce around the minimum instead of settling [S1]. With noisy stochastic gradients even a small constant rate leaves the iterate jittering [S3]. A decaying schedule such as step decay or cosine annealing fixes this [S2].' }[s.id]
    || 'This is fictional sample text for the demo. Write your own sentences in the sandbox.';
  s.draft = txt; $('draft').value = txt; prevLen = txt.length; save(); renderStats(); toast('Sample text inserted (demo only; not counted as typing).');
};

// ---- sources / spaces ----------------------------------------------------------------------
$('sAdd').onclick = () => {
  const t = $('sTitle').value.trim(), x = $('sText').value.trim(); if (!t || !x) { toast('Give the source a title and some text.'); return; }
  const s = sp(); s.sources.push({ id: 'S' + s.nextSrc++, kind: $('sKind').value, title: t, text: x });
  $('sTitle').value = $('sText').value = ''; save(); renderSources();
};
$('newSpace').onclick = () => {
  const t = prompt('Name of the new space (a course or project):'); if (!t) return;
  const id = 'sp' + Date.now(); S.spaces.push(fresh({ id, title: t, prompt: 'Describe the task here (edit later).', sources: [], nextSrc: 1 })); S.active = id; save(); renderAll();
};
$('reset').onclick = () => { if (confirm('Erase all demo data in this browser?')) { localStorage.removeItem(KEY); location.reload(); } };

// ---- Proof of Understanding ------------------------------------------------------------------
let lastProof = null;
$('finish').onclick = (e) => busy(e.target, async () => {
  const s = sp();
  if (/\[S\d+\]/.test(s.draft) && !s.cite.length) await runCite();
  const p = s.process;
  const d = await api('/api/proof', { ctx: ctx(), coach_log: s.coachLog.map(({ q, a, level, note }) => ({ q, a, level, note })), cite_checks: s.cite,
    process: { typed_chars: p.typed_chars, paste_attempts: p.paste_attempts, bursts: p.bursts, assisted_input: p.assisted_input, minutes: Math.round(p.active_ms / 600) / 100 } });
  lastProof = d;
  const tierNote = { 'Standard': 'Rich process evidence and understanding shown.', 'Oral-verified recommended': 'A short oral check is recommended before this is treated as complete. A human decides.', 'Returned with reasons': 'Not issued yet. See the reasons below, fix them and finish again.' };
  $('proofBody').replaceChildren(h('div', { class: 'mut' }, 'PROOF OF UNDERSTANDING · demo'), h('h2', {}, d.artifact.title),
    h('div', { class: 'tier' }, d.tier), h('div', { class: 'mut' }, tierNote[d.tier] || ''),
    d.reasons.length ? h('ul', {}, d.reasons.map((r) => h('li', { class: 'err' }, r))) : null,
    h('h2', {}, 'Artifact'), h('div', {}, `${d.artifact.words} words, ${d.artifact.sources_in_room} sources in the room`),
    h('h2', {}, 'Process (signals only; raw typing stays with you)'), h('div', {}, d.process.summary),
    h('div', { class: 'mut' }, `typed ${d.process.typed_chars} chars · paste attempts ${d.process.paste_attempts} · large inputs ${d.process.bursts} · assisted input ${d.process.assisted_input ? 'on' : 'off'} · ~${d.process.minutes} min active`),
    h('h2', {}, 'Comprehension'), h('div', {}, 'In your own words: ' + d.comprehension.explained_in_own_words), h('div', {}, 'Citations: ' + d.comprehension.citations_real_and_supportive),
    h('h2', {}, 'Coach record'), ...d.coach_record.map((c) => h('div', { class: 'card' }, h('div', { class: 'mut' }, 'Q: ' + c.q), h('div', {}, 'A: ' + (c.a || '(no answer)')), h('div', { class: 'mut' }, c.level + (c.note ? ' · ' + c.note : '')))),
    h('p', { class: 'mut' }, d.note));
  $('proof').showModal();
});
$('pClose').onclick = () => $('proof').close(); $('pPrint').onclick = () => window.print();
$('pJson').onclick = () => { const a = h('a', { href: URL.createObjectURL(new Blob([JSON.stringify(lastProof, null, 2)], { type: 'application/json' })), download: 'proof-of-understanding.json' }); a.click(); };

// ---- boot ------------------------------------------------------------------------------------
fetch('/api/status').then((r) => r.json()).then((d) => { $('llm').textContent = d.key ? `LLM: ${d.llm} (${d.model})` : 'LLM: no DEEPSEEK_API_KEY found'; if (!d.key) $('llm').className = 'err'; }).catch(() => {});
renderAll(); showTab('H');
