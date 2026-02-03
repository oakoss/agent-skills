---
title: Command Anatomy
description: Markdown structure, YAML frontmatter fields, file locations, priority order, and organization patterns for Claude Code slash commands
tags:
  [
    frontmatter,
    description,
    allowed-tools,
    file-locations,
    priority,
    subdirectories,
    organization,
  ]
---

# Command Anatomy

## Markdown Structure

Every command is a markdown file with optional YAML frontmatter followed by instruction content. The filename (minus `.md`) becomes the command name.

```markdown
---
description: Brief description shown in /help
allowed-tools: Read, Grep, Glob
argument-hint: [filename]
---

# Command Title

## Steps

1. First action
2. Second action
3. Final action
```

## YAML Frontmatter Fields

All fields are optional. Only `description` is recommended so Claude knows when to use the command.

### description

Brief text shown in `/help` and used by the Skill tool to decide when to invoke the command.

```yaml
---
description: Create a conventional git commit with proper formatting
---
```

Commands without `description` do not appear in `/help` and cannot be invoked by the Skill tool.

### allowed-tools

Restricts which tools Claude can use without per-use approval when the command is active. Supports glob patterns for tool arguments.

```yaml
---
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git status:*), Read
---
```

Common patterns:

```yaml
---
allowed-tools: Read, Grep, Glob
---
```

```yaml
---
allowed-tools: Bash(gh *), Read, Grep
---
```

Required when using `` !`bash` `` injection syntax.

### argument-hint

Hint displayed during autocomplete to indicate expected arguments.

```yaml
---
argument-hint: [issue-number]
---
```

```yaml
---
argument-hint: [type] [name]
---
```

### disable-model-invocation

Prevents Claude from automatically loading this command. Use for commands with side effects (deploy, commit, send messages) where you want explicit control over timing.

```yaml
---
disable-model-invocation: true
---
```

When set to `true`, the description is not loaded into Claude context at all, reducing context cost to zero.

### user-invocable

Set to `false` to hide from the `/` menu. Use for background knowledge that Claude should apply automatically but users should not invoke directly.

```yaml
---
user-invocable: false
---
```

### model

Override the model used when this command is active.

```yaml
---
model: claude-sonnet-4-20250514
---
```

### context

Set to `fork` to run the command in an isolated subagent context. The command content becomes the prompt that drives the subagent. The subagent has no access to conversation history.

```yaml
---
context: fork
---
```

Only use `context: fork` with commands that have explicit task instructions. Guidelines-only content (like "use these conventions") produces no meaningful output in a subagent.

### agent

Specifies which subagent type to use when `context: fork` is set. Options include built-in agents (`Explore`, `Plan`, `general-purpose`) or custom subagents from `.claude/agents/`.

```yaml
---
context: fork
agent: Explore
---
```

If omitted, defaults to `general-purpose`.

### hooks

Hooks scoped to this command's lifecycle. See the Claude Code hooks documentation for configuration format.

```yaml
---
hooks:
  pre_tool_call:
    - matcher: Bash
      hooks:
        - command: echo "About to run bash"
          type: command
---
```

## Invocation control matrix

| Frontmatter                      | User can invoke | Claude can invoke | Context cost                  |
| -------------------------------- | --------------- | ----------------- | ----------------------------- |
| (default)                        | Yes             | Yes               | Description always loaded     |
| `disable-model-invocation: true` | Yes             | No                | Zero (description not loaded) |
| `user-invocable: false`          | No              | Yes               | Description always loaded     |

## File Locations

### Single-file commands

| Location                         | Invocation | Label in /help |
| -------------------------------- | ---------- | -------------- |
| `.claude/commands/name.md`       | `/name`    | (project)      |
| `.claude/commands/git/commit.md` | `/commit`  | (project:git)  |
| `~/.claude/commands/name.md`     | `/name`    | (user)         |
| Plugin `commands/name.md`        | `/name`    | (plugin-name)  |

