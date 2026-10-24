// Golden-session recorder (T-015). Drives the real editor (the S1 page) in
// Chromium through every editor action of each golden script and writes
// fixtures/golden/recorded/<session_id>.json; CI regenerates these recordings.
// Run from prototype/web:
//   npm i --no-save playwright-core@1.56.1 && node golden/record.mjs [session_id ...]
// Env: GOLDEN_PYTHON, GOLDEN_ACTIONS_JSON (test only).
// CHROMIUM overrides the pinned bundled browser for debugging only; do not freeze that output.
import { createRequire } from "node:module";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const web = resolve(here, "..");
const prototype = resolve(web, "..");
const goldenDir = join(prototype, "fixtures/golden");
const outDir = join(goldenDir, "recorded");
const require = createRequire(join(web, "package.json"));
const { createServer } = await import(require.resolve("vite"));
const { chromium } = require("playwright-core");
const pwVersion = require("playwright-core/package.json").version;

const EDITOR_ACTIONS = new Set(["type_paragraph", "type", "insert", "paste", "replace", "delete", "link", "accept_suggestion"]);
const MOD = "ControlOrMeta";
const python = process.env.GOLDEN_PYTHON ?? (existsSync(join(prototype, ".venv/bin/python")) ? join(prototype, ".venv/bin/python") : "python3");

function loadActions(sessionId) {
  if (process.env.GOLDEN_ACTIONS_JSON) return JSON.parse(readFileSync(process.env.GOLDEN_ACTIONS_JSON, "utf8"));
  const out = execFileSync(python, ["-m", "golden", "actions", sessionId], {
    cwd: join(prototype, "server"),
    env: { ...process.env, ROOM_LLM: "stub" },
    encoding: "utf8",
    maxBuffer: 64 * 1024 * 1024,
  });
  return JSON.parse(out);
}

const sessions = process.argv.slice(2).length
  ? process.argv.slice(2)
  : readdirSync(goldenDir).filter((f) => f.endsWith(".yaml")).map((f) => f.slice(0, -5)).sort();

const server = await createServer({
  root: prototype,
  configFile: false,
  cacheDir: join(web, "node_modules/.vite-golden"),
  logLevel: "error",
  server: { port: 5198, strictPort: true, fs: { allow: [prototype] } },
});
await server.listen();
const url = "http://localhost:5198/spikes/S1/page/index.html";
let browser;
let context;

const call = (page, fn, ...args) => page.evaluate(([f, a]) => window.s1[f](...a), [fn, args]);

