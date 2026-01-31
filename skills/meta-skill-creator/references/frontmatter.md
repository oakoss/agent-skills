---
title: Frontmatter
description: Required and optional YAML frontmatter fields for SKILL.md with constraints, examples, and usage guidance
tags:
  [
    frontmatter,
    name,
    description,
    license,
    metadata,
    allowed-tools,
    compatibility,
    hooks,
    model,
    context,
  ]
---

# Frontmatter

Every SKILL.md must begin with a YAML frontmatter block delimited by `---` on the very first line. No blank lines before it.

## Required Fields

### name

The skill identifier. Must match the parent directory name exactly.

| Constraint           | Rule                                         |
| -------------------- | -------------------------------------------- |
| Characters           | Lowercase letters, numbers, and hyphens only |
| Length               | 1-64 characters                              |
| Leading/trailing `-` | Not allowed                                  |
| Consecutive hyphens  | Not allowed (`--`)                           |
| Match directory      | Must match parent directory name             |

Valid examples:

```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

Invalid examples:

```yaml
name: PDF-Processing    # uppercase not allowed
name: -pdf              # cannot start with hyphen
name: pdf--processing   # consecutive hyphens not allowed
name: ab                # too short (min 4 chars for some validators)
```

### description

Describes what the skill does and when to use it. This is the primary mechanism for agent discovery.

| Constraint     | Rule                                              |
| -------------- | ------------------------------------------------- |
| Length         | 1-1024 characters                                 |
| Voice          | Third-person ("Extracts text", not "I help you")  |
| Trigger phrase | Must include "Use when..." or "Use for..." phrase |
| Content        | Keyword-rich for agent semantic matching          |

**Format**: `[Capability in 5-10 words]. Use when/for [keyword-packed trigger list].`

Good example:

```yaml
description: >
  Extracts text and tables from PDF files, fills forms, and merges documents.
  Use when working with PDF documents, form filling, or document extraction.
```

Poor example:

```yaml
description: Helps with PDFs.
```

### Trigger Optimization

Pack the trigger section with terms users actually type:

| Category      | Examples                                   |
| ------------- | ------------------------------------------ |
| Abbreviations | db, auth, sql, config, env, deps           |
| Library names | drizzle, tanstack, shadcn, zod             |
| Synonyms      | table/schema/model, query/fetch/get        |
| Action verbs  | add, create, fix, debug, setup, configure  |
| Problem words | error, failing, broken, not working, issue |

Agents use semantic understanding, not keyword matching. Trigger words help agents understand the domain and intent.

## Optional Fields (Open Standard)

These fields are defined by the [Agent Skills open standard](https://agentskills.io/specification) and are portable across all compatible agents.

### license

License name or reference to a bundled license file:

```yaml
license: MIT
license: Apache-2.0
license: Proprietary. LICENSE.txt has complete terms
```

### compatibility

Environment requirements. Max 500 characters. Only include if the skill has specific requirements:

```yaml
compatibility: Requires git, docker, and jq
compatibility: Designed for Claude Code (or similar products)
```

### metadata

Arbitrary key-value map for additional properties:

```yaml
metadata:
  author: example-org
  version: '1.0'
  source: https://docs.example.com
```

### allowed-tools

Space-delimited list of pre-approved tools. Experimental -- support varies by agent:

```yaml
allowed-tools: Read Grep Glob
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

Common configurations:

| Use Case           | Tools                 | Rationale                   |
| ------------------ | --------------------- | --------------------------- |
| Read-only analysis | `Read Grep Glob`      | Should not modify files     |
| Data processing    | `Read Bash(python:*)` | Run scripts, no file writes |
| Security review    | `Read Grep Glob`      | Audit without changes       |
| Documentation gen  | `Read Grep Write`     | Read code, write docs only  |

Behavior:

- **With allowed-tools**: Listed tools run without permission prompts
- **Without allowed-tools**: Standard permission model applies

## Optional Fields (Claude Code Extensions)

These fields are Claude Code specific and may not be supported by other agents.

### model

Override the conversation model when the skill is active:

```yaml
model: claude-sonnet-4-20250514
```

### context

Set to `fork` to run the skill in an isolated sub-agent with its own conversation history:

```yaml
context: fork
```

Use when the skill does complex multi-step work that would clutter the main conversation.

### agent

Agent type when `context: fork` is set:

```yaml
context: fork
agent: Explore
```

| Agent             | Use Case                        |
| ----------------- | ------------------------------- |
| `general-purpose` | Default, handles most tasks     |
| `Explore`         | Codebase exploration and search |
| `Plan`            | Implementation planning         |
| Custom name       | Agent from `.claude/agents/`    |

### hooks

Lifecycle hooks scoped to the skill execution:

```yaml
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: './scripts/security-check.sh $TOOL_INPUT'
  PostToolUse:
    - matcher: Write
      hooks:
        - type: command
          command: './scripts/validate-output.sh'
  Stop:
    - hooks:
        - type: command
          command: './scripts/cleanup.sh'
```

| Event         | When It Fires                  |
| ------------- | ------------------------------ |
| `PreToolUse`  | Before a tool is executed      |
| `PostToolUse` | After a tool completes         |
| `Stop`        | When the skill stops executing |

### user-invocable

Set to `false` to hide from the `/` slash menu. The skill can still be auto-discovered and invoked by the agent:

```yaml
user-invocable: false
```

### disable-model-invocation

Set to `true` to prevent the agent from invoking the skill automatically. Only users can invoke it via `/skill-name`:

```yaml
disable-model-invocation: true
```

### argument-hint

Hint text shown in autocomplete when users type `/skill-name`:

```yaml
argument-hint: '[issue-number]'
```

## Visibility Matrix

| Setting                          | Slash Menu | Agent Invocation | Auto-discovery |
| -------------------------------- | ---------- | ---------------- | -------------- |
| Default (no settings)            | Visible    | Allowed          | Yes            |
| `user-invocable: false`          | Hidden     | Allowed          | Yes            |
| `disable-model-invocation: true` | Visible    | Blocked          | Yes            |
