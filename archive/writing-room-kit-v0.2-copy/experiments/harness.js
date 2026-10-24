/* experiment harness v2 — feature-by-feature differentiation tests
 * same generator writes honest & executor sims = conservative test
 * v2 fixes: accuracy formula, F2 number-mutation variants, F7 '?' forms, honest realism (orphans/re-retrievals/return arcs) */
const fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..');
eval(fs.readFileSync(path.join(ROOT,'scripts','score.js'),'utf8').replace(/if\(typeof require!=="undefined"&&require\.main===module\)\{[\s\S]*$/,''));
function engineScore(s){return scoreSession(s)}
function mulberry32(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}

const TOPIC_KEYS=['supply','cost','legal','berlin','enforce','tenant','nyc'];
function passagesForTopic(k){return PASSAGES.filter(p=>{const t=p.text.toLowerCase();
 switch(k){case 'supply':return /supply|elasticity|stock|contraction/.test(t);
 case 'cost':return /premium|per-square-foot|afford/.test(t);
 case 'legal':return /ordinance|initial rent|judicial|compensation|constitutional/.test(t);
 case 'berlin':return /berlin|mietendeckel|freeze/.test(t);
 case 'enforce':return /enforcement|inspection|complain/.test(t);
 case 'tenant':return /tenant|tenancy|security|queue|waiting/.test(t);
 case 'nyc':return /new york|stabilisation/.test(t);
 default:return false}})}
function qFromPassage(p,rng,form){const t=topTerms(p.text,8);const words=t.slice(0,5).join(' ');
 const F={wh:['what happens with '+words+'?','why does '+words+' matter?','how far does '+words+' hold?'],
  casual:['hmm what about '+words,'so does '+words+' actually hold?','isn\'t there a risk with '+words],
  frag:[words+'?','and '+words+'?','what about the '+words+' side?']};
 const pool=form==='uniform'?F.wh:F[(['wh','casual','frag'])[Math.floor(rng()*3)]];
 return pool[Math.floor(rng()*pool.length)]}

/* F2: per-student variant = seeded number mutation of every passage */
function mutatedCorpus(seed){const rng=mulberry32(seed);
 return PASSAGES.map(p=>({pid:p.pid,text:p.text.replace(/\d+(\.\d+)?/g,m=>{const v=parseFloat(m);const nv=v<10?Math.round((v*(1+0.15+0.4*rng()))*10)/10:Math.round(v*(1+0.15+0.4*rng()));return String(nv)})}))}
function hookVerbatim(sess,corpus){const big=new Set();
 corpus.forEach(p=>{const ws=p.text.toLowerCase().replace(/[^a-z ]/g,'').split(/\s+/);
  for(let i=0;i<ws.length-4;i++)big.add(ws.slice(i,i+5).join(' '))});
 let hit=0;sess.hooks.forEach(h=>{const win=sess.essay.toLowerCase().replace(/[^a-z ]/g,'').split(/\s+/);
  const around=win.slice(Math.max(0,Math.floor(h.pos/6)-15),Math.floor(h.pos/6)+15);
  for(let i=0;i<around.length-4;i++){if(big.has(around.slice(i,i+5).join(' '))){hit++;break}}});
 return sess.hooks.length?hit/sess.hooks.length:0}

/* honest: return arcs, re-asks, misses, orphans, re-retrievals; essay copied from ITS OWN variant corpus */
function genHonest(rng,opt){opt=opt||{};const VC=opt.corpus||PASSAGES;
 const jumpP=0.5+rng()*0.3,retP=0.3+rng()*0.35,reaskP=0.2+rng()*0.3,missP=0.1+rng()*0.15,citeP=0.6+rng()*0.25;
 const queries=[],retrievals=[],hooks=[];let miss=0,lastK=null;const vis={};
 const nq=7+Math.floor(rng()*3);
 for(let i=0;i<nq;i++){
  if(rng()<missP){queries.push({text:'anything newer on housing stock turnover?',mark:'MISS',ts:i+1});miss++;continue}
  let k,form='wh';
  const seenKeys=Object.keys(vis);
  if(lastK&&rng()<reaskP){k=lastK;form='frag'} // re-ask same thread, new angle
  else if(seenKeys.length&&rng()<retP){k=seenKeys[Math.floor(rng()*seenKeys.length)];form='casual'} // return arc
  else{k=TOPIC_KEYS[Math.floor(rng()*TOPIC_KEYS.length)];if(rng()<jumpP)k=TOPIC_KEYS[Math.floor(rng()*TOPIC_KEYS.length)];form=rng()<0.5?'casual':'wh'}
  const cand=passagesForTopic(k);if(!cand.length)continue;
  const p=cand[Math.floor(rng()*cand.length)];
  queries.push({text:qFromPassage(p,rng,form),mark:form==='wh'&&rng()<0.5?'FACT':'DEEP',ts:i+1});
  vis[k]=i;lastK=k;
  if(rng()<0.85&&!retrievals.includes(p.pid))retrievals.push(p.pid);
  if(rng()<0.1&&!retrievals.includes(p.pid))retrievals.push(p.pid)} // re-retrieval
 // essay: verbatim fragments from the VARIANT passages it retrieved + meta lines
 const frags=[];
 retrievals.forEach(pid=>{if(rng()<citeP){const p=VC.filter(x=>x.pid===pid)[0]||PASSAGES.filter(x=>x.pid===pid)[0];
  const ss=p.text.split(/(?<=\.)\s/);frags.push({pid,txt:ss[Math.floor(rng()*ss.length)]})}});
 const META=['I keep coming back to this.','The hard question is whether that holds for the tail.','This is where I changed my mind.','Worth noting the tension here.'];
 let essay='Hong Kong should not add a hard cap on initial rents; the archive keeps pointing to tenure security and a light band instead. ';
 frags.forEach(f=>{essay+=(rng()<0.3?META[Math.floor(rng()*META.length)]+' ':'')+f.txt+' ';hooks.push({passage:f.pid,pos:essay.length-40})});
 return{essay,queries,retrievals,hooks,pasteChars:0,editBursts:6+Math.floor(rng()*9),_miss:miss}}

/* executor: AI pre-plans everything on the BASE corpus; DFS order, uniform forms, zero waste */
function genExecutor(rng){const order=TOPIC_KEYS.slice(0,6+Math.floor(rng()*3));
 const queries=[],retrievals=[],hooks=[];const done={};
 order.forEach((k,i)=>{if(done[k])return;done[k]=1;
  const cand=passagesForTopic(k);if(!cand.length)return;
  const p=cand[0];
  queries.push({text:qFromPassage(p,rng,'uniform'),mark:i<2?'FACT':'DEEP',ts:i+1});
  if(!retrievals.includes(p.pid))retrievals.push(p.pid)});
 let essay='The evidence supports a measured position. ';
 retrievals.forEach(pid=>{const p=PASSAGES.filter(x=>x.pid===pid)[0];if(!p)return;
  const ss=p.text.split(/(?<=\.)\s/);essay+='Therefore, the record shows: '+ss[0]+' ';
  hooks.push({passage:pid,pos:essay.length-60})});
 essay+='In conclusion, a balanced instrument is preferable.';
 return{essay,queries,retrievals,hooks,pasteChars:0,editBursts:5+Math.floor(rng()*10),_miss:0}}

/* hybrid: honest trail, outsider-AI essay (generic register, corpus drift) */
function genHybrid(rng){const h=genHonest(rng);
 h.essay='The debate over SDU rent control in Hong Kong raises fundamental questions about housing justice. Moreover, empirical evidence from comparable jurisdictions suggests that rent regulation entails significant tradeoffs between affordability and housing supply dynamics. Critics contend that well-intentioned interventions may inadvertently exacerbate existing market distortions, particularly for vulnerable populations. Furthermore, policymakers must carefully weigh distributional considerations against efficiency concerns. Ultimately, a nuanced approach balancing competing objectives remains essential for sustainable housing policy. In conclusion, policy should balance tenant protection with market stability.';
 h.hooks=h.hooks.slice(0,3);return h}

function formDiv(sess){const c=sess.queries.filter(q=>q.text).length;if(!c)return 0;
 const canon=sess.queries.filter(q=>/^(what|why|how|does|is|are|can|which)\b/i.test(q.text)&&/\?\s*$/.test(q.text)).length;
 return 1-canon/c}
function waste(sess){const orph=sess.retrievals.length?(sess.retrievals.filter(p=>!sess.hooks.some(h=>h.passage===p)).length/sess.retrievals.length):0;
 return (sess._miss||0)/Math.max(sess.queries.length,1)*0.5+orph*0.5}

const ROUNDS=10,N=8;
const feats={
 'F1 aliveness (returns+reasks)':{hi:true,fn:s=>{const a=engineScore(s).detail.aliveness;return a.returns+a.reasks}},
 'F2 hook-variant verbatim':{hi:true,fn:s=>s._hv},
 'F7 form diversity':{hi:true,fn:s=>formDiv(s)},
 'F8 waste rate':{hi:true,fn:s=>waste(s)},
 'F3 trajectory':{hi:true,fn:s=>engineScore(s).traj},
 'F4 spread':{hi:true,fn:s=>engineScore(s).spread},
 'F6 continuity':{hi:true,fn:s=>engineScore(s).cont}
};
const res={},raw={};Object.keys(feats).forEach(k=>{res[k]=[];raw[k]=[]});
const hybridCont=[];const traceDiff=[];
for(let r=1;r<=ROUNDS;r++){const rng=mulberry32(1000+r*77);const VC=mutatedCorpus(r*13);
 for(let i=0;i<N;i++){
  const H=genHonest(rng,{corpus:VC}),E=genExecutor(rng);
  H._hv=hookVerbatim(H,VC);E._hv=hookVerbatim(E,VC);
  Object.keys(feats).forEach(k=>{res[k].push([feats[k].fn(H),feats[k].fn(E)]);raw[k].push({r,h:feats[k].fn(H),e:feats[k].fn(E)})});
  if(r<=3)hybridCont.push(engineScore(genHybrid(rng)).cont);
 }}
console.log('feature'.padEnd(30)+'honest'.padEnd(9)+'executor'.padEnd(10)+'acc'.padEnd(7)+'verdict');
const out={};
Object.keys(feats).forEach(k=>{const a=res[k].map(x=>x[0]),b=res[k].map(x=>x[1]);
 const m=v=>v.reduce((x,y)=>x+y,0)/v.length;const th=(m(a)+m(b))/2;
 let right=0;res[k].forEach(([h,e])=>{if(h>th)right++;if(e<=th)right++});
 const acc=right/(res[k].length*2);
 out[k]={honest:+m(a).toFixed(2),executor:+m(b).toFixed(2),accuracy:+acc.toFixed(2),direction:m(a)>m(b)?'honest-high':'executor-high'};
 console.log(k.padEnd(30)+m(a).toFixed(2).padEnd(9)+m(b).toFixed(2).padEnd(10)+acc.toFixed(2).padEnd(7)+(acc>=0.8?(m(a)>m(b)?'STAY (honest-high)':'STAY (executor-high? inspect)'):'REMOVE/WEAK'))});
const mh=hybridCont.reduce((a,b)=>a+b,0)/hybridCont.length;
console.log('\nhybrid continuity mean='+mh.toFixed(1)+' vs honest '+out['F6 continuity'].honest+' (hybrid separation '+(out['F6 continuity'].honest-mh).toFixed(0)+' pts — the hybrid kill-signal)');
fs.writeFileSync(path.join(__dirname,'results.json'),JSON.stringify({summary:out,raw:raw,hybridCont:hybridCont.map(v=>+v.toFixed(1))},null,1));
console.log('results.json written');
