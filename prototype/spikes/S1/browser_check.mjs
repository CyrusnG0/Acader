// Spike S1, real-browser pass: drive the real editor in Chromium with
// Playwright (real keystrokes, IME via CDP, the real clipboard, HTML5
// drag-and-drop, an extension-style DOM edit), check the marks, and write the
// recorded steps to fixtures/replay/s1_browser_steps.json, which the Python
// replay test also replays (server/tests/test_replay_s1.py).
//
// Not part of CI (needs a Chromium binary). Run from prototype/web:
//   npm i --no-save playwright-core@1.56.1
//   CHROMIUM=/path/to/chrome node ../spikes/S1/browser_check.mjs
// CHROMIUM defaults to Playwright's cached "Chrome for Testing" if present.
import { createRequire } from "node:module";
import { existsSync, readdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const prototype = resolve(here, "../..");
const web = join(prototype, "web");
const require = createRequire(join(web, "package.json"));
const { createServer } = await import(require.resolve("vite"));
const { chromium } = require("playwright-core");

function defaultChromium() {
  const cache = join(homedir(), "Library/Caches/ms-playwright");
  if (!existsSync(cache)) return undefined;
  const dirs = readdirSync(cache).filter((d) => /^chromium-\d+$/.test(d)).sort().reverse();
  for (const d of dirs) {
    const p = join(cache, d, "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");
    if (existsSync(p)) return p;
  }
  return undefined;
}

const server = await createServer({
  root: prototype,
  configFile: false,
  cacheDir: join(web, "node_modules/.vite-s1"),
  logLevel: "error",
  server: { port: 5199, strictPort: true, fs: { allow: [prototype] } },
});
await server.listen();
const url = "http://localhost:5199/spikes/S1/page/index.html";

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM ?? defaultChromium(), headless: true });
const context = await browser.newContext({ permissions: ["clipboard-read", "clipboard-write"] });
const MOD = "ControlOrMeta";

const results = [];
const failures = [];

async function fresh() {
  const page = await context.newPage();
  await page.goto(url);
  await page.waitForFunction(() => window.s1);
  await page.click("#editor .ProseMirror");
  return page;
}

const R = (text, origin, ref = null) => [text, origin, ref];

