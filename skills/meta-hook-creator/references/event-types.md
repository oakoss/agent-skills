---
title: Event Types
description: All hook event types, when they fire, matcher patterns, and JSON input schemas
tags:
  [
    PreToolUse,
    PostToolUse,
    PostToolUseFailure,
    PermissionRequest,
    Notification,
    Stop,
    SubagentStop,
    SubagentStart,
    SessionStart,
    SessionEnd,
    PreCompact,
    UserPromptSubmit,
  ]
---

# Event Types

## Lifecycle Overview

Events fire in this order during a session:

1. `SessionStart` -- session begins or resumes
2. `UserPromptSubmit` -- user sends a prompt
3. `PreToolUse` -- before each tool call (can block)
4. `PermissionRequest` -- when permission dialog would appear (can auto-approve/deny)
5. `PostToolUse` -- after tool succeeds
6. `PostToolUseFailure` -- after tool fails
7. `SubagentStart` -- when a subagent spawns
8. `SubagentStop` -- when a subagent finishes (can force continue)
9. `Notification` -- when Claude Code sends a notification
10. `Stop` -- when Claude finishes responding (can force continue)
11. `PreCompact` -- before context compaction
12. `SessionEnd` -- session terminates

## SessionStart

Fires when a session begins or resumes. Use for environment setup and loading context.

**Matcher values:** `startup`, `resume`, `clear`, `compact`

**Input fields** (in addition to common fields):

| Field        | Description                                                  |
| ------------ | ------------------------------------------------------------ |
| `source`     | How session started: `startup`, `resume`, `clear`, `compact` |
| `model`      | Model identifier                                             |
| `agent_type` | Present when started with `claude --agent <name>`            |

**Decision control:** stdout text or `additionalContext` is added to Claude's context.

**Special:** `CLAUDE_ENV_FILE` env var is available only in this event. Write `export` statements to persist environment variables for the session.

```bash
#!/bin/bash
if [ -n "$CLAUDE_ENV_FILE" ]; then
  echo 'export NODE_ENV=development' >> "$CLAUDE_ENV_FILE"
  echo 'export PATH="$PATH:./node_modules/.bin"' >> "$CLAUDE_ENV_FILE"
fi
exit 0
```

## UserPromptSubmit

Fires when the user submits a prompt, before Claude processes it. Use for validation or adding context.

**Matcher:** Not supported. Always fires on every prompt.

**Input fields:**

| Field    | Description                 |
| -------- | --------------------------- |
| `prompt` | The text the user submitted |

**Decision control:**

| Field               | Description                                         |
| ------------------- | --------------------------------------------------- |
| `decision`          | `"block"` prevents processing and erases the prompt |
| `reason`            | Shown to user when blocked                          |
| `additionalContext` | String added to Claude's context                    |

Plain text stdout on exit 0 is also added as context.

## PreToolUse

Fires before a tool call executes. Use for validation, blocking, modifying inputs, or auto-approving.

**Matcher:** Tool name. Values include `Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Task`, `WebFetch`, `WebSearch`, and MCP tools (`mcp__<server>__<tool>`).

**Input fields:**

| Field         | Description                                |
| ------------- | ------------------------------------------ |
| `tool_name`   | Name of the tool                           |
| `tool_input`  | Tool parameters (varies by tool)           |
| `tool_use_id` | Unique identifier for this tool invocation |

**Tool input schemas by tool:**

```json
// Bash
{ "command": "npm test", "description": "Run tests", "timeout": 120000 }

// Write
{ "file_path": "/path/to/file.txt", "content": "file content" }

// Edit
{ "file_path": "/path/to/file.txt", "old_string": "original", "new_string": "replacement" }

// Read
{ "file_path": "/path/to/file.txt", "offset": 10, "limit": 50 }

// Glob
{ "pattern": "**/*.ts", "path": "/path/to/dir" }

// Grep
{ "pattern": "TODO.*fix", "path": "/path/to/dir", "glob": "*.ts" }
```

**Decision control** (via `hookSpecificOutput`):

