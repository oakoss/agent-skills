---
title: Patterns
description: Collaborative editing with Y.js, markdown support, form integration with react-hook-form, slash commands, and content syncing
tags:
  [
    tiptap,
    collaboration,
    yjs,
    markdown,
    form,
    react-hook-form,
    slash-commands,
    content-sync,
  ]
---

# Patterns

## Collaborative Editing with Y.js

```ts
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Collaboration from '@tiptap/extension-collaboration';
import * as Y from 'yjs';

const ydoc = new Y.Doc();

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      history: false,
    }),
    Collaboration.configure({
      document: ydoc,
    }),
  ],
  immediatelyRender: false,
});
```

Disable history when using Collaboration — local undo/redo conflicts with Y.js CRDT.

## Markdown Support

```ts
import { useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Markdown } from '@tiptap/markdown';

const editor = useEditor({
  extensions: [StarterKit, Markdown],
  content: '# Hello World\n\nThis is **Markdown**!',
  contentType: 'markdown',
  immediatelyRender: false,
});

const markdownOutput = editor.getMarkdown();

editor.commands.setContent('## New heading', { contentType: 'markdown' });
editor.commands.insertContent('**Bold** text', { contentType: 'markdown' });
```

Install: `npm install @tiptap/markdown@3.16.0`

Always specify `contentType: 'markdown'` when setting markdown content — without it, content is parsed as HTML.

Status: Beta (released Oct 2025, API stable but may change).

## Form Integration with react-hook-form

```tsx
import { useForm, Controller } from 'react-hook-form';

function BlogForm() {
  const { control, handleSubmit } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="content"
        control={control}
        render={({ field }) => (
          <Editor
            content={field.value}
            onUpdate={({ editor }) => {
              field.onChange(editor.getHTML());
            }}
          />
        )}
      />
    </form>
  );
}
```

## Slash Commands

```ts
import { Extension } from '@tiptap/core';
import Suggestion from '@tiptap/suggestion';

const SlashCommands = Extension.create({
  name: 'slashCommands',

  addOptions() {
    return {
      suggestion: {
        char: '/',
        items: ({ query }) => {
          return [
            {
              title: 'Heading 1',
              command: ({ editor, range }) => {
                editor
                  .chain()
                  .focus()
                  .deleteRange(range)
                  .setHeading({ level: 1 })
                  .run();
              },
            },
            {
              title: 'Bullet List',
              command: ({ editor, range }) => {
                editor
                  .chain()
                  .focus()
                  .deleteRange(range)
                  .toggleBulletList()
                  .run();
              },
            },
          ];
        },
      },
    };
  },

  addProseMirrorPlugins() {
    return [Suggestion({ editor: this.editor, ...this.options.suggestion })];
  },
});
```

## Content Syncing

Sync external content changes with `useEffect`:

```ts
import { useEffect } from 'react';

function Editor({ content }: { content: string }) {
  const editor = useEditor({
    extensions: [StarterKit],
    immediatelyRender: false,
  });

  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  return <EditorContent editor={editor} />;
}
```

Do not call `setContent` during render — always use `useEffect`.
