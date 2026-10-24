import { describe, expect, test } from "vitest";
import { Mark, Node, type Mark as PMMark } from "prosemirror-model";
import schemaJson from "../schema.json";
import { LINK_BY, ORIGIN_KINDS, editorSchema as schema } from "./schema";

const origin = (kind: string, ref: string | null = null) => schema.marks.origin.create({ kind, ref });
const text = (t: string, ...marks: PMMark[]) => schema.text(t, marks);
const para = (...children: Node[]) => schema.node("paragraph", null, children);
const doc = (...paras: Node[]) => schema.node("doc", null, paras);

const originOf = (marks: readonly PMMark[]) => marks.filter((m) => m.type.name === "origin");

/** A one-paragraph document JSON whose paragraph carries these links. */
const withLinks = (links: unknown) => ({ type: "doc", content: [{ type: "paragraph", attrs: { links } }] });
const check = (links: unknown) => Node.fromJSON(schema, withLinks(links)).check();

describe("nodes and marks (D-044)", () => {
  test("node and mark names are the D-044 list, in order", () => {
    expect(Object.keys(schemaJson.nodes)).toEqual([
      "doc",
      "paragraph",
      "heading",
      "blockquote",
      "bullet_list",
      "ordered_list",
      "list_item",
      "text",
      "hard_break",
    ]);
    expect(Object.keys(schema.nodes)).toEqual(Object.keys(schemaJson.nodes));
    expect(Object.keys(schema.marks)).toEqual(["origin", "em", "strong"]);
    expect("claim" in schema.marks).toBe(false);
  });

  test("em and strong have no attrs", () => {
    expect(Object.keys(schema.marks.em.spec.attrs ?? {})).toEqual([]);
    expect(Object.keys(schema.marks.strong.spec.attrs ?? {})).toEqual([]);
  });

  test.each([1, 2, 3])("heading level %s is accepted", (level) => {
    const d = Node.fromJSON(schema, { type: "doc", content: [{ type: "heading", attrs: { level } }] });
    expect(() => d.check()).not.toThrow();
  });

  test.each([4, 0, "1", null])("heading level %s is rejected", (level) => {
    expect(() =>
      Node.fromJSON(schema, { type: "doc", content: [{ type: "heading", attrs: { level } }] }).check(),
    ).toThrow(RangeError);
  });
});

describe("origin mark: closed list (event-log.md §4)", () => {
  test("the list is exactly the six kinds in the design table", () => {
    expect([...ORIGIN_KINDS]).toEqual(["typed", "paste_ext", "quote", "helper", "coach", "import"]);
    expect(Object.keys(schemaJson.marks.origin["x-ref-by-kind"])).toEqual([...ORIGIN_KINDS]);
  });

  test("attrs are kind (required) and ref (default null), nothing else", () => {
    const attrs = schema.marks.origin.spec.attrs ?? {};
    expect(Object.keys(attrs)).toEqual(["kind", "ref"]);
    expect("default" in attrs.kind).toBe(false);
    expect(attrs.ref.default).toBeNull();
    expect(() => schema.marks.origin.create({})).toThrow();
  });

  test.each([...ORIGIN_KINDS])("kind %s is accepted from JSON", (kind) => {
    const ref = kind === "typed" ? null : "ref-1";
    const m = Mark.fromJSON(schema, { type: "origin", attrs: { kind, ref } });
    expect(m.attrs).toEqual({ kind, ref });
  });

  test.each(["ai", "AI-written", "outside", "Typed", "", null, 1])(
    "kind %s outside the list is rejected from JSON",
    (kind) => {
      expect(() => Mark.fromJSON(schema, { type: "origin", attrs: { kind } })).toThrow(RangeError);
    },
  );

  test("a replayed doc with an unknown origin kind fails check()", () => {
    const json = {
      type: "doc",
      content: [
        {
          type: "paragraph",
          content: [{ type: "text", text: "x", marks: [{ type: "origin", attrs: { kind: "model", ref: null } }] }],
        },
      ],
    };
    expect(() => Node.fromJSON(schema, json).check()).toThrow(RangeError);
  });

  test("an unknown attribute on origin is dropped, never stored", () => {
    const m = Mark.fromJSON(schema, { type: "origin", attrs: { kind: "typed", ref: null, score: 1 } });
    expect(m.attrs).toEqual({ kind: "typed", ref: null });
  });

  test("a character carries at most one origin: a new origin replaces the old one", () => {
    const set = origin("typed").addToSet([origin("paste_ext", "p1")]);
    expect(originOf(set).map((m) => m.attrs.kind)).toEqual(["typed"]);
    const twoOrigins = { type: "text", text: "x", marks: [
      { type: "origin", attrs: { kind: "typed", ref: null } },
      { type: "origin", attrs: { kind: "paste_ext", ref: "p1" } },
    ] };
    expect(() => Node.fromJSON(schema, { type: "doc", content: [{ type: "paragraph", content: [twoOrigins] }] }).check()).toThrow(RangeError);
  });
});

