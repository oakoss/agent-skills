---
title: Communication and Orchestration Patterns
description: Agent communication methods including shared memory, message passing, event-driven, and task board patterns
tags: [communication, orchestration, shared-memory, message-passing, task-board]
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

## Orchestrator Delegation Pattern

An orchestrator agent spawns specialized sub-agents using the `Task` tool, then synthesizes their results.

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

## Enabling Orchestration

Add `Task` to an agent's tools list to allow it to spawn sub-agents:

```yaml
tools: Read, Grep, Glob, Task
```

## Depth Guidelines

- **2 levels max** recommended (orchestrator -> specialist)
- **3 levels** works but context gets thin
- **4+ levels** not recommended

## Communication Pattern Selection

| Pattern         | Best For                       | Tradeoffs                       |
| --------------- | ------------------------------ | ------------------------------- |
| Shared memory   | Simple state coordination      | Race conditions, no trace       |
| Message passing | Structured agent-to-agent flow | Complex setup, traceable        |
| Event-driven    | Loose coupling, scalability    | Hard to trace execution         |
| Task board      | Fungible swarms                | Requires task management system |

## Recovery Patterns

| Scenario     | Recovery                                                     |
| ------------ | ------------------------------------------------------------ |
| Agent dies   | Bead remains in-progress; any agent picks it up              |
| Wrong change | `git checkout -- [file]`; re-run with better instructions    |
| Conflict     | Check which change is correct; manually resolve              |
| Stale task   | Agent marks complete, board not updated; use atomic claiming |
