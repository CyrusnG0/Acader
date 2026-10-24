// @vitest-environment jsdom
/// <reference types="node" />
// Spike S1 (design/evaluation.md §1) and T-011 (paragraph links, D-044/D-045):
// do origin marks and paragraph links survive real editing, and does replay
// from the recorded steps give the same document?
//
// Every case runs in a real TipTap editor (jsdom), checks the marks and links,
// replays its recorded steps in JS, and is written to a shared fixture that the
// Python replay (server/tests/test_replay_s1.py) replays too. If the editor's
// output changes, this test fails until the fixture is regenerated on purpose:
//   UPDATE_S1_FIXTURES=1 npx vitest run src/editor/s1.test.ts
import { afterEach, describe, expect, test } from "vitest";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Editor } from "@tiptap/core";
import { AllSelection, TextSelection, type Command } from "@tiptap/pm/state";
import { closeHistory, redo, undo } from "@tiptap/pm/history";
import { Node as PMNode, Slice } from "@tiptap/pm/model";
import type { EditorView } from "@tiptap/pm/view";
import schemaJson from "../../schema.json";
import { editorSchema } from "../schema";
import { canonicalJson, docHash } from "./canonical";
import { createEditor } from "./editor";
import {
  setHeading,
  setParagraph,
  toggleBlockquote,
  toggleBulletList,
  toggleOrderedList,
} from "./formatting";
import {
  LINK_META,
  acceptSuggestion,
  linkParagraph,
  paragraphPosAt,
  unionLinks,
  unlinkParagraph,
  type Link,
} from "./links";
import { EXPLICIT_META, SLICE_MIME, insertMarked, originKey, stampSlice } from "./origin";
import {
  ALLOWED_STEP_TYPES,
  ReplayError,
  flattenStepJson,
  recordKey,
  replaySteps,
  type JsonObject,
} from "./record";
import { Step } from "@tiptap/pm/transform";

const FIXTURE = resolve(dirname(fileURLToPath(import.meta.url)), "../../../fixtures/replay/s1_steps.json");

// ---------- helpers ----------

const editors: Editor[] = [];
afterEach(() => {
  while (editors.length) editors.pop()!.destroy();
});

function setup(logId = "log_A"): { editor: Editor; view: EditorView } {
  let n = 0;
  const element = document.createElement("div");
  document.body.append(element);
  const editor = createEditor({ element, logId, newPasteId: () => `${logId}_paste_${++n}` });
  editors.push(editor);
  return { editor, view: editor.view };
}

function beforeInput(view: EditorView, inputType: string, data: string | null = null) {
  view.dom.dispatchEvent(new InputEvent("beforeinput", { inputType, data, bubbles: true, cancelable: true }));
}

/** What ProseMirror dispatches for a keystroke: insertText at the selection, no meta. */
function type(view: EditorView, text: string, inputType = "insertText") {
  beforeInput(view, inputType, text);
  view.dispatch(view.state.tr.insertText(text));
}

/** A key press through the editor's real keymaps (TipTap's and ours). */
function press(view: EditorView, key: string, mods: { shift?: boolean; mod?: boolean } = {}): boolean {
  const ev = new KeyboardEvent("keydown", {
    key,
    shiftKey: !!mods.shift,
    ctrlKey: !!mods.mod,
    bubbles: true,
    cancelable: true,
  });
  return view.someProp("handleKeyDown", (f) => f(view, ev)) ?? false;
}

function select(view: EditorView, from: number, to = from) {
  view.dispatch(view.state.tr.setSelection(TextSelection.create(view.state.doc, from, to)));
}

const quote = { kind: "quote", ref: "b81" };

type Run = { text: string; origin: string | null; ref: string | null };

/** The text runs of every textblock, in document order. */
function runs(doc: PMNode): Run[][] {
  const out: Run[][] = [];
  doc.descendants((block) => {
    if (!block.isTextblock) return true;
    const row: Run[] = [];
    block.forEach((t) => {
      if (!t.isText) return;
      const o = t.marks.find((m) => m.type.name === "origin");
      row.push({
        text: t.text ?? "",
        origin: o ? (o.attrs.kind as string) : null,
        ref: o ? (o.attrs.ref as string | null) : null,
      });
    });
    out.push(row);
    return false;
  });
  return out;
}

const r = (text: string, origin: string, ref: string | null = null): Run => ({ text, origin, ref });

const linkStr = (l: Link) => `${l.claim_id}/${l.by}${l.suggestion_id ? `/${l.suggestion_id}` : ""}`;

/** The links of every paragraph, in document order (nested paragraphs included). */
function links(doc: PMNode): string[][] {
  const out: string[][] = [];
  doc.descendants((n) => {
    if (n.type.name === "paragraph") out.push(((n.attrs.links ?? []) as Link[]).map(linkStr));
    return true;
  });
  return out;
}

/** The block structure, e.g. `ul(li(p[c1/student],p[]))`; headings as h1..h3, other text blocks as their name. */
function outline(doc: PMNode): string {
  const short: Record<string, string> = { bullet_list: "ul", ordered_list: "ol", list_item: "li", blockquote: "bq" };
  const walk = (n: PMNode): string => {
    if (n.type.name === "paragraph") return `p[${((n.attrs.links ?? []) as Link[]).map(linkStr).join(",")}]`;
    if (n.type.name === "heading") return `h${n.attrs.level}`;
    return `${short[n.type.name] ?? n.type.name}(${n.children.map(walk).join(",")})`;
  };
  return doc.children.map(walk).join(",");
}

/** Text nodes with the names of their non-origin marks. */
function formats(doc: PMNode): [string, string[]][] {
  const out: [string, string[]][] = [];
  doc.descendants((n) => {
    if (n.isText) out.push([n.text ?? "", n.marks.map((m) => m.type.name).filter((m) => m !== "origin")]);
    return true;
  });
  return out;
}

/** Every character carries exactly one origin. */
function everyCharHasOrigin(doc: PMNode) {
  doc.descendants((n) => {
    if (n.isText) expect(n.marks.filter((m) => m.type.name === "origin")).toHaveLength(1);
  });
}

// --- building documents ---

const L = (claim_id: string, by: Link["by"] = "student", suggestion_id?: string): Link =>
  suggestion_id === undefined ? { claim_id, by } : { claim_id, by, suggestion_id };

