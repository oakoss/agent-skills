---
title: Sub-Agent Configuration and Prompt Engineering
description: How to configure custom agents with frontmatter, tools, models, and effective prompts
tags: [configuration, frontmatter, tools, model-selection, prompt-engineering]
---

# Sub-Agent Configuration and Prompt Engineering

## File Format

Markdown files with YAML frontmatter in `.claude/agents/`:

```yaml
---
name: code-reviewer
description: Expert code reviewer. Use proactively after code changes.
tools: Read, Grep, Glob, Bash
model: inherit
permissionMode: default
skills: project-workflow
hooks:
  PostToolUse:
    - matcher: 'Edit|Write'
      hooks:
        - type: command
          command: './scripts/run-linter.sh'
---
Your sub-agent's system prompt goes here.
```

## Agent Locations and Priority

| Location | Path                    | Priority |
| -------- | ----------------------- | -------- |
| Project  | `.claude/agents/*.md`   | Highest  |
| User     | `~/.claude/agents/*.md` | Lower    |
| CLI      | `--agents '{...}'`      | Inline   |

## Session Restart Required

Agents are loaded at session startup only. New agent files created mid-session require a Claude Code restart to be discovered.

## Tool Access by Agent Type

| Agent Type     | Recommended Tools                         |
| -------------- | ----------------------------------------- |
| Read-only      | `Read, Grep, Glob, LS`                    |
| File creators  | `Read, Write, Edit, Glob, Grep` (NO Bash) |
| Script runners | `Read, Write, Edit, Glob, Grep, Bash`     |
| Research       | `Read, Grep, Glob, WebFetch, WebSearch`   |
| Orchestrators  | `Read, Grep, Glob, Task`                  |

**Principle**: Give agents the minimum tools needed. File creators should NOT have Bash.

## Model Selection

| Task Type          | Model  | Reason                |
| ------------------ | ------ | --------------------- |
| Content generation | Sonnet | Quality matters       |
| Code writing       | Sonnet | Bugs are expensive    |
| Creative work      | Opus   | Maximum quality       |
| Deploy scripts     | Haiku  | Just running commands |
| Format checks      | Haiku  | Pass/fail only        |

## Avoiding Bash Approval Spam

When sub-agents have Bash, they default to heredocs for file creation, triggering dozens of approval prompts.

**Solutions** (in order of preference):

1. **Remove Bash** from tools list if the agent only creates files
2. **Put critical instructions FIRST** in the prompt (right after frontmatter)
3. **Remove contradictory instructions** -- if you want Write tool usage, remove all bash examples from the prompt

## Prompt Engineering for Agents

### Orchestrator Agent Example

```yaml
---
name: release-orchestrator
description: Coordinates release preparation by delegating to specialized agents.
tools: Read, Grep, Glob, Bash, Task
---

You are a release orchestrator. When invoked:

1. Spawn code-reviewer agent -> Review uncommitted changes
2. Spawn test-runner agent -> Run full test suite
3. Spawn doc-validator agent -> Check documentation currency
4. Collect reports and synthesize: Blockers / Warnings / Ready YES|NO

Spawn agents in parallel when tasks are independent.
```

### Nesting Depth Limits

| Level | Example                    | Status                      |
| ----- | -------------------------- | --------------------------- |
| 1     | Claude -> orchestrator     | Works                       |
| 2     | orchestrator -> specialist | Works                       |
| 3     | specialist -> sub-task     | Works but context gets thin |
| 4+    | Deeper nesting             | Not recommended             |
