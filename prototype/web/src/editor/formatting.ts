// Block formatting for the toolbar and tests, as plain functions over a TipTap
// editor. They use TipTap core commands only; no input rules or paste rules.
import type { Editor } from "@tiptap/core";

export const setHeading = (editor: Editor, level: 1 | 2 | 3): boolean =>
  editor.chain().focus().setNode("heading", { level }).run();

export const setParagraph = (editor: Editor): boolean => editor.chain().focus().setNode("paragraph").run();

export const toggleBulletList = (editor: Editor): boolean =>
  editor.chain().focus().toggleList("bullet_list", "list_item").run();

export const toggleOrderedList = (editor: Editor): boolean =>
  editor.chain().focus().toggleList("ordered_list", "list_item").run();

export const toggleBlockquote = (editor: Editor): boolean => editor.chain().focus().toggleWrap("blockquote").run();
