---
title: TUI Reference
description: Terminal UI features including keyboard shortcuts, themes, saved views, density modes, bookmarks, context window sizing, and detail pane tabs
tags:
  [
    TUI,
    keyboard,
    shortcuts,
    theme,
    views,
    density,
    bookmarks,
    context-window,
    detail-pane,
    command-palette,
  ]
---

# TUI Reference

Launch with `cass` (no flags). **Do not use from AI agents — use `--robot` mode instead.**

## Keyboard Shortcuts

### Navigation

- `Up/Down`: Move selection
- `Left/Right`: Switch panes
- `Tab/Shift+Tab`: Cycle focus
- `Enter`: Open in `$EDITOR`
- `Space`: Full-screen detail view
- `Home/End`: Jump to first/last result
- `PageUp/PageDown`: Scroll by page

### Filtering

- `F3`: Agent filter
- `F4`: Workspace filter
- `F5/F6`: Time filters (from/to)
- `Shift+F3`: Scope to current result's agent
- `Shift+F4`: Clear workspace filter
- `Shift+F5`: Cycle presets (24h/7d/30d/all)
- `Ctrl+Del`: Clear all filters

### Modes

- `F2`: Toggle theme (6 presets)
- `F7`: Context window size (S/M/L/XL)
- `F9`: Match mode (prefix/standard)
- `F12`: Ranking mode
- `Ctrl+B`: Toggle border style

### Selection and Actions

- `m`: Toggle selection
- `Ctrl+A`: Select all
- `A`: Bulk actions menu
- `Ctrl+Enter`: Add to queue
- `Ctrl+O`: Open all queued
- `y`: Copy path/content
- `Ctrl+Y`: Copy all selected
- `/`: Find in detail pane
- `n/N`: Next/prev match

### Views and Palette

- `Ctrl+P`: Command palette
- `1-9`: Load saved view
- `Shift+1-9`: Save view to slot

### Source Filtering (multi-machine)

- `F11`: Cycle source filter (all/local/remote)
- `Shift+F11`: Source selection menu

### Global

- `Ctrl+C`: Quit
- `F1` or `?`: Toggle help
- `Ctrl+Shift+R`: Force re-index
- `Ctrl+Shift+Del`: Reset all TUI state

## Detail Pane Tabs

| Tab          | Content                         | Switch With |
| ------------ | ------------------------------- | ----------- |
| **Messages** | Full conversation with markdown | `[` / `]`   |
| **Snippets** | Keyword-extracted summaries     | `[` / `]`   |
| **Raw**      | Unformatted JSON/text           | `[` / `]`   |

## Context Window Sizing

| Size       | Characters | Use Case                  |
| ---------- | ---------- | ------------------------- |
| **Small**  | ~200       | Quick scanning            |
| **Medium** | ~400       | Default balanced view     |
| **Large**  | ~800       | Longer passages           |
| **XLarge** | ~1600      | Full context, code review |

**Peek Mode** (`Ctrl+Space`): Temporarily expand to XL without changing default.

## Theme Presets

Cycle through 6 built-in themes with `F2`:

| Theme             | Description                      | Best For                |
| ----------------- | -------------------------------- | ----------------------- |
| **Dark**          | Tokyo Night-inspired deep blues  | Low-light environments  |
| **Light**         | High-contrast light background   | Bright environments     |
| **Catppuccin**    | Warm pastels, reduced eye strain | All-day coding          |
| **Dracula**       | Purple-accented dark theme       | Popular developer theme |
| **Nord**          | Arctic-inspired cool tones       | Calm, focused work      |
| **High Contrast** | Maximum readability              | Accessibility needs     |

All themes validated against WCAG contrast requirements (4.5:1 minimum for text).

### Role-Aware Message Styling

| Role          | Visual Treatment             |
| ------------- | ---------------------------- |
| **User**      | Blue-tinted background, bold |
| **Assistant** | Green-tinted background      |
| **System**    | Gray/muted background        |
| **Tool**      | Orange-tinted background     |

## Saved Views

Save filter configurations to 9 slots for instant recall.

**What Gets Saved:**

- Active filters (agent, workspace, time range)
- Current ranking mode
- The search query

**Keyboard:**

- `Shift+1` through `Shift+9`: Save current view
- `1` through `9`: Load view from slot

**Via Command Palette:** `Ctrl+P` → "Save/Load view"

Views persist in `tui_state.json` across sessions.

## Density Modes

Control lines per search result. Cycle with `Shift+D`:

| Mode         | Lines | Best For                |
| ------------ | ----- | ----------------------- |
| **Compact**  | 3     | Maximum results visible |
| **Cozy**     | 5     | Balanced view (default) |
| **Spacious** | 8     | Detailed preview        |

## Bookmark System

Save important results with notes and tags. In TUI: Press `b` to bookmark, add notes and tags.

**Bookmark Structure:**

- `title`: Short description
- `source_path`, `line_number`, `agent`, `workspace`
- `note`: Your annotations
- `tags`: Comma-separated labels
- `snippet`: Extracted content

Storage: `~/.local/share/coding-agent-search/bookmarks.db` (SQLite)
