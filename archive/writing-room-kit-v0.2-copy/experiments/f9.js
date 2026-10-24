/* F9/F10 — the "shower thought" pair: construction direction
 * HYPOTHESIS (user): honest writers build start->finish (text grows, citations born at the frontier);
 * outsiders build end->start (finished text exists first; process is reverse-engineered from it).
 * Testable cores:
 *  F9 PHASE SEPARATION: honest INTERLEAVE queries and writing; executors run a batch job (all queries, then all typing)
 *  F10 CITATION BIRTH: honest cite-at-frontier or draft-then-cite-in-many-sittings; executor cites into a text that
 *      arrived in giant chunks (conjunction: batch-cite AND chunky growth) */
const fs=require('fs'),path=require('path');
eval(fs.readFileSync(path.join(__dirname,'..','scripts','score.js'),'utf8').replace(/if\(typeof require!=="undefined"&&require\.main===module\)\{[\s\S]*$/,''));
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}
const TOPIC_KEYS=['supply','cost','legal','berlin','enforce','tenant','nyc'];
function passagesForTopic(k){return PASSAGES.filter(p=>{const t=p.text.toLowerCase();
 switch(k){case 'supply':return /supply|elasticity|stock|contraction/.test(t);
 case 'cost':return /premium|per-square-foot|afford/.test(t);
 case 'legal':return /ordinance|initial rent|judicial|compensation|constitutional/.test(t);
 case 'berlin':return /berlin|mietendeckel|freeze/.test(t);
 case 'enforce':return /enforcement|inspection|complain/.test(t);
 case 'tenant':return /tenant|tenancy|security|queue|waiting/.test(t);
 case 'nyc':return /new york|stabilisation/.test(t);default:return false}})}
function qFromPassage(p,rng,form){const t=topTerms(p.text,8);const words=t.slice(0,5).join(' ');
 const F={wh:['what happens with '+words+'?','why does '+words+' matter?'],casual:['hmm what about '+words,'so does '+words+' actually hold?'],frag:[words+'?','and '+words+'?']};
 const pool=form==='uniform'?F.wh:F[(['wh','casual','frag'])[Math.floor(rng()*3)]];
 return pool[Math.floor(rng()*pool.length)]}
/* honest: interleaved research/write; two citation styles (as-you-go 60%, draft-then-cite 40%); bursts are MEDIUM (sittings) */
function genHonest(rng){const style=rng()<0.6?'asYouGo':'drafter';
 const queries=[],retrievals=[],hooks=[];let essay='',burstTs=[],qTs=[];
 let t=1;const nq=7+Math.floor(rng()*3);
 for(let i=0;i<nq;i++){qTs.push(t++);
  if(rng()<0.6){ // writing interlude between research
   const add=180+Math.floor(rng()*260);essay+=new Array(add).fill('w').join('')+' ';burstTs.push(t++)}}
 // assemble real essay text from retrievals for hooks
 qTs.forEach((_,i)=>{const k=TOPIC_KEYS[i%TOPIC_KEYS.length];const cand=passagesForTopic(k);
  if(cand.length&&rng()<0.85){const p=cand[Math.floor(rng()*cand.length)];queries.push({text:qFromPassage(p,rng,rng()<0.5?'casual':'wh'),mark:'DEEP',ts:qTs[i]});if(!retrievals.includes(p.pid))retrievals.push(p.pid)}});
 const frags=retrievals.map(pid=>{const p=PASSAGES.filter(x=>x.pid===pid)[0];return{pid,txt:p.text.split(/(?<=\.)\s/)[0]}});
 if(style==='asYouGo'){frags.forEach(f=>{essay+=f.txt+' ';hooks.push({passage:f.pid,pos:essay.length-60,atLen:essay.length})})}
 else{frags.forEach(f=>{essay+=f.txt+' '}); // full draft
  frags.forEach(f=>hooks.push({passage:f.pid,pos:essay.length-60,atLen:essay.length}))} // then cites in one re-read pass
 return{essay,queries,retrievals,hooks,pasteChars:0,editBursts:burstTs.length||5,_burstTs:burstTs,_style:style}}
