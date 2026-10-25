// @vitest-environment jsdom
import { describe, expect, test, vi } from 'vitest';
import { BLIND_SPOT_GLOSS, receiptText, renderReceipt } from './render';
import type { GoldenSession, SentenceView } from './types';

/** Narrow synthetic derivative for renderer states, not a frozen engine receipt. */
function sample(): GoldenSession {
  const sentence: SentenceView = {id:'s1',paragraph_id:'p1',from:1,to:45,text:'A source supports a carefully bounded claim.',band:'student_linked',chain:{steps:[],notes:['No source text checked.'],history:[],history_note:'No sentence history available.'}};
  return {
    session_id:'renderer-derived',receipt_hash:'abc123',view_context:{synthetic:true,header:{student_name:'Synthetic Student A',assignment_title:'A care-plan rationale',submitted_at:'2026-11-02T14:26:00Z',source_count:1},paragraphs:[{id:'p1',text:sentence.text,sentence_ids:['s1']}],sentences:[sentence]},
    receipt:{receipt_id:'r1',log_id:'l1',seal_hash:'def456',seal_seq:12,status:'complete',questions_pending:false,built_from:'replay',replay_note:null,summary:{text:'One claim is linked by the student, not checked.',event_ids:[12]},questions:[{q:'What changes if the clinical setting changes?',pillar:'logic',why:'student_linked_claim',why_text:'This part carries the argument and is linked by the student, not checked against a source.',paragraph_id:'p1',span:{from:1,to:45},grounding:['c1'],event_ids:[12],artifact_ids:[]}],more_places:[],bands:{total_words:7,by_words:{traced_source:0,traced_coach:0,declared:0,student_linked:7,untraced:0},by_claims:{traced_source:0,traced_coach:0,declared:0,student_linked:1,untraced:0},mechanics:46,quoted_words:0,event_ids:[12]},moments:[],coach:{asked:0,by_outcome:{}},reading:{sources:[{source_id:'nursing',title:'A nursing paper',opened:{abstract:1},anchored:{abstract:1},event_ids:[1]}]},declared:{imports:[],by_tool:[],declared_claims:0,declared_claims_anchored:0},facts:{pastes:{editor:{count:0},cards:{cards_with_paste:0},coach_answers:{answers_with_paste:0}},replacement_edits:{count:0}},inferred_links:0,map_suggestions:0,blind_spots:[],engine:{version:'receipt/1',git_sha:'fixture',editor_pair:'test pair',lock_hash:'abcdef'}}
  };
}
const mounted = (session=sample(), callback=vi.fn()) => {const node=renderReceipt(session,callback);document.body.replaceChildren(node);return {node,callback};};

