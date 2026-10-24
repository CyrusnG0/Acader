// Paragraph links (D-044, D-045): a paragraph carries a `links` list, each item
// pointing at a claim in the student's map. Links are set on purpose, by the
// three commands below, as one `attr` step each. Ordinary editing never
// changes them, except where two paragraphs are joined or split:
//
// - Typing, IME, replacement, adding a sentence, deleting all the text of a
//   paragraph: links unchanged.
// - Enter splits a paragraph; ProseMirror copies the node, so both halves keep
//   their links, except Enter at the end, where the new paragraph starts empty
//   (keepOnSplit is false). Enter at the start of a linked paragraph leaves the
//   text paragraph linked and the new empty one above it unlinked (J3).
// - Joining two paragraphs (Backspace, Delete, deleting a selection across
//   paragraphs, a multi-paragraph internal paste) gives the surviving paragraph
//   the union of both link lists (J1, J2). A paragraph that is deleted whole
//   takes its links with it.
// - External paste and drop never bring links (stampSlice clears them).
import { Plugin, type Command, type EditorState, type Transaction } from "@tiptap/pm/state";
import { ReplaceStep } from "@tiptap/pm/transform";
import { isHistoryTransaction } from "@tiptap/pm/history";
import type { Node as PMNode, Slice } from "@tiptap/pm/model";
import { LINK_BY } from "../schema";

export type Link = { claim_id: string; by: "student" | "coach" | "import"; suggestion_id?: string };

/** Meta on every transaction that changes links: "link" | "unlink" | "accept" | "structure". */
export const LINK_META = "wr-links";

/**
 * Set by the internal paste on its transaction: the slice as it came off the clipboard.
 * ProseMirror's fitter rebuilds the open-start paragraph of a pasted slice with default
 * attrs (the step's slice shows `links: []` there), so J2 reads the first paragraph's
 * links from this slice instead.
 */
export const PASTE_SLICE_META = "wr-paste-slice";

export const linkKey =(l: Link): string => `${l.claim_id}\u0000${l.by}\u0000${l.suggestion_id ?? ""}`;

/** `a` in its order, then each item of `b` not already present, in b's order. Never mutates. */
export function unionLinks(a: readonly Link[], b: readonly Link[]): Link[] {
  const seen = new Set(a.map(linkKey));
  const out = [...a];
  for (const l of b) {
    const k = linkKey(l);
    if (!seen.has(k)) {
      seen.add(k);
      out.push(l);
    }
  }
  return out;
}

export const linksOf = (node: PMNode): readonly Link[] => (node.attrs.links ?? []) as readonly Link[];

const sameLinks = (a: readonly Link[], b: readonly Link[]): boolean =>
  a.length === b.length && a.every((l, i) => linkKey(l) === linkKey(b[i]));

/** Position directly before the innermost paragraph that contains `pos`. */
export function paragraphPosAt(state: EditorState, pos: number = state.selection.from): number | null {
  const $pos = state.doc.resolve(pos);
  for (let d = $pos.depth; d > 0; d--) {
    if ($pos.node(d).type.name === "paragraph") return $pos.before(d);
  }
  return null;
}

function paragraphAt(state: EditorState, pos: number): PMNode | null {
  const node = state.doc.nodeAt(pos);
  return node && node.type.name === "paragraph" ? node : null;
}

function canonical(link: Link): Link | null {
  if (typeof link.claim_id !== "string" || link.claim_id === "") return null;
  if (!LINK_BY.includes(link.by)) return null;
  if (link.suggestion_id !== undefined && (typeof link.suggestion_id !== "string" || link.by !== "student")) return null;
  return link.suggestion_id === undefined
    ? { claim_id: link.claim_id, by: link.by }
    : { claim_id: link.claim_id, by: link.by, suggestion_id: link.suggestion_id };
}

function setLinks(state: EditorState, pos: number, next: Link[], meta: string, dispatch?: (tr: Transaction) => void): boolean {
  if (dispatch) dispatch(state.tr.setNodeAttribute(pos, "links", next).setMeta(LINK_META, meta));
  return true;
}

function link(pos: number, l: Link, meta: string): Command {
  return (state, dispatch) => {
    const para = paragraphAt(state, pos);
    const item = canonical(l);
    if (!para || !item) return false;
    const current = linksOf(para);
    if (current.some((x) => linkKey(x) === linkKey(item))) return false;
    return setLinks(state, pos, [...current, item], meta, dispatch);
  };
}

/** Link the paragraph at `pos` (the position before it) to a claim. One undoable `attr` step. */
export const linkParagraph = (pos: number, l: Link): Command => link(pos, l, "link");

/** Remove every link with this claim_id from the paragraph at `pos`. */
export const unlinkParagraph =
  (pos: number, claim_id: string): Command =>
  (state, dispatch) => {
    const para = paragraphAt(state, pos);
    if (!para) return false;
    const current = linksOf(para);
    const next = current.filter((x) => x.claim_id !== claim_id);
    if (next.length === current.length) return false;
    return setLinks(state, pos, [...next], "unlink", dispatch);
  };

