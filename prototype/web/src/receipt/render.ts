import type { Band, GoldenSession, Receipt, SentenceView } from './types';
import './receipt.css';

const BANDS: {id: Exclude<Band, 'mechanics'>; label: string}[] = [
  {id: 'traced_source', label: 'Traced to a source or lecture'},
  {id: 'traced_coach', label: 'Traced to a Coach exchange'},
  {id: 'declared', label: 'Declared outside help'},
  {id: 'student_linked', label: 'Linked by student, not checked'},
  {id: 'untraced', label: 'Untraced'},
];
export const BLIND_SPOT_GLOSS = 'Untraced is not AI. It means this platform has no record of where it came from. Retyping, writing offline and outside help all look the same here.';
// These conservative stems mirror the existing server receipt wording policy.
// Identifiers remain in data attributes; displayed strings always pass this guard.
const BANNED = /\bdetect\w*|\bcatch\w*|\bcaught\b|\bcheat\w*|\bghost\w*|\bforensic\w*|\bai[\s\-\u2010-\u2015]*generated\b|\bsuspicio\w*|\bsuspect\w*|\bflag\w*|\bviolat\w*|\bintegrity\s+scor\w*|\bprobabilit\w*|\b100\s*%|\bone hundred per\s*cent\b|\bhundred percent\b/i;
export function receiptText(value: unknown): string {
  const text = typeof value === 'string' ? value : String(value ?? '');
  return BANNED.test(text) ? 'Text omitted by the wording policy.' : text;
}
function el<K extends keyof HTMLElementTagNameMap>(tag: K, text?: unknown, className?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = receiptText(text);
  if (className) node.className = className;
  return node;
}
function record(value: unknown): Record<string, unknown> { return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}; }
function rows(value: unknown): Record<string, unknown>[] { return Array.isArray(value) ? value.map(record) : []; }
function count(value: unknown): number { return typeof value === 'number' && Number.isInteger(value) && value >= 0 ? value : 0; }
function date(value: string): string {
  const parsed = new Date(value);
  return Number.isNaN(parsed.valueOf()) ? 'Submission date unavailable' : new Intl.DateTimeFormat('en-GB', {day:'numeric', month:'long', year:'numeric', timeZone:'UTC'}).format(parsed);
}
function section(title: string, className?: string): HTMLElement {
  const node = el('section', undefined, className); node.append(el('h2', title)); return node;
}
function disclosure(title: string, className: string): HTMLDetailsElement {
  const node = el('details', undefined, className); node.append(el('summary', title)); return node;
}
function factList(parent: HTMLElement, facts: [string, unknown][]): void {
  const list = el('dl', undefined, 'receipt-fact-list');
  for (const [label, value] of facts) { list.append(el('dt', label), el('dd', value)); }
  parent.append(list);
}
function sentenceButton(sentence: SentenceView, onSentence: (sentenceId: string, trigger: HTMLElement) => void): HTMLButtonElement {
  const button = el('button', sentence.text, 'receipt-sentence-link');
  button.type = 'button'; button.dataset.sentenceId = sentence.id;
  button.setAttribute('aria-label', receiptText(`Read evidence for: ${sentence.text}`));
  button.addEventListener('click', () => onSentence(sentence.id, button));
  return button;
}
function bar(counts: Record<string, number>, title: string, unit: string): HTMLElement {
  const wrap = el('div', undefined, 'receipt-band-group');
  const total = BANDS.reduce((sum, band) => sum + count(counts[band.id]), 0);
  wrap.append(el('p', `${title} · ${total} ${unit}`, 'receipt-label'));
  const graphic = el('div', undefined, 'receipt-bar'); graphic.setAttribute('role', 'img');
  graphic.setAttribute('aria-label', receiptText(`${title}: ${BANDS.map(b => `${count(counts[b.id])} ${b.label.toLowerCase()}`).join('; ')}`));
  graphic.dataset.bandUnit = unit;
  if (!total) { graphic.classList.add('receipt-bar-empty'); wrap.append(graphic, el('p', `No ${unit} in the five bands.`, 'receipt-label')); return wrap; }
  for (const band of BANDS) {
    const amount = count(counts[band.id]); if (!amount) continue;
    const segment = el('span', undefined, `receipt-band receipt-band-${band.id}`);
    segment.style.flexGrow = String(amount); segment.style.flexBasis = '0';
    segment.dataset.band = band.id; segment.dataset.count = String(amount); graphic.append(segment);
  }
  wrap.append(graphic); return wrap;
}
function bandTable(receipt: Receipt): HTMLTableElement {
  const table = el('table', undefined, 'receipt-band-table');
  table.append(el('caption', 'Counts by evidence band'));
  const head = el('thead'); const row = el('tr');
  for (const title of ['Evidence band', 'Words', 'Claims']) { const th = el('th', title); th.scope='col'; row.append(th); }
  head.append(row); table.append(head); const body = el('tbody');
  for (const band of BANDS) {
    const tr = el('tr'); tr.dataset.bandRow = band.id;
    const name = el('th'); name.scope = 'row'; const key = el('span', undefined, `receipt-band-key receipt-band-${band.id}`); key.setAttribute('aria-hidden','true'); name.append(key, document.createTextNode(band.label));
    const words = el('td', receipt.bands.by_words[band.id] ?? 0); words.dataset.countKind='words';
    const claims = el('td', receipt.bands.by_claims[band.id] ?? 0); claims.dataset.countKind='claims';
    tr.append(name, words, claims); body.append(tr);
  }
  table.append(body); return table;
}
function renderMoments(receipt: Receipt): HTMLElement {
  const node = section('Thinking moments'); const list = el('ul', undefined, 'receipt-plain-list');
  for (const moment of receipt.moments) {
    const kind = moment.kind;
    const text = kind === 'claim_edit_after_limitation' ? `Claim ${receiptText(moment.claim_id)} changed after opening a limitation passage.`
      : kind === 'set_aside' ? `A source was set aside: ${receiptText(moment.reason_tag || 'reason not supplied')}.`
      : kind === 'coach_revised' ? 'A Coach answer was revised.'
      : kind === 'coach_disagreed' ? 'The student disagreed with the Coach and recorded a reason.'
      : 'A thinking moment is recorded in the receipt.';
    list.append(el('li', text));
  }
  if (!list.childElementCount) node.append(el('p','No thinking moments recorded.','receipt-muted')); else node.append(list);
  return node;
}
function renderCoach(receipt: Receipt): HTMLElement {
  const node = section('Coach record'); const coach = receipt.coach; const outcomes = record(coach.by_outcome);
  factList(node, [['Questions asked', count(coach.asked)], ['Answered', count(outcomes.answered)], ['Revised', count(outcomes.revised)], ['Disagreed', count(outcomes.disagreed)], ['Declined', count(outcomes.declined)], ['No outcome recorded', count(outcomes.no_outcome)]]);
  const questions = rows(coach.questions); if (questions.length) {
    const list = el('ul', undefined, 'receipt-plain-list');
    const allowedPillars = new Set(['reading','logic','writing','communication']);
    const allowedOutcomes = new Set(['answered','revised','disagreed','declined','no_outcome']);
    for (const q of questions) list.append(el('li', `${allowedPillars.has(String(q.pillar)) ? q.pillar : 'Question'} · ${allowedOutcomes.has(String(q.outcome)) ? String(q.outcome).replace('_',' ') : 'outcome recorded'}`));
    node.append(list);
  }
  node.append(el('p','Outcomes are facts, never grades.','receipt-muted')); return node;
}
function renderReading(receipt: Receipt): HTMLElement {
  const node = section('Reading depth'); if (!receipt.reading.sources.length) {node.append(el('p','No source activity recorded.','receipt-muted')); return node;}
  const table = el('table', undefined, 'receipt-reading-table'); table.append(el('caption','Opened and anchored parts of each source'));
  const head = el('thead'); const row = el('tr'); for (const label of ['Source','Opened','Anchored']) {const th=el('th',label);th.scope='col';row.append(th);}head.append(row);table.append(head);
  const body=el('tbody');
  for (const source of receipt.reading.sources) {
    const tr=el('tr'); tr.dataset.sourceId=source.source_id; const title=el('th',source.title || 'Untitled source');title.scope='row';
    const parts = (values:Record<string,number>) => Object.entries(values).map(([key,value])=>`${receiptText(key.replaceAll('_',' '))}: ${count(value)}`).join('; ') || 'None recorded';
    tr.append(title,el('td',parts(source.opened)),el('td',parts(source.anchored)));body.append(tr);
  }
  table.append(body);node.append(table);return node;
}
function renderDeclared(receipt: Receipt): HTMLElement {
  const node = section('Declared help'); const tools=rows(receipt.declared.by_tool);
  if (!tools.length) node.append(el('p','No outside help declared.','receipt-muted'));
  else {const list=el('ul',undefined,'receipt-plain-list');for(const tool of tools)list.append(el('li',`${receiptText(tool.tool_name || 'Unnamed tool')}: ${count(tool.count)} imports, ${count(tool.size_chars)} characters.`));node.append(list);}
  factList(node,[['Declared claims',count(receipt.declared.declared_claims)],['Later anchored',count(receipt.declared.declared_claims_anchored)]]);return node;
}
function renderFacts(receipt: Receipt): HTMLElement {
  const node=section('Other facts');const pastes=record(receipt.facts.pastes);const editor=record(pastes.editor);const cards=record(pastes.cards);const answers=record(pastes.coach_answers);const replacements=record(receipt.facts.replacement_edits);
  factList(node,[['Editor pastes',count(editor.count)],['Cards containing pasted text',count(cards.cards_with_paste)],['Coach answers containing pasted text',count(answers.answers_with_paste)],['Replacement edits reported by the browser',count(replacements.count)]]);
  node.append(el('p','Replacement edits are a lower bound from browser reports.','receipt-muted'));return node;
}