| Field                      | Description                                                 |
| -------------------------- | ----------------------------------------------------------- |
| `permissionDecision`       | `"allow"`, `"deny"`, or `"ask"`                             |
| `permissionDecisionReason` | Shown to user (allow/ask) or Claude (deny)                  |
| `updatedInput`             | Modified tool parameters, combine with `"allow"` or `"ask"` |
| `additionalContext`        | String added to Claude's context before tool executes       |

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed"
  }
}
```

## PermissionRequest

Fires when a permission dialog is about to appear. Use for auto-approving or denying.

**Matcher:** Tool name, same values as PreToolUse.

**Input fields:** Same as PreToolUse but without `tool_use_id`. Includes `permission_suggestions` array with the "always allow" options.

**Decision control** (via `hookSpecificOutput.decision`):

| Field                | Description                                          |
| -------------------- | ---------------------------------------------------- |
| `behavior`           | `"allow"` grants permission, `"deny"` denies it      |
| `updatedInput`       | For `"allow"`: modifies tool input before execution  |
| `updatedPermissions` | For `"allow"`: applies permission rule updates       |
| `message`            | For `"deny"`: tells Claude why permission was denied |
| `interrupt`          | For `"deny"`: if `true`, stops Claude entirely       |

## PostToolUse

Fires after a tool completes successfully. Use for formatting, logging, or feedback.

**Matcher:** Tool name, same values as PreToolUse.

**Input fields:**

| Field           | Description                         |
| --------------- | ----------------------------------- |
| `tool_name`     | Name of the tool                    |
| `tool_input`    | Arguments sent to the tool          |
| `tool_response` | Result returned by the tool         |
| `tool_use_id`   | Unique identifier for the tool call |

**Decision control:**

| Field                  | Description                               |
| ---------------------- | ----------------------------------------- |
| `decision`             | `"block"` prompts Claude with the reason  |
| `reason`               | Explanation shown to Claude when blocked  |
| `additionalContext`    | Additional context for Claude             |
| `updatedMCPToolOutput` | For MCP tools: replaces the tool's output |

## PostToolUseFailure

Fires when a tool execution fails. Use for logging, alerts, or corrective feedback.

**Matcher:** Tool name, same values as PreToolUse.

**Input fields:** Same as PostToolUse but with error info instead of `tool_response`:

| Field          | Description                                     |
| -------------- | ----------------------------------------------- |
| `error`        | String describing what went wrong               |
| `is_interrupt` | Whether failure was caused by user interruption |

**Decision control:** `additionalContext` only.

## Notification

Fires when Claude Code sends a notification.

**Matcher values:** `permission_prompt`, `idle_prompt`, `auth_success`, `elicitation_dialog`

**Input fields:**

| Field               | Description              |
| ------------------- | ------------------------ |
| `message`           | Notification text        |
| `title`             | Optional title           |
| `notification_type` | Which notification fired |

**Decision control:** Cannot block notifications. `additionalContext` adds context to the conversation.

## SubagentStart

Fires when a subagent spawns via the Task tool.

**Matcher values:** Agent type -- `Bash`, `Explore`, `Plan`, or custom agent names.

**Input fields:**

| Field        | Description                    |
| ------------ | ------------------------------ |
| `agent_id`   | Unique identifier for subagent |
| `agent_type` | Agent name (used for matching) |

**Decision control:** Cannot block creation. `additionalContext` is injected into the subagent's context.

## SubagentStop

Fires when a subagent finishes. Uses same decision control as Stop.

**Matcher values:** Same as SubagentStart.

**Input fields:**

| Field                   | Description                                   |
| ----------------------- | --------------------------------------------- |
| `stop_hook_active`      | `true` if already continuing from a stop hook |
| `agent_id`              | Subagent identifier                           |
| `agent_type`            | Agent name (used for matching)                |
| `agent_transcript_path` | Path to subagent's transcript                 |

## Stop

Fires when the main agent finishes responding. Does not fire on user interrupt.

**Matcher:** Not supported. Always fires.

**Input fields:**

| Field              | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `stop_hook_active` | `true` if already continuing from a previous stop hook |

**Decision control:**

| Field      | Description                                                 |
| ---------- | ----------------------------------------------------------- |
| `decision` | `"block"` prevents Claude from stopping                     |
| `reason`   | Required when blocking; tells Claude why it should continue |

Always check `stop_hook_active` to prevent infinite loops.

## PreCompact

Fires before context compaction.

**Matcher values:** `manual`, `auto`

**Input fields:**

| Field                 | Description                                 |
| --------------------- | ------------------------------------------- |
| `trigger`             | `"manual"` or `"auto"`                      |
| `custom_instructions` | User input from `/compact` (empty for auto) |

## SessionEnd

Fires when a session terminates. Use for cleanup and logging.

**Matcher values:** `clear`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`

**Input fields:**

| Field    | Description           |
| -------- | --------------------- |
| `reason` | Why the session ended |

Cannot block session termination.

## Matcher Patterns

| Pattern              | Matches                      |
| -------------------- | ---------------------------- |
| `"Bash"`             | Specific tool                |
| `"Edit\|Write"`      | Multiple tools (regex OR)    |
| `"Bash.*"`           | Regex pattern                |
| `"mcp__memory__.*"`  | All tools from an MCP server |
| `"mcp__.*__write.*"` | Write tools from any server  |
| `"*"` or `""`        | All occurrences              |
| Omit matcher         | All occurrences              |

## Common Input Fields

All events receive these fields via stdin JSON:

| Field             | Description                  |
| ----------------- | ---------------------------- |
| `session_id`      | Current session identifier   |
| `transcript_path` | Path to conversation JSON    |
| `cwd`             | Current working directory    |
| `permission_mode` | Current permission mode      |
| `hook_event_name` | Name of the event that fired |