const T = (text: string, kind = "typed", ref: string | null = null) => ({
  type: "text",
  text,
  marks: [{ type: "origin", attrs: { kind, ref } }],
});

const P = (linkList: Link[], ...content: JsonObject[]): JsonObject => ({
  type: "paragraph",
  attrs: { links: linkList },
  content,
});

const TXT = (text: string) => T(text, "quote", "b81");

/** Replace the whole document with these blocks (an explicit load, like opening a saved draft). */
function load(view: EditorView, ...blocks: JsonObject[]) {
  const doc = PMNode.fromJSON(view.state.schema, { type: "doc", content: blocks });
  doc.check();
  view.dispatch(view.state.tr.replaceWith(0, view.state.doc.content.size, doc.content).setMeta(EXPLICIT_META, true));
}

/** Textblocks in document order with the position before each. */
function textblocks(view: EditorView): { node: PMNode; pos: number }[] {
  const out: { node: PMNode; pos: number }[] = [];
  view.state.doc.descendants((node, pos) => {
    if (node.isTextblock) {
      out.push({ node, pos });
      return false;
    }
    return true;
  });
  return out;
}
/** Position inside the nth textblock at a text offset. */
const inB = (view: EditorView, n: number, offset: number) => textblocks(view)[n].pos + 1 + offset;
const startB = (view: EditorView, n: number) => inB(view, n, 0);
const endB = (view: EditorView, n: number) => inB(view, n, textblocks(view)[n].node.content.size);
const beforeB = (view: EditorView, n: number) => textblocks(view)[n].pos;

class FakeClipboard {
  store = new Map<string, string>();
  setData(t: string, v: string) {
    this.store.set(t, v);
  }
  getData(t: string) {
    return this.store.get(t) ?? "";
  }
  clearData() {
    this.store.clear();
  }
  get types() {
    return [...this.store.keys()];
  }
  get files() {
    return [];
  }
}

function fire(view: EditorView, type: string, field: "clipboardData" | "dataTransfer", data: FakeClipboard, extra = {}) {
  const ev = new Event(type, { bubbles: true, cancelable: true });
  Object.defineProperty(ev, field, { value: data });
  Object.assign(ev, extra);
  view.dom.dispatchEvent(ev);
  return ev;
}

const externalClipboard = (text: string, html?: string) => {
  const c = new FakeClipboard();
  c.setData("text/plain", text);
  if (html) c.setData("text/html", html);
  return c;
};

/** A clipboard as the editor's own copy writes it, built from a doc range with its parents (paragraphs kept). */
function internalClipboard(view: EditorView, from: number, to: number, logId = "log_A") {
  const c = new FakeClipboard();
  const slice = view.state.doc.slice(from, to, true);
  c.setData("text/plain", view.state.doc.textBetween(from, to, "\n"));
  c.setData(SLICE_MIME, JSON.stringify({ log_id: logId, slice: slice.toJSON() }));
  return c;
}

/** Run a command; return whether it applied and how many transactions it dispatched. */
function run(view: EditorView, cmd: Command): { ok: boolean; dispatched: number } {
  let dispatched = 0;
  const ok = cmd(view.state, (tr) => {
    dispatched++;
    view.dispatch(tr);
  });
  return { ok, dispatched };
}

// ---------- recorded cases ----------

type Case = { name: string; start: JsonObject; steps: JsonObject[]; doc: JsonObject; doc_hash: string };
const recorded: Case[] = [];

async function finish(name: string, view: EditorView) {
  const log = recordKey.getState(view.state)!;
  // Reload from steps, in the editor's own (TipTap) schema and in the schema
  // built straight from schema.json (what the Python replay loads).
  expect(replaySteps(view.state.schema, log.start, log.steps).eq(view.state.doc)).toBe(true);
  expect(replaySteps(editorSchema, log.start, log.steps).toJSON()).toEqual(view.state.doc.toJSON());
  everyCharHasOrigin(view.state.doc);
  for (const s of log.steps) expect(ALLOWED_STEP_TYPES.has(s.stepType as string), `${name}: ${s.stepType}`).toBe(true);
  const doc = view.state.doc.toJSON() as JsonObject;
  recorded.push({ name, start: log.start, steps: [...log.steps], doc, doc_hash: await docHash(doc) });
}

