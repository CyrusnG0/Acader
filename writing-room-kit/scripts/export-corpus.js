/* Regenerate data/corpus.json and data/corpus-for-sims.md from the engine corpus. */
const fs=require('fs'),path=require('path'),E=require('./engine');
const dir=path.join(__dirname,'..','data');
fs.writeFileSync(path.join(dir,'corpus.json'),JSON.stringify(E.CORPUS,null,1));
let md='# Course Archive (fictional) - URBP 3010 Housing Policy Workshop\n\nAll documents, people and organisations are invented for coursework.\nEssay question: **"Should Hong Kong tighten rent control on subdivided units? Take a position and defend it with evidence from the course archive."**\n\n';
E.CORPUS.forEach(d=>{md+='### '+d.id+' - '+d.title+'  ('+d.type+')\n';d.paras.forEach((p,i)=>{md+='**'+d.id+'p'+(i+1)+'**: '+p+'\n\n'})});
fs.writeFileSync(path.join(dir,'corpus-for-sims.md'),md.trimEnd()+'\n');
console.log('exported',E.CORPUS.length,'docs');
