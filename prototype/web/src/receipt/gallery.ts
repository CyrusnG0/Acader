import type { GoldenGallery, GoldenSession } from './types';
import { renderReceipt, receiptText } from './render';
import { createChainDialog } from './chain';
import './gallery.css';

function el<K extends keyof HTMLElementTagNameMap>(tag:K,value?:string,cls?:string):HTMLElementTagNameMap[K]{const e=document.createElement(tag);if(value)e.textContent=receiptText(value);if(cls)e.className=cls;return e}
function status(s:GoldenSession):string{return s.receipt.status==='questions_pending'?'Questions pending':s.receipt.status==='replay_mismatch'?'Browser copy used':'Ready'}
export function renderGallery(data:GoldenGallery,target:HTMLElement):void{
 if(data.schema_version!==1||data.synthetic!==true||!Array.isArray(data.sessions))throw new Error('Review data unavailable');
 target.replaceChildren();const sessions=[...data.sessions].sort((a,b)=>a.view_context.header.student_name.localeCompare(b.view_context.header.student_name,'en'));
 const skip=el('a','Skip to the receipt','gallery-skip');skip.href='#receipt-heading';target.append(skip);
 const header=el('header',undefined,'gallery-header');header.append(el('strong','The Writing Room'),el('span','Synthetic review gallery · teacher view','receipt-label receipt-muted'));
 const theme=el('button','Dark theme');theme.type='button';const setTheme=(dark:boolean)=>{document.documentElement.dataset.theme=dark?'dark':'light';theme.textContent=dark?'Light theme':'Dark theme';theme.setAttribute('aria-pressed',String(dark))};setTheme(document.documentElement.dataset.theme==='dark'||matchMedia('(prefers-color-scheme: dark)').matches);theme.addEventListener('click',()=>setTheme(document.documentElement.dataset.theme!=='dark'));header.append(theme);target.append(header);
 const navigation=el('details',undefined,'gallery-submissions');navigation.append(el('summary',`Sample submissions (${sessions.length})`));const table=el('table');table.append(el('caption','Alphabetical sample submissions'));
 const head=el('thead');const headrow=el('tr');for(const label of ['Student','Status']){const th=el('th',label);th.scope='col';headrow.append(th)}head.append(headrow);table.append(head);const body=el('tbody');
 for(const session of sessions){const row=el('tr');const name=el('td');const link=el('a',session.view_context.header.student_name);link.href='?session='+encodeURIComponent(session.session_id);link.dataset.sessionId=session.session_id;name.append(link);row.append(name,el('td',status(session)));body.append(row)}table.append(body);navigation.append(table);target.append(navigation);
 const requested=new URLSearchParams(location.search).get('session');const session=sessions.find(s=>s.session_id===requested)||sessions.find(s=>s.session_id==='honest-nursing')||sessions[0];
 if(!session){target.append(el('p','No synthetic receipts are available.'));return}
 const chain=createChainDialog(session);const article=renderReceipt(session,(id,trigger)=>chain.open(id,trigger));const heading=article.querySelector('h1');if(heading){heading.id='receipt-heading';heading.tabIndex=-1}target.append(article,chain.element);
 const caption=el('p','Development gallery only. Every session is synthetic, with deterministic test questions. No student data, release controls or production access are implemented.','gallery-caption receipt-label receipt-muted');target.append(caption);
}
const prior=new Map<HTMLDetailsElement,boolean>();window.addEventListener('beforeprint',()=>{document.querySelectorAll<HTMLDetailsElement>('.receipt-document details').forEach(d=>{if(!prior.has(d))prior.set(d,d.open);d.open=true})});window.addEventListener('afterprint',()=>{prior.forEach((open,d)=>d.open=open);prior.clear()});
