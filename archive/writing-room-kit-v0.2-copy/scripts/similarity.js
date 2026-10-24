#!/usr/bin/env node
/* collusion screen: 3-word shingle Jaccard across essays. node similarity.js runs/*.json */
const fs=require('fs'),path=require('path');
const files=process.argv.slice(2);
if(files.length<2){console.log("usage: node similarity.js a.json b.json ...  (reports pairs with overlap > 0.35)");process.exit(0)}
const sh=t=>{const w=(t||"").toLowerCase().match(/[a-z0-9']{3,}/g)||[];const s=new Set();for(let i=0;i<w.length-2;i++)s.add(w.slice(i,i+3).join(' '));return s};
const docs=files.map(f=>({f:path.basename(f),s:sh(JSON.parse(fs.readFileSync(f,'utf8')).essay)}));
let hits=0;
for(let i=0;i<docs.length;i++)for(let j=i+1;j<docs.length;j++){const a=docs[i].s,b=docs[j].s;let inter=0;a.forEach(x=>{if(b.has(x))inter++});
 const jac=a.size+b.size?inter/(a.size+b.size-inter):0;
 if(jac>0.35){hits++;console.log('SIMILAR '+Math.round(jac*100)+'%  '+docs[i].f+'  <->  '+docs[j].f)}}
if(!hits)console.log('no suspicious overlap (>35%) across '+docs.length+' essays');
