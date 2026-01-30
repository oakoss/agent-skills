---
title: Troubleshooting and Anti-Patterns
description: Common agent issues, anti-patterns to avoid, and debugging strategies
tags: [troubleshooting, anti-patterns, debugging, failure-recovery]
---

# Troubleshooting and Anti-Patterns

## Anti-Patterns

| Anti-Pattern                                 | Why It Fails                           | Fix                                                              |
| -------------------------------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| Too many agents                              | Coordination overhead > benefit        | Start with 2-3, add only if needed                               |
| Delegating without a clear objective         | "Fix this" gives no direction          | Provide a manifest: objective, constraints, tools                |
| Passing entire codebase to a sub-agent       | Context overflow                       | Use context distillation -- pass only relevant symbols and facts |
| Ignoring sub-agent logs                      | Silent failures are hard to debug      | Always review agent reports                                      |
| Specialized agents for software dev at scale | Brittle, single points of failure      | Use fungible agents with a shared task board                     |
| Giving Bash to file-creation agents          | Approval spam, wrong patterns          | Remove Bash, use Write/Edit tools                                |
| Burying critical instructions deep in prompt | Instructions past line 300 get ignored | Put critical rules FIRST after frontmatter                       |
| Unsupervised recursive delegation            | "Inception loops", token waste         | Max 3 levels deep, require recursion_depth in metadata           |
| Agents committing directly                   | No review, messy git history           | Agents edit files, humans review and commit                      |
| Haiku for content generation                 | Quality drops significantly            | Default to Sonnet, Haiku only for script execution               |

## Troubleshooting Guide

### Agent Does Not Appear in `/agents`

Created the agent file mid-session. Restart Claude Code -- agents are loaded at startup only.

### Agent Uses Bash Heredocs Instead of Write Tool

Bash is in the tools list and the model defaults to shell commands. Remove Bash from tools or put "USE WRITE TOOL FOR ALL FILES" as the first instruction.

### Agent Loses Track Mid-Task (Context Rot)

Context window filled with verbose outputs. Split into smaller batches (3-5 items instead of 10+). Use agents for context isolation.

### Orchestrator Sub-Agents Return Incomplete Results

Nesting too deep (3+ levels). Keep orchestration to 2 levels. Give each sub-agent a focused, bounded task.

### Fungible Agent Picks Up Stale Task

Another agent already completed it but the board was not updated. Ensure agents mark tasks in-progress before starting and closed when done. Use atomic task claiming if the system supports it.

### Agents Make Conflicting File Edits

Multiple agents edited the same file. Assign non-overlapping item lists per agent. Review with `git diff` before committing and resolve manually.

### Agent Fails and Task Is Stuck

The in-progress task has no active agent. Start a new agent with the same initial prompt. It reads the task board, sees the stuck task, and resumes or restarts it.

### Handoff Drift (Original Objective Lost)

Multi-step delegation without re-stating the goal. Include a "Manifest of Objective" in every sub-agent prompt: objective, constraints, expected output format.
