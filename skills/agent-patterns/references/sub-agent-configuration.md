---
title: Sub-Agent Configuration and Prompt Engineering
description: How to configure custom agents with frontmatter, tools, models, permission modes, and effective prompts
tags:
  [
    configuration,
    frontmatter,
    tools,
    model-selection,
    prompt-engineering,
    permissions,
  ]
---

# Sub-Agent Configuration and Prompt Engineering

## File Format

Markdown files with YAML frontmatter. The body becomes the system prompt. Subagents receive only this system prompt plus basic environment details (working directory), not the full Claude Code system prompt.

```yaml
---
name: code-reviewer
description: Expert code reviewer. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: sonnet
color: Blue
permissionMode: default
skills:
  - api-conventions
hooks:
  PostToolUse:
    - matcher: 'Edit|Write'
      hooks:
        - type: command
          command: './scripts/run-linter.sh'
---
Your sub-agent's system prompt goes here.
```

## Supported Frontmatter Fields

| Field             | Required | Description                                                                                   |
| ----------------- | -------- | --------------------------------------------------------------------------------------------- |
| `name`            | Yes      | Unique identifier using lowercase letters and hyphens                                         |
| `description`     | Yes      | When Claude should delegate to this subagent                                                  |
| `tools`           | No       | Allowlist of tools the subagent can use; inherits all tools if omitted                        |
| `disallowedTools` | No       | Denylist of tools to remove from inherited or specified list                                  |
| `model`           | No       | `sonnet`, `opus`, `haiku`, or `inherit` (default: `inherit`)                                  |
| `permissionMode`  | No       | `default`, `acceptEdits`, `dontAsk`, `bypassPermissions`, or `plan`                           |
| `skills`          | No       | Skills to inject into subagent context at startup (full content, not just available)          |
| `hooks`           | No       | Lifecycle hooks scoped to this subagent                                                       |
| `color`           | No       | Background color for UI identification (Red, Blue, Green, Yellow, Purple, Orange, Pink, Cyan) |

## Agent Locations and Priority

| Priority    | Location                   | Scope                   |
| ----------- | -------------------------- | ----------------------- |
| 1 (highest) | `--agents` CLI flag        | Current session only    |
| 2           | `.claude/agents/*.md`      | Current project         |
| 3           | `~/.claude/agents/*.md`    | All your projects       |
| 4 (lowest)  | Plugin `agents/` directory | Where plugin is enabled |

When multiple subagents share the same name, the higher-priority location wins.

## CLI-Defined Subagents

Pass JSON when launching Claude Code for session-scoped agents:

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

Use `prompt` for the system prompt (equivalent to the markdown body in file-based agents).

## Tool Access Patterns

| Agent Type     | Recommended Tools                       | Notes                          |
| -------------- | --------------------------------------- | ------------------------------ |
| Read-only      | `Read, Grep, Glob`                      | Reviewers, auditors            |
| File creators  | `Read, Write, Edit, Glob, Grep`         | NO Bash (causes approval spam) |
| Script runners | `Read, Write, Edit, Glob, Grep, Bash`   | Full access                    |
| Research       | `Read, Grep, Glob, WebFetch, WebSearch` | External data access           |

Subagents inherit all tools by default, including MCP tools. Use `disallowedTools` to explicitly deny tools:

```yaml
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
---
```

## Permission Modes

| Mode                | Behavior                                                           |
| ------------------- | ------------------------------------------------------------------ |
| `default`           | Standard permission checking with prompts                          |
| `acceptEdits`       | Auto-accept file edits                                             |
| `dontAsk`           | Auto-deny permission prompts (explicitly allowed tools still work) |
| `bypassPermissions` | Skip all permission checks (use with caution)                      |
| `plan`              | Plan mode (read-only exploration)                                  |

If the parent uses `bypassPermissions`, this takes precedence and cannot be overridden.

## Model Selection

| Task Type          | Model  | Reason             |
| ------------------ | ------ | ------------------ |
| Content generation | Sonnet | Quality matters    |
| Code writing       | Sonnet | Bugs are expensive |
| Creative work      | Opus   | Maximum quality    |
| Fast lookups       | Haiku  | Speed over depth   |
| Format checks      | Haiku  | Pass/fail only     |

Default is `inherit` (uses the main conversation's model).

## Preloading Skills

Inject skill content directly into a subagent's context at startup:

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

Subagents do not inherit skills from the parent conversation. Each skill must be listed explicitly. The full skill content is injected, not just made available for invocation.

## Prompt Engineering for Agents

### Put Critical Instructions First

Instructions past approximately line 300 in the system prompt get deprioritized by models. Structure prompts with the most important rules immediately after frontmatter.

### Avoiding Bash Approval Spam

When subagents have Bash, they default to heredocs for file creation, triggering approval prompts.

Solutions (in order of preference):

1. Remove Bash from tools list if the agent only creates files
2. Put "USE WRITE TOOL FOR ALL FILES" as the first instruction
3. Remove contradictory examples that show bash-based file creation

### Write Clear Descriptions

Claude uses the `description` field to decide when to auto-delegate. Include phrases like "use proactively" for eager delegation:

```yaml
description: Expert code reviewer. Use proactively after code changes.
```

### Hooks for Validation

Use `PreToolUse` hooks to validate operations before they execute:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/validate-command.sh'
  PostToolUse:
    - matcher: 'Edit|Write'
      hooks:
        - type: command
          command: './scripts/run-linter.sh'
```

Hook scripts receive JSON via stdin with tool input in `tool_input`. Exit code 2 blocks the operation and feeds the error message back to Claude via stderr. Supported events: `PreToolUse`, `PostToolUse`, `Stop` (converted to `SubagentStop` at runtime).

## Disabling Specific Subagents

Add to the `deny` array in settings to prevent Claude from using specific agents:

```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```
