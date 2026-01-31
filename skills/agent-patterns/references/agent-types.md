---
title: Agent Types and Design Patterns
description: Core multi-agent patterns including fungible swarms, pipelines, hierarchical, peer collaboration, and exploration
tags: [fungible, specialized, swarm, pipeline, hierarchical, peer-review]
---

# Agent Types and Design Patterns

## Pattern 1: Fungible Agent Swarm

All agents are identical and interchangeable. Each picks the highest-priority available task. No role assignment needed.

**When to use**: Software development at scale, task-based workflows, systems that need resilience to agent failure.

**How it works**:

1. Front-load planning into structured tasks (beads/issues with dependency graphs)
2. Spawn N identical agents with the same initial prompt
3. Each agent reads the task board and picks the next unblocked task
4. If an agent dies, another picks up its in-progress task

**Properties**:

| Property                    | Fungible Agents          | Specialized Agents       |
| --------------------------- | ------------------------ | ------------------------ |
| **Failure handling**        | Simple (any agent works) | Complex (need matching)  |
| **Scaling**                 | Just add more            | Requires role balancing  |
| **Single point of failure** | No                       | Yes (each role)          |
| **Coordination overhead**   | Low (via task board)     | High (role dependencies) |
| **Human involvement**       | Front-loaded in planning | Ongoing                  |

**Initial prompt template** (same for all agents):

```text
Read ALL of AGENTS.md and README.md carefully. Understand the codebase architecture.
Register with agent communication system. Check for messages and respond promptly.
Use the task board to find your next highest-priority unblocked task.
Mark tasks in-progress before starting. Inform other agents via messages.
When idle, check the task board for the next available task. Use ultrathink.
```

**When an agent fails**: Start a new session with the same prompt. It reads the task board, sees what is in-progress or stuck, and either resumes or picks a new task. No special logic needed.

## Pattern 2: Sequential Pipeline

Each agent builds on the previous agent's output.

```text
User Query -> Researcher -> Analyst -> Writer -> Editor -> Output
```

**When to use**: Multi-step workflows with clear dependencies.

**Pros**: Clear dependencies, easy to debug.
**Cons**: No parallelization, bottleneck at any stage.

## Pattern 3: Hierarchical (Manager-Worker)

A manager decomposes work, workers execute in parallel, an aggregator combines results.

```text
            Manager Agent
            /     |     \
  Worker 1   Worker 2   Worker 3
            \     |     /
            Aggregator Agent
```

**When to use**: Complex tasks with independent subtasks that benefit from parallelization.

## Pattern 4: Peer Collaboration (Round Table)

Multiple agents iterate until consensus. Useful when review improves quality.

```text
Coder <-> Reviewer <-> Tester -> Consensus
```

**When to use**: Code generation with review, quality-critical outputs.
**Cons**: May not converge, expensive (multiple LLM calls per iteration).

## Pattern 5: Agent Swarm (Exploration)

Multiple agents independently explore the solution space. A selector picks the best result.

**When to use**: Creative brainstorming, exploring multiple approaches.

## Built-in Subagents

Claude Code includes built-in subagents that Claude automatically uses when appropriate:

| Subagent          | Model    | Tools     | Purpose                                                     |
| ----------------- | -------- | --------- | ----------------------------------------------------------- |
| Explore           | Haiku    | Read-only | File discovery, code search, codebase exploration           |
| Plan              | Inherits | Read-only | Codebase research during plan mode                          |
| General-purpose   | Inherits | All tools | Complex research, multi-step operations, code modifications |
| Bash              | Inherits | Terminal  | Running terminal commands in separate context               |
| Claude Code Guide | Haiku    | Read-only | Answering questions about Claude Code features              |

Explore supports thoroughness levels: **quick** (targeted lookups), **medium** (balanced), **very thorough** (comprehensive).

## Nesting Constraint

Subagents cannot spawn other subagents. If a workflow requires multi-step delegation, chain subagents from the main conversation. Each subagent completes its task and returns results to Claude, which then passes relevant context to the next subagent.

## Choosing the Right Pattern

| Scenario                                  | Recommended Pattern                           |
| ----------------------------------------- | --------------------------------------------- |
| Large codebase, many tasks                | Fungible swarm                                |
| Multi-step data processing                | Sequential pipeline                           |
| Independent subtasks needing parallelism  | Hierarchical (chained from main conversation) |
| Code review, quality-critical output      | Peer collaboration                            |
| Creative exploration, multiple approaches | Agent swarm                                   |
| Multi-phase release workflow              | Orchestrator delegation (chained subagents)   |
