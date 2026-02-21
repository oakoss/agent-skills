---
title: Formatting and Display
description: Platform-aware hotkey formatting with formatForDisplay, display components, and package overview
tags: [formatForDisplay, display, kbd, platform, macOS, symbols, packages]
---

# Formatting and Display

## formatForDisplay

Converts a hotkey string into a platform-appropriate display string. On macOS, modifiers render as symbols. On Windows/Linux, modifiers render as text.

```tsx
import { formatForDisplay } from '@tanstack/react-hotkeys';

// On macOS:
formatForDisplay('Mod+S'); // "⌘S"
formatForDisplay('Mod+Shift+Z'); // "⇧⌘Z"
formatForDisplay('Control+Alt+D'); // "⌃⌥D"

// On Windows/Linux:
formatForDisplay('Mod+S'); // "Ctrl+S"
formatForDisplay('Mod+Shift+Z'); // "Ctrl+Shift+Z"
formatForDisplay('Control+Alt+D'); // "Ctrl+Alt+D"
```

### Platform Override

Force a specific platform rendering regardless of the user's OS:

```tsx
import { formatForDisplay } from '@tanstack/react-hotkeys';

formatForDisplay('Mod+S', { platform: 'mac' }); // "⌘S"
formatForDisplay('Mod+S', { platform: 'windows' }); // "Ctrl+S"
```

## Display Components

### Shortcut Badge

```tsx
import { formatForDisplay } from '@tanstack/react-hotkeys';

function ShortcutBadge({ hotkey }: { hotkey: string }) {
  return <kbd className="shortcut-badge">{formatForDisplay(hotkey)}</kbd>;
}

// <ShortcutBadge hotkey="Mod+S" />       → ⌘S (Mac) or Ctrl+S (Win)
// <ShortcutBadge hotkey="Mod+Shift+P" /> → ⇧⌘P (Mac) or Ctrl+Shift+P (Win)
```

### Menu Item with Hotkey

```tsx
import { useHotkey, formatForDisplay } from '@tanstack/react-hotkeys';

function MenuItem({
  label,
  hotkey,
  onAction,
}: {
  label: string;
  hotkey: string;
  onAction: () => void;
}) {
  useHotkey(hotkey, () => onAction());

  return (
    <div className="menu-item">
      <span>{label}</span>
      <span className="menu-shortcut">{formatForDisplay(hotkey)}</span>
    </div>
  );
}

// <MenuItem label="Save" hotkey="Mod+S" onAction={save} />
// <MenuItem label="Undo" hotkey="Mod+Z" onAction={undo} />
```

### Command Palette Item

```tsx
import { formatForDisplay } from '@tanstack/react-hotkeys';
import type { Hotkey } from '@tanstack/react-hotkeys';

interface Command {
  id: string;
  label: string;
  hotkey?: Hotkey;
  action: () => void;
}

function CommandPaletteItem({ command }: { command: Command }) {
  return (
    <div className="command-item" onClick={command.action}>
      <span>{command.label}</span>
      {command.hotkey && <kbd>{formatForDisplay(command.hotkey)}</kbd>}
    </div>
  );
}
```

## macOS Modifier Symbols

On macOS, `formatForDisplay` converts modifiers to standard Apple symbols:

| Modifier | Symbol | Display                   |
| -------- | ------ | ------------------------- |
| Command  | ⌘      | `Mod` on Mac renders as ⌘ |
| Shift    | ⇧      | `Shift` renders as ⇧      |
| Option   | ⌥      | `Alt` renders as ⌥        |
| Control  | ⌃      | `Control` renders as ⌃    |

On Windows/Linux, all modifiers display as text joined with `+`.

## Packages

| Package                      | Description                         |
| ---------------------------- | ----------------------------------- |
| `@tanstack/hotkeys-core`     | Framework-agnostic core utilities   |
| `@tanstack/react-hotkeys`    | React hooks (re-exports core)       |
| `@tanstack/hotkeys-devtools` | DevTools for debugging hotkey state |

Install `@tanstack/react-hotkeys` for React projects — it includes the core package automatically.