describe("typed text is always typed (D21)", () => {
  test("typing into an empty document", async () => {
    const { view } = setup();
    type(view, "Hello");
    expect(runs(view.state.doc)).toEqual([[r("Hello", "typed")]]);
    await finish("typed_plain", view);
  });

  for (const kind of ["paste_ext", "quote", "helper", "coach", "import"]) {
    test(`typing inside a ${kind} span`, async () => {
      const { view } = setup();
      insertMarked(view, "abcdef", { kind, ref: `${kind}_1` });
      select(view, 4);
      type(view, "XY");
      expect(runs(view.state.doc)).toEqual([
        [r("abc", kind, `${kind}_1`), r("XY", "typed"), r("def", kind, `${kind}_1`)],
      ]);
      await finish(`typed_inside_${kind}`, view);
    });
  }

  test("typing at both edges of a quote span", async () => {
    const { view } = setup();
    insertMarked(view, "quoted", quote);
    select(view, 1);
    type(view, "<");
    select(view, view.state.doc.content.size - 1);
    type(view, ">");
    expect(runs(view.state.doc)).toEqual([[r("<", "typed"), r("quoted", "quote", "b81"), r(">", "typed")]]);
    await finish("typed_edges_quote", view);
  });

  test("typing between two different marked spans", async () => {
    const { view } = setup();
    insertMarked(view, "one", quote);
    insertMarked(view, "two", { kind: "coach", ref: "q1" });
    select(view, 4);
    type(view, " ");
    expect(runs(view.state.doc)).toEqual([[r("one", "quote", "b81"), r(" ", "typed"), r("two", "coach", "q1")]]);
    await finish("typed_between_spans", view);
  });

  test("a keystroke through handleTextInput is one step, already typed, also inside a span", async () => {
    const { view } = setup();
    insertMarked(view, "abcd", quote);
    const before = recordKey.getState(view.state)!.steps.length;
    select(view, 3);
    const keystroke = (ch: string) => {
      const { from, to } = view.state.selection;
      const handled = view.someProp("handleTextInput", (f) => f(view, from, to, ch, () => view.state.tr.insertText(ch, from, to)));
      expect(handled).toBe(true);
    };
    keystroke("x");
    keystroke("y");
    expect(recordKey.getState(view.state)!.steps.length - before).toBe(2);
    expect(runs(view.state.doc)).toEqual([[r("ab", "quote", "b81"), r("xy", "typed"), r("cd", "quote", "b81")]]);
    expect(view.state.selection.from).toBe(5);
    await finish("keystroke_handle_text_input", view);
  });

  test("select-all then type replaces everything with typed text", async () => {
    const { view } = setup();
    insertMarked(view, "a quote", quote);
    view.dispatch(view.state.tr.setSelection(new AllSelection(view.state.doc)));
    type(view, "fresh");
    expect(runs(view.state.doc)).toEqual([[r("fresh", "typed")]]);
    await finish("select_all_type", view);
  });

  test("astral characters (UTF-16 positions) inside a span", async () => {
    const { view } = setup();
    insertMarked(view, "café 😀 naïve", quote);
    select(view, 1 + "café 😀".length); // after the emoji (two UTF-16 units)
    type(view, "🎓");
    type(view, "!");
    expect(runs(view.state.doc)).toEqual([
      [r("café 😀", "quote", "b81"), r("🎓!", "typed"), r(" naïve", "quote", "b81")],
    ]);
    await finish("typed_astral", view);
  });

  test("Enter inside a span splits it; both halves keep their marks; typing after is typed", async () => {
    const { view } = setup();
    insertMarked(view, "firstsecond", quote);
    select(view, 6);
    expect(press(view, "Enter")).toBe(true);
    type(view, "new ");
    expect(runs(view.state.doc)).toEqual([[r("first", "quote", "b81")], [r("new ", "typed"), r("second", "quote", "b81")]]);
    await finish("split_paragraph", view);
  });

  test("deleting across a span edge leaves the remaining marks alone", async () => {
    const { view } = setup();
    type(view, "mine ");
    insertMarked(view, "theirs", quote);
    view.dispatch(view.state.tr.delete(4, 9));
    expect(runs(view.state.doc)).toEqual([[r("min", "typed"), r("irs", "quote", "b81")]]);
    await finish("delete_across_edge", view);
  });
});

describe("input_kind counts (replacements are typed)", () => {
  test("spellcheck / autocorrect replacement inside a quote is typed and counted", async () => {
    const { view } = setup();
    insertMarked(view, "teh word", quote);
    select(view, 1, 4);
    type(view, "the", "insertReplacementText");
    expect(runs(view.state.doc)).toEqual([[r("the", "typed"), r(" word", "quote", "b81")]]);
    expect(originKey.getState(view.state)!.counts).toEqual({ keyboard: 0, ime: 0, dictation: 0, replacement: 1 });
    await finish("replacement_in_quote", view);
  });

  test("IME composition text is typed and counted as ime", async () => {
    const { view } = setup();
    insertMarked(view, "ab", quote);
    select(view, 2);
    type(view, "日本", "insertCompositionText");
    type(view, "x");
    expect(runs(view.state.doc)).toEqual([[r("a", "quote", "b81"), r("日本x", "typed"), r("b", "quote", "b81")]]);
    expect(originKey.getState(view.state)!.counts).toEqual({ keyboard: 1, ime: 1, dictation: 0, replacement: 0 });
    await finish("ime_in_quote", view);
  });

  test("an extension editing the page directly (Grammarly-style DOM change) is typed", async () => {
    const { view } = setup();
    insertMarked(view, "recieve it", quote);
    const span = view.dom.querySelector("span[data-origin-kind]")!;
    const textNode = span.firstChild as Text;
    textNode.data = "receive it"; // a DOM edit no ProseMirror command made
    (view as unknown as { domObserver: { flush(): void } }).domObserver.flush();
    const rows = runs(view.state.doc);
    expect(rows[0].map((x) => x.text).join("")).toBe("receive it");
    // Only the changed characters became typed; the rest is still the quote.
    expect(rows[0].filter((x) => x.origin === "typed").map((x) => x.text).join("").length).toBeGreaterThan(0);
    expect(rows[0].filter((x) => x.origin === "typed").map((x) => x.text).join("").length).toBeLessThanOrEqual(3);
    await finish("dom_edit_in_quote", view);
  });
});

