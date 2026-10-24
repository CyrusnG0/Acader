// @vitest-environment jsdom
/// <reference types="node" />
// Spike S1 (design/evaluation.md §1): do origin and claim marks survive real
// editing, and does replay from the recorded steps give the same document?
//
// Every case runs in a real TipTap editor (jsdom), checks the marks, replays
// its recorded steps in JS, and is written to a shared fixture that the Python
// replay (server/tests/test_replay_s1.py) replays too. If the editor's output
// changes, this test fails until the fixture is regenerated on purpose:
//   UPDATE_S1_FIXTURES=1 npx vitest run src/editor/s1.test.ts
import { afterEach, describe, expect, test } from "vitest";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { Editor } from "@tiptap/core";
import { AllSelection, TextSelection } from "@tiptap/pm/state";
import { splitBlock } from "@tiptap/pm/commands";
import { closeHistory, redo, undo } from "@tiptap/pm/history";
import type { Node as PMNode } from "@tiptap/pm/model";
import type { EditorView } from "@tiptap/pm/view";
import schemaJson from "../../schema.json";
import { editorSchema } from "../schema";
import { canonicalJson, docHash } from "./canonical";
import { createEditor } from "./editor";
import { SLICE_MIME, insertMarked, originKey } from "./origin";
import { flattenStepJson, recordKey, replaySteps, type JsonObject } from "./record";
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

function select(view: EditorView, from: number, to = from) {
  view.dispatch(view.state.tr.setSelection(TextSelection.create(view.state.doc, from, to)));
}

const quote = { kind: "quote", ref: "b81" };

type Run = { text: string; origin: string | null; ref: string | null; claim: string | null };

function runs(doc: PMNode): Run[][] {
  const out: Run[][] = [];
  doc.forEach((para) => {
    const row: Run[] = [];
    para.forEach((t) => {
      const o = t.marks.find((m) => m.type.name === "origin");
      const c = t.marks.find((m) => m.type.name === "claim");
      row.push({
        text: t.text ?? "",
        origin: o ? (o.attrs.kind as string) : null,
        ref: o ? (o.attrs.ref as string | null) : null,
        claim: c ? `${c.attrs.claim_id}/${c.attrs.by}` : null,
      });
    });
    out.push(row);
  });
  return out;
}

const r = (text: string, origin: string, ref: string | null = null, claim: string | null = null): Run => ({
  text,
  origin,
  ref,
  claim,
});

/** Every character carries exactly one origin. */
function everyCharHasOrigin(doc: PMNode) {
  doc.descendants((n) => {
    if (n.isText) expect(n.marks.filter((m) => m.type.name === "origin")).toHaveLength(1);
  });
}

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

  for (const by of ["student", "coach", "import"]) {
    test(`typing inside and at the edges of a claim span (by ${by})`, async () => {
      const { view } = setup();
      insertMarked(view, "claimed", quote, { claim_id: "c3", by, suggestion_id: by === "student" ? "s1" : null });
      select(view, 4);
      type(view, "_");
      select(view, 1);
      type(view, "[");
      select(view, view.state.doc.content.size - 1);
      type(view, "]");
      expect(runs(view.state.doc)).toEqual([
        [
          r("[", "typed"),
          r("cla", "quote", "b81", `c3/${by}`),
          r("_", "typed"),
          r("imed", "quote", "b81", `c3/${by}`),
          r("]", "typed"),
        ],
      ]);
      await finish(`typed_claim_${by}`, view);
    });
  }

  test("a keystroke through handleTextInput is one step, already typed, also inside a span", async () => {
    const { view } = setup();
    insertMarked(view, "abcd", quote, { claim_id: "c9", by: "coach" });
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
    expect(runs(view.state.doc)).toEqual([
      [r("ab", "quote", "b81", "c9/coach"), r("xy", "typed"), r("cd", "quote", "b81", "c9/coach")],
    ]);
    expect(view.state.selection.from).toBe(5);
    await finish("keystroke_handle_text_input", view);
  });

  test("select-all then type replaces everything with typed text", async () => {
    const { view } = setup();
    insertMarked(view, "a quote", quote, { claim_id: "c1", by: "student" });
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
    splitBlock(view.state, view.dispatch);
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
    insertMarked(view, "quoted", quote, { claim_id: "c2", by: "student" });
    const clip = new FakeClipboard();
    select(view, 1, view.state.doc.content.size - 1);
    fire(view, "copy", "clipboardData", clip);
    expect(JSON.parse(clip.getData(SLICE_MIME)).log_id).toBe("log_A");
    select(view, view.state.doc.content.size - 1);
    fire(view, "paste", "clipboardData", clip);
    expect(runs(view.state.doc)).toEqual([
      [r("I ", "typed"), r("quoted", "quote", "b81", "c2/student"), r("I ", "typed"), r("quoted", "quote", "b81", "c2/student")],
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

describe("schema parity: TipTap builds the same schema as web/schema.json", () => {
  test("nodes and marks match the spec loaded by schema.ts (and so by the Python replay)", () => {
    const { editor } = setup();
    const tip = editor.schema;
    expect(Object.keys(tip.nodes).sort()).toEqual(Object.keys(schemaJson.nodes).sort());
    expect(Object.keys(tip.marks).sort()).toEqual(Object.keys(schemaJson.marks).sort());
    expect(tip.topNodeType.name).toBe(schemaJson.topNode);
    for (const [name, spec] of Object.entries(schemaJson.nodes) as [string, { content?: string; group?: string }][]) {
      expect(tip.nodes[name].spec.content ?? undefined, name).toBe(spec.content);
      expect(tip.nodes[name].spec.group ?? undefined, name).toBe(spec.group);
    }
    for (const name of Object.keys(schemaJson.marks)) {
      const ours = editorSchema.marks[name];
      const theirs = tip.marks[name];
      expect(theirs.spec.inclusive, name).toBe(ours.spec.inclusive);
      expect(theirs.spec.excludes, name).toBe(ours.spec.excludes);
      expect(Object.keys(theirs.spec.attrs ?? {}).sort(), name).toEqual(Object.keys(ours.spec.attrs ?? {}).sort());
      for (const [attr, a] of Object.entries(ours.spec.attrs ?? {})) {
        expect(theirs.spec.attrs![attr].default, `${name}.${attr}`).toEqual(a.default);
        expect("default" in theirs.spec.attrs![attr], `${name}.${attr} required`).toBe("default" in a);
      }
    }
  });

  test("TipTap's marks reject a kind outside the closed list", () => {
    const { editor } = setup();
    expect(() => editor.schema.marks.origin.create({ kind: "ai", ref: null })).toThrow();
    expect(() => editor.schema.marks.claim.create({ claim_id: "c1", by: "model" })).toThrow();
  });

  test("canonical JSON matches Python's json.dumps(sort_keys, ensure_ascii=False)", () => {
    expect(canonicalJson({ b: 1, a: [null, true, "é😀"], "\u{1F600}": 0, "～": 1 })).toBe(
      '{"a":[null,true,"é😀"],"b":1,"～":1,"😀":0}',
    );
    expect(() => canonicalJson({ x: 0.5 })).toThrow();
  });
});

// ---------- fixture: written on request, otherwise compared ----------

describe("replay fixture (shared with the Python replay)", () => {
  test("the recorded cases match prototype/fixtures/replay/s1_steps.json", () => {
    expect(recorded.length).toBeGreaterThanOrEqual(25);
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
