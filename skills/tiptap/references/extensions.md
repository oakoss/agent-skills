---
title: Extensions Catalog
description: Tiptap extension catalog with StarterKit contents, additional extensions, community extensions, and custom extension development templates
tags: [tiptap, extensions, starterkit, custom-extensions, community, node, mark]
---

# Extensions Catalog

## StarterKit Contents

**Marks**: Bold, Italic, Strike, Code, Link (v3), Underline (v3)

**Nodes**: Document, Paragraph, Text, Heading, BulletList, OrderedList, ListItem, Blockquote, CodeBlock, HorizontalRule, HardBreak

**Functionality**: Undo/Redo, Dropcursor, Gapcursor, ListKeymap (v3), TrailingNode (v3)

The v3 config key for disabling undo/redo is `undoRedo` (renamed from `history`).

## Additional Official Extensions

### Image

```ts
import Image from '@tiptap/extension-image';

Image.configure({
  inline: true,
  allowBase64: false,
});
```

### Text Styling

- **TextStyle** — `@tiptap/extension-text-style` — text style container (required by Color)
- **Color** — `@tiptap/extension-color` — text color
- **Highlight** — `@tiptap/extension-highlight` — highlighting
- **FontFamily** — `@tiptap/extension-font-family`
- **Subscript / Superscript**

### Typography

```ts
import Typography from '@tiptap/extension-typography';
// Converts: (c) -> copyright, -> -> arrow, ... -> ellipsis, "text" -> smart quotes
```

### Placeholder

```ts
import Placeholder from '@tiptap/extension-placeholder';

Placeholder.configure({
  placeholder: 'Start writing...',
  emptyEditorClass: 'is-editor-empty',
});
```

Requires CSS for the placeholder to display. See [Prose Styling](prose-styling.md) reference.

### Tables

```ts
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';

const extensions = [
  Table.configure({ resizable: true }),
  TableRow,
  TableCell,
  TableHeader,
];
```

### Task Lists

```ts
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';

const extensions = [TaskList, TaskItem.configure({ nested: true })];
```

### Code Blocks with Syntax Highlighting

```ts
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { common, createLowlight } from 'lowlight';

const lowlight = createLowlight(common);
CodeBlockLowlight.configure({ lowlight });
```

### Collaboration

```ts
import Collaboration from '@tiptap/extension-collaboration';
import CollaborationCursor from '@tiptap/extension-collaboration-cursor';
import * as Y from 'yjs';

const ydoc = new Y.Doc();
const extensions = [
  Collaboration.configure({ document: ydoc }),
  CollaborationCursor.configure({
    provider,
    user: { name: 'John Doe', color: '#3b82f6' },
  }),
];
```

### Markdown

```ts
import { Markdown } from '@tiptap/markdown';

const editor = useEditor({
  extensions: [StarterKit, Markdown],
  content: '# Hello',
  contentType: 'markdown',
  immediatelyRender: false,
});

const md = editor.getMarkdown();
editor.commands.setContent('## New heading', { contentType: 'markdown' });
```

Package: `@tiptap/markdown` (not `@tiptap/extension-markdown`).

### Utilities

- **CharacterCount** — `@tiptap/extension-character-count`
- **Focus** — `@tiptap/extension-focus`
- **TextAlign** — `@tiptap/extension-text-align`

## Pro Extensions (Paid)

Content AI, AI Image, Comments, FileHandler, Mathematics, TableOfContents, UniqueID.

## Community Extensions

| Extension                           | Purpose                        |
| ----------------------------------- | ------------------------------ |
| tiptap-extension-global-drag-handle | Notion-like block drag handles |
| @tiptap-pro/extension-emoji         | Emoji picker                   |
| tiptap-youtube                      | YouTube embeds                 |
| @joeattardi/tiptap-indent           | Text indentation               |
| tiptap-text-direction               | RTL/LTR support                |
| tiptap-slash-command                | Slash command menu             |
| tiptap-extension-details-summary    | Collapsible sections           |

## Custom Extension Development

### Node Template

```ts
import { Node } from '@tiptap/core';

export const CustomNode = Node.create({
  name: 'customNode',
  group: 'block',
  content: 'inline*',

  parseHTML() {
    return [{ tag: 'div[data-custom]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', { 'data-custom': '', ...HTMLAttributes }, 0];
  },

  addCommands() {
    return {
      insertCustomNode:
        () =>
        ({ commands }) => {
          return commands.insertContent({ type: this.name });
        },
    };
  },
});
```

### Mark Template

```ts
import { Mark } from '@tiptap/core';

export const CustomMark = Mark.create({
  name: 'customMark',

  parseHTML() {
    return [{ tag: 'span[data-custom]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', { 'data-custom': '', ...HTMLAttributes }, 0];
  },

  addCommands() {
    return {
      toggleCustomMark:
        () =>
        ({ commands }) => {
          return commands.toggleMark(this.name);
        },
    };
  },
});
```

### Extension Template

```ts
import { Extension } from '@tiptap/core';

export const CustomExtension = Extension.create({
  name: 'customExtension',

  addOptions() {
    return {};
  },

  addCommands() {
    return {};
  },

  addKeyboardShortcuts() {
    return {
      'Mod-Shift-x': () => this.editor.commands.toggleCustomMark(),
    };
  },
});
```

## Installation Quick Reference

```bash
# Core
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm

# Media
npm install @tiptap/extension-image

# Text Styling
npm install @tiptap/extension-text-style @tiptap/extension-color @tiptap/extension-highlight

# Content
npm install @tiptap/extension-typography @tiptap/extension-placeholder

# Tables
npm install @tiptap/extension-table @tiptap/extension-table-row @tiptap/extension-table-cell @tiptap/extension-table-header

# Task Lists
npm install @tiptap/extension-task-list @tiptap/extension-task-item

# Code Blocks with Syntax Highlighting
npm install @tiptap/extension-code-block-lowlight lowlight

# Collaboration
npm install @tiptap/extension-collaboration @tiptap/extension-collaboration-cursor yjs

# Markdown
npm install @tiptap/markdown

# Utilities
npm install @tiptap/extension-character-count @tiptap/extension-focus @tiptap/extension-text-align
```
