/* Turn a draft plus an essay into a run file. Structure comes from the arm rule, never from the worker.
   node finalize.js draft.json --essay essay.txt --arm A4 --n 1 --struct typed|pasted|retyped [--notes notes.txt] [--writer name] [--out runs] */
const fs=require('fs'),path=require('path');
const a=process.argv.slice(2),g=k=>{const i=a.indexOf('--'+k);return i>=0?a[i+1]:null};
if(!a[0]||!g('essay')||!g('arm')||!g('struct')){console.log('usage: see header');process.exit(1)}
const d=JSON.parse(fs.readFileSync(a[0],'utf8')),essay=fs.readFileSync(g('essay'),'utf8').trim();
const words=essay.split(/\s+/).length,st=g('struct'),n=g('n')||'1';
d.essay=essay;d.notes=g('notes')?fs.readFileSync(g('notes'),'utf8').trim():(d.notes||'');
d.hooks=[];const re=/\[(D\d+p\d+)\]/g;let m;while((m=re.exec(essay)))d.hooks.push({passage:m[1],pos:m.index});
if(st==='pasted'){d.pasteChars=essay.length+100;d.editBursts=1+(words%3)}
else{d.pasteChars=0;d.editBursts=Math.max(6,Math.round(words/60))}
d.arm=g('arm');d.writer=g('writer')||'claude-worker';d.struct_rule=st;
d.session_id=g('arm')+'-'+n;
const out=path.join(g('out')||'runs',d.session_id+'.json');
fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(d,null,1));
console.log('wrote '+out+' hooks='+d.hooks.length+' words='+words);