describe("paste and drop (D26)", () => {
  test("external paste is paste_ext, and forged marks in its HTML are ignored", async () => {
    const { view } = setup();
    type(view, "x");
    const forged = '<p>outside <span data-origin-kind="quote" data-origin-ref="b81">forged</span> <b>bold</b></p>';
    fire(view, "paste", "clipboardData", externalClipboard("outside forged bold", forged));
    expect(runs(view.state.doc)).toEqual([[r("x", "typed"), r("outside forged bold", "paste_ext", "log_A_paste_1")]]);
    await finish("paste_external_html", view);
  });

  test("external plain-text paste into a quote span is paste_ext", async () => {
    const { view } = setup();
    insertMarked(view, "abcd", quote);
    select(view, 3);
    fire(view, "paste", "clipboardData", externalClipboard("PASTE"));
    expect(runs(view.state.doc)).toEqual([
      [r("ab", "quote", "b81"), r("PASTE", "paste_ext", "log_A_paste_1"), r("cd", "quote", "b81")],
    ]);
    await finish("paste_external_in_quote", view);
  });

  test("internal copy and paste keeps marks (same log_id)", async () => {
    const { view } = setup();
    type(view, "I ");
    insertMarked(view, "quoted", quote);
    const clip = new FakeClipboard();
    select(view, 1, view.state.doc.content.size - 1);
    fire(view, "copy", "clipboardData", clip);
    expect(JSON.parse(clip.getData(SLICE_MIME)).log_id).toBe("log_A");
    select(view, view.state.doc.content.size - 1);
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc)).toEqual([
      [r("I ", "typed"), r("quoted", "quote", "b81"), r("I ", "typed"), r("quoted", "quote", "b81")],
    ]);
    await finish("copy_paste_internal", view);
  });

  test("cut and paste (a move) keeps marks", async () => {
    const { view } = setup();
    insertMarked(view, "move me", quote);
    type(view, " stay");
    select(view, 1, 8);
    const clip = new FakeClipboard();
    fire(view, "cut", "clipboardData", clip);
    select(view, view.state.doc.content.size - 1);
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc)).toEqual([[r(" stay", "typed"), r("move me", "quote", "b81")]]);
    await finish("cut_paste_move", view);
  });

  test("a writing-room slice from another log is paste_ext", async () => {
    const a = setup("log_A");
    insertMarked(a.view, "from A", quote);
    select(a.view, 1, 7);
    const clip = new FakeClipboard();
    fire(a.view, "copy", "clipboardData", clip);
    const b = setup("log_B");
    fire(b.view, "paste", "clipboardData", clip);
    expect(runs(b.view.state.doc)).toEqual([[r("from A", "paste_ext", "log_B_paste_1")]]);
    await finish("paste_other_log", b.view);
  });

  test("a malformed writing-room slice falls back to paste_ext", async () => {
    const { view } = setup();
    const clip = externalClipboard("junk");
    clip.setData(SLICE_MIME, '{"log_id":"log_A","slice":{"content":[{"type":"nope"}]}}');
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc)).toEqual([[r("junk", "paste_ext", "log_A_paste_1")]]);
    await finish("paste_malformed_slice", view);
  });

  function mockDropPos(view: EditorView, pos: number) {
    (view as unknown as { posAtCoords: () => unknown }).posAtCoords = () => ({ pos, inside: -1 });
  }

  test("drag-and-drop inside the document keeps marks", async () => {
    const { view } = setup();
    insertMarked(view, "drag", quote);
    type(view, " end");
    select(view, 1, 5);
    (view as unknown as { dragging: unknown }).dragging = { slice: view.state.selection.content(), move: true };
    mockDropPos(view, view.state.doc.content.size - 1);
    fire(view, "drop", "dataTransfer", new FakeClipboard(), { clientX: 0, clientY: 0 });
    expect(runs(view.state.doc)).toEqual([[r(" end", "typed"), r("drag", "quote", "b81")]]);
    await finish("drag_move_internal", view);
  });

  test("drop from outside is paste_ext", async () => {
    const { view } = setup();
    type(view, "ab");
    mockDropPos(view, 2);
    fire(view, "drop", "dataTransfer", externalClipboard("DROP"), { clientX: 0, clientY: 0 });
    expect(runs(view.state.doc)).toEqual([[r("a", "typed"), r("DROP", "paste_ext", "log_A_paste_1"), r("b", "typed")]]);
    await finish("drop_external", view);
  });
});

describe("undo / redo keep marks", () => {
  test("undo restores the span; redo brings the typed text back", async () => {
    const { view } = setup();
    insertMarked(view, "abcd", quote);
    view.dispatch(closeHistory(view.state.tr));
    select(view, 3);
    type(view, "T");
    expect(runs(view.state.doc)).toEqual([[r("ab", "quote", "b81"), r("T", "typed"), r("cd", "quote", "b81")]]);
    undo(view.state, view.dispatch);
    expect(runs(view.state.doc)).toEqual([[r("abcd", "quote", "b81")]]);
    redo(view.state, view.dispatch);
    expect(runs(view.state.doc)).toEqual([[r("ab", "quote", "b81"), r("T", "typed"), r("cd", "quote", "b81")]]);
    // Undo produced markSet steps (the exact inverse of replacing an origin); the log holds them flat.
    expect(recordKey.getState(view.state)!.steps.some((s) => s.stepType === "markSet")).toBe(false);
    await finish("undo_redo", view);
  });

  test("nested markSet steps are flattened into mark steps both replays load", () => {
    const add = { stepType: "addMark", mark: { type: "origin", attrs: { kind: "typed", ref: null } }, from: 1, to: 2 };
    const rem = { stepType: "removeMark", mark: { type: "origin", attrs: { kind: "typed", ref: null } }, from: 1, to: 2 };
    const nested = { stepType: "markSet", steps: [rem, { stepType: "markSet", steps: [add, rem] }] };
    expect(flattenStepJson(nested)).toEqual([rem, add, rem]);
    // Upstream: nested markSet JSON does not load (prosemirror-transform 1.12). If this starts
    // passing, the flattening may no longer be needed for JS, but prosemirror-py still has no markSet.
    expect(() => Step.fromJSON(editorSchema, nested)).toThrow();
  });
});

// ---------- paragraph links (D-044, D-045) ----------

