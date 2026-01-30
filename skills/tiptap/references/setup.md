---
title: Setup and Configuration
description: Tiptap installation, SSR-safe editor setup with immediatelyRender, Tailwind typography plugin, shadcn integration, dependencies, and React version compatibility
tags:
  [tiptap, setup, ssr, immediatelyRender, tailwind, shadcn, react, dependencies]
---

# Setup and Configuration

## Installation

```bash
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm @tiptap/extension-image @tiptap/extension-color @tiptap/extension-text-style @tiptap/extension-typography
```

- `@tiptap/pm` is a required peer dependency (ProseMirror engine)
- StarterKit bundles 20+ essential extensions
- Image/color/typography are common additions not in StarterKit

## SSR-Safe Editor

```ts
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

export function Editor() {
  const editor = useEditor({
    extensions: [StarterKit],
    content: '<p>Hello World!</p>',
    immediatelyRender: false,
    editorProps: {
      attributes: {
        class: 'prose prose-sm focus:outline-none min-h-[200px] p-4',
      },
    },
  });

  return <EditorContent editor={editor} />;
}
```

`immediatelyRender: false` is required for Next.js/SSR apps. Without it, you get: "SSR has been detected, please set `immediatelyRender` explicitly to `false`". This is the #1 reported Tiptap error.

## Tailwind Typography

```bash
npm install @tailwindcss/typography
```

```ts
import typography from '@tailwindcss/typography';

export default {
  plugins: [typography],
};
```

Without this, formatted content (headings, lists, links) looks unstyled.

## Extension Configuration

```ts
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import Typography from '@tiptap/extension-typography';

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: { levels: [1, 2, 3] },
      bulletList: { keepMarks: true },
    }),
    Image.configure({
      inline: true,
      allowBase64: false,
      resize: {
        enabled: true,
        directions: ['top-right', 'bottom-right', 'bottom-left', 'top-left'],
        minWidth: 100,
        minHeight: 100,
        alwaysPreserveAspectRatio: true,
      },
    }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: { class: 'text-primary underline' },
    }),
    Typography,
  ],
  immediatelyRender: false,
});
```

Extension order matters — dependencies must load first. Set `allowBase64: false` to prevent huge JSON payloads.

## React Version Compatibility

| Scope          | React 19             | React 18                     |
| -------------- | -------------------- | ---------------------------- |
| Core Tiptap    | Supported (v2.10.0+) | Supported                    |
| UI Components  | Works                | Recommended by official docs |
| Pro Extensions | May require React 18 | Full support                 |

Pro drag-handle extension depends on archived tippyjs-react without React 19 support.

## Drag Handle Note

Drag handle functionality requires minimum v3.14.0 (regression fixed in that release).

## Package Version Resolutions

If you encounter ProseMirror multiple version conflicts:

```json
{
  "resolutions": {
    "prosemirror-model": "~1.21.0",
    "prosemirror-view": "~1.33.0",
    "prosemirror-state": "~1.4.3"
  }
}
```
