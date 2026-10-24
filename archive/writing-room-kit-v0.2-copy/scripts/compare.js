#!/usr/bin/env node
/* batch report: node compare.js runs/*.json > report.md */
const fs=require('fs'),path=require('path');
const dir=path.join(__dirname);
eval(fs.readFileSync(path.join(dir,'score.js'),'utf8').replace(/if\(typeof require!=="undefined"&&require\.main===module\)\{[\s\S]*$/,''));
const files=process.argv.slice(2);
if(!files.length){console.log("usage: node compare.js runs/*.json");process.exit(0)}
const groups={};
files.forEach(f=>{const o=JSON.parse(fs.readFileSync(f,'utf8'));const r=scoreAny(o);
 const name=path.basename(f).replace(/\.json$/i,'').replace(/^example-/,'').replace(/^wr-/,'').replace(/^mx-/,'mx-');
 const persona=(name.startsWith('mx-')?'mx-'+name.slice(3).split('-')[0]:name.split('-')[0]);
 (groups[persona]=groups[persona]||[]).push({f:path.basename(f),o,r})});
let out='# Batch coherence report\n\n';
Object.keys(groups).forEach(p=>{const g=groups[p],cs=g.map(x=>x.r.composite).sort((a,b)=>a-b);
 const mean=Math.round(cs.reduce((a,b)=>a+b,0)/cs.length);
 out+='## '+p+'  (n='+g.length+')\n\ncomposite: min '+cs[0]+' · mean '+mean+' · max '+cs[cs.length-1]+'\n\n';
 const comps=['trace','cont','orphanScore','struct','traj','spread'];
 const has=g.some(x=>x.r.traj!==undefined);
 if(has){out+='| run | comp | trace | cont | orphan | struct | traj | spread | flags |\n|---|---|---|---|---|---|---|---|---|\n';
  g.forEach(x=>{out+='| '+x.f+' | '+x.r.composite+' | '+x.r.trace+' | '+x.r.cont+' | '+x.r.orphanScore+' | '+x.r.struct+' | '+x.r.traj+' | '+x.r.spread+' | '+(x.r.flags.join('; ')||'—')+' |\n'})}
 else{out+='| run | comp | eff | calib | anchor | commit | flags |\n|---|---|---|---|---|---|---|\n';
  g.forEach(x=>{out+='| '+x.f+' | '+x.r.composite+' | '+x.r.efficiency+' | '+x.r.calibration+' | '+x.r.anchoring+' | '+x.r.commitment+' | '+(x.r.flags.join('; ')||'—')+' |\n'})}
 const flagCount={};g.forEach(x=>x.r.flags.forEach(f=>{const k=f.split(/[0-9]/)[0].trim();flagCount[k]=(flagCount[k]||0)+1}));
 const top=Object.entries(flagCount).sort((a,b)=>b[1]-a[1]).slice(0,4);
 if(top.length)out+='\nMost common flags: '+top.map(x=>x[0]+' ('+x[1]+')').join(', ')+'\n';
 out+='\n'});
console.log(out);
