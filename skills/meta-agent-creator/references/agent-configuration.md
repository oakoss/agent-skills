---
title: Agent Configuration
description: YAML frontmatter fields, file locations, priority order, permission modes, skill preloading, and lifecycle hooks
tags:
  [
    frontmatter,
    yaml,
    configuration,
    permissions,
    hooks,
    skills,
    location,
    priority,
  ]
---

# Agent Configuration

## File Structure

Subagent files use YAML frontmatter for configuration followed by the system prompt in Markdown:

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices. Use proactively after code changes.
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

The frontmatter defines metadata and configuration. The body becomes the system prompt. Subagents receive only this system prompt plus basic environment details, not the full parent system prompt.

## File Locations and Priority

When multiple subagents share the same name, the higher-priority location wins.

| Location                     | Scope                   | Priority    |
| ---------------------------- | ----------------------- | ----------- |
| `--agents` CLI flag (JSON)   | Current session only    | 1 (highest) |
| `.claude/agents/`            | Current project         | 2           |
| `~/.claude/agents/`          | All projects            | 3           |
| Plugin's `agents/` directory | Where plugin is enabled | 4 (lowest)  |

Project subagents in `.claude/agents/` should be checked into version control for team sharing.

## YAML Frontmatter Fields

### Required Fields

| Field         | Description                                           |
| ------------- | ----------------------------------------------------- |
| `name`        | Unique identifier using lowercase letters and hyphens |
| `description` | When the parent should delegate to this subagent      |

### Optional Fields

| Field             | Description                                                      | Default                            |
| ----------------- | ---------------------------------------------------------------- | ---------------------------------- |
| `tools`           | Comma-separated allowlist of tools the subagent can use          | Inherits all tools (including MCP) |
| `disallowedTools` | Comma-separated denylist removed from inherited or specified set | None                               |
| `model`           | Model alias: `sonnet`, `opus`, `haiku`, or `inherit`             | `inherit`                          |
| `permissionMode`  | How the subagent handles permission prompts                      | `default`                          |
| `skills`          | Skills to inject into the subagent's context at startup          | None (no inheritance from parent)  |
| `hooks`           | Lifecycle hooks scoped to this subagent                          | None                               |

## Permission Modes

The `permissionMode` field controls how the subagent handles permission prompts. Subagents inherit the permission context from the main conversation but can override the mode.

```yaml
---
name: auto-fixer
description: Automatically fix lint errors. Use proactively after lint failures.
tools: Read, Edit, Grep, Glob
permissionMode: acceptEdits
---
```

| Mode                | Behavior                                                           |
| ------------------- | ------------------------------------------------------------------ |
| `default`           | Standard permission checking with prompts                          |
| `acceptEdits`       | Auto-accept file edits                                             |
| `dontAsk`           | Auto-deny permission prompts (explicitly allowed tools still work) |
| `bypassPermissions` | Skip all permission checks (use with caution)                      |
| `plan`              | Plan mode (read-only exploration)                                  |

If the parent uses `bypassPermissions`, it takes precedence and cannot be overridden by the subagent.

## Skill Preloading

Use the `skills` field to inject skill content into a subagent's context at startup. Subagents do not inherit skills from the parent conversation.

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---
Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

The full content of each skill is injected into the subagent's context, not just made available for invocation.

## Lifecycle Hooks

Define hooks directly in the subagent's frontmatter. These hooks only run while that specific subagent is active.

| Event         | Matcher Input | When It Fires                                                       |
| ------------- | ------------- | ------------------------------------------------------------------- |
| `PreToolUse`  | Tool name     | Before the subagent uses a tool                                     |
| `PostToolUse` | Tool name     | After the subagent uses a tool                                      |
| `Stop`        | (none)        | When the subagent finishes (converted to `SubagentStop` at runtime) |

```yaml
---
name: safe-editor
description: Edit files with automatic linting after changes
tools: Read, Edit, Grep, Glob
hooks:
  PostToolUse:
    - matcher: 'Edit|Write'
      hooks:
        - type: command
          command: './scripts/run-linter.sh'
---
```

### Project-Level Hooks

Configure hooks in `settings.json` that respond to subagent lifecycle events in the main session:

```json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db-connection.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "hooks": [{ "type": "command", "command": "./scripts/cleanup.sh" }]
      }
    ]
  }
}
```

`SubagentStart` supports matchers to target specific agent types. `SubagentStop` fires for all subagent completions regardless of matcher values.

## CLI-Defined Agents

Pass subagent definitions as JSON via the `--agents` flag for session-only agents:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

The JSON format uses `prompt` for the system prompt (equivalent to the markdown body in file-based agents). CLI-defined agents have the highest priority and are not saved to disk.

## Built-in Agents

Claude Code includes several built-in subagents that are used automatically:

| Agent           | Model    | Tools                     | Purpose                              |
| --------------- | -------- | ------------------------- | ------------------------------------ |
| Explore         | Haiku    | Read-only (no Write/Edit) | Fast codebase search and analysis    |
| Plan            | Inherits | Read-only (no Write/Edit) | Research for plan mode               |
| general-purpose | Inherits | All tools                 | Complex multi-step tasks             |
| Bash            | Inherits | Terminal commands         | Running commands in separate context |

### Explore Thoroughness Levels

When invoking Explore, specify a thoroughness level: **quick** for targeted lookups, **medium** for balanced exploration, or **very thorough** for comprehensive analysis.

## Foreground vs Background Execution

- **Foreground**: Blocks main conversation until complete. Permission prompts pass through to the user.
- **Background**: Runs concurrently. Permissions are pre-approved before launch; unapproved prompts are auto-denied. MCP tools are not available in background subagents.

Press **Ctrl+B** to background a running task, or ask to "run this in the background."

## Resuming Agents

Each subagent invocation creates a new instance with fresh context. To continue a previous subagent's work, ask to resume it. Resumed subagents retain their full conversation history.

Transcripts are stored at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`.

## Disabling Agents

Prevent specific subagents from being used via permission rules:

```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

Or via CLI:

```bash
claude --disallowedTools "Task(Explore)"
```