describe("link commands", () => {
  test("linkParagraph adds one link as one attr step; unlinkParagraph removes it", async () => {
    const { view } = setup();
    load(view, P([], T("Alpha")), P([], T("Beta")));
    const before = recordKey.getState(view.state)!.steps.length;
    expect(run(view, linkParagraph(beforeB(view, 0), L("c1")))).toEqual({ ok: true, dispatched: 1 });
    const added = recordKey.getState(view.state)!.steps.slice(before);
    expect(added.map((s) => s.stepType)).toEqual(["attr"]);
    expect(links(view.state.doc)).toEqual([["c1/student"], []]);
    expect(paragraphPosAt(view.state, inB(view, 1, 2))).toBe(beforeB(view, 1));
    await finish("link_command", view);
  });

  test("unlinkParagraph removes every link with that claim_id", async () => {
    const { view } = setup();
    load(view, P([L("c1"), L("c2", "coach"), L("c1", "import")], T("Alpha")));
    expect(run(view, unlinkParagraph(0, "nope")).ok).toBe(false);
    expect(run(view, unlinkParagraph(0, "c1"))).toEqual({ ok: true, dispatched: 1 });
    expect(links(view.state.doc)).toEqual([["c2/coach"]]);
    await finish("unlink_command", view);
  });

  test("acceptSuggestion writes a student link with the suggestion_id; bad calls change nothing", async () => {
    const { view } = setup();
    load(view, P([], T("Alpha")), { type: "heading", attrs: { level: 1 }, content: [T("Title")] });
    const accept = acceptSuggestion(0, "c1", "s1");
    expect(run(view, accept)).toEqual({ ok: true, dispatched: 1 });
    expect(links(view.state.doc)).toEqual([["c1/student/s1"]]);
    const steps = recordKey.getState(view.state)!.steps.length;
    const docBefore = view.state.doc;
    const refused: Command[] = [
      acceptSuggestion(0, "c1", "s1"), // duplicate
      linkParagraph(0, L("c1", "student", "s1")), // duplicate by key
      linkParagraph(0, { claim_id: "", by: "student" }), // empty claim_id
      linkParagraph(0, { claim_id: "c2", by: "model" as Link["by"] }), // closed list
      linkParagraph(0, { claim_id: "c2", by: "coach", suggestion_id: "s2" }), // suggestion only with student
      linkParagraph(0, { claim_id: "c2", by: "student", suggestion_id: null as unknown as string }),
      linkParagraph(3, L("c2")), // not a paragraph position
      linkParagraph(textblocks(view)[1].pos, L("c2")), // a heading
      unlinkParagraph(textblocks(view)[1].pos, "c1"),
      acceptSuggestion(textblocks(view)[1].pos, "c1", "s9"),
    ];
    for (const cmd of refused) expect(run(view, cmd)).toEqual({ ok: false, dispatched: 0 });
    expect(view.state.doc).toBe(docBefore);
    expect(recordKey.getState(view.state)!.steps.length).toBe(steps);
    // The same claim with no suggestion is a different link and is allowed.
    expect(run(view, linkParagraph(0, L("c1"))).ok).toBe(true);
    expect(links(view.state.doc)).toEqual([["c1/student/s1", "c1/student"]]);
    await finish("accept_suggestion", view);
  });

  test("link commands are one undo step and carry the link meta", () => {
    const { view } = setup();
    load(view, P([], T("Alpha")));
    view.dispatch(closeHistory(view.state.tr));
    let meta: unknown;
    linkParagraph(0, L("c1"))(view.state, (tr) => {
      meta = tr.getMeta(LINK_META);
      view.dispatch(tr);
    });
    expect(meta).toBe("link");
    undo(view.state, view.dispatch);
    expect(links(view.state.doc)).toEqual([[]]);
  });

  test("unionLinks keeps a's order, then b's new items, and never mutates", () => {
    const a = [L("c1"), L("c2", "coach")];
    const b = [L("c2", "coach"), L("c3"), L("c1", "student", "s1")];
    const out = unionLinks(a, b);
    expect(out.map(linkStr)).toEqual(["c1/student", "c2/coach", "c3/student", "c1/student/s1"]);
    expect(a).toHaveLength(2);
    expect(unionLinks([], [])).not.toBe(unionLinks([], []));
  });
});

describe("typing never touches links", () => {
  test("typing inside a linked paragraph", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("abcdef")));
    select(view, 4);
    type(view, "XY");
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    expect(runs(view.state.doc)).toEqual([[r("abc", "quote", "b81"), r("XY", "typed"), r("def", "quote", "b81")]]);
    await finish("typed_inside_linked", view);
  });

  test("typing at the start and the end of a linked paragraph", async () => {
    const { view } = setup();
    load(view, P([L("c1"), L("c2", "coach")], TXT("mid")));
    select(view, 1);
    type(view, "[");
    select(view, endB(view, 0));
    type(view, "]");
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"]]);
    expect(runs(view.state.doc)).toEqual([[r("[", "typed"), r("mid", "quote", "b81"), r("]", "typed")]]);
    await finish("typed_edges_linked", view);
  });

  test("adding a sentence to a linked paragraph", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("First.")), P([L("c2")], T("Second.")));
    select(view, endB(view, 0));
    for (const ch of " And one more sentence.") type(view, ch);
    expect(links(view.state.doc)).toEqual([["c1/student"], ["c2/student"]]);
    await finish("sentence_added_linked", view);
  });

  test("IME composition in a linked paragraph", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("ab")));
    select(view, 2);
    type(view, "日本", "insertCompositionText");
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    expect(runs(view.state.doc)).toEqual([[r("a", "quote", "b81"), r("日本", "typed"), r("b", "quote", "b81")]]);
    await finish("ime_in_linked", view);
  });

  test("a replacement in a linked paragraph", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("teh word")));
    select(view, 1, 4);
    type(view, "the", "insertReplacementText");
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    await finish("replacement_in_linked", view);
  });

  test("deleting all the text of a linked paragraph leaves its links", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("everything")), P([L("c2")], T("next")));
    select(view, startB(view, 0), endB(view, 0));
    view.dispatch(view.state.tr.deleteSelection());
    expect(links(view.state.doc)).toEqual([["c1/student"], ["c2/student"]]);
    expect(textblocks(view)[0].node.content.size).toBe(0);
    await finish("delete_all_text_linked", view);
  });
});

describe("Enter and split", () => {
  test("Enter in the middle: both halves keep the links; typing after is typed", async () => {
    const { view } = setup();
    load(view, P([L("c1"), L("c2", "coach")], TXT("firstsecond")));
    select(view, 6);
    expect(press(view, "Enter")).toBe(true);
    type(view, "new ");
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"], ["c1/student", "c2/coach"]]);
    expect(runs(view.state.doc)).toEqual([[r("first", "quote", "b81")], [r("new ", "typed"), r("second", "quote", "b81")]]);
    await finish("split_linked_middle", view);
  });

  test("Enter at the end: the new paragraph has no links, also after typing in it", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("tail")));
    select(view, endB(view, 0));
    expect(press(view, "Enter")).toBe(true);
    expect(links(view.state.doc)).toEqual([["c1/student"], []]);
    type(view, "more");
    expect(links(view.state.doc)).toEqual([["c1/student"], []]);
    await finish("enter_end_linked", view);
  });

  test("Enter at the start: the new empty paragraph above has no links, the text keeps them", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("body")));
    select(view, startB(view, 0));
    expect(press(view, "Enter")).toBe(true);
    expect(links(view.state.doc)).toEqual([[], ["c1/student"]]);
    expect(textblocks(view)[0].node.content.size).toBe(0);
    expect(textblocks(view)[1].node.textContent).toBe("body");
    await finish("enter_start_linked", view);
  });
});

