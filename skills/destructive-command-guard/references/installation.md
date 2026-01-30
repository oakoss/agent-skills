---
title: Installation and Claude Code Setup
description: Installing DCG via script, source, or prebuilt binaries and configuring the Claude Code hook
tags: [installation, setup, claude-code, hook, configuration]
---

# Installation and Claude Code Setup

## Quick Install (Recommended)

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh?$(date +%s)" | bash

# Easy mode: auto-update PATH
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh?$(date +%s)" | bash -s -- --easy-mode

# System-wide (requires sudo)
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/destructive_command_guard/master/install.sh?$(date +%s)" | sudo bash -s -- --system
```

## From Source (Requires Rust Nightly)

```bash
cargo +nightly install --git https://github.com/Dicklesworthstone/destructive_command_guard
```

## Prebuilt Binaries

Available for: Linux x86_64, Linux ARM64, macOS Intel, macOS Apple Silicon, Windows

## Claude Code Configuration

Add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "dcg"
          }
        ]
      }
    ]
  }
}
```

**Important:** Restart Claude Code after adding the hook.

## CLI Usage

Test commands manually:

```bash
# Show version with build metadata
dcg --version

# Test a command
echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | dcg
```

## Exit Codes

| Code | Meaning                            |
| ---- | ---------------------------------- |
| `0`  | Command is safe, proceed           |
| `2`  | Command is blocked, do not execute |

## Example Block Message

```text
================================================================
BLOCKED  dcg
----------------------------------------------------------------
Reason:  git reset --hard destroys uncommitted changes. Use 'git stash' first.

Command:  git reset --hard HEAD~1

Tip: If you need to run this command, execute it manually in a terminal.
     Consider using 'git stash' first to save your changes.
================================================================
```

## Contextual Suggestions

| Command Type                   | Suggestion                                          |
| ------------------------------ | --------------------------------------------------- |
| `git reset`, `git checkout --` | "Consider using 'git stash' first"                  |
| `git clean`                    | "Use 'git clean -n' first to preview"               |
| `git push --force`             | "Consider using '--force-with-lease'"               |
| `rm -rf`                       | "Verify the path carefully before running manually" |