async function record(sessionId) {
  const spec = loadActions(sessionId);
  const editor = spec.actions.filter((a) => EDITOR_ACTIONS.has(a.action));
  const page = await context.newPage();
  const entries = [];
  let current = null;
  try {
    await page.goto(url);
    await page.waitForFunction(() => window.s1);
    await page.click("#editor .ProseMirror");
    let prevLen = 0;
    let prevCounts = await call(page, "counts");

    // Returns the block for paragraph id pK; creates it (Enter at the end) when new.
    async function paragraph(id, mustBeNew) {
      const m = /^p(\d+)$/.exec(id ?? "");
      if (!m) throw new Error(`bad paragraph_id ${id}`);
      const k = Number(m[1]);
      let blocks = await call(page, "blocks");
      if (k === blocks.length + 1) {
        const last = blocks[blocks.length - 1];
        await call(page, "select", last.end);
        await page.keyboard.press("Enter");
        blocks = await call(page, "blocks");
      } else if (mustBeNew && !(k === 1 && blocks.length === 1 && blocks[0].text === "")) {
        // (p1 is "new" while the document is still the single empty initial paragraph)
        throw new Error(`paragraph ${id} is not new (document has ${blocks.length})`);
      }
      const b = blocks[k - 1];
      if (!b) throw new Error(`paragraph ${id} does not exist (document has ${blocks.length})`);
      if (b.end - b.start !== b.text.length) throw new Error(`paragraph ${id} holds non-text content (hard_break?)`);
      return b;
    }
    function find(b, needle, what) {
      const i = b.text.indexOf(needle);
      if (i < 0) throw new Error(`${what} ${JSON.stringify(needle)} not found in ${JSON.stringify(b.text)}`);
      return i;
    }
    async function placeCursor(a, mustBeNew) {
      const b = await paragraph(a.paragraph_id, mustBeNew);
      let pos = b.end;
      if (a.after != null) pos = b.start + find(b, a.after, "after") + a.after.length;
      await call(page, "select", pos);
      return { b, pos };
    }
    const typeText = async (text, keys) => (keys ? page.keyboard.type(text) : page.keyboard.insertText(text));

    for (const a of editor) {
      current = a;
      let paste_id = null;
      let at = null;
      switch (a.action) {
        case "type_paragraph":
          await placeCursor(a, true);
          await typeText(a.text, a.keys);
          break;
        case "type":
          await placeCursor(a, false);
          await typeText(a.text, a.keys);
          break;
        case "insert": {
          const { pos } = await placeCursor(a, false);
          at = pos;
          for (const run of a.runs) await call(page, "insertMarked", run.text, run.kind, run.ref ?? null);
          break;
        }
        case "paste": {
          const { pos } = await placeCursor(a, false);
          at = pos;
          const before = await call(page, "pasteCount");
          await page.evaluate(async (text) => {
            await navigator.clipboard.write([new ClipboardItem({ "text/plain": new Blob([text], { type: "text/plain" }) })]);
          }, a.text);
          await page.keyboard.press(`${MOD}+v`);
          const after = await call(page, "pasteCount");
          if (after !== before + 1) throw new Error(`paste id counter went ${before} -> ${after}, expected +1`);
          paste_id = `paste_${after}`;
          break;
        }
        case "replace":
        case "delete": {
          const b = await paragraph(a.paragraph_id, false);
          const i = find(b, a.find, "find");
          await call(page, "select", b.start + i, b.start + i + a.find.length);
          if (a.action === "replace") await typeText(a.text, a.keys);
          else await page.keyboard.press("Backspace");
          break;
        }
        case "link": {
          const b = await paragraph(a.paragraph_id, false);
          if (!(await call(page, "link", b.before, { claim_id: a.claim_id, by: a.by }))) throw new Error("link did nothing");
          break;
        }
        case "accept_suggestion": {
          const b = await paragraph(a.paragraph_id, false);
          if (!(await call(page, "accept", b.before, a.claim_id, a.suggestion_id))) throw new Error("accept_suggestion did nothing");
          break;
        }
      }
      const res = await call(page, "result");
      if (!res.js_replay_equal) throw new Error("js_replay_equal is false");
      const counts = await call(page, "counts");
      const input_kind = {};
      for (const k of ["keyboard", "ime", "dictation", "replacement"]) input_kind[k] = (counts[k] ?? 0) - (prevCounts[k] ?? 0);
      entries.push({
        index: a.index,
        action: a.action,
        steps: res.steps.slice(prevLen),
        input_kind,
        doc_rev: res.steps.length,
        doc_hash: res.doc_hash,
        paste_id,
        at,
        _doc: res.doc,
      });
      prevLen = res.steps.length;
      prevCounts = counts;
    }
    current = null;
    // doc only where the builder needs it: before a non-editor action, and at the end
    entries.forEach((e, i) => {
      const next = entries[i + 1];
      const doc = e._doc;
      delete e._doc;
      if (!next || e.index + 1 !== next.index) e.doc = doc;
    });
  } catch (err) {
    console.error(`FAIL ${sessionId} action ${current ? current.index : "-"} (${current ? current.action : "setup"}): ${err.message}`);
    await page.close();
    return false;
  }
  await page.close();
  mkdirSync(outDir, { recursive: true });
  const body = {
    "x-note": "Recorded in real Chromium by prototype/web/golden/record.mjs. Regenerate after editor, schema.json or script changes. The golden test (server/tests/test_golden_sessions.py) replays these steps in Python.",
    browser: `Chromium ${browser.version()} (playwright-core ${pwVersion}, headless)`,
    session_id: sessionId,
    editor_actions_sha256: spec.editor_actions_sha256,
    actions: entries,
  };
  writeFileSync(join(outDir, `${sessionId}.json`), JSON.stringify(body, null, 1) + "\n");
  console.log(`recorded ${sessionId}: ${entries.length} editor actions`);
  return true;
}

let failed = false;
try {
  browser = await chromium.launch({ executablePath: process.env.CHROMIUM, headless: true });
  context = await browser.newContext({ permissions: ["clipboard-read", "clipboard-write"] });
  for (const s of sessions) {
    try {
      if (!(await record(s))) failed = true;
    } catch (err) {
      console.error(`FAIL ${s}: ${err.message}`);
      failed = true;
    }
  }
} finally {
  await browser?.close();
  await server.close();
}
process.exit(failed ? 1 : 0);