describe("joins give the surviving paragraph the union of links (D-045)", () => {
  test("Backspace at the start of P2", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("one ")), P([L("c1"), L("c2", "coach")], T("two")));
    select(view, startB(view, 1));
    expect(press(view, "Backspace")).toBe(true);
    expect(textblocks(view)).toHaveLength(1);
    expect(textblocks(view)[0].node.textContent).toBe("one two");
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"]]);
    await finish("join_backspace_union", view);
  });

  test("Delete at the end of P1", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("one ")), P([L("c2", "coach"), L("c1")], T("two")));
    select(view, endB(view, 0));
    expect(press(view, "Delete")).toBe(true);
    expect(textblocks(view)[0].node.textContent).toBe("one two");
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"]]);
    await finish("join_delete_forward", view);
  });

  test("deleting a selection from inside P1 to inside P3 drops the middle paragraph's links", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("aaa")), P([L("c9", "coach")], T("bbb")), P([L("c3"), L("c1")], T("ccc")));
    select(view, inB(view, 0, 1), inB(view, 2, 2));
    expect(press(view, "Backspace")).toBe(true);
    expect(textblocks(view)).toHaveLength(1);
    expect(textblocks(view)[0].node.textContent).toBe("ac");
    expect(links(view.state.doc)).toEqual([["c1/student", "c3/student"]]);
    await finish("join_across_three", view);
  });

  test("undo and redo of a join restore the links exactly", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("one ")), P([L("c1"), L("c2", "coach")], T("two")));
    view.dispatch(closeHistory(view.state.tr));
    select(view, startB(view, 1));
    press(view, "Backspace");
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"]]);
    undo(view.state, view.dispatch);
    expect(links(view.state.doc)).toEqual([["c1/student"], ["c1/student", "c2/coach"]]);
    expect(runs(view.state.doc)).toEqual([[r("one ", "typed")], [r("two", "typed")]]);
    redo(view.state, view.dispatch);
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"]]);
    await finish("undo_redo_join", view);
  });

  test("undo and redo of a link command", async () => {
    const { view } = setup();
    load(view, P([], T("one")));
    view.dispatch(closeHistory(view.state.tr));
    run(view, acceptSuggestion(0, "c1", "s1"));
    expect(links(view.state.doc)).toEqual([["c1/student/s1"]]);
    undo(view.state, view.dispatch);
    expect(links(view.state.doc)).toEqual([[]]);
    redo(view.state, view.dispatch);
    expect(links(view.state.doc)).toEqual([["c1/student/s1"]]);
    await finish("undo_redo_link", view);
  });
});

describe("paste and links", () => {
  test("internal paste of whole paragraphs keeps their links", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("one")), P([L("c2", "coach")], T("two")), P([]));
    const clip = internalClipboard(view, startB(view, 0), endB(view, 1));
    select(view, startB(view, 2));
    fire(view, "paste", "clipboardData", clip);
    expect(links(view.state.doc)).toEqual([["c1/student"], ["c2/coach"], ["c1/student"], ["c2/coach"]]);
    expect(runs(view.state.doc).map((row) => row.map((x) => x.text).join(""))).toEqual(["one", "two", "one", "two"]);
    await finish("paste_internal_paragraphs", view);
  });

  test("internal multi-paragraph paste into the middle of X: X's head gets F's links, the tail paragraph L's and X's", async () => {
    const { view } = setup();
    load(view, P([L("f1")], T("first")), P([L("l1", "coach")], T("last")), P([L("x1"), L("x2")], T("abcd")));
    const clip = internalClipboard(view, inB(view, 0, 2), inB(view, 1, 2));
    select(view, inB(view, 2, 2));
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc).map((row) => row.map((x) => x.text).join(""))).toEqual(["first", "last", "abrst", "lacd"]);
    expect(links(view.state.doc)).toEqual([["f1/student"], ["l1/coach"], ["x1/student", "x2/student", "f1/student"], ["l1/coach", "x1/student", "x2/student"]]);
    await finish("paste_internal_multi_middle", view);
  });

  test("an inline fragment pasted inside a non-empty paragraph changes nothing", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("one")), P([L("c2", "coach")], T("two")));
    // A text selection inside one paragraph copies just its inline content.
    const clip = new FakeClipboard();
    select(view, inB(view, 0, 1), inB(view, 0, 3));
    fire(view, "copy", "clipboardData", clip);
    select(view, inB(view, 1, 1));
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc).map((row) => row.map((x) => x.text).join(""))).toEqual(["one", "tnewo"]);
    expect(links(view.state.doc)).toEqual([["c1/student"], ["c2/coach"]]);
    await finish("paste_internal_fragment", view);
  });

  test("one paragraph (or part of one) pasted into an empty paragraph brings its links", async () => {
    const { view } = setup();
    load(view, P([L("c1"), L("c2", "coach")], T("source text")), P([]));
    const clip = internalClipboard(view, inB(view, 0, 7), inB(view, 0, 11)); // "text", with its paragraph around it
    select(view, startB(view, 1));
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc).map((row) => row.map((x) => x.text).join(""))).toEqual(["source text", "text"]);
    expect(links(view.state.doc)).toEqual([["c1/student", "c2/coach"], ["c1/student", "c2/coach"]]);
    await finish("paste_internal_into_empty", view);
  });

  test("external paste, with forged data-links and origin in its HTML, brings no links", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("abcd")));
    select(view, 3);
    const html =
      '<p data-links="cX">pasted <span data-origin-kind="quote" data-origin-ref="b81">forged</span> <span data-links="cY">x</span></p>';
    fire(view, "paste", "clipboardData", externalClipboard("pasted forged x", html));
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    expect(runs(view.state.doc)[0].filter((x) => x.origin === "paste_ext")).toHaveLength(1);
    expect(runs(view.state.doc)[0].some((x) => x.origin === "quote")).toBe(false);
    await finish("paste_external_into_linked", view);
  });

  test("stampSlice clears links on every paragraph, keeps other attrs, strips marks and stamps paste_ext", () => {
    const { view } = setup();
    const schema = view.state.schema;
    const doc = PMNode.fromJSON(schema, {
      type: "doc",
      content: [
        P([L("c1"), L("c2", "coach")], T("one")),
        { type: "heading", attrs: { level: 3 }, content: [T("two")] },
        { type: "bullet_list", content: [{ type: "list_item", content: [P([L("c3")], T("three"))] }] },
      ],
    });
    const stamped = stampSlice(schema, new Slice(doc.content, 0, 0), "px");
    const seen: string[] = [];
    stamped.content.descendants((n) => {
      if (n.type.name === "paragraph") expect(n.attrs.links).toEqual([]);
      if (n.type.name === "heading") expect(n.attrs.level).toBe(3);
      if (n.isText) {
        expect(n.marks.map((m) => `${m.type.name}:${m.attrs.kind}:${m.attrs.ref}`)).toEqual(["origin:paste_ext:px"]);
        seen.push(n.text!);
      }
      return true;
    });
    expect(seen).toEqual(["one", "two", "three"]);
  });

  test("external multi-paragraph paste: new paragraphs have no links; the joins only union X's own", async () => {
    const { view } = setup();
    load(view, P([L("c1")], T("abcd")));
    select(view, 3);
    const html = '<p data-links="cX">first</p><p>middle</p><p data-links="cY">last</p>';
    fire(view, "paste", "clipboardData", externalClipboard("first\n\nmiddle\n\nlast", html));
    expect(runs(view.state.doc).map((row) => row.map((x) => x.text).join(""))).toEqual(["abfirst", "middle", "lastcd"]);
    expect(links(view.state.doc)).toEqual([["c1/student"], [], ["c1/student"]]);
    await finish("paste_external_multi_para", view);
  });
});