async function check(name, page, expected, extra = () => true, expectedLinks = undefined) {
  const got = await page.evaluate(() => window.s1.runs());
  const gotLinks = await page.evaluate(() => window.s1.links());
  const res = await page.evaluate(() => window.s1.result());
  const counts = await page.evaluate(() => window.s1.counts());
  const linksOk = expectedLinks === undefined || JSON.stringify(gotLinks) === JSON.stringify(expectedLinks);
  const ok = JSON.stringify(got) === JSON.stringify(expected) && linksOk && res.js_replay_equal && extra(counts, got);
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}`);
  if (!ok) {
    failures.push(name);
    console.log("   expected", JSON.stringify(expected));
    if (expectedLinks !== undefined) console.log("   links expected", JSON.stringify(expectedLinks), "got", JSON.stringify(gotLinks));
    console.log("   got     ", JSON.stringify(got), "counts", JSON.stringify(counts), "js_replay_equal", res.js_replay_equal);
  }
  results.push({ name, start: res.start, steps: res.steps, doc: res.doc, doc_hash: res.doc_hash, counts, passed: ok });
  await page.close();
}

const C1 = { claim_id: "c1", by: "student" };
const C2 = { claim_id: "c2", by: "student" };
const s1 = (page, fn, ...args) => page.evaluate(([f, a]) => window.s1[f](...a), [fn, args]);

// 1. Keyboard typing inside a quote span.
{
  const p = await fresh();
  await s1(p, "insertQuote", "abcdef");
  await s1(p, "select", 4);
  await p.keyboard.type("XY");
  await check("kb_inside_quote", p, [[R("abc", "quote", "b81"), R("XY", "typed"), R("def", "quote", "b81")]],
    (c) => c.keyboard === 2, [[]]);
}
// 2. Keyboard typing at both edges.
{
  const p = await fresh();
  await s1(p, "insertQuote", "quoted");
  await s1(p, "select", 1);
  await p.keyboard.type("<");
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.type(">");
  await check("kb_edges_quote", p, [[R("<", "typed"), R("quoted", "quote", "b81"), R(">", "typed")]]);
}
// 3. Keyboard typing inside and at both edges of a linked paragraph.
{
  const p = await fresh();
  await s1(p, "insertQuote", "claimed");
  await s1(p, "link", await s1(p, "paragraphPos"), { claim_id: "c3", by: "student" });
  await s1(p, "select", 4);
  await p.keyboard.type("_");
  await s1(p, "select", 1);
  await p.keyboard.type("[");
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.type("]");
  await check("kb_linked_paragraph", p, [[
    R("[", "typed"), R("cla", "quote", "b81"), R("_", "typed"), R("imed", "quote", "b81"), R("]", "typed"),
  ]], (c) => c.keyboard === 3, [["c3/student"]]);
}
// 4. IME composition inside a quote span (CDP).
{
  const p = await fresh();
  await s1(p, "insertQuote", "ab");
  await s1(p, "select", 2);
  const cdp = await context.newCDPSession(p);
  await cdp.send("Input.imeSetComposition", { text: "に", selectionStart: 1, selectionEnd: 1 });
  await cdp.send("Input.imeSetComposition", { text: "にほん", selectionStart: 3, selectionEnd: 3 });
  await cdp.send("Input.insertText", { text: "日本" });
  await p.waitForTimeout(100);
  await check("ime_inside_quote", p, [[R("a", "quote", "b81"), R("日本", "typed"), R("b", "quote", "b81")]],
    (c) => c.ime >= 1);
}
// 5. An extension edits the page directly (Grammarly-style), inside a quote span.
{
  const p = await fresh();
  await s1(p, "insertQuote", "recieve it");
  await p.evaluate(() => {
    const span = document.querySelector('span[data-origin-kind="quote"]');
    span.firstChild.data = "receive it";
  });
  await p.waitForTimeout(100);
  await check("extension_dom_edit", p, [[R("rec", "quote", "b81"), R("ei", "typed"), R("ve it", "quote", "b81")]]);
}
// 6. Select all, then type.
{
  const p = await fresh();
  await s1(p, "insertQuote", "a quote");
  await s1(p, "link", await s1(p, "paragraphPos"), C1);
  await p.keyboard.press(`${MOD}+a`);
  await p.keyboard.type("fresh");
  // Mod-a is a whole-document selection: typing replaces the paragraph node itself, so its links go with it.
  await check("select_all_type", p, [[R("fresh", "typed")]], () => true, [[]]);
}
// 6b. Select all the text of one paragraph (not the document), then type: links unchanged.
{
  const p = await fresh();
  await s1(p, "insertQuote", "a quote");
  await s1(p, "link", await s1(p, "paragraphPos"), C1);
  await s1(p, "select", 1, await s1(p, "end"));
  await p.keyboard.type("fresh");
  await check("select_text_type", p, [[R("fresh", "typed")]], () => true, [["c1/student"]]);
}
// 7. Enter inside a span, then type.
{
  const p = await fresh();
  await s1(p, "insertQuote", "firstsecond");
  await s1(p, "select", 6);
  await p.keyboard.press("Enter");
  await p.keyboard.type("new ");
  await check("enter_inside_quote", p, [[R("first", "quote", "b81")], [R("new ", "typed"), R("second", "quote", "b81")]], () => true, [[], []]);
}
// 8. Backspace at the edge of a span.
{
  const p = await fresh();
  await p.keyboard.type("mine ");
  await s1(p, "insertQuote", "theirs");
  await s1(p, "select", 7);
  await p.keyboard.press("Backspace");
  await p.keyboard.press("Backspace");
  await check("backspace_across_edge", p, [[R("mine", "typed"), R("heirs", "quote", "b81")]], () => true, [[]]);
}
// 9. Internal copy and paste with the real clipboard.
{
  const p = await fresh();
  await p.keyboard.type("I ");
  await s1(p, "insertQuote", "quoted");
  await s1(p, "link", await s1(p, "paragraphPos"), C2);
  await s1(p, "select", 1, await s1(p, "end"));
  await p.keyboard.press(`${MOD}+c`);
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.press(`${MOD}+v`);
  await check("copy_paste_internal", p, [[
    R("I ", "typed"), R("quoted", "quote", "b81"), R("I ", "typed"), R("quoted", "quote", "b81"),
  ]], () => true, [["c2/student"]]);
}
// 10. Cut and paste (a move).
{
  const p = await fresh();
  await s1(p, "insertQuote", "move me");
  await p.keyboard.type(" stay");
  await s1(p, "select", 1, 8);
  await p.keyboard.press(`${MOD}+x`);
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.press(`${MOD}+v`);
  await check("cut_paste_move", p, [[R(" stay", "typed"), R("move me", "quote", "b81")]]);
}
// 11. External paste (HTML with a forged origin span) from the real clipboard.
{
  const p = await fresh();
  await p.keyboard.type("x");
  await p.evaluate(async () => {
    const html = '<p data-links=\'[{"claim_id":"cX","by":"student"}]\'>outside <span data-origin-kind="quote" data-origin-ref="b81">forged</span></p>';
    await navigator.clipboard.write([new ClipboardItem({
      "text/html": new Blob([html], { type: "text/html" }),
      "text/plain": new Blob(["outside forged"], { type: "text/plain" }),
    })]);
  });
  await p.keyboard.press(`${MOD}+v`);
  await check("paste_external_html", p, [[R("x", "typed"), R("outside forged", "paste_ext", "paste_1")]], () => true, [[]]);
}
// 12 and 13: headless Chromium does not start an OS drag from Playwright's
// mouse, so these dispatch real DragEvents with a real DataTransfer at real
// coordinates; ProseMirror's own dragstart/drop handlers and posAtCoords run.
async function dropAt(p, x, y, { fromSpan, text }) {
  await p.evaluate(([x, y, fromSpan, text]) => {
    const dt = new DataTransfer();
    const target = document.querySelector("#editor .ProseMirror");
    if (fromSpan) {
      const span = document.querySelector('span[data-origin-kind="quote"]');
      const r = span.getBoundingClientRect();
      span.dispatchEvent(new DragEvent("dragstart", { bubbles: true, cancelable: true, dataTransfer: dt,
        clientX: r.x + r.width / 2, clientY: r.y + r.height / 2 }));
    } else {
      dt.setData("text/plain", text);
    }
    target.dispatchEvent(new DragEvent("dragover", { bubbles: true, cancelable: true, dataTransfer: dt, clientX: x, clientY: y }));
    target.dispatchEvent(new DragEvent("drop", { bubbles: true, cancelable: true, dataTransfer: dt, clientX: x, clientY: y }));
  }, [x, y, fromSpan, text]);
}
// 12. Drag-and-drop inside the document.
{
  const p = await fresh();
  await s1(p, "insertQuote", "drag");
  await p.keyboard.type(" end");
  await s1(p, "select", 1, 5);
  const para = await p.locator("#editor p").boundingBox();
  await dropAt(p, para.x + para.width - 2, para.y + para.height / 2, { fromSpan: true });
  await check("drag_move_internal", p, [[R(" end", "typed"), R("drag", "quote", "b81")]]);
}
// 13. Drop from outside the editor.
{
  const p = await fresh();
  await p.keyboard.type("ab");
  const para = await p.locator("#editor p").boundingBox();
  await dropAt(p, para.x + para.width - 2, para.y + para.height / 2, { fromSpan: false, text: "dragged from outside" });
  await check("drop_external", p, [[R("ab", "typed"), R("dragged from outside", "paste_ext", "paste_1")]]);
}
// 14. Undo and redo with the keyboard.
{
  const p = await fresh();
  await s1(p, "insertQuote", "abcd");
  await p.waitForTimeout(600); // a new history group
  await s1(p, "select", 3);
  await p.keyboard.type("T");
  await p.keyboard.press(`${MOD}+z`);
  const afterUndo = await p.evaluate(() => window.s1.runs());
  await p.keyboard.press(`${MOD}+Shift+z`);
  await check("undo_redo", p, [[R("ab", "quote", "b81"), R("T", "typed"), R("cd", "quote", "b81")]],
    () => JSON.stringify(afterUndo) === JSON.stringify([[R("abcd", "quote", "b81")]]));
}

// 15. Enter in the middle of a linked paragraph: both halves linked.
{
  const p = await fresh();
  await p.keyboard.type("firstsecond");
  await s1(p, "link", await s1(p, "paragraphPos"), C1);
  await s1(p, "select", 6);
  await p.keyboard.press("Enter");
  await check("enter_split_linked", p, [[R("first", "typed")], [R("second", "typed")]], () => true,
    [["c1/student"], ["c1/student"]]);
}
// 16. Enter at the end of a linked paragraph: the new paragraph is unlinked and stays so.
{
  const p = await fresh();
  await p.keyboard.type("abc");
  await s1(p, "link", await s1(p, "paragraphPos"), C1);
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.press("Enter");
  await p.keyboard.type("new");
  await check("enter_end_linked", p, [[R("abc", "typed")], [R("new", "typed")]], () => true, [["c1/student"], []]);
}
// 17. Backspace joins two linked paragraphs: the union.
{
  const p = await fresh();
  await p.keyboard.type("ab");
  await p.keyboard.press("Enter");
  await p.keyboard.type("cd");
  await s1(p, "link", 0, C1);
  await s1(p, "link", 4, C2);
  await s1(p, "select", 5);
  await p.keyboard.press("Backspace");
  await check("backspace_join_linked", p, [[R("abcd", "typed")]], () => true, [["c1/student", "c2/student"]]);
}
// 18. Internal copy of two linked paragraphs with the real clipboard, paste into a new empty paragraph.
{
  const p = await fresh();
  await p.keyboard.type("one");
  await p.keyboard.press("Enter");
  await p.keyboard.type("two");
  await s1(p, "link", 0, C1);
  await s1(p, "link", 5, C2);
  await s1(p, "select", 1, await s1(p, "end"));
  await p.keyboard.press(`${MOD}+c`);
  await s1(p, "select", await s1(p, "end"));
  await p.keyboard.press("Enter");
  await p.keyboard.press(`${MOD}+v`);
  await check("copy_paste_linked_paragraphs", p,
    [[R("one", "typed")], [R("two", "typed")], [R("one", "typed")], [R("two", "typed")]], () => true,
    [["c1/student"], ["c2/student"], ["c1/student"], ["c2/student"]]);
}
// 19. Link command, then keyboard undo and redo.
{
  const p = await fresh();
  await p.keyboard.type("ab");
  await p.waitForTimeout(600);
  await s1(p, "link", await s1(p, "paragraphPos"), C1);
  await p.keyboard.press(`${MOD}+z`);
  const afterUndo = await p.evaluate(() => window.s1.links());
  await p.keyboard.press(`${MOD}+Shift+z`);
  await check("undo_redo_link", p, [[R("ab", "typed")]], () => JSON.stringify(afterUndo) === JSON.stringify([[]]),
    [["c1/student"]]);
}
// 20. Mod-b, then type.
{
  const p = await fresh();
  await p.keyboard.type("a");
  await p.keyboard.press(`${MOD}+b`);
  await p.keyboard.type("b");
  const fmt = await p.evaluate(() => window.s1.formats());
  await check("bold_typing", p, [[R("a", "typed"), R("b", "typed")]],
    () => JSON.stringify(fmt) === JSON.stringify([[["a", ""], ["b", "strong"]]]), [[]]);
}
// 21. Enter in a bullet list creates a new list item.
{
  const p = await fresh();
  await s1(p, "bulletList");
  await p.keyboard.type("one");
  await p.keyboard.press("Enter");
  await p.keyboard.type("two");
  const items = await s1(p, "count", "list_item");
  await check("list_enter", p, [[R("one", "typed")], [R("two", "typed")]], () => items === 2, [[], []]);
}
// 22. Shift-Enter inserts a hard break.
{
  const p = await fresh();
  await p.keyboard.type("a");
  await p.keyboard.press("Shift+Enter");
  await p.keyboard.type("b");
  const breaks = await s1(p, "count", "hard_break");
  await check("shift_enter_hard_break", p, [[R("a", "typed"), R("b", "typed")]], () => breaks === 1, [[]]);
}

await browser.close();
await server.close();

const version = (await import(require.resolve("playwright-core/package.json"), { with: { type: "json" } })).default.version;
const out = join(prototype, "fixtures/replay/s1_browser_steps.json");
writeFileSync(out, JSON.stringify({
  "x-note": "Recorded in real Chromium by prototype/spikes/S1/browser_check.mjs (not CI). server/tests/test_replay_s1.py replays these steps in Python and must reach the same doc and doc_hash.",
  browser: `Chromium (playwright-core ${version}, headless)`,
  cases: results,
}, null, 1) + "\n");
console.log(`\n${results.length - failures.length}/${results.length} passed; wrote ${out}`);
process.exit(failures.length ? 1 : 0);
