// S1 browser page: mounts the real editor and exposes a small handle that
// browser_check.mjs drives through Playwright (real keyboard, IME, clipboard,
// drag-and-drop, extension-style DOM edits).
import { createEditor } from "../../../web/src/editor/editor";
import { insertMarked, originKey } from "../../../web/src/editor/origin";
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

function runs() {
  const out: [string, string | null, string | null, string | null][][] = [];
  view.state.doc.forEach((p) => {
    const row: [string, string | null, string | null, string | null][] = [];
    p.forEach((t) => {
      const o = t.marks.find((m) => m.type.name === "origin");
      const c = t.marks.find((m) => m.type.name === "claim");
      row.push([t.text ?? "", o ? o.attrs.kind : null, o ? o.attrs.ref : null, c ? `${c.attrs.claim_id}/${c.attrs.by}` : null]);
    });
    out.push(row);
  });
  return out;
}

(window as unknown as { s1: unknown }).s1 = {
  runs,
  counts: () => originKey.getState(view.state)!.counts,
  insertQuote(text: string, claim?: { claim_id: string; by: string }) {
    insertMarked(view, text, { kind: "quote", ref: "b81" }, claim);
  },
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
