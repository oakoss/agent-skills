---
title: Modern Unix Toolbox
description: Deep dive into Rust-powered CLI tools including ripgrep, fd, bat, zoxide, fzf, and eza with advanced usage patterns
tags: [ripgrep, fd, bat, zoxide, fzf, eza, rust-cli, unix-tools]
---

# Modern Unix Toolbox

Modern Unix utilities, primarily written in Rust, prioritize speed, safety, and human-friendly defaults over their legacy counterparts.

## ripgrep (rg)

The gold standard for text search. Faster than `grep`, `ag`, and `git grep`. Respects `.gitignore` and skips binary/hidden files by default.

```bash
# Basic search with context
rg "auth-error" -C 3

# Search only in TypeScript JSX files, excluding tests
rg "auth-error" -g "*.tsx" -g "!*.test.*" --stats

# List only files with matches (no content)
rg -l "TODO"

# Match whole words only
rg -w "user"

# Define custom file type and search it
rg --type-add 'web:*.{html,css,js}' --type web "pattern"

# Output matches as JSON (pipe to jq for structured analysis)
rg "TODO" --json | jq '.data.lines.text'

# Search with PCRE2 for advanced regex features
rg -P "(?<=function\s)\w+" --only-matching
```

## fd

A simple, fast alternative to `find`. Colorized output and smart case-sensitivity by default.

```bash
# Find all PDF files
fd -e pdf

# Find files matching a pattern in a specific path
fd "config" /path/to/search

# Execute a command for every result
fd -e tsx -x prettier --write {}

# Find and delete all .DS_Store files
fd -H .DS_Store -x rm -f {}

# Find directories only
fd -t d "test"

# Find files modified in the last hour
fd --changed-within 1h
```

## bat

A `cat` replacement with syntax highlighting for 100+ languages and Git integration.

```bash
# View file with full decorations
bat --style=header,grid,numbers file.ts

# View specific line range
bat -r 10:20 file.py

# Show non-printable characters (debug encoding issues)
bat -A file.txt

# Use as a pager for other tools
rg "pattern" | bat -l ts

# Plain output (no decorations, useful in pipes)
bat --plain file.ts
```

## zoxide (z)

Intelligent directory jumping that remembers where you have been.

```bash
# Jump to best match for "project"
z project

# Go back to previous directory
z -

# Interactive selection using fzf
zi

# Add a directory to the database manually
zoxide add /path/to/project

# List all tracked directories ranked by frequency
zoxide query --list
```

## fzf (Fuzzy Finder)

The glue of the modern CLI. Provides interactive fuzzy search for files, history, and any list.

```bash
# Interactive file selection
fzf

# Search through command history (keybinding)
# CTRL-R

# File search with preview
fzf --preview 'bat --color=always {}'

# Pipe any list into fzf for selection
git branch | fzf | xargs git checkout

# Multi-select mode
fd -e ts | fzf -m | xargs bat
```

**Keybindings (when configured):**

| Keybinding | Action                           |
| ---------- | -------------------------------- |
| CTRL-T     | Fuzzy search for files           |
| CTRL-R     | Fuzzy search command history     |
| ALT-C      | Fuzzy search and cd to directory |

## eza

A metadata-rich `ls` replacement with tree views and Git status integration.

```bash
# Tree view with depth limit
eza --tree --level=2

# Show all files with git status and icons
eza -la --git --icons

# Sort by modification time
eza -l --sort=modified

# Show only directories
eza -D
```

## Terminal Setup

For the best experience, use these tools inside a modern terminal emulator with a Nerd Font for proper icon support:

| Component   | Recommendation                  |
| ----------- | ------------------------------- |
| Terminal    | Warp, Ghostty, or Kitty         |
| Font        | JetBrains Mono Nerd Font        |
| Shell       | Zsh with starship prompt, or Nu |
| Multiplexer | tmux or Zellij                  |
