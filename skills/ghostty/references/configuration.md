---
title: Configuration
description: Ghostty config file format, themes, fonts, keybinds, keybind actions, and debugging
tags:
  [
    config,
    themes,
    fonts,
    keybinds,
    keybind-actions,
    splits,
    tabs,
    windows,
    debugging,
  ]
---

# Configuration

## Config File Location

Ghostty uses a plain-text key-value config file:

```text
~/.config/ghostty/config
```

Configuration is optional. Without a config file, Ghostty uses sensible defaults. Use `ghostty +edit-config` to open the file in your editor.

## Config File Format

The config file uses simple `key = value` syntax with no quotes needed for most values:

```text
font-family = JetBrains Mono
font-size = 14
theme = catppuccin-mocha
cursor-style = block
window-padding-x = 8
window-padding-y = 8
background-opacity = 0.95
```

Lines starting with `#` are comments.

## Themes

Ghostty ships with hundreds of built-in themes. Preview them interactively:

```bash
ghostty +list-themes
```

Set a theme in config:

```text
theme = catppuccin-mocha
```

Use different themes for light and dark system appearance:

```text
theme = light:catppuccin-latte,dark:catppuccin-mocha
```

Custom themes are placed in `~/.config/ghostty/themes/` as plain config files containing color definitions.

## Font Configuration

List available fonts:

```bash
ghostty +list-fonts
```

Set font in config:

```text
font-family = JetBrains Mono
font-size = 14
```

Set bold, italic, and bold-italic variants:

```text
font-family = JetBrains Mono
font-family-bold = JetBrains Mono Bold
font-family-italic = JetBrains Mono Italic
font-family-bold-italic = JetBrains Mono Bold Italic
```

## Keybind Configuration

Keybinds map key combinations to keybind actions:

```text
keybind = ctrl+shift+t=new_tab
keybind = ctrl+shift+n=new_window
keybind = ctrl+shift+enter=new_split:right
keybind = ctrl+shift+minus=new_split:down
keybind = ctrl+shift+w=close_surface
```

### Key Keybind Actions

#### Window and Tab Management

```text
keybind = ctrl+shift+n=new_window
keybind = ctrl+shift+t=new_tab
keybind = ctrl+shift+page_up=previous_tab
keybind = ctrl+shift+page_down=next_tab
keybind = ctrl+shift+1=goto_tab:1
keybind = ctrl+shift+2=goto_tab:2
keybind = ctrl+end=last_tab
keybind = ctrl+shift+left=move_tab:-1
keybind = ctrl+shift+right=move_tab:1
keybind = ctrl+shift+o=toggle_tab_overview
```

#### Split Management

Create splits:

```text
keybind = ctrl+shift+enter=new_split:right
keybind = ctrl+shift+minus=new_split:down
keybind = ctrl+shift+backslash=new_split:auto
```

Navigate between splits:

```text
keybind = ctrl+shift+up=goto_split:up
keybind = ctrl+shift+down=goto_split:down
keybind = ctrl+shift+left=goto_split:left
keybind = ctrl+shift+right=goto_split:right
keybind = ctrl+tab=goto_split:next
keybind = ctrl+shift+tab=goto_split:previous
```

Resize splits:

```text
keybind = super+shift+up=resize_split:up,10
keybind = super+shift+down=resize_split:down,10
keybind = super+shift+equal=equalize_splits
```

Zoom into a split:

```text
keybind = ctrl+shift+z=toggle_split_zoom
```

#### Surface and Display

```text
keybind = ctrl+shift+w=close_surface
keybind = f11=toggle_fullscreen
keybind = ctrl+shift+comma=reload_config
```

#### Font Size

```text
keybind = ctrl+equal=increase_font_size:1
keybind = ctrl+minus=decrease_font_size:1
keybind = ctrl+0=reset_font_size
```

### Unbinding Keys

Remove a default keybind:

```text
keybind = ctrl+shift+t=unbind
```

### Key Sequences

Chain multiple keypresses:

```text
keybind = ctrl+a>1=goto_tab:1
keybind = ctrl+a>2=goto_tab:2
```

## Launch Command

Set the default command instead of the login shell:

```text
command = /usr/bin/fish
```

## Window Configuration

```text
window-decoration = true
window-title-font-family = JetBrains Mono
window-padding-x = 8
window-padding-y = 8
window-padding-color = extend
confirm-close-surface = false
resize-overlay = never
```

## Debugging

Validate your config for errors:

```bash
ghostty +validate-config
```

Show the fully resolved config (includes defaults):

```bash
ghostty +show-config
```

Show all options with documentation:

```bash
ghostty +show-config --default --docs
```

Check which font renders a specific character:

```bash
ghostty +show-face U+2603
```

Check version:

```bash
ghostty --version
```
