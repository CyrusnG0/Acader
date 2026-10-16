/* kit self-test: engine behaviour + score separation */
const fs=require('fs'),path=require('path');
eval(fs.readFileSync(path.join(__dirname,'score.js'),'utf8').replace(/if\(typeof require!=="undefined"&&require\.main===module\)\{[\s\S]*$/,''));
let fail=0;const t=(name,cond)=>{console.log((cond?'PASS ':'FAIL ')+name);if(!cond)fail++};
t('classify CONCLUSION',classify("what should I argue in my essay")==="CONCLUSION");
t('classify BROAD',classify("rent")==="BROAD");
t('classify FACT',classify("does the ordinance cap initial rents")==="FACT");
t('classify DEEP',classify("why does enforcement miss the newest arrivals")==="DEEP");
t('retrieve supply->D6',(retrieve("what happens to supply under a hard cap on rent levels")||{}).passage?.pid?.startsWith("D6"));
t('retrieve berlin->D7',(retrieve("berlin rent freeze outcome")||{}).passage?.pid?.startsWith("D7"));
t('retrieve miss->null',retrieve("purple elephant quantum jump")===null);
const S=require('fs').readdirSync(path.join(__dirname,'..','sessions')).filter(f=>f.endsWith('.json')).map(f=>({f,r:scoreSession(JSON.parse(fs.readFileSync(path.join(__dirname,'..','sessions',f),'utf8')))}));
S.forEach(x=>console.log('  '+x.f.padEnd(24)+'composite='+x.r.composite));
const g=n=>S.find(x=>x.f.includes(n)).r.composite;
t('honest separates from pasted',g('honest')-g('pasted')>50);
t('hybrid strictly between',g('pasted')<g('hybrid')&&g('hybrid')<g('honest'));
t('lazy below honest',g('lazy')<g('honest'));

/* tooling: librarian -> finalize -> validate round trip, and forgery rejection */
const cp=require('child_process'),os=require('os');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'wr-')),draft=path.join(tmp,'d.json'),sd=__dirname;
const run=(f,args)=>cp.spawnSync('node',[path.join(sd,f),...args],{encoding:'utf8'});
run('librarian.js',[draft,'what happens to supply under a hard cap on rent levels','--id','t']);
run('librarian.js',[draft,'what should I argue in my essay']);
run('librarian.js',[draft,'purple elephant quantum jump']);
const dj=JSON.parse(fs.readFileSync(draft,'utf8'));
t('librarian records retrieval, CONCLUSION and MISS',dj.retrievals.length===1&&dj.queries.map(q=>q.mark).join()==='DEEP,CONCLUSION,MISS');
fs.writeFileSync(path.join(tmp,'e.txt'),'Hard caps shrink stock [D6p1]. '+'More words here. '.repeat(40));
const fo=run('finalize.js',[draft,'--essay',path.join(tmp,'e.txt'),'--arm','A9','--n','1','--struct','pasted','--out',tmp]);
const rf=JSON.parse(fs.readFileSync(path.join(tmp,'A9-1.json'),'utf8'));
t('finalize parses hook and sets pasted structure',rf.hooks.length===1&&rf.hooks[0].passage==='D6p1'&&rf.pasteChars>=300&&rf.editBursts<=3);
t('validate passes an engine-made run',run('validate.js',[path.join(tmp,'A9-1.json')]).status===0);
rf.retrievals.push('D10p3');fs.writeFileSync(path.join(tmp,'forged.json'),JSON.stringify(rf));
t('validate rejects a forged retrieval',run('validate.js',[path.join(tmp,'forged.json')]).status===1);
process.exit(fail?1:0);
