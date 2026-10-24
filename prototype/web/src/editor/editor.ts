// The S1 editor: TipTap on web/schema.json with the input plugin, step
// recorder and undo history. M3 builds the real editor on this.
import { Editor, Extension } from "@tiptap/core";
import Document from "@tiptap/extension-document";
import Paragraph from "@tiptap/extension-paragraph";
import Text from "@tiptap/extension-text";
import { history, redo, undo } from "@tiptap/pm/history";
import { schemaMarks } from "./marks";
import { originPlugin, type OriginOptions } from "./origin";
import { recordPlugin } from "./record";

export function writingRoomExtension(opts: OriginOptions) {
  return Extension.create({
    name: "writingRoom",
    addProseMirrorPlugins() {
      return [originPlugin(opts), recordPlugin(), history()];
    },
    addKeyboardShortcuts() {
      const run = (cmd: typeof undo) => () => cmd(this.editor.view.state, this.editor.view.dispatch);
      return { "Mod-z": run(undo), "Shift-Mod-z": run(redo), "Mod-y": run(redo) };
    },
  });
}

export interface CreateEditorOptions extends OriginOptions {
  element?: HTMLElement;
}

export function createEditor(opts: CreateEditorOptions): Editor {
  return new Editor({
    element: opts.element,
    extensions: [Document, Paragraph, Text, ...schemaMarks, writingRoomExtension(opts)],
    // No input rules or paste rules: they would rewrite text on input.
    enableInputRules: false,
    enablePasteRules: false,
  });
}
