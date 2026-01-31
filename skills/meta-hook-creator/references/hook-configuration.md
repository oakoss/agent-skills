---
title: Hook Configuration
description: Hook types, exit codes, JSON output schema, environment variables, and settings locations
tags:
  [
    command,
    prompt,
    agent,
    exit-codes,
    JSON,
    environment,
    settings,
    async,
    configuration,
  ]
---

# Hook Configuration

## Settings Locations

| Location                      | Scope                     | Shareable                 |
| ----------------------------- | ------------------------- | ------------------------- |
| `~/.claude/settings.json`     | All your projects         | No, local to your machine |
| `.claude/settings.json`       | Single project            | Yes, commit to repo       |
| `.claude/settings.local.json` | Single project (personal) | No, gitignored            |
| Managed policy settings       | Organization-wide         | Yes, admin-controlled     |
| Plugin `hooks/hooks.json`     | When plugin is enabled    | Yes, bundled with plugin  |
| Skill/agent frontmatter       | While component is active | Yes, defined in component |

Hooks are snapshotted at startup. Mid-session changes require review in the `/hooks` menu before taking effect.

## Configuration Structure

Three levels of nesting: event, matcher group, hook handlers.

```json
{
  "hooks": {
    "<EventType>": [
      {
        "matcher": "<regex-pattern>",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/script.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

Multiple matcher groups per event and multiple hooks per matcher are supported. All matching hooks run in parallel. Identical handlers are deduplicated automatically.

## Hook Types

### Command Hooks

Execute a shell command. Receives JSON input on stdin, communicates via exit codes and stdout.

| Field           | Required | Description                                         |
| --------------- | -------- | --------------------------------------------------- |
| `type`          | Yes      | `"command"`                                         |
| `command`       | Yes      | Shell command to execute                            |
| `timeout`       | No       | Seconds before canceling (default: 600)             |
| `async`         | No       | If `true`, runs in background without blocking      |
| `statusMessage` | No       | Custom spinner message while hook runs              |
| `once`          | No       | If `true`, runs only once per session (skills only) |

### Prompt Hooks

Send a prompt to an LLM for single-turn evaluation. Returns a yes/no JSON decision.

| Field           | Required | Description                                       |
| --------------- | -------- | ------------------------------------------------- |
| `type`          | Yes      | `"prompt"`                                        |
| `prompt`        | Yes      | Prompt text; use `$ARGUMENTS` for hook input JSON |
| `model`         | No       | Model to use (defaults to a fast model)           |
| `timeout`       | No       | Seconds before canceling (default: 30)            |
| `statusMessage` | No       | Custom spinner message                            |

Supported events: PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest, UserPromptSubmit, Stop, SubagentStop.

**Response schema:**

```json
{
  "ok": true,
  "reason": "Explanation (required when ok is false)"
}
```

### Agent Hooks

Spawn a subagent with tool access (Read, Grep, Glob) for multi-turn verification.

| Field           | Required | Description                                        |
| --------------- | -------- | -------------------------------------------------- |
| `type`          | Yes      | `"agent"`                                          |
| `prompt`        | Yes      | Prompt describing what to verify; use `$ARGUMENTS` |
| `model`         | No       | Model to use (defaults to a fast model)            |
| `timeout`       | No       | Seconds before canceling (default: 60)             |
| `statusMessage` | No       | Custom spinner message                             |

Same supported events and response schema as prompt hooks. Up to 50 turns.

## Exit Codes

| Code  | Meaning        | Effect                                               |
| ----- | -------------- | ---------------------------------------------------- |
| `0`   | Success        | Continue normally; stdout parsed for JSON output     |
| `2`   | Blocking error | Block the action; stderr fed back to Claude as error |
| Other | Non-blocking   | stderr shown in verbose mode; execution continues    |

**Exit 2 behavior per event:**

| Event                | Can Block? | Effect on Exit 2                          |
| -------------------- | ---------- | ----------------------------------------- |
| `PreToolUse`         | Yes        | Blocks the tool call                      |
| `PermissionRequest`  | Yes        | Denies the permission                     |
| `UserPromptSubmit`   | Yes        | Blocks prompt processing, erases prompt   |
| `Stop`               | Yes        | Prevents stopping, continues conversation |
| `SubagentStop`       | Yes        | Prevents subagent from stopping           |
| `PostToolUse`        | No         | Shows stderr to Claude (tool already ran) |
| `PostToolUseFailure` | No         | Shows stderr to Claude                    |
| `Notification`       | No         | Shows stderr to user only                 |
| `SubagentStart`      | No         | Shows stderr to user only                 |
| `SessionStart`       | No         | Shows stderr to user only                 |
| `SessionEnd`         | No         | Shows stderr to user only                 |
| `PreCompact`         | No         | Shows stderr to user only                 |

## JSON Output

Print JSON to stdout on exit 0 for structured control. JSON is ignored on non-zero exit.

**Top-level fields (all events):**

| Field            | Default | Description                                              |
| ---------------- | ------- | -------------------------------------------------------- |
| `continue`       | `true`  | `false` stops Claude entirely; overrides other decisions |
| `stopReason`     | none    | Message shown to user when `continue` is `false`         |
| `suppressOutput` | `false` | `true` hides stdout from verbose mode                    |
| `systemMessage`  | none    | Warning message shown to the user                        |

**Event-specific fields** go in `hookSpecificOutput` with a `hookEventName` field:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Not allowed in production"
  }
}
```

Choose one approach per hook: exit codes alone, or exit 0 with JSON. Do not mix.

## Environment Variables

| Variable             | Available In      | Description                    |
| -------------------- | ----------------- | ------------------------------ |
| `CLAUDE_PROJECT_DIR` | All hooks         | Project root path              |
| `CLAUDE_ENV_FILE`    | SessionStart only | File path to persist env vars  |
| `CLAUDE_PLUGIN_ROOT` | Plugin hooks      | Plugin directory               |
| `CLAUDE_CODE_REMOTE` | All hooks         | `"true"` if remote web session |

Standard shell environment variables are also available.

## Async Hooks

Set `"async": true` on command hooks to run in the background. Claude continues immediately.

- Only `type: "command"` supports async
- Cannot return decisions (action already proceeded)
- Output delivered on next conversation turn via `systemMessage` or `additionalContext`
- Each firing creates a separate background process (no deduplication)
- Default timeout same as sync hooks (600s)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/run-tests.sh",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## Hooks in Skills and Agents

Skills and agents can define hooks in YAML frontmatter. These hooks are scoped to the component's lifecycle and cleaned up when it finishes.

```yaml
---
name: secure-operations
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/security-check.sh'
          once: true
---
```

All hook events are supported. For subagents, `Stop` hooks are automatically converted to `SubagentStop`. The `once: true` option runs the hook only once per session (skills only).

## The /hooks Menu

Type `/hooks` in Claude Code to view, add, and delete hooks interactively. Hook source labels:

| Label       | Source                        |
| ----------- | ----------------------------- |
| `[User]`    | `~/.claude/settings.json`     |
| `[Project]` | `.claude/settings.json`       |
| `[Local]`   | `.claude/settings.local.json` |
| `[Plugin]`  | Plugin's `hooks/hooks.json`   |

## Disabling Hooks

- Remove the hook entry from settings JSON, or delete via `/hooks` menu
- Set `"disableAllHooks": true` in settings to temporarily disable all hooks
- No way to disable individual hooks while keeping them in config

## Debugging

Run `claude --debug` to see hook execution details. Toggle verbose mode with `Ctrl+O`.
