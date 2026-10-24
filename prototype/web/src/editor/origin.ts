// The input plugin (design/event-log.md §4, D21, D26).
//
// - Typed text is always `typed`. Every text the student enters through the
//   keyboard, IME, dictation or a replacement (spellcheck, autocorrect,
//   extensions that edit the page) gets origin=typed, also inside or at the
//   edge of a marked span. The plugin does this after the
//   fact (appendTransaction), so it covers every input path ProseMirror has,
//   including DOM edits it only sees through its mutation observer.
// - `input_kind` (keyboard, ime, dictation, replacement) is kept as counts in
//   the plugin state, never on the mark.
// - Copy writes application/x-writing-room-slice with the marks and log_id.
//   A paste with that type and the same log_id restores the marks; any other
//   paste, and any drop from outside the editor, is `paste_ext`.
// - Moves inside the document (drag-and-drop) and undo/redo keep marks.
import { Plugin, PluginKey, TextSelection, type EditorState, type Transaction } from "@tiptap/pm/state";
import { Fragment, Slice, type Mark, type Node as PMNode, type Schema } from "@tiptap/pm/model";
import { isHistoryTransaction } from "@tiptap/pm/history";
import type { EditorView } from "@tiptap/pm/view";
import { PASTE_SLICE_META } from "./links";

export const SLICE_MIME = "application/x-writing-room-slice";
/** Set on a transaction whose marks were set on purpose (quote, helper, import, internal paste, replay). */
export const EXPLICIT_META = "wr-explicit";

export type InputKind = "keyboard" | "ime" | "dictation" | "replacement";
export const INPUT_KINDS: readonly InputKind[] = ["keyboard", "ime", "dictation", "replacement"];

export interface OriginState {
  counts: Record<InputKind, number>;
}

export interface OriginOptions {
  logId: string;
  /** Returns a fresh paste_id for each external paste or drop. */
  newPasteId: () => string;
}

export const originKey = new PluginKey<OriginState>("wr-origin");

/** beforeinput inputType → input_kind. Anything else that inserts text counts as keyboard. */
export function inputKindOf(inputType: string | undefined, composing: boolean): InputKind {
  if (inputType === "insertReplacementText") return "replacement";
  if (inputType === "insertFromDictation") return "dictation";
  if (composing || inputType === "insertCompositionText" || inputType === "insertFromComposition") return "ime";
  return "keyboard";
}

function isUserInput(tr: Transaction): boolean {
  if (!tr.docChanged) return false;
  if (tr.getMeta(EXPLICIT_META)) return false;
  const ui = tr.getMeta("uiEvent");
  if (ui === "paste" || ui === "drop" || ui === "cut") return false;
  if (isHistoryTransaction(tr)) return false;
  if (tr.getMeta("appendedTransaction")) return false;
  return true;
}

type Range = [number, number];

/** Ranges (in the coordinates after `tr`) where `tr` inserted content. */
function insertedRanges(tr: Transaction): Range[] {
  const out: Range[] = [];
  tr.mapping.maps.forEach((map, i) => {
    const rest = tr.mapping.slice(i + 1);
    map.forEach((_oldStart, _oldEnd, newStart, newEnd) => {
      if (newEnd > newStart) out.push([rest.map(newStart, 1), rest.map(newEnd, -1)]);
    });
  });
  return out.filter(([a, b]) => b > a);
}

function rangeHasText(doc: PMNode, [a, b]: Range): boolean {
  let found = false;
  doc.nodesBetween(a, b, (n) => {
    if (n.isText) found = true;
    return !found;
  });
  return found;
}

/** Strip every mark from a slice, stamp origin=paste_ext with one paste_id, and clear paragraph links. */
export function stampSlice(schema: Schema, slice: Slice, pasteId: string): Slice {
  const origin = schema.marks.origin.create({ kind: "paste_ext", ref: pasteId });
  const walk = (frag: Fragment): Fragment => {
    const nodes: PMNode[] = [];
    frag.forEach((n) => {
      if (n.isText) nodes.push(n.mark([origin]));
      else if (n.type.spec.attrs && "links" in n.type.spec.attrs) {
        // Outside text never brings links (D-045); other attrs, e.g. a heading level, stay.
        nodes.push(n.type.create({ ...n.attrs, links: [] }, walk(n.content)).mark([] as readonly Mark[]));
      } else nodes.push(n.copy(walk(n.content)).mark([] as readonly Mark[]));
    });
    return Fragment.from(nodes);
  };
  return new Slice(walk(slice.content), slice.openStart, slice.openEnd);
}

/** Insert text with an explicit origin (quote, helper, coach, import). */
export function insertMarked(view: EditorView, text: string, origin: { kind: string; ref: string | null }): void {
  const { state } = view;
  const marks = [state.schema.marks.origin.create(origin)];
  const { from, to } = state.selection;
  const tr = state.tr.replaceWith(from, to, state.schema.text(text, marks)).setMeta(EXPLICIT_META, true);
  view.dispatch(tr);
}

