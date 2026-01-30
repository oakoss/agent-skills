---
title: Multi-Agent Coordination
description: Hierarchical, sequential, parallel, and handoff orchestration patterns, delegation manifests, recursion limits, and A2A communication
tags:
  [multi-agent, delegation, hierarchical, sequential, parallel, a2a, manifest]
---

# Multi-Agent Coordination

## Orchestration Patterns

### Hierarchical Orchestration

Parent agent delegates to specialized subagents. The parent validates output and handles errors.

```text
Supervisor
  ├── architect-agent (produces design doc)
  ├── developer-agent (implements features)
  └── reviewer-agent (validates code quality)
```

Use when: complex tasks requiring multiple specialized capabilities.

### Sequential Pipeline (Chain of Experts)

One agent passes output to the next in a defined sequence.

```text
architect -> developer -> reviewer -> deployer
```

Use when: tasks have clear phases where each depends on the previous output.

### Parallel Execution

Independent tasks run simultaneously, results aggregated by parent.

```text
Supervisor
  ├── frontend-agent (parallel)
  ├── backend-agent (parallel)
  └── [aggregate results]
```

Use when: tasks are independent and can run concurrently.

### Handoff Pattern

One agent passes full context to another when its expertise is exhausted.

```text
generalist-agent -> specialist-agent (with full context transfer)
```

Use when: task requires expertise transition (e.g., architecture to implementation).

## Delegation Manifests

Every subagent must receive a clear objective manifest:

```ts
interface DelegationManifest {
  objective: string;
  constraints: string[];
  maxTokens: number;
  availableTools: string[];
  planId: string;
  currentStepIndex: number;
}
```

Key rules:

- Never delegate with vague objectives ("fix this")
- Include specific constraints and success criteria
- List available tools explicitly
- Reference the current plan step

## Recursion Limits

To prevent "Inception Loops" and excessive token spend:

- **Maximum delegation depth**: 3 levels
- Each subagent must report its `recursionDepth` in metadata
- If depth limit is reached, task must be completed at current level or escalated to user

```text
Level 0: User request
Level 1: Supervisor agent
Level 2: Specialist agent
Level 3: Executor agent (max depth, no further delegation)
```

## A2A Communication (Peer-to-Peer)

Unlike hierarchical delegation, Agent-to-Agent (A2A) focuses on peer collaboration.

### Request-Response Pattern

```json
{
  "type": "A2A_REQUEST",
  "from": "frontend-dev",
  "to": "backend-architect",
  "payload": {
    "action": "QUERY_SCHEMA",
    "params": { "table": "users" }
  }
}
```

### Negotiation Protocol

When agents have conflicting plans:

1. **Proposal**: Agent A proposes a change
2. **Critique**: Agent B provides feedback with constraints
3. **Synthesis**: Parent or third agent resolves based on project priorities

### Shared Working Memory (Blackboard)

Agents post findings to a shared state to avoid redundant work:

- Discovered symbols and types
- Architectural decisions
- Blockers and dependencies
- Completed sub-tasks

## Anti-Patterns

| Anti-Pattern                         | Consequence                          | Fix                           |
| ------------------------------------ | ------------------------------------ | ----------------------------- |
| Delegating without clear objective   | Subagent wastes tokens on wrong task | Use delegation manifests      |
| Unsupervised agent-to-agent calls    | Uncontrolled recursive delegation    | Require parent supervision    |
| Passing entire codebase              | Token bloat, "lost in the middle"    | Use context distillation      |
| Ignoring subagent logs               | Silent failures hard to debug        | Log all interactions          |
| Generic agents for specialized tasks | Poor quality output                  | Select most appropriate skill |
| No recursion depth tracking          | Inception loops, runaway token spend | Enforce max depth of 3        |
