---
title: React Hooks and Configuration
description: Installation, HotkeysProvider, useHotkey hook, options API, element scoping, conditional hotkeys, and input handling
tags:
  [
    useHotkey,
    HotkeysProvider,
    target,
    enabled,
    preventDefault,
    ignoreInputs,
    conflictBehavior,
    scoped,
    Mod,
  ]
---

# React Hooks and Configuration

## Installation

```bash
npm install @tanstack/react-hotkeys
```

The React package re-exports everything from `@tanstack/hotkeys-core`, so no separate core install is needed.

## HotkeysProvider

Wraps your app to set default options for all hotkey hooks. Per-hook options override provider defaults.

```tsx
import { HotkeysProvider } from '@tanstack/react-hotkeys';

function App() {
  return (
    <HotkeysProvider
      defaultOptions={{
        hotkey: {
          preventDefault: true,
          stopPropagation: true,
          conflictBehavior: 'warn',
        },
        hotkeySequence: {
          timeout: 1500,
        },
        hotkeyRecorder: {
          onCancel: () => console.log('Recording cancelled'),
        },
      }}
    >
      <Editor />
    </HotkeysProvider>
  );
}
```

`HotkeysProvider` is optional. Without it, hooks use built-in defaults.

## useHotkey

Registers a single keyboard shortcut. Uses `Mod` to abstract Cmd (macOS) / Ctrl (Windows/Linux).

```tsx
import { useHotkey } from '@tanstack/react-hotkeys';

function Editor() {
  useHotkey('Mod+S', () => save());
  useHotkey('Mod+Z', () => undo());
  useHotkey('Mod+Shift+Z', () => redo());
  useHotkey('Escape', () => closePanel());

  return <div>Editor</div>;
}
```

### Options

| Option             | Type                                        | Default     | Description                                                |
| ------------------ | ------------------------------------------- | ----------- | ---------------------------------------------------------- |
| `enabled`          | `boolean`                                   | `true`      | Enable/disable the hotkey dynamically                      |
| `preventDefault`   | `boolean`                                   | smart       | Auto-enabled for modifier combos; manual for single keys   |
| `stopPropagation`  | `boolean`                                   | `false`     | Stop event from bubbling up the DOM                        |
| `eventType`        | `'keydown' \| 'keyup'`                      | `'keydown'` | When the hotkey fires                                      |
| `requireReset`     | `boolean`                                   | `false`     | Only fire once per key press (ignore key repeat)           |
| `ignoreInputs`     | `boolean`                                   | smart       | Smart default ignores single keys in inputs, allows combos |
| `target`           | `RefObject<Element> \| string`              | `document`  | Scope hotkey to a specific element                         |
| `platform`         | `'mac' \| 'windows' \| 'linux'`             | auto        | Override platform detection                                |
| `conflictBehavior` | `'warn' \| 'replace' \| 'error' \| 'allow'` | `'warn'`    | How to handle duplicate hotkey registrations               |

### Options Examples

```tsx
import { useHotkey } from '@tanstack/react-hotkeys';

function AdvancedEditor() {
  // Fire on keyup instead of keydown
  useHotkey('Shift', () => deactivateShiftMode(), {
    eventType: 'keyup',
  });

  // Only fire once per key press, not on key repeat
  useHotkey('Escape', () => closePanel(), {
    requireReset: true,
  });

  // Allow browser default behavior
  useHotkey('Mod+P', () => customPrint(), {
    preventDefault: false,
  });

  // Force single key to work inside text inputs
  useHotkey('Enter', () => submitForm(), {
    ignoreInputs: false,
  });

  // Replace existing registration instead of warning
  useHotkey('Mod+S', () => customSave(), {
    conflictBehavior: 'replace',
  });

  return <div>Advanced editor</div>;
}
```

## Element Scoping

Scope hotkeys to specific elements using the `target` option with a ref. The target element **must** have `tabIndex` to receive focus.

```tsx
import { useRef } from 'react';
import { useHotkey } from '@tanstack/react-hotkeys';

function ScopedEditor() {
  const editorRef = useRef<HTMLDivElement>(null);

  useHotkey('Mod+S', () => saveEditor(), { target: editorRef });
  useHotkey('Escape', () => exitEditor(), { target: editorRef });

  return (
    <div ref={editorRef} tabIndex={-1}>
      <p>Hotkeys only work when this editor is focused</p>
    </div>
  );
}
```

Use `tabIndex={-1}` for programmatic focus only (not in tab order), or `tabIndex={0}` to include in the natural tab order.

## Conditional Hotkeys

Use the `enabled` option to dynamically enable/disable hotkeys without unmounting.

```tsx
import { useState } from 'react';
import { useHotkey } from '@tanstack/react-hotkeys';

function ConditionalEditor() {
  const [isEditing, setIsEditing] = useState(false);

  useHotkey('Mod+S', () => save(), { enabled: isEditing });
  useHotkey('Escape', () => setIsEditing(false), { enabled: isEditing });
  useHotkey('E', () => setIsEditing(true), { enabled: !isEditing });

  return <div>{isEditing ? <textarea /> : <p>Press E to edit</p>}</div>;
}
```

## Input Field Handling

By default, `ignoreInputs` uses smart detection:

- **Single keys** (e.g., `Escape`, `Enter`) are ignored inside `<input>`, `<textarea>`, and `[contenteditable]`
- **Modifier combos** (e.g., `Mod+S`) fire even inside inputs

Override this behavior per-hook:

```tsx
import { useHotkey } from '@tanstack/react-hotkeys';

function FormWithHotkeys() {
  // Forces Enter to fire inside inputs
  useHotkey('Enter', () => submitForm(), {
    ignoreInputs: false,
  });

  // Mod+S works inside inputs by default (smart detection)
  useHotkey('Mod+S', () => saveDraft());

  return (
    <form>
      <input type="text" placeholder="Type here..." />
      <button type="submit">Submit</button>
    </form>
  );
}
```

## Hotkey String Format

Hotkeys use `+` to join keys. Modifiers come first, then the key.

| Hotkey string   | Description                       |
| --------------- | --------------------------------- |
| `Mod+S`         | Cmd+S (Mac) or Ctrl+S (Win/Linux) |
| `Mod+Shift+Z`   | Redo shortcut                     |
| `Control+Alt+D` | Explicit Ctrl (not Mod)           |
| `Escape`        | Single key                        |
| `Shift`         | Modifier alone                    |
| `ArrowUp`       | Arrow keys                        |
| `F1`            | Function keys                     |

Use `Mod` for cross-platform shortcuts. Use `Control` or `Meta` only when you need a specific physical key regardless of platform.
