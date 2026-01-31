---
title: Tool Selection
description: Tool access patterns, common tool combinations, model selection guide, and capability planning
tags: [tools, model, haiku, sonnet, opus, permissions, allowlist, denylist]
---

# Tool Selection

## Available Tools

Subagents can use any of Claude Code's internal tools. By default, subagents inherit all tools from the main conversation, including MCP tools.

| Tool        | Purpose                   | Include When               |
| ----------- | ------------------------- | -------------------------- |
| `Read`      | Read file contents        | Always (basic exploration) |
| `Grep`      | Search content by pattern | Pattern matching needed    |
| `Glob`      | Find files by name        | File discovery needed      |
| `Bash`      | Run shell commands        | Diagnostics, tests, builds |
| `Write`     | Create new files          | Agent creates artifacts    |
| `Edit`      | Modify existing files     | Agent makes code changes   |
| `WebFetch`  | Fetch web content         | Documentation lookup       |
| `WebSearch` | Search the web            | Research tasks             |

## Tool Access Control

### Allowlist with `tools`

Restrict a subagent to specific tools only:

```yaml
---
name: read-only-reviewer
description: Reviews code without modifications. Use proactively after code changes.
tools: Read, Grep, Glob
---
```

When `tools` is specified, the subagent can only use those tools. Omit the field entirely to inherit all tools from the parent conversation (including MCP tools).

### Denylist with `disallowedTools`

Remove specific tools from the inherited set:

```yaml
---
name: safe-researcher
description: Research agent that cannot modify files
disallowedTools: Write, Edit
---
```

This inherits all tools except Write and Edit. Use `disallowedTools` when you want most tools but need to block a few.

### Combining Both

You can use both fields together. The `disallowedTools` removes tools from the `tools` allowlist:

```yaml
---
name: restricted-bash
description: Run diagnostics without file modifications
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit
---
```

## Common Tool Combinations

### Read-Only Reviewer

```yaml
tools: Read, Grep, Glob
```

For code review, style checking, and analysis tasks. Cannot modify files or run commands.

### Investigator with Diagnostics

```yaml
tools: Read, Grep, Glob, Bash
```

For debugging, test execution, and system diagnostics. Can run commands but cannot modify source files directly.

### Agent That Can Fix Issues

```yaml
tools: Read, Grep, Glob, Edit
```

For automated fixes like lint corrections or refactoring. Can modify existing files but cannot create new ones or run commands.

### Full Modification Agent

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash
```

For implementation tasks that require creating files, editing code, and running builds/tests.

### Research Agent

```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```

For documentation lookup, API research, and gathering external information.

### All Tools (Default)

```yaml
# Omit the tools field entirely
```

Inherits everything from the parent conversation, including MCP tools. Use when the agent needs full capabilities.

## Conditional Tool Validation with Hooks

For finer control than allowlist/denylist, use `PreToolUse` hooks to validate specific operations:

```yaml
---
name: db-reader
description: Execute read-only database queries
tools: Bash
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/validate-readonly-query.sh'
---
```

The hook script receives JSON via stdin with the tool input in `tool_input`. Exit code 0 allows the operation, exit code 2 blocks it and feeds the stderr message back to the agent.

## Model Selection Guide

| Model     | Cost           | Speed          | Best For                                                        |
| --------- | -------------- | -------------- | --------------------------------------------------------------- |
| `haiku`   | Low            | Fast           | Code review, style checks, simple validation, codebase search   |
| `sonnet`  | Medium         | Medium         | Debugging, security analysis, implementation, complex reasoning |
| `opus`    | High           | Slow           | Architecture decisions, multi-system analysis, nuanced judgment |
| `inherit` | Same as parent | Same as parent | When cost/speed should match the main conversation              |

### Decision Tree

```text
Is this a simple checklist or search task?
  Yes -> haiku
  No -> Does it require modifying code or deep reasoning?
    Yes -> sonnet
    No -> Does it involve architecture or cross-system decisions?
      Yes -> opus
      No -> sonnet (safe default)
```

### Model Configuration

```yaml
---
name: fast-reviewer
model: haiku
---
```

- **Model alias**: `sonnet`, `opus`, or `haiku`
- **`inherit`**: Uses the same model as the main conversation
- **Omitted**: Defaults to `inherit`

### Cost Optimization Patterns

Route simple tasks to haiku to reduce costs:

```yaml
---
name: style-checker
description: Check code style and formatting. Use proactively after file edits.
tools: Read, Grep, Glob
model: haiku
---
```

Reserve sonnet or opus for tasks requiring deeper analysis:

```yaml
---
name: security-auditor
description: Audit code for security vulnerabilities. Use proactively before releases.
tools: Read, Grep, Glob, Bash
model: sonnet
---
```
