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

Requires Rust nightly toolchain (minimum Rust 1.85, edition 2024). The repository includes a `rust-toolchain.toml` that automatically selects the correct toolchain.

```bash
cargo +nightly install --git https://github.com/Dicklesworthstone/destructive_command_guard destructive_command_guard
```

## Prebuilt Binaries

Available for: Linux x86_64, Linux ARM64, macOS Intel, macOS Apple Silicon, Windows

## Claude Code Configuration

Add to `~/.claude/settings.json` (global) or `.claude/settings.json` (project):

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

**Important:** Restart Claude Code after adding the hook. Alternatively, use the `/hooks` interactive menu to add hooks (takes effect immediately without restart).

Hook settings can be placed in three locations:

| Location                      | Scope          | Committed |
| ----------------------------- | -------------- | --------- |
| `~/.claude/settings.json`     | All projects   | No        |
| `.claude/settings.json`       | Single project | Yes       |
| `.claude/settings.local.json` | Single project | No        |

## Claude Code Hook API Context

DCG uses the `PreToolUse` hook event, which fires before any tool call. Claude Code supports additional hook events and types that may be relevant for layered safety:

| Hook Event           | When It Fires                     | Relevant to DCG           |
| -------------------- | --------------------------------- | ------------------------- |
| `PreToolUse`         | Before tool execution (can block) | Primary DCG hook          |
| `PostToolUse`        | After tool succeeds               | Audit logging             |
| `PostToolUseFailure` | After tool fails                  | Error tracking            |
| `PermissionRequest`  | When permission dialog appears    | Alternative to PreToolUse |
| `Stop`               | When Claude finishes responding   | Session summary           |
| `SubagentStop`       | When subagent finishes            | Subagent safety           |

Hook types beyond `"type": "command"` (what DCG uses):

- `"type": "prompt"` -- sends hook input to a Claude model for yes/no judgment
- `"type": "agent"` -- spawns a subagent that can read files and run tools to verify conditions

DCG uses `"type": "command"` for deterministic, sub-millisecond blocking. Prompt/agent hooks are useful for complementary checks requiring judgment.

### Structured JSON Output

In addition to exit codes, PreToolUse hooks can return structured JSON on stdout for finer control:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "git reset --hard destroys uncommitted changes. Use git stash first."
  }
}
```

DCG uses exit codes (simpler, faster) rather than JSON output, but the JSON format supports three decisions: `"allow"`, `"deny"`, and `"ask"` (escalate to user).

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