export function originPlugin(opts: OriginOptions): Plugin<OriginState> {
  // The latest beforeinput type, consumed by the next transaction that inserts text.
  let pendingKind: string | undefined;
  let viewRef: EditorView | null = null;

  const onCopy = (view: EditorView, event: ClipboardEvent, cut: boolean): boolean => {
    const sel = view.state.selection;
    const data = event.clipboardData;
    if (sel.empty || !data) return false;
    const slice = sel.content();
    const { dom, text } = view.serializeForClipboard(slice);
    event.preventDefault();
    data.clearData();
    data.setData("text/html", dom.innerHTML);
    data.setData("text/plain", text);
    data.setData(SLICE_MIME, JSON.stringify({ log_id: opts.logId, slice: slice.toJSON() }));
    if (cut) view.dispatch(view.state.tr.deleteSelection().scrollIntoView().setMeta("uiEvent", "cut"));
    return true;
  };

  return new Plugin<OriginState>({
    key: originKey,
    view(view) {
      viewRef = view;
      return { destroy: () => { viewRef = null; } };
    },
    state: {
      init: () => ({ counts: { keyboard: 0, ime: 0, dictation: 0, replacement: 0 } }),
      apply(tr, value) {
        if (!isUserInput(tr)) return value;
        if (!insertedRanges(tr).some((r) => rangeHasText(tr.doc, r))) return value;
        const kind = inputKindOf(pendingKind, viewRef?.composing ?? false);
        pendingKind = undefined;
        return { counts: { ...value.counts, [kind]: value.counts[kind] + 1 } };
      },
    },
    appendTransaction(trs: readonly Transaction[], _old: EditorState, state: EditorState) {
      let ranges: Range[] = [];
      for (const tr of trs) {
        ranges = ranges
          .map(([a, b]): Range => [tr.mapping.map(a, 1), tr.mapping.map(b, -1)])
          .filter(([a, b]) => b > a);
        if (isUserInput(tr)) ranges.push(...insertedRanges(tr));
      }
      if (ranges.length === 0) return null;
      const { origin } = state.schema.marks;
      const typed = origin.create({ kind: "typed", ref: null });
      const tr = state.tr;
      for (const [a, b] of ranges) {
        tr.addMark(a, b, typed); // excludes: origin, so this replaces any other origin
      }
      return tr.docChanged ? tr.setMeta(EXPLICIT_META, "typed") : null;
    },
    props: {
      // Plain keystrokes: insert the text already marked typed, so a keystroke is one
      // step instead of two (insert, then appendTransaction's addMark). Text inserted
      // any other way (IME, DOM edits, replacements) still goes through appendTransaction.
      handleTextInput(view, from, to, text) {
        const { state } = view;
        const typed = state.schema.marks.origin.create({ kind: "typed", ref: null });
        // The cursor's other marks (strong, em) carry over; its origin never does.
        const carried = (state.storedMarks ?? state.doc.resolve(from).marks()).filter((m) => m.type !== typed.type);
        const tr = state.tr.replaceWith(from, to, state.schema.text(text, typed.addToSet(carried)));
        // Put the cursor after the text (mapping alone would keep an AllSelection).
        tr.setSelection(TextSelection.create(tr.doc, tr.mapping.map(to)));
        view.dispatch(tr.scrollIntoView());
        return true;
      },
      transformPasted(slice, view) {
        // An internal drag keeps its marks; everything else from the clipboard is outside text.
        if (view.dragging) return slice;
        return stampSlice(view.state.schema, slice, opts.newPasteId());
      },
      handlePaste(view, event) {
        const raw = event.clipboardData?.getData(SLICE_MIME);
        if (!raw) return false;
        let restored: Slice;
        try {
          const parsed = JSON.parse(raw) as { log_id?: unknown; slice?: unknown };
          if (parsed.log_id !== opts.logId) return false;
          restored = Slice.fromJSON(view.state.schema, parsed.slice as never);
          restored.content.forEach((n) => n.check());
        } catch {
          return false; // malformed: PM inserts the already-stamped paste_ext slice
        }
        view.dispatch(
          view.state.tr
            .replaceSelection(restored)
            .scrollIntoView()
            .setMeta("paste", true)
            .setMeta("uiEvent", "paste")
            .setMeta(EXPLICIT_META, "internal")
            .setMeta(PASTE_SLICE_META, restored),
        );
        return true;
      },
      handleDOMEvents: {
        beforeinput(_view, event) {
          pendingKind = (event as InputEvent).inputType;
          return false;
        },
        copy: (view, event) => onCopy(view, event as ClipboardEvent, false),
        cut: (view, event) => onCopy(view, event as ClipboardEvent, true),
      },
    },
  });
}
