import type { GoldenSession, SentenceView } from './types';
import { receiptText } from './render';

function text<K extends keyof HTMLElementTagNameMap>(tag:K,value:string,cls?:string):HTMLElementTagNameMap[K]{const e=document.createElement(tag);e.textContent=receiptText(value);if(cls)e.className=cls;return e}
function dateHour(value:string):string{const d=new Date(value);return Number.isNaN(d.valueOf())?'Date unavailable':new Intl.DateTimeFormat('en-GB',{day:'numeric',month:'short',year:'numeric',hour:'2-digit',timeZone:'UTC',hour12:false}).format(d)+' UTC'}
export function createChainDialog(session:GoldenSession):{element:HTMLDialogElement;open:(id:string,trigger:HTMLElement)=>void}{
 const dialog=document.createElement('dialog');dialog.className='chain-dialog';dialog.setAttribute('aria-labelledby','chain-title');let opener:HTMLElement|null=null;
 const close=()=>{dialog.close();opener?.focus()};dialog.addEventListener('cancel',()=>{queueMicrotask(()=>opener?.focus())});
 function show(sentence:SentenceView){
  dialog.replaceChildren();const header=text('header','');header.className='chain-dialog-header';const title=text('h2','This sentence’s chain');title.id='chain-title';title.tabIndex=-1;
  const button=text('button','Back to the receipt');button.type='button';button.addEventListener('click',close);header.append(title,button);dialog.append(header);
  dialog.append(text('p','Synthetic evidence from the recorded golden session.','receipt-label receipt-muted'));
  const final=text('blockquote',sentence.text,'chain-final');dialog.append(final);
  const steps=text('ol','','chain-steps');
  for(const step of sentence.chain.steps){const li=text('li','');li.dataset.evidenceKind=step.kind;li.dataset.evidenceId=step.id;li.append(text('h3',step.label),text('p',step.text,'chain-evidence-text'),text('p',step.relationship,'receipt-label receipt-muted'));
   const refs=text('ul','','chain-event-refs');for(const ref of step.events)refs.append(text('li',`Event ${ref.seq} · ${dateHour(ref.at)}`));if(!step.events.length)refs.append(text('li','No matching event is available.'));li.append(refs);steps.append(li)}
  dialog.append(steps);for(const note of sentence.chain.notes)dialog.append(text('p',note,'chain-note'));
  const history=text('section','');history.append(text('h3','Recorded draft spans'),text('p',sentence.chain.history_note,'receipt-label receipt-muted'));
  if(!sentence.chain.history.length)history.append(text('p','No supported draft history is available.'));
  for(const version of sentence.chain.history){const article=text('article','','chain-version');article.dataset.docRev=String(version.doc_rev);article.append(text('h4',`Document revision ${version.doc_rev}`),text('p',version.text,'chain-evidence-text'));if(version.removed)article.append(text('p',`Removed: ${version.removed}`));if(version.added)article.append(text('p',`Added: ${version.added}`));for(const ref of version.events)article.append(text('p',`Event ${ref.seq} · ${dateHour(ref.at)}`,'receipt-label receipt-muted'));history.append(article)}
  dialog.append(history);dialog.showModal();title.focus();
 }
 return {element:dialog,open(id,trigger){const s=session.view_context.sentences.find(v=>v.id===id);if(!s)return;opener=trigger;show(s)}};
}
