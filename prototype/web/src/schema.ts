// Loads the one editor schema (web/schema.json, D33) into ProseMirror.
// Every attribute with an `enum` list gets a validate check, so a mark whose
// value is outside the closed list fails Mark.fromJSON and node.check().
import { Schema, type AttributeSpec, type MarkSpec, type NodeSpec } from "prosemirror-model";
import schemaJson from "../schema.json";

type JsonAttr = { default?: unknown; validate?: string; enum?: readonly unknown[] };
type JsonSpec = { attrs?: Record<string, JsonAttr>; [key: string]: unknown };
type JsonSchema = {
  topNode?: string;
  nodes: Record<string, JsonSpec>;
  marks: Record<string, JsonSpec>;
};

export const ORIGIN_KINDS: readonly string[] = schemaJson.marks.origin.attrs.kind.enum;
export const CLAIM_BY: readonly string[] = schemaJson.marks.claim.attrs.by.enum;

function typeCheck(types: string, where: string, value: unknown): void {
  const got = value === null ? "null" : typeof value;
  if (!types.split("|").includes(got)) {
    throw new RangeError(`Expected ${types} for ${where}, got ${got}`);
  }
}

function toAttrSpec(where: string, spec: JsonAttr): AttributeSpec {
  const out: AttributeSpec = {};
  if ("default" in spec) out.default = spec.default;
  const { validate, enum: allowed } = spec;
  if (validate !== undefined || allowed !== undefined) {
    out.validate = (value: unknown) => {
      if (validate !== undefined) typeCheck(validate, where, value);
      if (allowed !== undefined && !allowed.includes(value)) {
        throw new RangeError(`${where} must be one of ${allowed.join(", ")}, got ${String(value)}`);
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
