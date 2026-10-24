// Loads the one editor schema (web/schema.json, D33) into ProseMirror.
// Every attribute with an `enum` list gets a validate check, so a mark whose
// value is outside the closed list fails Mark.fromJSON and node.check().
//
// An attr with `items` (the paragraph `links` list) is an array whose items are
// plain objects: keys must be a subset of `items`, a key without `optional: true`
// is required, each present key is checked with its own validate / enum, and a
// key with `only_when: { other: value }` may only be present when the sibling
// key `other` equals `value`. The Python loader (engine/replay) implements the
// same rules.
import { Schema, type AttributeSpec, type MarkSpec, type NodeSpec } from "prosemirror-model";
import schemaJson from "../schema.json";

export type JsonAttr = {
  default?: unknown;
  validate?: string;
  enum?: readonly unknown[];
  items?: Record<string, JsonAttr>;
  optional?: boolean;
  only_when?: Record<string, unknown>;
};
type JsonSpec = { attrs?: Record<string, JsonAttr>; [key: string]: unknown };
type JsonSchema = {
  topNode?: string;
  nodes: Record<string, JsonSpec>;
  marks: Record<string, JsonSpec>;
};

export const ORIGIN_KINDS: readonly string[] = schemaJson.marks.origin.attrs.kind.enum;
export const LINK_BY: readonly string[] = schemaJson.nodes.paragraph.attrs.links.items.by.enum;

function kindOf(value: unknown): string {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  return typeof value;
}

function typeCheck(types: string, where: string, value: unknown): void {
  const got = kindOf(value);
  if (!types.split("|").includes(got)) {
    throw new RangeError(`Expected ${types} for ${where}, got ${got}`);
  }
}

function checkOne(where: string, spec: JsonAttr, value: unknown): void {
  if (spec.validate !== undefined) typeCheck(spec.validate, where, value);
  if (spec.enum !== undefined && !spec.enum.includes(value)) {
    throw new RangeError(`${where} must be one of ${spec.enum.join(", ")}, got ${String(value)}`);
  }
}

function checkItem(where: string, items: Record<string, JsonAttr>, item: unknown): void {
  typeCheck("object", where, item);
  const obj = item as Record<string, unknown>;
  for (const key of Object.keys(obj)) {
    if (!(key in items)) throw new RangeError(`Unknown key ${key} in ${where}`);
  }
  for (const [key, spec] of Object.entries(items)) {
    if (!(key in obj)) {
      if (!spec.optional) throw new RangeError(`Missing key ${key} in ${where}`);
      continue;
    }
    checkOne(`${where}.${key}`, spec, obj[key]);
    for (const [other, expected] of Object.entries(spec.only_when ?? {})) {
      if (obj[other] !== expected) {
        throw new RangeError(`${where}.${key} is only allowed when ${other} is ${String(expected)}`);
      }
    }
  }
}

export function toAttrSpec(where: string, spec: JsonAttr): AttributeSpec {
  const out: AttributeSpec = {};
  if ("default" in spec) out.default = spec.default;
  const { validate, enum: allowed, items } = spec;
  if (validate !== undefined || allowed !== undefined || items !== undefined) {
    out.validate = (value: unknown) => {
      checkOne(where, spec, value);
      if (items !== undefined) {
        (value as unknown[]).forEach((item, i) => checkItem(`${where}[${i}]`, items, item));
      }
    };
  }
  return out;
}

function mapSpecs(specs: Record<string, JsonSpec>): Record<string, NodeSpec & MarkSpec> {
  return Object.fromEntries(
    Object.entries(specs).map(([name, { attrs, ...rest }]) => {
      const out: Record<string, unknown> = { ...rest };
      if (attrs) {
        out.attrs = Object.fromEntries(
          Object.entries(attrs).map(([attr, a]) => [attr, toAttrSpec(`${name}.${attr}`, a)]),
        );
      }
      return [name, out];
    }),
  );
}

export function buildSchema(json: JsonSchema): Schema {
  return new Schema({
    topNode: json.topNode,
    nodes: mapSpecs(json.nodes),
    marks: mapSpecs(json.marks),
  });
}

export const editorSchema = buildSchema(schemaJson);
