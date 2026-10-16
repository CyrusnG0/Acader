/* Hard checks on run files. node validate.js runs/*.json */
const fs=require('fs'),E=require('./engine');
let bad=0;
const pid=new Set(E.PASSAGES.map(p=>p.pid));
const ALLTXT=E.PASSAGES.map(p=>p.text).join(' ');
const LOWER={test:w=>new RegExp('(^|[^A-Za-z])'+w+'([^A-Za-z]|$)').test(ALLTXT)};
function leaks(essay,rets){
  const keep=new Set(),other=new Set(),df={};
  const toks=t=>(t.match(/\d[\d,.]*\d|[A-Z][a-z]{3,}/g)||[]).filter(x=>/\D/.test(x)||x.length>=2);
  E.PASSAGES.forEach(p=>{const u=new Set(toks(p.text+(rets.includes(p.pid)?' '+p.dtitle:'')));u.forEach(x=>{df[x]=(df[x]||0)+1;(rets.includes(p.pid)?keep:other).add(x)})});
  // only specific facts: numbers, and names/terms found in at most 2 passages
  return [...new Set(toks(essay.replace(/\[D\d+p\d+\]/g,' ')))].filter(x=>other.has(x)&&!keep.has(x)&&(/\d/.test(x)||(df[x]<=4&&!LOWER.test(x.toLowerCase()))));
}
process.argv.slice(2).forEach(f=>{
  const errs=[],warns=[];let s;
  try{s=JSON.parse(fs.readFileSync(f,'utf8'))}catch(e){console.log('FAIL '+f+' bad JSON');bad++;return}
  ['session_id','essay','queries','retrievals','hooks'].forEach(k=>{if(s[k]==null)errs.push('missing '+k)});
  if(!errs.length){
    s.retrievals.forEach(p=>{if(!pid.has(p))errs.push('unknown passage '+p)});
    // replay: each retrieval must be reproducible from a query, in order
    const replay=[];s.queries.forEach(q=>{if(E.classify(q.text)==='CONCLUSION')return;const r=E.retrieve(q.text);if(r)replay.push(r.passage.pid)});
    if(JSON.stringify(replay)!==JSON.stringify(s.retrievals))errs.push('retrievals not reproducible from queries (replay '+replay.length+' vs '+s.retrievals.length+')');
    const inl=[...s.essay.matchAll(/\[(D\d+p\d+)\]/g)].map(m=>m[1]).sort().join(),hk=s.hooks.map(h=>h.passage).sort().join();
    if(inl!==hk)errs.push('hooks do not match inline [DxPy] markers');
    const lk=leaks(s.essay,s.retrievals);
    if(lk.length){(s.arm==='A1'?errs:warns).push('possible use of unretrieved facts: '+lk.slice(0,8).join(', ')+(s.arm==='A1'?' [invalid_adherence]':''))}
  }
  console.log((errs.length?'FAIL ':'ok   ')+f+(errs.length?'  '+errs.join('; '):'')+(warns.length?'  WARN '+warns.join('; '):''));
  if(errs.length)bad++;
});
process.exit(bad?1:0);