/* executor: script phases — ALL queries first, then transcribe pre-written essay in 1-3 giant chunks, cite after */
function genExecutor(rng){const order=TOPIC_KEYS.slice(0,7);const queries=[],retrievals=[],hooks=[];let t=1;
 order.forEach(k=>{const cand=passagesForTopic(k);if(!cand.length)return;const p=cand[0];
  queries.push({text:qFromPassage(p,rng,'uniform'),mark:'DEEP',ts:t++});if(!retrievals.includes(p.pid))retrievals.push(p.pid)});
 let essay='';const burstTs=[];
 retrievals.forEach((pid,i)=>{const p=PASSAGES.filter(x=>x.pid===pid)[0];if(!p)return;
  essay+=p.text.split(/(?<=\.)\s/)[0]+' ';
  if(i%3===2||i===retrievals.length-1)burstTs.push(t++)}); // 1-3 giant chunks AFTER queries
 retrievals.forEach(pid=>{const p=PASSAGES.filter(x=>x.pid===pid)[0];hooks.push({passage:pid,pos:essay.length-60,atLen:essay.length})});
 return{essay,queries,retrievals,hooks,pasteChars:0,editBursts:burstTs.length,_burstTs:burstTs}}
/* F9: interleave = # of query<->burst alternations on the merged timeline (needs >=4 events) */
function interleave(s){const ev=s.queries.map(q=>({t:q.ts,k:'q'})).concat((s._burstTs||[]).map(t=>({t:t,k:'b'})));
 ev.sort((a,b)=>a.t-b.t);let alt=0;for(let i=1;i<ev.length;i++)if(ev[i].k!==ev[i-1].k)alt++;return alt}
/* F10: citation birth = batchCite fraction x chunkiness(mean burst chars) */
function citeBirth(s){const fin=s.essay.length;const batch=s.hooks.filter(h=>(h.atLen||0)>=fin*0.95).length/Math.max(s.hooks.length,1);
 const nb=Math.max(s.editBursts,1),chunk=fin/nb;return batch*(chunk/400)}
const R=10,N=16,res={F9:[],F10:[]};const raw={F9:[],F10:[]};
for(let r=1;r<=R;r++){const rng=mulberry32(2000+r*31);
 for(let i=0;i<N;i++){const H=genHonest(rng),E=genExecutor(rng);
  res.F9.push([interleave(H),interleave(E)]);res.F10.push([citeBirth(H),citeBirth(E)])}}
function verdict(name,pairs){const m=v=>v.reduce((a,b)=>a+b,0)/v.length;
 const a=pairs.map(x=>x[0]),b=pairs.map(x=>x[1]);const th=(m(a)+m(b))/2;let right=0;
 pairs.forEach(([h,e])=>{if(h>th)right++;if(e<=th)right++});const acc=right/(pairs.length*2);
 console.log(name.padEnd(34)+'honest='+m(a).toFixed(2).padEnd(8)+'executor='+m(b).toFixed(2).padEnd(11)+'acc='+acc.toFixed(2).padEnd(6)+(acc>=0.8?'STAY':'WEAK/RETHINK'));
 // drafter sub-check: do draft-then-cite honests survive?
 return acc}
const a9=verdict('F9 interleave (phases)',res.F9);
const a10=verdict('F10 citation birth (conj)',res.F10);
const H=res.F9.map(x=>x[0]).reduce((a,b)=>a+b,0)/res.F9.length;
console.log('\nnote: honest pool mixes as-you-go and draft-then-cite styles; executor = phase-separated transcriber');
console.log('raw saved');fs.writeFileSync(path.join(__dirname,'f9-results.json'),JSON.stringify({F9:res.F9,F10:res.F10},null,1));
