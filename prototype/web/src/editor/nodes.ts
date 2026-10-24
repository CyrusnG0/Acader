// TipTap node extensions built from web/schema.json (D33, D-044), so TipTap's
// schema equals buildSchema(schemaJson). Structure (group, content, inline,
// defining, selectable, attrs and their validation) comes from the JSON;
// rendering and parsing can't live in JSON and are added here.
//
// `doc` and `text` use TipTap's own Document and Text (same content and group).
import { Node } from "@tiptap/core";
import Document from "@tiptap/extension-document";
import Text from "@tiptap/extension-text";
import schemaJson from "../../schema.json";
import { toAttrSpec, type JsonAttr } from "../schema";

type JsonNode = {
  group?: string;
  content?: string;
  inline?: boolean;
  defining?: boolean;
  selectable?: boolean;
  attrs?: Record<string, JsonAttr>;
};

type Rendering = {
  parse: Array<{ tag: string }>;
  tag: (attrs: Record<string, unknown>) => string;
  hole: boolean;
};

const nodeSpecs = schemaJson.nodes as Record<string, JsonNode>;

function level(el: HTMLElement): number {
  return Math.min(3, Number(el.tagName.slice(1)) || 1);
}

/** Attrs that need more than the JSON gives: HTML never brings links in; headings read their level from the tag. */
function extraAttrs(name: string, attr: string): Record<string, unknown> {
  if (name === "paragraph" && attr === "links") {
    return {
      keepOnSplit: false,
      parseHTML: () => [],
      renderHTML: (attrs: Record<string, unknown>) => {
        const links = (attrs.links ?? []) as Array<{ claim_id: string }>;
        return links.length ? { "data-links": links.map((l) => l.claim_id).join(" ") } : {};
      },
    };
  }
  if (name === "heading" && attr === "level") {
    return { parseHTML: level, rendered: false };
  }
  return {};
}

const RENDER: Record<string, Rendering> = {
  paragraph: { parse: [{ tag: "p" }], tag: () => "p", hole: true },
  heading: {
    parse: ["h1", "h2", "h3", "h4", "h5", "h6"].map((tag) => ({ tag })),
    tag: (attrs) => `h${attrs.level as number}`,
    hole: true,
  },
  blockquote: { parse: [{ tag: "blockquote" }], tag: () => "blockquote", hole: true },
  bullet_list: { parse: [{ tag: "ul" }], tag: () => "ul", hole: true },
  ordered_list: { parse: [{ tag: "ol" }], tag: () => "ol", hole: true },
  list_item: { parse: [{ tag: "li" }], tag: () => "li", hole: true },
  hard_break: { parse: [{ tag: "br" }], tag: () => "br", hole: false },
};

function nodeFromJson(name: string, spec: JsonNode, rendering: Rendering) {
  const attrs = spec.attrs ?? {};
  return Node.create({
    name,
    group: spec.group,
    content: spec.content,
    inline: spec.inline,
    defining: spec.defining,
    selectable: spec.selectable,
    addAttributes() {
      return Object.fromEntries(
        Object.entries(attrs).map(([attr, a]) => {
          const pm = toAttrSpec(`${name}.${attr}`, a);
          return [attr, { default: pm.default, validate: pm.validate, ...extraAttrs(name, attr) }];
        }),
      );
    },
    parseHTML() {
      return rendering.parse;
    },
    renderHTML({ node, HTMLAttributes }) {
      const tag = rendering.tag(node.attrs);
      return rendering.hole ? [tag, HTMLAttributes, 0] : [tag, HTMLAttributes];
    },
  });
}

/** One TipTap extension per node in schema.json, in the file's order. */
export const schemaNodes = Object.entries(nodeSpecs).map(([name, spec]) => {
  if (name === "doc") return Document;
  if (name === "text") return Text;
  return nodeFromJson(name, spec, RENDER[name]);
});
