---
title: Sequences and Recording
description: Multi-key sequences with useHotkeySequence, shortcut recording with useHotkeyRecorder, and key state tracking with useKeyHold and useHeldKeys
tags:
  [
    useHotkeySequence,
    useHotkeyRecorder,
    useKeyHold,
    useHeldKeys,
    useHeldKeyCodes,
    sequence,
    recording,
    key-state,
  ]
---

# Sequences and Recording

## useHotkeySequence

Registers a multi-key sequence (Vim-style) that triggers when all keys are pressed in order within a timeout window.

```tsx
import { useHotkeySequence } from '@tanstack/react-hotkeys';

function VimEditor() {
  useHotkeySequence(['G', 'G'], () => scrollToTop());

  useHotkeySequence(['D', 'D'], () => deleteLine());

  useHotkeySequence(['D', 'I', 'W'], () => deleteInnerWord(), {
    timeout: 500,
  });

  return <div>Vim-style editor</div>;
}
```

### Sequence Options

| Option    | Type      | Default | Description                                          |
| --------- | --------- | ------- | ---------------------------------------------------- |
| `timeout` | `number`  | `1000`  | Max milliseconds between keys before sequence resets |
| `enabled` | `boolean` | `true`  | Enable/disable the sequence dynamically              |

### Sequences with Modifiers

Each step in a sequence can include modifier keys:

```tsx
import { useHotkeySequence } from '@tanstack/react-hotkeys';

function EditorWithChords() {
  // Ctrl+K then Ctrl+C (VS Code-style comment toggle)
  useHotkeySequence(['Mod+K', 'Mod+C'], () => toggleComment());

  // Leader key pattern: Space then F to find
  useHotkeySequence([' ', 'F'], () => openFindDialog());

  return <div>Editor with chord sequences</div>;
}
```

## useHotkeyRecorder

Lets users record their own keyboard shortcuts. Captures the key combination pressed and returns it as a hotkey string.

```tsx
import { useHotkeyRecorder, formatForDisplay } from '@tanstack/react-hotkeys';

function ShortcutRecorder() {
  const {
    isRecording,
    recordedHotkey,
    startRecording,
    stopRecording,
    cancelRecording,
  } = useHotkeyRecorder({
    onRecord: (hotkey) => {
      console.log('Recorded:', hotkey);
    },
  });

  return (
    <div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording
          ? 'Press a key combination...'
          : recordedHotkey
            ? formatForDisplay(recordedHotkey)
            : 'Click to record'}
      </button>
      {isRecording && <button onClick={cancelRecording}>Cancel</button>}
    </div>
  );
}
```

### Recorder Return Value

| Property          | Type             | Description                 |
| ----------------- | ---------------- | --------------------------- |
| `isRecording`     | `boolean`        | Whether recording is active |
| `recordedHotkey`  | `string \| null` | The recorded hotkey string  |
| `startRecording`  | `() => void`     | Begin capturing keystrokes  |
| `stopRecording`   | `() => void`     | Stop and finalize recording |
| `cancelRecording` | `() => void`     | Stop without saving         |

### Recorder Options

| Option     | Type                       | Default | Description                            |
| ---------- | -------------------------- | ------- | -------------------------------------- |
| `onRecord` | `(hotkey: string) => void` | —       | Called when recording completes        |
| `onCancel` | `() => void`               | —       | Called when recording is cancelled     |
| `onClear`  | `() => void`               | —       | Called when recorded hotkey is cleared |

### Settings Panel Example

```tsx
import { useState } from 'react';
import {
  useHotkey,
  useHotkeyRecorder,
  formatForDisplay,
} from '@tanstack/react-hotkeys';

function ShortcutSettings() {
  const [shortcuts, setShortcuts] = useState<Record<string, string>>({
    save: 'Mod+S',
    find: 'Mod+F',
    undo: 'Mod+Z',
  });
  const [editingAction, setEditingAction] = useState<string | null>(null);

  const { isRecording, startRecording, cancelRecording } = useHotkeyRecorder({
    onRecord: (hotkey) => {
      if (editingAction) {
        setShortcuts((prev) => ({ ...prev, [editingAction]: hotkey }));
        setEditingAction(null);
      }
    },
    onCancel: () => setEditingAction(null),
  });

  return (
    <div>
      <h3>Keyboard Shortcuts</h3>
      {Object.entries(shortcuts).map(([action, hotkey]) => (
        <div key={action}>
          <span>{action}</span>
          <button
            onClick={() => {
              setEditingAction(action);
              startRecording();
            }}
          >
            {editingAction === action && isRecording
              ? 'Press keys...'
              : formatForDisplay(hotkey)}
          </button>
        </div>
      ))}
      {isRecording && <button onClick={cancelRecording}>Cancel</button>}
    </div>
  );
}
```

## useKeyHold

Returns a boolean indicating whether a specific key is currently held down. Optimized to only re-render when the tracked key changes state.

```tsx
import { useKeyHold } from '@tanstack/react-hotkeys';

function ShiftIndicator() {
  const isShiftHeld = useKeyHold('Shift');

  return (
    <div style={{ opacity: isShiftHeld ? 1 : 0.5 }}>
      {isShiftHeld ? 'Shift is pressed!' : 'Press Shift'}
    </div>
  );
}
```

### Hold-to-Reveal Pattern

```tsx
import { useKeyHold } from '@tanstack/react-hotkeys';

function FileItem({ file }: { file: { name: string; id: string } }) {
  const isShiftHeld = useKeyHold('Shift');

  return (
    <div className="file-item">
      <span>{file.name}</span>
      {isShiftHeld ? (
        <button className="danger" onClick={() => permanentlyDelete(file.id)}>
          Permanently Delete
        </button>
      ) : (
        <button onClick={() => moveToTrash(file.id)}>Move to Trash</button>
      )}
    </div>
  );
}
```

### Shortcut Overlay Pattern

```tsx
import { useKeyHold } from '@tanstack/react-hotkeys';

function ShortcutHints() {
  const isModHeld = useKeyHold('Meta');

  if (!isModHeld) return null;

  return (
    <div className="shortcut-overlay">
      <div>S - Save</div>
      <div>Z - Undo</div>
      <div>Shift+Z - Redo</div>
      <div>K - Command Palette</div>
    </div>
  );
}
```

## useHeldKeys

Returns an array of all currently pressed key names. Re-renders on every key change.

```tsx
import { useHeldKeys } from '@tanstack/react-hotkeys';

function KeyDisplay() {
  const heldKeys = useHeldKeys();

  return (
    <div>
      {heldKeys.length > 0 ? `Held: ${heldKeys.join(' + ')}` : 'No keys held'}
    </div>
  );
}
```

## useHeldKeyCodes

Returns a record mapping key names to their physical `event.code` values. Useful for distinguishing left vs right modifier keys.

```tsx
import { useHeldKeyCodes } from '@tanstack/react-hotkeys';

function KeyDebugDisplay() {
  const heldCodes = useHeldKeyCodes();

  return (
    <ul>
      {Object.entries(heldCodes).map(([keyName, keyCode]) => (
        <li key={keyName}>
          {keyName}: <small>{keyCode}</small>
        </li>
      ))}
    </ul>
  );
}
```

`useHeldKeyCodes` distinguishes physical keys like `ShiftLeft` vs `ShiftRight`, while `useHeldKeys` normalizes both to `Shift`.
