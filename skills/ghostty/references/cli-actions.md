---
title: CLI Actions
description: Ghostty CLI actions, command-line flags, IPC commands, and the distinction between CLI and keybind actions
tags:
  [
    cli,
    actions,
    ipc,
    new-window,
    list-themes,
    list-fonts,
    list-actions,
    validate-config,
    flags,
  ]
---

# CLI Actions

## CLI Location

On macOS, Ghostty's CLI binary is inside the app bundle:

```bash
/Applications/Ghostty.app/Contents/MacOS/ghostty
```

If symlinked to your PATH, use `ghostty` directly. On Linux, it is typically available as `ghostty` after installation.

## CLI Actions vs Keybind Actions

Ghostty has two distinct types of actions:

- **CLI actions** use the `+action` syntax on the command line (e.g., `ghostty +list-themes`)
- **Keybind actions** are configured in the config file and triggered by key combinations (e.g., `keybind = ctrl+shift+t=new_tab`)

These are separate systems. Not all keybind actions have CLI equivalents.

## Available CLI Actions

### Discovery and Inspection

List all keybind actions available for configuration:

```bash
ghostty +list-actions
```

Show general help and list all CLI actions:

```bash
ghostty +help
```

Get help for a specific action:

```bash
ghostty +list-themes --help
```

### Theme Management

Browse and preview built-in themes in an interactive TUI:

```bash
ghostty +list-themes
```

Filter by color scheme:

```bash
ghostty +list-themes --color=dark
ghostty +list-themes --color=light
```

In the theme preview, press `?` to list available keybindings. Press `c` to copy the selected theme name to the clipboard.

### Font Management

List available fonts using Ghostty's font discovery:

```bash
ghostty +list-fonts
```

Show which font renders a specific Unicode codepoint:

```bash
ghostty +show-face U+1F600
```

### Keybind Inspection

List current keybind configuration:

```bash
ghostty +list-keybinds
```

List only the built-in default keybinds:

```bash
ghostty +list-keybinds --default
```

### Color Reference

List all named RGB colors:

```bash
ghostty +list-colors
```

### Configuration

Show current configuration in valid config file format:

```bash
ghostty +show-config
```

Show all options with defaults and documentation:

```bash
ghostty +show-config --default --docs
```

Open config file in your editor (`$VISUAL` or `$EDITOR`):

```bash
ghostty +edit-config
```

Validate config file for errors:

```bash
ghostty +validate-config
```

### IPC: New Window

Open a new window in a running Ghostty instance:

```bash
ghostty +new-window
```

Open a new window running a specific command:

```bash
ghostty +new-window -e htop
```

Open a new window in a specific GTK application instance:

```bash
ghostty +new-window --class=com.example.MyGhostty
```

**Platform note:** `+new-window` uses D-Bus IPC and only works on Linux/GTK. On macOS, Ghostty does not support this IPC mechanism. On Linux, D-Bus activation allows this to work even when Ghostty is not running.

### SSH Terminfo

Manage SSH terminfo cache for remote hosts:

```bash
ghostty +ssh-cache
```

### Crash Reports

Inspect and manage crash reports:

```bash
ghostty +crash-report
```

### Fun

Display the animation from the Ghostty website:

```bash
ghostty +boo
```

## Command-Line Flags

### Running Commands

Execute a command inside the terminal:

```bash
ghostty -e htop
ghostty -e "bash -c 'echo hello && sleep 5'"
```

### Working Directory

Start in a specific directory:

```bash
ghostty --working-directory=/path/to/project
```

### Configuration

Load an additional config file:

```bash
ghostty --config-file=/path/to/custom-config
```

Any config option can be set via command-line flag:

```bash
ghostty --font-size=14 --font-family="JetBrains Mono" --theme=catppuccin-mocha
```

### Display Info

```bash
ghostty --version
ghostty --help
```

### GTK/Wayland Options

Set GTK application ID or Wayland app ID:

```bash
ghostty --class=com.example.MyGhostty
```

Disable single-instance mode to allow independent windows with custom config:

```bash
ghostty --gtk-single-instance=false --font-size=20
```