describe("headings, lists, quotes, line breaks and formatting (D-044)", () => {
  test("a paragraph becomes h1, h2, h3; typing in a heading is typed", async () => {
    const { editor, view } = setup();
    load(view, P([], TXT("Title")));
    select(view, 3);
    for (const level of [1, 2, 3] as const) {
      expect(setHeading(editor, level)).toBe(true);
      expect(outline(view.state.doc)).toBe(`h${level}`);
    }
    select(view, endB(view, 0));
    type(view, "!");
    expect(runs(view.state.doc)).toEqual([[r("Title", "quote", "b81"), r("!", "typed")]]);
    await finish("heading_levels", view);
  });

  test("paragraph to heading drops the links; undo restores them", async () => {
    const { editor, view } = setup();
    load(view, P([L("c1"), L("c2", "coach")], T("Heading text")));
    view.dispatch(closeHistory(view.state.tr));
    select(view, 3);
    setHeading(editor, 2);
    expect(outline(view.state.doc)).toBe("h2");
    expect(links(view.state.doc)).toEqual([]);
    undo(view.state, view.dispatch);
    expect(outline(view.state.doc)).toBe("p[c1/student,c2/coach]");
    redo(view.state, view.dispatch);
    undo(view.state, view.dispatch);
    view.dispatch(closeHistory(view.state.tr));
    // Back to a paragraph by command: a fresh paragraph, no links.
    setHeading(editor, 1);
    setParagraph(editor);
    expect(outline(view.state.doc)).toBe("p[]");
    await finish("paragraph_to_heading_drops_links", view);
  });

  test("bullet list: wrap keeps links, Enter splits the item, Tab sinks, Shift-Tab lifts", async () => {
    const { editor, view } = setup();
    load(view, P([L("c1")], T("one")));
    select(view, endB(view, 0));
    expect(toggleBulletList(editor)).toBe(true);
    expect(outline(view.state.doc)).toBe("ul(li(p[c1/student]))");
    expect(press(view, "Enter")).toBe(true);
    expect(outline(view.state.doc)).toBe("ul(li(p[c1/student]),li(p[]))");
    type(view, "two");
    expect(press(view, "Tab")).toBe(true);
    expect(outline(view.state.doc)).toBe("ul(li(p[c1/student],ul(li(p[]))))");
    expect(press(view, "Tab", { shift: true })).toBe(true);
    expect(outline(view.state.doc)).toBe("ul(li(p[c1/student]),li(p[]))");
    expect(runs(view.state.doc)).toEqual([[r("one", "typed")], [r("two", "typed")]]);
    await finish("bullet_list_items", view);
  });

  test("ordered list over two paragraphs; Enter on an empty item leaves the list", async () => {
    const { editor, view } = setup();
    load(view, P([L("c1")], T("one")), P([L("c2", "coach")], T("two")));
    select(view, startB(view, 0), endB(view, 1));
    expect(toggleOrderedList(editor)).toBe(true);
    expect(outline(view.state.doc)).toBe("ol(li(p[c1/student]),li(p[c2/coach]))");
    select(view, endB(view, 1));
    press(view, "Enter");
    expect(outline(view.state.doc)).toBe("ol(li(p[c1/student]),li(p[c2/coach]),li(p[]))");
    press(view, "Enter");
    expect(outline(view.state.doc)).toBe("ol(li(p[c1/student]),li(p[c2/coach])),p[]");
    await finish("ordered_list", view);
  });

  test("a linked paragraph wrapped in a blockquote keeps its links", async () => {
    const { editor, view } = setup();
    load(view, P([L("c1")], T("quoted")));
    select(view, 3);
    expect(toggleBlockquote(editor)).toBe(true);
    expect(outline(view.state.doc)).toBe("bq(p[c1/student])");
    expect(toggleBlockquote(editor)).toBe(true);
    expect(outline(view.state.doc)).toBe("p[c1/student]");
    toggleBlockquote(editor);
    await finish("blockquote_wrap_linked", view);
  });

  test("Shift-Enter inserts a hard break; the text around it is typed", async () => {
    const { view } = setup();
    load(view, P([L("c1")]));
    select(view, 1);
    type(view, "a");
    expect(press(view, "Enter", { shift: true })).toBe(true);
    type(view, "b");
    const para = view.state.doc.child(0);
    expect(para.children.map((n) => n.type.name)).toEqual(["text", "hard_break", "text"]);
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    expect(runs(view.state.doc)).toEqual([[r("a", "typed"), r("b", "typed")]]);
    await finish("hard_break", view);
  });

  test("bold and italic: toggling a selection is a mark step that leaves origins alone; stored marks type as typed + mark", async () => {
    const { view } = setup();
    load(view, P([L("c1")], TXT("hello world")));
    const before = recordKey.getState(view.state)!.steps.length;
    select(view, 1, 6);
    expect(press(view, "b", { mod: true })).toBe(true);
    const added = recordKey.getState(view.state)!.steps.slice(before);
    expect(added.map((s) => s.stepType)).toEqual(["addMark"]);
    expect(formats(view.state.doc)).toEqual([["hello", ["strong"]], [" world", []]]);
    expect(runs(view.state.doc)).toEqual([[r("hello", "quote", "b81"), r(" world", "quote", "b81")]]);
    // A collapsed cursor with strong stored: a keystroke is typed + strong.
    select(view, endB(view, 0));
    expect(press(view, "b", { mod: true })).toBe(true);
    const { from, to } = view.state.selection;
    expect(view.someProp("handleTextInput", (f) => f(view, from, to, "!", () => view.state.tr))).toBe(true);
    // And an italic keystroke through the plain insertText path.
    expect(press(view, "i", { mod: true })).toBe(true);
    type(view, "?");
    expect(formats(view.state.doc).slice(-2)).toEqual([["!", ["strong"]], ["?", ["em", "strong"]]]);
    expect(runs(view.state.doc)[0].slice(-2)).toEqual([r("!", "typed"), r("?", "typed")]);
    expect(links(view.state.doc)).toEqual([["c1/student"]]);
    await finish("bold_italic", view);
  });
});