describe("paragraph links: [{claim_id, by, suggestion_id?}] (D-044, D-045)", () => {
  test("the attr is `links`, default [], and nothing else", () => {
    const attrs = schema.nodes.paragraph.spec.attrs ?? {};
    expect(Object.keys(attrs)).toEqual(["links"]);
    expect(attrs.links.default).toEqual([]);
    expect(schema.nodes.paragraph.create().attrs.links).toEqual([]);
    expect(Node.fromJSON(schema, { type: "doc", content: [{ type: "paragraph" }] }).child(0).attrs.links).toEqual([]);
  });

  test("by is the closed list student | coach | import", () => {
    expect([...LINK_BY]).toEqual(["student", "coach", "import"]);
  });

  test("valid items pass check(), with and without suggestion_id", () => {
    expect(() => check([])).not.toThrow();
    expect(() => check([{ claim_id: "c1", by: "student" }])).not.toThrow();
    expect(() => check([{ claim_id: "c1", by: "student", suggestion_id: "s9" }])).not.toThrow();
    expect(() => check([{ claim_id: "c1", by: "coach" }, { claim_id: "c2", by: "import" }])).not.toThrow();
    expect(() => check([{ claim_id: "", by: "coach" }])).not.toThrow(); // the commands refuse it, the schema does not
  });

  test.each([
    ["not an array", { claim_id: "c1", by: "student" }],
    ["a string", "c1"],
    ["null", null],
    ["item not an object", ["c1"]],
    ["item is null", [null]],
    ["item is an array", [["c1", "student"]]],
    ["by model", [{ claim_id: "c1", by: "model" }]],
    ["by mapper", [{ claim_id: "c1", by: "mapper" }]],
    ["missing claim_id", [{ by: "student" }]],
    ["missing by", [{ claim_id: "c1" }]],
    ["claim_id a number", [{ claim_id: 7, by: "student" }]],
    ["unknown key", [{ claim_id: "c1", by: "student", score: 1 }]],
    ["suggestion_id with by coach", [{ claim_id: "c1", by: "coach", suggestion_id: "s1" }]],
    ["suggestion_id with by import", [{ claim_id: "c1", by: "import", suggestion_id: "s1" }]],
    ["suggestion_id null", [{ claim_id: "c1", by: "student", suggestion_id: null }]],
    ["suggestion_id a number", [{ claim_id: "c1", by: "student", suggestion_id: 3 }]],
  ])("rejected: %s", (_name, links) => {
    expect(() => check(links)).toThrow(RangeError);
  });

  test("create() refuses a bad links value too", () => {
    expect(() => schema.nodes.paragraph.create({ links: [{ claim_id: "c1", by: "model" }] })).toThrow(RangeError);
  });
});

// D21: typed text is always `typed`, including at the edges of marked spans.
// The schema's share of that rule is `inclusive: false`: text inserted at the
// edge of a marked span never inherits its origin mark. Typing inside a span is
// the input plugin's job (T-004, spike S1), not the schema's.
describe("typed text at the edges of marked spans (D21)", () => {
  test("origin is not inclusive", () => {
    expect(schema.marks.origin.spec.inclusive).toBe(false);
  });

  const pasted = text("PASTED", origin("paste_ext", "p1"));
  const quoted = text("QUOTE", origin("quote", "b7"));
  const typed = text("typed ", origin("typed"));

  const inherited = (d: Node, pos: number) => d.resolve(pos).marks();
  const nonTyped = (marks: readonly PMMark[]) => originOf(marks).filter((m) => m.attrs.kind !== "typed").length;

  test("after a pasted span at the end of a paragraph", () => {
    const d = doc(para(typed, pasted));
    expect(nonTyped(inherited(d, d.content.size - 1))).toBe(0);
  });

  test("before a pasted span at the start of a paragraph", () => {
    const d = doc(para(pasted, typed));
    expect(nonTyped(inherited(d, 1))).toBe(0);
  });

  test("between two different marked spans", () => {
    const d = doc(para(pasted, quoted));
    expect(nonTyped(inherited(d, 1 + pasted.nodeSize))).toBe(0);
  });

  test("between a marked span and typed text, on either side", () => {
    const d = doc(para(typed, quoted, typed));
    expect(nonTyped(inherited(d, 1 + typed.nodeSize))).toBe(0);
    expect(nonTyped(inherited(d, 1 + typed.nodeSize + quoted.nodeSize))).toBe(0);
  });

  test("every non-typed kind behaves the same at the edge", () => {
    for (const kind of ORIGIN_KINDS.filter((k) => k !== "typed")) {
      const span = text("SPAN", origin(kind, "r1"));
      const d = doc(para(span));
      expect(nonTyped(inherited(d, 1))).toBe(0);
      expect(nonTyped(inherited(d, 1 + span.nodeSize))).toBe(0);
    }
  });
});
