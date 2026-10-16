/* The only way a run obtains retrievals.
   node scripts/librarian.js <draft.json> "question" [--id session-id] */
const fs=require('fs'),E=require('./engine');
const a=process.argv.slice(2);
if(a.length<2){console.log('usage: node librarian.js draft.json "question" [--id ID]');process.exit(1)}
const file=a[0],q=a[1],i=a.indexOf('--id'),id=i>0?a[i+1]:'draft';
let d=fs.existsSync(file)?JSON.parse(fs.readFileSync(file,'utf8')):
 {version:'0.1',session_id:id,created:new Date().toISOString(),task:'URBP3010-w9-essay',notes:'',essay:'',queries:[],retrievals:[],hooks:[],pasteChars:0,editBursts:0};
const ts=d.queries.length+1,m=E.classify(q);
if(m==='CONCLUSION'){
  d.queries.push({text:q,mark:m,ts});
  console.log("LIBRARIAN: I can't conclude, argue or take a position. Tell me which claim you want to check and I will find where the archive speaks to it.");
}else{
  const r=E.retrieve(q);
  if(!r){d.queries.push({text:q,mark:'MISS',ts});console.log('LIBRARIAN: No passage matches. Try different words.')}
  else{d.queries.push({text:q,mark:m,ts});d.retrievals.push(r.passage.pid);
    console.log('['+r.passage.pid+'] ('+r.passage.dtitle+')\n'+r.passage.text)}
}
fs.writeFileSync(file,JSON.stringify(d,null,1));