describe("schema parity: TipTap builds the same schema as web/schema.json", () => {
  test("nodes and marks match the spec loaded by schema.ts (and so by the Python replay)", () => {
    const { editor } = setup();
    const tip = editor.schema;
    expect(Object.keys(tip.nodes).sort()).toEqual(Object.keys(schemaJson.nodes).sort());
    expect(Object.keys(tip.marks).sort()).toEqual(Object.keys(schemaJson.marks).sort());
    expect(tip.topNodeType.name).toBe(schemaJson.topNode);
    const same = (name: string, theirs: Record<string, { default?: unknown }> | null | undefined, ours: Record<string, { default?: unknown }> | null | undefined) => {
      expect(Object.keys(theirs ?? {}).sort(), name).toEqual(Object.keys(ours ?? {}).sort());
      for (const [attr, a] of Object.entries(ours ?? {})) {
        expect(theirs![attr].default, `${name}.${attr}`).toEqual(a.default);
        expect("default" in theirs![attr], `${name}.${attr} required`).toBe("default" in a);
      }
    };
    for (const name of Object.keys(schemaJson.nodes)) {
      const ours = editorSchema.nodes[name].spec;
      const theirs = tip.nodes[name].spec;
      expect(theirs.content ?? undefined, `${name}.content`).toBe(ours.content);
      expect(theirs.group ?? undefined, `${name}.group`).toBe(ours.group);
      expect(!!theirs.inline, `${name}.inline`).toBe(!!ours.inline);
      expect(!!theirs.defining, `${name}.defining`).toBe(!!ours.defining);
      expect(theirs.selectable, `${name}.selectable`).toBe(ours.selectable);
      same(name, theirs.attrs, ours.attrs);
    }
    for (const name of Object.keys(schemaJson.marks)) {
      const ours = editorSchema.marks[name].spec;
      const theirs = tip.marks[name].spec;
      expect(theirs.inclusive, name).toBe(ours.inclusive);
      expect(theirs.excludes, name).toBe(ours.excludes);
      same(name, theirs.attrs, ours.attrs);
    }
  });

  test("TipTap's schema rejects what schema.json rejects", () => {
    const { editor } = setup();
    expect(() => editor.schema.marks.origin.create({ kind: "ai", ref: null })).toThrow();
    expect(() => editor.schema.nodes.paragraph.create({ links: [{ claim_id: "c1", by: "model" }] })).toThrow();
    expect(() => editor.schema.nodes.paragraph.create({ links: [{ claim_id: "c1", by: "coach", suggestion_id: "s" }] })).toThrow();
    expect(() => editor.schema.nodes.heading.create({ level: 4 })).toThrow();
  });

  test("canonical JSON matches Python's json.dumps(sort_keys, ensure_ascii=False)", () => {
    expect(canonicalJson({ b: 1, a: [null, true, "é😀"], "\u{1F600}": 0, "～": 1 })).toBe(
      '{"a":[null,true,"é😀"],"b":1,"～":1,"😀":0}',
    );
    expect(() => canonicalJson({ x: 0.5 })).toThrow();
  });
});

describe("the step allowlist (D-044)", () => {
  test("replaySteps refuses a step type outside the list, before loading it", () => {
    const start = { type: "doc", content: [{ type: "paragraph" }] };
    expect(() => replaySteps(editorSchema, start, [{ stepType: "markSet", steps: [] }])).toThrow(ReplayError);
    expect(() => replaySteps(editorSchema, start, [{ stepType: "nope" }])).toThrow(ReplayError);
    expect(() => replaySteps(editorSchema, start, [{}])).toThrow(ReplayError);
    expect([...ALLOWED_STEP_TYPES].sort()).toEqual(
      ["addMark", "addNodeMark", "attr", "docAttr", "removeMark", "removeNodeMark", "replace", "replaceAround"],
    );
  });
});

// ---------- fixture: written on request, otherwise compared ----------

describe("replay fixture (shared with the Python replay)", () => {
  test("the recorded cases match prototype/fixtures/replay/s1_steps.json", () => {
    expect(recorded.length).toBeGreaterThanOrEqual(50);
    expect(new Set(recorded.map((c) => c.name)).size).toBe(recorded.length);
    for (const c of recorded) {
      for (const s of c.steps) expect(ALLOWED_STEP_TYPES.has(s.stepType as string), `${c.name}: ${s.stepType}`).toBe(true);
    }
    const fixture = {
      "x-note":
        "Generated by prototype/web/src/editor/s1.test.ts (UPDATE_S1_FIXTURES=1). Each case: start doc, recorded steps, the browser's final doc and its doc_hash. server/tests/test_replay_s1.py replays the steps in Python and must reach the same doc and hash.",
      schema_version: schemaJson["x-writing-room"].schema_version,
      cases: [...recorded].sort((a, b) => a.name.localeCompare(b.name)),
    };
    const text = JSON.stringify(fixture, null, 1) + "\n";
    if (process.env.UPDATE_S1_FIXTURES) {
      mkdirSync(dirname(FIXTURE), { recursive: true });
      writeFileSync(FIXTURE, text);
    }
    expect(JSON.parse(readFileSync(FIXTURE, "utf8"))).toEqual(JSON.parse(text));
  });
});
