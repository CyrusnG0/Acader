/* Loads the scoring engine from score.js without forking it. */
const fs=require('fs'),path=require('path');
const src=fs.readFileSync(path.join(__dirname,'score.js'),'utf8')
  .replace(/if\(typeof require!=="undefined"&&require\.main===module\)\{[\s\S]*$/,'');
module.exports=new Function(src+';return {CORPUS,PASSAGES,cwords,topTerms,classify,retrieve,scoreSession};')();