### Skill directories

| Location                         | Invocation | Label in /help |
| -------------------------------- | ---------- | -------------- |
| `.claude/skills/name/SKILL.md`   | `/name`    | (project)      |
| `~/.claude/skills/name/SKILL.md` | `/name`    | (user)         |
| Plugin `skills/name/SKILL.md`    | `/name`    | (plugin-name)  |

Skills are the recommended format. They support additional files (templates, scripts, reference docs) alongside `SKILL.md`.

### Automatic discovery in monorepos

When editing files in subdirectories, Claude Code also discovers skills from nested `.claude/skills/` directories. For example, editing a file in `packages/frontend/` also loads skills from `packages/frontend/.claude/skills/`.

## Priority Order

When commands share a name across levels:

1. **Enterprise** (managed settings) -- highest priority
2. **Personal** (`~/.claude/`)
3. **Project** (`.claude/`)

Plugin commands use namespacing (`plugin-name:skill-name`) and never conflict with other levels. If a skill directory and a command file share the same name, the skill takes precedence.

## Organizing Commands with Subdirectories

Use subdirectories to categorize project commands:

```text
.claude/commands/
├── git/
│   ├── commit.md          # /commit -> "(project:git)"
│   ├── pr.md              # /pr -> "(project:git)"
│   └── sync.md            # /sync -> "(project:git)"
├── dev/
│   ├── feature.md         # /feature -> "(project:dev)"
│   └── debug.md           # /debug -> "(project:dev)"
└── docs/
    └── update.md          # /update -> "(project:docs)"
```

The subdirectory name appears in parentheses in `/help` as `(project:subdirectory)`.

### Naming Conventions

| Pattern     | Example            | Use Case           |
| ----------- | ------------------ | ------------------ |
| `verb-noun` | `create-component` | Action commands    |
| `noun`      | `commit`           | Well-known actions |
| `verb`      | `review`           | Context-dependent  |

## Skill Tool Permissions

Claude invokes commands programmatically via the Skill tool. Control access through permission rules:

| Rule                 | Matches                     |
| -------------------- | --------------------------- |
| `Skill(commit)`      | Only `/commit` with no args |
| `Skill(review-pr *)` | `/review-pr` with any args  |
| `Skill`              | Deny all skill invocations  |

### Character Budget

Skill descriptions consume a shared character budget (default: 15,000 characters). When exceeded, Claude sees fewer commands. Check with `/context` and increase via the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable.

### Enabling Automatic Invocation

Reference commands in CLAUDE.md to encourage Claude to use them automatically:

```markdown
When writing tests, run /write-unit-test to generate test files.
After fixing bugs, run /verify-fix to ensure the fix is complete.
```

This works because Claude reads CLAUDE.md at the start of every session and treats its content as project instructions.

## Built-in Commands

These commands are built-in and cannot be overridden:

| Command        | Purpose                 |
| -------------- | ----------------------- |
| `/help`        | Get usage help          |
| `/compact`     | Compact conversation    |
| `/memory`      | Edit CLAUDE.md files    |
| `/init`        | Initialize CLAUDE.md    |
| `/permissions` | View/update permissions |
| `/agents`      | Manage subagents        |
| `/mcp`         | Manage MCP servers      |
| `/context`     | View context usage      |

Run `/help` in Claude Code for the full list.

## Commands vs Skills vs Subagents

| Aspect           | Single-file command     | Skill directory                     | Subagent                 |
| ---------------- | ----------------------- | ----------------------------------- | ------------------------ |
| Structure        | One `.md` file          | Directory with `SKILL.md` + extras  | `.claude/agents/name.md` |
| Discovery        | Explicit (`/command`)   | Automatic or explicit               | Delegated by Claude      |
| Supporting files | No                      | Yes (scripts, templates, docs)      | Can preload skills       |
| Best for         | Simple reusable prompts | Complex capabilities with resources | Isolated task delegation |