/** The student accepts a suggestion: a student link carrying the suggestion_id. */
export const acceptSuggestion = (pos: number, claim_id: string, suggestion_id: string): Command =>
  link(pos, { claim_id, by: "student", suggestion_id }, "accept");

// ---------- structural rule ----------

function textblocksOf(slice: Slice): PMNode[] {
  const out: PMNode[] = [];
  slice.content.descendants((n) => {
    if (n.isTextblock) out.push(n);
    return true;
  });
  return out;
}

/** Start position (before the node) of the paragraph containing `pos` in `doc`, or null. */
function paragraphStartAt(doc: PMNode, pos: number): number | null {
  if (pos < 0 || pos > doc.content.size) return null;
  const $pos = doc.resolve(pos);
  return $pos.parent.type.name === "paragraph" ? $pos.before() : null;
}

type Target = { pos: number; clear: boolean; add: readonly Link[] };

export function linksPlugin(): Plugin {
  return new Plugin({
    appendTransaction(trs, _old, newState) {
      const targets: Target[] = [];
      trs.forEach((tr, t) => {
        if (!tr.docChanged || isHistoryTransaction(tr) || tr.getMeta(LINK_META)) return;
        // Positions in the document after step i → the final document.
        const toFinal = (pos: number, i: number): number | null => {
          let p = pos;
          const own = tr.mapping.slice(i + 1).mapResult(p, 1);
          if (own.deleted) return null;
          p = own.pos;
          for (let k = t + 1; k < trs.length; k++) {
            const r = trs[k].mapping.mapResult(p, 1);
            if (r.deleted) return null;
            p = r.pos;
          }
          return p;
        };
        const record = (posAfter: number | null, i: number, clear: boolean, add: readonly Link[]) => {
          if (posAfter === null) return;
          const pos = toFinal(posAfter, i);
          if (pos !== null) targets.push({ pos, clear, add });
        };

        tr.steps.forEach((step, i) => {
          if (!(step instanceof ReplaceStep)) return;
          const before = tr.docs[i];
          const after = tr.docs[i + 1] ?? tr.doc;
          const map = step.getMap();
          const $a = before.resolve(step.from);
          const $b = before.resolve(step.to);
          const X = $a.parent;
          const Y = $b.parent;
          const S = step.slice;
          const blocks = textblocksOf(S);
          const multi = blocks.length >= 2;
          const left = paragraphStartAt(after, map.map(step.from, -1));
          const right = paragraphStartAt(after, map.map(step.to, 1));

          // J1 (tail join): the tail of Y survives in the paragraph at `right`.
          if (Y.type.name === "paragraph" && $b.parentOffset < Y.content.size && (X !== Y || multi)) {
            record(right, i, false, linksOf(Y));
          }
          // J2 (head join): the first pasted paragraph merges into the paragraph at `left`.
          const pasted = tr.getMeta(PASTE_SLICE_META) as Slice | undefined;
          const F = pasted && pasted.openStart > 0 ? textblocksOf(pasted)[0] : blocks[0];
          if (
            (pasted ? pasted.openStart > 0 && S.size > 0 : S.openStart > 0) &&
            F &&
            F.type.name === "paragraph" &&
            F.content.size > 0 &&
            (multi || (X === Y && X.content.size === 0))
          ) {
            record(left, i, false, linksOf(F));
          }
          // J3 (new empty paragraph above a linked paragraph).
          if (
            X.type.name === "paragraph" &&
            linksOf(X).length > 0 &&
            $a.parentOffset === 0 &&
            X.content.size > 0 &&
            left !== null &&
            right !== null &&
            left !== right
          ) {
            const leftNode = after.nodeAt(left);
            if (leftNode && leftNode.type.name === "paragraph" && leftNode.content.size === 0) {
              record(left, i, true, []);
            }
          }
        });
      });
      if (targets.length === 0) return null;

      // Group by final position, in the order the rules fired.
      const byPos = new Map<number, Target[]>();
      for (const target of targets) {
        const list = byPos.get(target.pos) ?? [];
        list.push(target);
        byPos.set(target.pos, list);
      }
      const tr = newState.tr;
      for (const pos of [...byPos.keys()].sort((a, b) => a - b)) {
        const node = newState.doc.nodeAt(pos);
        if (!node || node.type.name !== "paragraph") continue;
        const current = linksOf(node);
        const list = byPos.get(pos)!;
        let next: Link[] = list.some((x) => x.clear) ? [] : [...current];
        for (const target of list) next = unionLinks(next, target.add);
        if (!sameLinks(current, next)) tr.setNodeAttribute(pos, "links", next);
      }
      return tr.docChanged ? tr.setMeta(LINK_META, "structure") : null;
    },
  });
}
