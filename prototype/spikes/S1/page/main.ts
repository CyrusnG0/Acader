// S1 browser page: mounts the real editor and exposes a small handle that
// browser_check.mjs drives through Playwright (real keyboard, IME, clipboard,
// drag-and-drop, extension-style DOM edits).
import { createEditor } from "../../../web/src/editor/editor";
import { insertMarked, originKey } from "../../../web/src/editor/origin";
import { linkParagraph, paragraphPosAt, unlinkParagraph, type Link } from "../../../web/src/editor/links";
import { toggleBulletList } from "../../../web/src/editor/formatting";
import { recordKey, replaySteps } from "../../../web/src/editor/record";
import { docHash } from "../../../web/src/editor/canonical";
import { editorSchema } from "../../../web/src/schema";

let n = 0;
const editor = createEditor({
  element: document.getElementById("editor")!,
  logId: "log_browser",
  newPasteId: () => `paste_${++n}`,
});
const view = editor.view;

type Row = [string, string | null, string | null][];

/** [text, origin kind, origin ref] per text run, one row per textblock in document order. */
function runs() {
  const out: Row[] = [];
  view.state.doc.descendants((block) => {
    if (!block.isTextblock) return true;
    const row: Row = [];
    block.forEach((t) => {
      if (!t.isText) return;
      const o = t.marks.find((m) => m.type.name === "origin");
      row.push([t.text ?? "", o ? o.attrs.kind : null, o ? o.attrs.ref : null]);
    });
    out.push(row);
    return false;
  });
  return out;
}

/** The links of every paragraph, in document order, as "claim_id/by[/suggestion_id]". */
function links() {
  const out: string[][] = [];
  view.state.doc.descendants((p) => {
    if (p.type.name === "paragraph") {
      out.push((p.attrs.links as Link[]).map((l) => `${l.claim_id}/${l.by}${l.suggestion_id ? `/${l.suggestion_id}` : ""}`));
    }
    return true;
  });
  return out;
}

(window as unknown as { s1: unknown }).s1 = {
  runs,
  links,
  /** [text, "mark,mark"] per text run (marks other than origin), one row per textblock. */
  formats() {
    const out: [string, string][][] = [];
    view.state.doc.descendants((block) => {
      if (!block.isTextblock) return true;
      const row: [string, string][] = [];
      block.forEach((t) => {
        if (t.isText) row.push([t.text ?? "", t.marks.filter((m) => m.type.name !== "origin").map((m) => m.type.name).join(",")]);
      });
      out.push(row);
      return false;
    });
    return out;
  },
  /** How many nodes of this type the document holds. */
  count(type: string) {
    let c = 0;
    view.state.doc.descendants((n) => {
      if (n.type.name === type) c++;
      return true;
    });
    return c;
  },
  bulletList: () => toggleBulletList(editor),
  counts: () => originKey.getState(view.state)!.counts,
  insertQuote(text: string) {
    insertMarked(view, text, { kind: "quote", ref: "b81" });
  },
  /** Position before the paragraph that contains the cursor (or `pos`). */
  paragraphPos: (pos?: number) => paragraphPosAt(view.state, pos),
  link: (pos: number, l: Link) => linkParagraph(pos, l)(view.state, view.dispatch),
  unlink: (pos: number, claimId: string) => unlinkParagraph(pos, claimId)(view.state, view.dispatch),
  select(from: number, to = from) {
    editor.commands.focus();
    editor.commands.setTextSelection({ from, to });
  },
  end: () => view.state.doc.content.size - 1,
  async result() {
    const log = recordKey.getState(view.state)!;
    const doc = view.state.doc.toJSON();
    const replayed = replaySteps(editorSchema, log.start, log.steps).toJSON();
    return {
      start: log.start,
      steps: log.steps,
      doc,
      doc_hash: await docHash(doc),
      js_replay_equal: JSON.stringify(replayed) === JSON.stringify(doc),
    };
  },
};
