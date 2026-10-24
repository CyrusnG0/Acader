// The editor: TipTap on web/schema.json with the input plugin, link rules,
// step recorder and undo history. M3 builds the real editor on this.
import { Editor, Extension } from "@tiptap/core";
import { history, redo, undo } from "@tiptap/pm/history";
import { schemaMarks } from "./marks";
import { schemaNodes } from "./nodes";
import { linksPlugin } from "./links";
import { originPlugin, type OriginOptions } from "./origin";
import { recordPlugin } from "./record";

export function writingRoomExtension(opts: OriginOptions) {
  return Extension.create({
    name: "writingRoom",
    addProseMirrorPlugins() {
      return [originPlugin(opts), linksPlugin(), recordPlugin(), history()];
    },
    addKeyboardShortcuts() {
      const run = (cmd: typeof undo) => () => cmd(this.editor.view.state, this.editor.view.dispatch);
      return {
        "Mod-z": run(undo),
        "Shift-Mod-z": run(redo),
        "Mod-y": run(redo),
        // In a list item Enter splits the item; elsewhere TipTap's default Enter runs.
        Enter: () => this.editor.commands.splitListItem("list_item"),
        "Shift-Enter": () => {
          const { state, dispatch } = this.editor.view;
          const br = state.schema.nodes.hard_break;
          dispatch(state.tr.replaceSelectionWith(br.create()).scrollIntoView());
          return true;
        },
        Tab: () => this.editor.commands.sinkListItem("list_item"),
        "Shift-Tab": () => this.editor.commands.liftListItem("list_item"),
        "Mod-b": () => this.editor.commands.toggleMark("strong"),
        "Mod-i": () => this.editor.commands.toggleMark("em"),
      };
    },
  });
}

export interface CreateEditorOptions extends OriginOptions {
  element?: HTMLElement;
}

export function createEditor(opts: CreateEditorOptions): Editor {
  return new Editor({
    element: opts.element,
    extensions: [...schemaNodes, ...schemaMarks, writingRoomExtension(opts)],
    // No input rules or paste rules: they would rewrite text on input.
    enableInputRules: false,
    enablePasteRules: false,
  });
}
