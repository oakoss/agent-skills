---
title: Setup and Configuration
description: Tiptap installation, SSR-safe editor setup with immediatelyRender, Tailwind typography plugin, shadcn integration, dependencies, and React version compatibility
tags:
  [tiptap, setup, ssr, immediatelyRender, tailwind, shadcn, react, dependencies]
---

# Setup and Configuration

## Installation

```bash
npm install @tiptap/react @tiptap/starter-kit @tiptap/pm
```

- `@tiptap/pm` is a required peer dependency (ProseMirror engine)
- StarterKit bundles marks, nodes, and functionality extensions
- Additional extensions (Image, Color, Typography) installed separately as needed

## SSR-Safe Editor

```tsx
'use client';

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

  if (!editor) return null;

  return <EditorContent editor={editor} />;
}
```

`immediatelyRender: false` is required for Next.js/SSR apps. Without it: "SSR has been detected, please set `immediatelyRender` explicitly to `false`". This is the most common Tiptap error.

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
    }),
    Typography,
  ],
  immediatelyRender: false,
});
```

Extension order matters — dependencies must load first. Set `allowBase64: false` to prevent huge JSON payloads.

Link and Underline are included in StarterKit v3 by default. Do not install them separately.

## React Version Compatibility

| Scope          | React 19             | React 18                     |
| -------------- | -------------------- | ---------------------------- |
| Core Tiptap    | Supported (v2.10.0+) | Supported                    |
| UI Components  | Works                | Recommended by official docs |
| Pro Extensions | May require React 18 | Full support                 |

Pro drag-handle extension depends on archived tippyjs-react without React 19 support.

## Bundler Compatibility

Tiptap v3 ships as ESM. Create React App (CRA) is incompatible with the v3 module structure. Use Vite or another modern bundler.

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

## shadcn Minimal Tiptap

Pre-built component with toolbar, dark mode, and image upload:

```bash
npx shadcn@latest add https://raw.githubusercontent.com/Aslam97/shadcn-minimal-tiptap/main/registry/block-registry.json
```

Requires wrapping the app with `TooltipProvider` from `@/components/ui/tooltip`.
