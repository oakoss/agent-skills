---
title: Troubleshooting and Anti-Patterns
description: Common agent issues, anti-patterns to avoid, and debugging strategies
tags: [troubleshooting, anti-patterns, debugging, failure-recovery]
---

# Troubleshooting and Anti-Patterns

## Anti-Patterns

| Anti-Pattern                                        | Why It Fails                            | Fix                                                                         |
| --------------------------------------------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| Too many agents                                     | Coordination overhead > benefit         | Start with 2-3, add only if needed                                          |
| Delegating without a clear objective                | "Fix this" gives no direction           | Provide a manifest: objective, constraints, tools                           |
| Passing entire codebase to a sub-agent              | Context overflow                        | Use context distillation -- pass only relevant symbols and facts            |
| Ignoring sub-agent logs                             | Silent failures are hard to debug       | Always review agent reports                                                 |
| Specialized agents for software dev at scale        | Brittle, single points of failure       | Use fungible agents with a shared task board                                |
| Giving Bash to file-creation agents                 | Approval spam, wrong patterns           | Remove Bash, use Write/Edit tools                                           |
| Burying critical instructions deep in prompt        | Instructions past line 300 get ignored  | Put critical rules FIRST after frontmatter                                  |
| Expecting nested sub-agent spawning                 | Subagents cannot spawn other subagents  | Chain subagents from the main conversation                                  |
| Agents committing directly                          | No review, messy git history            | Agents edit files, humans review and commit                                 |
| Haiku for content generation                        | Quality drops significantly             | Default to Sonnet, Haiku only for fast lookups or script execution          |
| Vague agent descriptions                            | Claude cannot auto-delegate effectively | Write specific descriptions with "use proactively" or "use when..." phrases |
| Running many subagents that return detailed results | Context consumed in main conversation   | Request concise summaries; isolate verbose output                           |

## Troubleshooting Guide

### Agent Does Not Appear in `/agents`

Created the agent file mid-session. Use the `/agents` command to reload, or restart Claude Code. Agents are loaded at startup or via the `/agents` interface.

### Agent Uses Bash Heredocs Instead of Write Tool

Bash is in the tools list and the model defaults to shell commands. Remove Bash from tools or put "USE WRITE TOOL FOR ALL FILES" as the first instruction.

### Agent Loses Track Mid-Task (Context Rot)

Context window filled with verbose outputs. Split into smaller batches (3-5 items instead of 10+). Use subagents for context isolation -- verbose tool outputs stay in the subagent's context while only the summary returns.

### Subagent Returns Incomplete Results

The task was too broad for a single subagent context window. Break the work into smaller, focused subagent calls chained from the main conversation. Each subagent should have a bounded, specific task.

### Fungible Agent Picks Up Stale Task

Another agent already completed it but the board was not updated. Ensure agents mark tasks in-progress before starting and closed when done. Use atomic task claiming if the system supports it.

### Agents Make Conflicting File Edits

Multiple agents edited the same file. Assign non-overlapping item lists per agent. Review with `git diff` before committing and resolve manually.

### Agent Fails and Task Is Stuck

The in-progress task has no active agent. Start a new agent with the same initial prompt. It reads the task board, sees the stuck task, and resumes or restarts it.

### Background Subagent Fails Due to Missing Permissions

Background subagents auto-deny anything not pre-approved. Resume the subagent in the foreground to retry with interactive permission prompts.

### Handoff Drift (Original Objective Lost)

Multi-step delegation without re-stating the goal. Include a "Manifest of Objective" in every sub-agent prompt: objective, constraints, expected output format.

### MCP Tools Not Available in Background Subagent

MCP tools are not supported in background subagents. Run the subagent in the foreground instead, or restructure the workflow to avoid MCP tool usage in background tasks.
