---
title: Communication and Orchestration Patterns
description: Agent communication methods including chaining subagents, foreground vs background execution, shared memory, message passing, and task board patterns
tags:
  [
    communication,
    orchestration,
    shared-memory,
    message-passing,
    task-board,
    background,
  ]
---

# Communication and Orchestration Patterns

## Communication Methods

### Shared Memory

All agents read/write to a shared state object. Simple but prone to race conditions.

### Message Passing

Agents send structured messages to each other. Clear communication flow, traceable, but more complex.

### Event-Driven

Agents subscribe to events and publish when done. Loose coupling, scalable, but harder to trace execution.

### Task Board (Recommended for Fungible Swarms)

Agents read from a shared task board (beads, issues, or similar). Each agent claims work independently. No central assignment needed.

## Orchestration via Chaining

Subagents cannot spawn other subagents. Orchestration works by chaining subagents from the main conversation:

```text
Main conversation -> Subagent A (completes, returns results)
Main conversation -> Subagent B (uses A's results)
Main conversation -> Subagent C (uses B's results)
Main conversation synthesizes all results
```

For parallel work, ask Claude to spawn multiple subagents simultaneously:

```text
Use separate subagents to research authentication, database, and API modules in parallel
```

Each subagent explores its area independently, then Claude synthesizes the findings. This works best when the research paths do not depend on each other.

## Custom Agent as Orchestrator Template

A custom agent can coordinate multi-step workflows by describing the steps in its system prompt. Claude chains subagent calls from the main conversation when instructed:

```yaml
---
name: release-orchestrator
description: Coordinates release preparation by delegating to specialized agents.
tools: Read, Grep, Glob, Bash
---

You are a release orchestrator. When invoked:

1. Review uncommitted changes using git diff
2. Run the full test suite
3. Check documentation currency
4. Synthesize: Blockers / Warnings / Ready YES|NO
```

## Foreground vs Background Execution

| Mode       | Behavior                                | Permission Handling                          |
| ---------- | --------------------------------------- | -------------------------------------------- |
| Foreground | Blocks main conversation until complete | Prompts passed through to user               |
| Background | Runs concurrently while user continues  | Pre-approved upfront; auto-denies unapproved |

Background subagents cannot use MCP tools. If a background subagent fails due to missing permissions, resume it in the foreground to retry with interactive prompts.

To background a running task: press **Ctrl+B**. To request background execution: ask Claude to "run this in the background".

## Resuming Subagents

Each subagent invocation creates a new instance with fresh context. To continue an existing subagent's work:

```text
Continue that code review and now analyze the authorization logic
```

Resumed subagents retain their full conversation history, including all previous tool calls, results, and reasoning. Subagent transcripts persist independently of the main conversation and survive main conversation compaction.

## Communication Pattern Selection

| Pattern         | Best For                       | Tradeoffs                       |
| --------------- | ------------------------------ | ------------------------------- |
| Shared memory   | Simple state coordination      | Race conditions, no trace       |
| Message passing | Structured agent-to-agent flow | Complex setup, traceable        |
| Event-driven    | Loose coupling, scalability    | Hard to trace execution         |
| Task board      | Fungible swarms                | Requires task management system |

## Recovery Patterns

| Scenario               | Recovery                                                     |
| ---------------------- | ------------------------------------------------------------ |
| Agent dies             | Bead remains in-progress; any agent picks it up              |
| Wrong change           | `git checkout -- [file]`; re-run with better instructions    |
| Conflict               | Check which change is correct; manually resolve              |
| Stale task             | Agent marks complete, board not updated; use atomic claiming |
| Background agent fails | Resume in foreground to retry with interactive permissions   |
