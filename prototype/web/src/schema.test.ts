import { describe, expect, test } from "vitest";
import { Mark, Node, type Mark as PMMark } from "prosemirror-model";
import schemaJson from "../schema.json";
import { CLAIM_BY, ORIGIN_KINDS, editorSchema as schema } from "./schema";

const origin = (kind: string, ref: string | null = null) => schema.marks.origin.create({ kind, ref });
const claim = (claim_id: string, by: string, suggestion_id: string | null = null) =>
  schema.marks.claim.create({ claim_id, by, suggestion_id });
const text = (t: string, ...marks: PMMark[]) => schema.text(t, marks);
const para = (...children: Node[]) => schema.node("paragraph", null, children);
const doc = (...paras: Node[]) => schema.node("doc", null, paras);

const originOf = (marks: readonly PMMark[]) => marks.filter((m) => m.type.name === "origin");
const claimOf = (marks: readonly PMMark[]) => marks.filter((m) => m.type.name === "claim");

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

describe("claim mark {claim_id, by} with optional suggestion_id", () => {
  test("attrs are claim_id and by (required) and suggestion_id (default null)", () => {
    const attrs = schema.marks.claim.spec.attrs ?? {};
    expect(Object.keys(attrs)).toEqual(["claim_id", "by", "suggestion_id"]);
    expect("default" in attrs.claim_id).toBe(false);
    expect("default" in attrs.by).toBe(false);
    expect(attrs.suggestion_id.default).toBeNull();
  });

  test("by is the closed list student | coach | import", () => {
    expect([...CLAIM_BY]).toEqual(["student", "coach", "import"]);
    expect(() => Mark.fromJSON(schema, { type: "claim", attrs: { claim_id: "c1", by: "mapper" } })).toThrow(RangeError);
    expect(() => Mark.fromJSON(schema, { type: "claim", attrs: { claim_id: "c1", by: "model" } })).toThrow(RangeError);
  });

  test("suggestion_id is optional and kept when given", () => {
    expect(Mark.fromJSON(schema, { type: "claim", attrs: { claim_id: "c1", by: "student" } }).attrs).toEqual({
      claim_id: "c1",
      by: "student",
      suggestion_id: null,
    });
    expect(
      Mark.fromJSON(schema, { type: "claim", attrs: { claim_id: "c1", by: "student", suggestion_id: "s9" } }).attrs
        .suggestion_id,
    ).toBe("s9");
  });

  test("claim_id and by are required; claim_id must be a string", () => {
    expect(() => schema.marks.claim.create({ by: "student" })).toThrow();
    expect(() => schema.marks.claim.create({ claim_id: "c1" })).toThrow();
    expect(() => Mark.fromJSON(schema, { type: "claim", attrs: { claim_id: 7, by: "student" } })).toThrow(RangeError);
  });

  test("a claim mark sits alongside the origin mark", () => {
    const t = text("linked", origin("typed"), claim("c1", "student"));
    expect(originOf(t.marks)).toHaveLength(1);
    expect(claimOf(t.marks)).toHaveLength(1);
    expect(() => doc(para(t)).check()).not.toThrow();
  });
});

// D21: typed text is always `typed`, including at the edges of marked spans.
// The schema's share of that rule is `inclusive: false`: text inserted at the
// edge of a marked span never inherits its origin or claim mark. Typing inside
// a span is the input plugin's job (T-004, spike S1), not the schema's.
describe("typed text at the edges of marked spans (D21)", () => {
  test("origin and claim are not inclusive", () => {
    expect(schema.marks.origin.spec.inclusive).toBe(false);
    expect(schema.marks.claim.spec.inclusive).toBe(false);
  });

  const pasted = text("PASTED", origin("paste_ext", "p1"), claim("c1", "student", "s1"));
  const quoted = text("QUOTE", origin("quote", "b7"));
  const typed = text("typed ", origin("typed"));

  const inherited = (d: Node, pos: number) => d.resolve(pos).marks();
  const nonTyped = (marks: readonly PMMark[]) =>
    originOf(marks).filter((m) => m.attrs.kind !== "typed").length + claimOf(marks).length;

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

  test("every non-typed kind and every claim `by` behaves the same at the edge", () => {
    for (const kind of ORIGIN_KINDS.filter((k) => k !== "typed")) {
      for (const by of CLAIM_BY) {
        const span = text("SPAN", origin(kind, "r1"), claim("c1", by));
        const d = doc(para(span));
        expect(nonTyped(inherited(d, 1))).toBe(0);
        expect(nonTyped(inherited(d, 1 + span.nodeSize))).toBe(0);
      }
    }
  });
});
