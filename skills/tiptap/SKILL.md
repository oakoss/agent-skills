---
name: tiptap
description: 'Builds rich text editors with Tiptap — headless editor framework with React and Tailwind v4. Covers SSR-safe setup, image uploads, prose styling, and collaborative editing. Use when adding a rich text editor, configuring Tiptap extensions, handling image uploads in editors, or setting up collaborative editing with Y.js.'
version: 1.0.0
tags: [tiptap, rich-text, editor, prosemirror, react, tailwind]
---

# Tiptap Rich Text Editor

Headless rich text editor built on ProseMirror. React 19 supported, Tailwind v4 compatible.

## Critical Setup Rules

| Rule                                            | Why                                                                        |
| ----------------------------------------------- | -------------------------------------------------------------------------- |
| Set `immediatelyRender: false` in `useEditor()` | Required for SSR/Next.js — prevents hydration mismatch (#1 reported error) |
| Install `@tiptap/pm` peer dependency            | ProseMirror engine, required but not auto-installed                        |
| Install `@tailwindcss/typography`               | Without it, formatted content looks unstyled                               |
| Set `allowBase64: false` on Image extension     | Prevents megabyte-size JSON payloads                                       |
| Use Vite, not Create React App                  | CRA incompatible with Tiptap v3 module structure                           |

## Core Dependencies

| Package                   | Purpose                                                              |
| ------------------------- | -------------------------------------------------------------------- |
| `@tiptap/react`           | React integration                                                    |
| `@tiptap/starter-kit`     | 20+ essential extensions (headings, lists, bold, italic, link, etc.) |
| `@tiptap/pm`              | ProseMirror peer dependency                                          |
| `@tailwindcss/typography` | Prose styling for headings, lists, links                             |

## StarterKit Extensions (v3)

| Category      | Included                                                                                                                |
| ------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Marks         | Bold, Italic, Strike, Code, Link (new), Underline (new)                                                                 |
| Nodes         | Document, Paragraph, Text, Heading, BulletList, OrderedList, ListItem, Blockquote, CodeBlock, HorizontalRule, HardBreak |
| Functionality | History, Dropcursor, Gapcursor, ListKeymap (new), TrailingNode (new)                                                    |

## Common Additional Extensions

| Extension         | Package                                 | Use Case                            |
| ----------------- | --------------------------------------- | ----------------------------------- |
| Image             | `@tiptap/extension-image`               | Image support with resize           |
| Color             | `@tiptap/extension-color`               | Text color                          |
| Typography        | `@tiptap/extension-typography`          | Smart quotes, dashes, ellipsis      |
| Placeholder       | `@tiptap/extension-placeholder`         | Placeholder text                    |
| Table             | `@tiptap/extension-table`               | Table support (+ Row, Cell, Header) |
| TaskList          | `@tiptap/extension-task-list`           | Checkbox task lists                 |
| CodeBlockLowlight | `@tiptap/extension-code-block-lowlight` | Syntax-highlighted code             |
| Collaboration     | `@tiptap/extension-collaboration`       | Real-time multi-user editing        |
| Markdown          | `@tiptap/extension-markdown`            | Bidirectional markdown (Beta)       |

## Use Case Extension Bundles

| Use Case       | Extensions                                                             |
| -------------- | ---------------------------------------------------------------------- |
| Blog editor    | StarterKit + Image + Typography + Placeholder + CharacterCount         |
| Comment system | StarterKit (minimal) + Link + Typography + Placeholder                 |
| Documentation  | StarterKit + Image + Table + CodeBlockLowlight + TaskList              |
| Notion-like    | StarterKit + Image + Table + TaskList + Collaboration + slash commands |
| Form input     | StarterKit (minimal) + Placeholder + CharacterCount                    |

## Common Mistakes

| Mistake                                   | Fix                                                                |
| ----------------------------------------- | ------------------------------------------------------------------ |
| Missing `immediatelyRender: false`        | Add to `useEditor()` config — required for SSR                     |
| No `prose` classes on editor container    | Add `className="prose prose-sm dark:prose-invert max-w-none"`      |
| Images stored as base64                   | Set `allowBase64: false`, use upload handler                       |
| Using EditorProvider + useEditor together | Choose one — EditorProvider wraps useEditor internally             |
| History enabled with Collaboration        | Set `history: false` in StarterKit when using Y.js                 |
| ProseMirror version conflicts             | Add `resolutions` for prosemirror-model/view/state in package.json |
| Using CRA with Tiptap v3                  | Switch to Vite                                                     |
| Not checking `editor` for null            | `useEditor()` returns `Editor \| null` — guard before use          |

## Integration Options

| Option                | When to Use                                               |
| --------------------- | --------------------------------------------------------- |
| shadcn minimal-tiptap | Pre-built component with toolbar, dark mode, image upload |
| Custom `useEditor()`  | Full control, headless approach                           |

Install shadcn component: `npx shadcn@latest add https://raw.githubusercontent.com/Aslam97/shadcn-minimal-tiptap/main/registry/block-registry.json`

## Delegation

- **Tailwind styling**: see `tailwind` skill
- **Form integration**: see `tanstack-form` skill

## References

- [Setup and Configuration](references/setup.md)
- [Extensions Catalog](references/extensions.md)
- [Image Upload](references/image-upload.md)
- [Patterns](references/patterns.md)
- [Known Issues and Errors](references/known-issues.md)
- [Prose Styling](references/prose-styling.md)
