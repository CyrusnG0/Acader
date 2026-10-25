// Local synthetic review only. Generate actual stub receipts, then launch Vite.
import { spawnSync, spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname, delimiter } from 'node:path';
const web=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const prototype=resolve(web,'..');
const python=process.env.GOLDEN_PYTHON||(existsSync(resolve(prototype,'.venv/bin/python'))?resolve(prototype,'.venv/bin/python'):'python3');
const output=resolve(web,'public/review/golden-receipts.json');
const result=spawnSync(python,['-m','golden','export',output],{cwd:prototype,env:{...process.env,ROOM_LLM:'stub',PYTHONPATH:[resolve(prototype,'server'),resolve(prototype,'..'),process.env.PYTHONPATH].filter(Boolean).join(delimiter)},stdio:'inherit'});
if(result.status!==0){console.error('Could not prepare the synthetic gallery. Install the prototype locked Python dependencies, then retry.');process.exit(result.status||1)}
const vite=spawn(process.execPath,[resolve(web,'node_modules/vite/bin/vite.js'),...process.argv.slice(2)],{cwd:web,stdio:'inherit'});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>vite.kill(signal));
vite.on('exit',code=>process.exit(code||0));
