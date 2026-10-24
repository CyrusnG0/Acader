// TipTap mark extensions built from web/schema.json (D33), so the editor's
// schema and the Python replay's schema come from the same file. Rendering
// (parseHTML / renderHTML) can't live in JSON, so it is added here: each mark
// is a <span> carrying its attrs as data-* attributes.
import { Mark } from "@tiptap/core";
import schemaJson from "../../schema.json";
import { toAttrSpec, type JsonAttr } from "../schema";

type JsonMark = {
  inclusive?: boolean;
  excludes?: string;
  attrs?: Record<string, JsonAttr>;
};

const dataName = (mark: string, attr: string) => `data-${mark}-${attr.replace(/_/g, "-")}`;

function markFromJson(name: string, spec: JsonMark) {
  const attrs = spec.attrs ?? {};
  return Mark.create({
    name,
    inclusive: spec.inclusive,
    excludes: spec.excludes,
    addAttributes() {
      return Object.fromEntries(
        Object.entries(attrs).map(([attr, a]) => {
          const pm = toAttrSpec(`${name}.${attr}`, a);
          const required = !("default" in a);
          return [
            attr,
            {
              ...(required ? { isRequired: true } : { default: pm.default }),
              validate: pm.validate,
              parseHTML: (el: HTMLElement) => el.getAttribute(dataName(name, attr)),
              renderHTML: (values: Record<string, unknown>) => {
                const v = values[attr];
                return v === null || v === undefined ? {} : { [dataName(name, attr)]: String(v) };
              },
            },
          ];
        }),
      );
    },
    parseHTML() {
      return [{ tag: `span[data-${name}-${Object.keys(attrs)[0]?.replace(/_/g, "-")}]` }];
    },
    renderHTML({ HTMLAttributes }) {
      return ["span", HTMLAttributes, 0];
    },
  });
}

const marks = schemaJson.marks as Record<string, JsonMark>;

/** One TipTap extension per mark in schema.json (origin, claim). */
export const schemaMarks = Object.entries(marks).map(([name, spec]) => markFromJson(name, spec));
