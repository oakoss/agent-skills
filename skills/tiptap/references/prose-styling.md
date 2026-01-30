---
title: Prose Styling
description: Tailwind Typography prose styling for Tiptap editor, custom CSS overrides, dark mode support, and placeholder styling
tags: [tiptap, tailwind, prose, css, styling, dark-mode, typography]
---

# Prose Styling

## Tailwind Prose Classes

Apply to the editor container:

```tsx
<EditorContent
  editor={editor}
  className="prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none"
/>
```

- `prose` provides consistent formatting for headings, lists, links
- `dark:prose-invert` handles dark mode automatically
- `max-w-none` removes the default max-width

## Custom CSS Overrides

```css
.tiptap {
  @apply prose prose-sm sm:prose-base lg:prose-lg dark:prose-invert max-w-none;

  h1 {
    @apply text-3xl font-bold mt-8 mb-4;
  }

  h2 {
    @apply text-2xl font-semibold mt-6 mb-3;
  }

  p {
    @apply my-4 text-base leading-7;
  }

  ul,
  ol {
    @apply my-4 ml-6;
  }

  code {
    @apply bg-muted px-1.5 py-0.5 rounded text-sm font-mono;
  }

  pre {
    @apply bg-muted p-4 rounded-lg overflow-x-auto;
  }

  blockquote {
    @apply border-l-4 border-primary pl-4 italic my-4;
  }
}
```

Uses semantic Tailwind v4 colors (`bg-muted`, `border-primary`).

## Placeholder Styling

```css
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  color: var(--muted-foreground);
  float: left;
  height: 0;
  pointer-events: none;
}
```

Requires the Placeholder extension with `emptyEditorClass: 'is-editor-empty'`.
