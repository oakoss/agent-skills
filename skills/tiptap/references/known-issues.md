---
title: Known Issues and Errors
description: Documented Tiptap issues with solutions covering SSR, performance, styling, image upload, build errors, TypeScript, extensions, content sync, placeholders, and collaboration
tags:
  [
    tiptap,
    issues,
    errors,
    ssr,
    performance,
    typescript,
    debugging,
    troubleshooting,
  ]
---

# Known Issues and Errors

## Issue #1: SSR Hydration Mismatch

**Error**: "SSR has been detected, please set `immediatelyRender` explicitly to `false`"

Tiptap defaults to `immediatelyRender: true`, causing server/client HTML mismatch.

**Fix**: Set `immediatelyRender: false` in `useEditor()`.

## Issue #2: Editor Re-renders on Every Keystroke

**Symptom**: Laggy typing, poor performance in large documents.

`useEditor()` re-renders the component on every change.

**Fix**: Use `useEditorState()` for read-only rendering, or memoize extensions:

```ts
const extensions = useMemo(() => [StarterKit, Image, Link], []);

const editor = useEditor({ extensions, immediatelyRender: false });
```

Lazy load extensions when possible:

```ts
const extensions = [
  StarterKit,
  ...(needsTables ? [Table, TableRow, TableCell] : []),
];
```

## Issue #3: Tailwind Typography Not Working

**Symptom**: Headings/lists render unstyled.

**Fix**: Install `@tailwindcss/typography` and add `prose` classes:

```tsx
<EditorContent
  editor={editor}
  className="prose prose-sm dark:prose-invert max-w-none"
/>
```

## Issue #4: Image Upload Base64 Bloat

**Symptom**: JSON payloads become megabytes.

**Fix**: Set `allowBase64: false` and implement upload handler. See [Image Upload](image-upload.md).

## Issue #5: Build Fails in Create React App

**Error**: "jsx-runtime" module resolution errors.

CRA is incompatible with Tiptap v3 ESM module structure.

**Fix**: Switch to Vite or another modern bundler.

## Issue #6: ProseMirror Multiple Versions Conflict

**Error**: "Looks like multiple versions of prosemirror-model were loaded"

Installing additional Tiptap extensions can pull different ProseMirror versions.

**Fix**: Add resolutions to package.json:

```json
{
  "resolutions": {
    "prosemirror-model": "~1.21.0",
    "prosemirror-view": "~1.33.0",
    "prosemirror-state": "~1.4.3"
  }
}
```

Or clean reinstall:

```bash
rm -rf node_modules package-lock.json && npm install
```

## Issue #7: EditorProvider vs useEditor Confusion

Using both together causes SSR errors. EditorProvider is a wrapper around useEditor for React Context — they should not be used simultaneously.

**Fix**: Choose one:

```tsx
// Option 1: EditorProvider only
<EditorProvider immediatelyRender={false} extensions={[StarterKit]}>
  <EditorContent />
</EditorProvider>;

// Option 2: useEditor only
const editor = useEditor({
  extensions: [StarterKit],
  immediatelyRender: false,
});
```

## Issue #8: TypeScript Null Errors

**Error**: "Type 'Editor | null' is not assignable to type 'Editor'"

`useEditor()` returns `Editor | null`. Editor is null during initial render.

**Fix**: Guard before use:

```tsx
const editor = useEditor({
  extensions: [StarterKit],
  immediatelyRender: false,
});
if (!editor) return null;

// Event handlers
<button
  disabled={!editor}
  onClick={() => editor?.chain().focus().toggleBold().run()}
>
  Bold
</button>;
```

## Issue #9: Extensions Not Working

**Symptom**: Extension installed but commands don't work, no errors.

**Fix**: Ensure extension is imported AND added to the `extensions` array. Check with:

```ts
console.log(editor.extensionManager.extensions.map((e) => e.name));
```

## Issue #10: Content Not Updating

**Symptom**: Editor doesn't reflect prop changes.

**Fix**: Sync with `useEffect`, never call `setContent` during render:

```ts
useEffect(() => {
  if (editor && content !== editor.getHTML()) {
    editor.commands.setContent(content);
  }
}, [content, editor]);
```

## Issue #11: Placeholder Not Showing

**Fix**: Install extension AND add CSS:

```css
.tiptap p.is-editor-empty:first-child::before {
  content: attr(data-placeholder);
  color: var(--muted-foreground);
  float: left;
  height: 0;
  pointer-events: none;
}
```

## Issue #12: Collaborative Editing Conflicts

**Symptom**: Content overwrites, cursor positions wrong, undo/redo breaks.

**Fix**: Disable undo/redo when using Y.js. In v3, use `undoRedo: false` (renamed from `history`):

```ts
StarterKit.configure({ undoRedo: false });
```

## Debugging Tips

```ts
const editor = useEditor({
  extensions: [StarterKit],
  onBeforeCreate: ({ editor }) => console.log('Creating:', editor),
  onCreate: ({ editor }) => console.log('Created:', editor),
  onUpdate: ({ editor }) => console.log('Updated:', editor.getJSON()),
});

// Inspect state
console.log(editor.getJSON());
console.log(editor.getHTML());
console.log(editor.state);
console.log(editor.extensionManager.extensions.map((e) => e.name));
console.log(editor.isEditable);
console.log(editor.state.selection);
console.log(editor.getAttributes('heading'));
```