describe('receipt document rendering',()=>{
  test('first-screen sections preserve compiled text, counts, questions and exact gloss',()=>{
    const s=sample();const {node}=mounted(s);
    expect(node.querySelector('h1')?.textContent).toBe(s.view_context.header.assignment_title);
    expect(node.querySelector('.receipt-summary')?.textContent).toBe(s.receipt.summary.text);
    expect(node.querySelector('.receipt-question-text')?.textContent).toBe(s.receipt.questions[0].q);
    expect(node.querySelector('[data-blind-spot]')?.textContent).toBe(BLIND_SPOT_GLOSS);
    const row=node.querySelector('[data-band-row="student_linked"]');
    expect(row?.querySelector('[data-count-kind="words"]')?.textContent).toBe('7');
    expect(row?.querySelector('[data-count-kind="claims"]')?.textContent).toBe('1');
    expect(node.textContent).toContain('46 words of references and formatting counted apart as mechanics.');
    const sections=[...node.querySelectorAll(':scope > section')];
    expect(sections.map(x=>x.querySelector('h2')?.textContent)).toEqual(['Summary','Where to ask','How the work was built']);
    expect(node.querySelector('.receipt-gloss')?.previousElementSibling?.getAttribute('class')).toBe('receipt-band-group');
  });
  test('hashes stay in About and disclosures start closed',()=>{
    const {node}=mounted();const about=node.querySelector('.receipt-about')!;
    expect(about.textContent).toContain('def456');expect(about.textContent).toContain('abc123');
    expect(node.querySelector('.receipt-header')?.textContent).not.toContain('def456');
    expect([...node.querySelectorAll('details')].every(d=>!d.open)).toBe(true);
    expect(node.textContent).not.toContain('Mark as discussed');expect(node.textContent).not.toContain('Remove my record');
  });
  test('question evidence and every final sentence use the exact sentence identifier',()=>{
    const {node,callback}=mounted();const buttons=node.querySelectorAll<HTMLButtonElement>('[data-sentence-id="s1"]');expect(buttons).toHaveLength(2);
    buttons[0].click();expect(callback).toHaveBeenCalledWith('s1',buttons[0]);
    buttons[1].focus();expect(document.activeElement).toBe(buttons[1]);buttons[1].click();expect(callback).toHaveBeenLastCalledWith('s1',buttons[1]);
  });
  test('final paragraphs preserve readable spaces between independently linked sentences',()=>{
    const s=sample();const first=s.view_context.sentences[0];const second={...first,id:'s2',from:46,to:67,text:'Another bounded point.'};s.view_context.sentences.push(second);s.view_context.paragraphs[0].sentence_ids.push('s2');
    const {node}=mounted(s);expect(node.querySelector('.receipt-final-paragraph')?.textContent).toBe(`${first.text} ${second.text}`);expect(node.querySelector('.receipt-final-paragraph')?.querySelectorAll('[data-sentence-id]')).toHaveLength(2);
  });
  test('a paragraph name alone never fabricates a question-to-sentence correspondence',()=>{
    const s=sample();s.receipt.questions[0].span={from:1000,to:1050};const {node}=mounted(s);
    expect(node.querySelector('.receipt-question [data-sentence-id]')).toBeNull();
    expect(node.querySelector('.receipt-question')?.textContent).toContain('no matching final sentence');
    expect(node.querySelectorAll('.receipt-final-paragraph [data-sentence-id]')).toHaveLength(1);
  });
  test('pending questions preserve the span but render no null or fabricated question',()=>{
    const s=sample();s.receipt.status='questions_pending';s.receipt.questions_pending=true;s.receipt.questions[0].q=null;
    const {node}=mounted(s);expect(node.querySelector('[data-state="questions_pending"]')?.textContent).toBe('Questions pending.');
    expect(node.querySelector('.receipt-question-text')?.textContent).toBe('Question not ready.');
    expect(node.textContent).not.toContain('null');expect(node.textContent).not.toContain('What changes if');
    expect(node.querySelector('.receipt-question [data-sentence-id="s1"]')).not.toBeNull();
  });
  test('replay mismatch uses its compiled fallback note without changing displayed counts',()=>{
    const s=sample();s.receipt.status='replay_mismatch';s.receipt.replay_note="Built from the browser's copy (replay mismatch).";
    const {node}=mounted(s);expect(node.querySelector('[data-state="replay_mismatch"]')?.textContent).toBe(s.receipt.replay_note);
    expect(node.querySelector('[data-band-row="student_linked"] td')?.textContent).toBe('7');
  });
  test('empty word and claim denominators stay readable without invalid arithmetic',()=>{
    const s=sample();for(const key of Object.keys(s.receipt.bands.by_words)) {s.receipt.bands.by_words[key]=0;s.receipt.bands.by_claims[key]=0;}s.receipt.bands.total_words=0;s.receipt.questions=[];s.receipt.bands.mechanics=0;s.view_context.paragraphs=[];s.view_context.sentences=[];
    const {node}=mounted(s);expect(node.querySelectorAll('.receipt-bar-empty')).toHaveLength(2);expect(node.querySelectorAll('.receipt-band')).toHaveLength(0);
    expect(node.textContent).toContain('No words in the five bands.');expect(node.textContent).toContain('No claims in the five bands.');
    expect(node.textContent).not.toMatch(/NaN|Infinity/);expect(node.textContent).toContain('No final text');
  });
  test('student, source, question and document prose is text, never HTML',()=>{
    const s=sample();const hostile='<img src=x onerror=alert(1)>';s.view_context.header.student_name=hostile;s.receipt.questions[0].q=hostile;s.receipt.reading.sources[0].title=hostile;s.view_context.sentences[0].text=hostile;
    const {node}=mounted(s);expect(node.querySelector('img')).toBeNull();expect(node.querySelector('[onerror]')).toBeNull();
    expect(node.textContent?.match(/<img src=x onerror=alert\(1\)>/g)?.length).toBeGreaterThanOrEqual(4);
  });
  test('source titles, declared tools and known activity counts render without exposing internal keys',()=>{
    const s=sample();s.receipt.declared={by_tool:[{tool_name:'Example tool',count:2,size_chars:30}],declared_claims:2,declared_claims_anchored:1};s.receipt.facts={pastes:{editor:{count:3},cards:{cards_with_paste:1},coach_answers:{answers_with_paste:2}},replacement_edits:{count:4}};s.receipt.inferred_links=1;
    const {node}=mounted(s);expect(node.textContent).toContain('A nursing paper');expect(node.textContent).toContain('Example tool: 2 imports, 30 characters.');expect(node.textContent).toContain('1 accepted from map suggestions');
    expect(node.textContent).toContain('Editor pastes');expect(node.textContent).not.toContain('cards_with_paste');expect(node.textContent).not.toContain('flags');
  });
  test('a missing sentence stays explicit instead of guessing from paragraph text',()=>{
    const s=sample();s.view_context.sentences=[];const {node}=mounted(s);
    expect(node.querySelector('.receipt-final-paragraph')?.textContent).toContain('No sentence correspondence');expect(node.querySelectorAll('[data-sentence-id]')).toHaveLength(0);
  });
  test.each(['detect','caught','cheating','ghostwriter','forensic','AI-generated','suspicious','suspect','flagship','violation','integrity score','probability','100%'])('new rendered context respects the existing wording stem %s',(text)=>{
    expect(receiptText(text)).toBe('Text omitted by the wording policy.');
    const s=sample();s.receipt.reading.sources[0].title=text;const {node}=mounted(s);expect(node.querySelector('[data-source-id] th')?.textContent).toBe('Text omitted by the wording policy.');
  });
  test('more places sit under the questions in a closed disclosure, in document order and without rank',()=>{
    const s=sample();const first=s.view_context.sentences[0];const second={...first,id:'s2',paragraph_id:'p2',from:46,to:67,text:'A second bounded point.'};
    s.view_context.sentences.push(second);s.view_context.paragraphs.push({id:'p2',text:second.text,sentence_ids:['s2']});
    s.receipt.more_places=[
      {paragraph_id:'p2',why:'untraced_claim',why_text:'This part carries the argument, and there is no record here of where it came from.',span:{from:46,to:67},grounding:['b1'],event_ids:[12]},
      {paragraph_id:'p1',why:'declared_not_anchored',why_text:'This claim came from declared outside help and was never connected to a source.',span:{from:1,to:45},grounding:['kd'],event_ids:[12]}];
    const {node,callback}=mounted(s);const disclosure=node.querySelector<HTMLDetailsElement>('.receipt-more-places');
    expect(disclosure).not.toBeNull();expect(disclosure!.open).toBe(false);
    expect(disclosure!.querySelector('summary')?.textContent).toBe('More places to ask');
    expect(disclosure!.closest('.receipt-questions')).toBe(node.querySelector('.receipt-questions'));
    expect(disclosure!.querySelector('ol')).toBeNull();
    const items=[...disclosure!.querySelectorAll('.receipt-more-place')];
    expect(items.map(item=>item.getAttribute('data-paragraph-id'))).toEqual(['p2','p1']);
    expect(items.map(item=>item.querySelector('.receipt-label')?.textContent)).toEqual([
      s.receipt.more_places[0].why_text,s.receipt.more_places[1].why_text]);
    expect(disclosure!.textContent).not.toMatch(/(^|\s)\d+[.)]\s/);
    const buttons=disclosure!.querySelectorAll<HTMLButtonElement>('button[data-sentence-id]');
    expect(buttons).toHaveLength(2);expect(buttons[0].type).toBe('button');
    buttons[0].focus();expect(document.activeElement).toBe(buttons[0]);
    buttons[0].click();expect(callback).toHaveBeenCalledWith('s2',buttons[0]);
  });
  test('no more-places disclosure is rendered when no other grounded place exists',()=>{
    const {node}=mounted();expect(node.querySelector('.receipt-more-places')).toBeNull();
  });
  test('more-places reason text passes the wording guard',()=>{
    const s=sample();s.receipt.more_places=[{paragraph_id:'p1',why:'untraced_claim',why_text:'This was flagged.',span:{from:1,to:45},grounding:['b1'],event_ids:[12]}];
    const {node}=mounted(s);expect(node.querySelector('.receipt-more-places')?.textContent).toContain('Text omitted by the wording policy.');
  });
});