/** Render a teacher-only, synthetic receipt. No release, preview, or persistence behavior. */
export function renderReceipt(session: GoldenSession, onSentence: (sentenceId: string, trigger: HTMLElement) => void): HTMLElement {
  const receipt=session.receipt;const context=session.view_context;const root=el('article',undefined,'receipt-document');root.dataset.receiptId=receipt.receipt_id;
  const header=el('header',undefined,'receipt-header');header.append(el('p','Synthetic development receipt','receipt-label receipt-muted'));
  const title=el('h1',context.header.assignment_title);title.tabIndex=-1;title.id='receipt-title';header.append(title);
  header.append(el('p',context.header.student_name,'receipt-student'));
  header.append(el('p',`Submitted ${date(context.header.submitted_at)} · ${receipt.bands.total_words} body words · ${context.header.source_count} sources`,'receipt-label receipt-muted'));root.append(header);
  if(receipt.status==='replay_mismatch') {const note=el('p',receipt.replay_note || "Built from the browser's copy (replay mismatch).",'receipt-state');note.dataset.state='replay_mismatch';root.append(note);}
  const summary=section('Summary','receipt-summary-section');summary.append(el('p',receipt.summary.text,'receipt-summary'));root.append(summary);
  const questions=section('Where to ask','receipt-questions');
  if(receipt.questions_pending) {const pending=el('p','Questions pending.','receipt-state');pending.dataset.state='questions_pending';questions.append(pending);}
  if(!receipt.questions.length)questions.append(el('p',receipt.questions_pending?'Questions will appear when they are ready.':'No questions selected in this receipt.','receipt-muted'));
  for(const [index,q] of receipt.questions.entries()) {
    const item=el('div',undefined,'receipt-question');item.dataset.questionIndex=String(index);
    const targets=context.sentences.filter(s=>s.from<q.span.to&&s.to>q.span.from);
    if(targets.length) {const quote=el('blockquote');for(const sentence of targets)quote.append(sentenceButton(sentence,onSentence));item.append(quote);}
    else item.append(el('p','The question span has no matching final sentence in this view.','receipt-label receipt-muted'));
    item.append(el('p',q.q===null?'Question not ready.':q.q,'receipt-question-text'));
    item.append(el('p',q.why_text,'receipt-label receipt-muted'));questions.append(item);
  }
  root.append(questions);
  const built=section('How the work was built','receipt-bands');built.append(bar(receipt.bands.by_words,'By words','words'),bar(receipt.bands.by_claims,'By claims','claims'));
  const gloss=el('p',BLIND_SPOT_GLOSS,'receipt-gloss');gloss.dataset.blindSpot='true';built.append(gloss,bandTable(receipt));
  if(receipt.inferred_links>0)built.append(el('p',`Of the student links, ${receipt.inferred_links} accepted from map suggestions.`,'receipt-label'));
  built.append(el('p',`${receipt.bands.mechanics} words of references and formatting counted apart as mechanics.`,'receipt-label receipt-muted'));root.append(built);
  const details=disclosure('How it was built (details)','receipt-details');details.append(renderMoments(receipt),renderCoach(receipt),renderReading(receipt),renderDeclared(receipt),renderFacts(receipt));
  const draft=section('Final text and evidence');draft.append(el('p','Choose a sentence to read its own evidence.','receipt-label receipt-muted'));
  for(const paragraph of context.paragraphs) {
    const block=el('div',undefined,'receipt-final-paragraph');block.dataset.paragraphId=paragraph.id;
    for(const sid of paragraph.sentence_ids) {const sentence=context.sentences.find(s=>s.id===sid);if(sentence){if(block.childElementCount)block.append(document.createTextNode(' '));block.append(sentenceButton(sentence,onSentence));}}
    if(!block.childElementCount&&paragraph.text)block.append(el('p','No sentence correspondence is available for this paragraph.','receipt-muted'));
    draft.append(block);
  }
  if(!context.paragraphs.length)draft.append(el('p','No final text in this receipt.','receipt-muted'));
  details.append(draft);root.append(details);
  const about=disclosure('About this receipt','receipt-about');
  about.append(el('p','Record sealed at submission. Notes added after submission are dated, not sealed.'));
  about.append(el('p',`Check: verify ${receipt.seal_hash}`,'receipt-hash'));
  about.append(el('p',`Receipt hash: ${session.receipt_hash}`,'receipt-hash'));
  about.append(el('p','What this record cannot see: retyped text, work done offline, outside help not declared, and the student’s understanding.'));
  about.append(el('p',`${receipt.map_suggestions} links suggested by the map, not checked; none of them counts as traced.`));
  factList(about,[['Engine',receipt.engine.version],['Build',receipt.engine.git_sha],['Editor pair',receipt.engine.editor_pair],['Dependency lock',receipt.engine.lock_hash]]);
  root.append(about);return root;
}
