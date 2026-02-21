---
title: Communication and Orchestration Patterns
description: Agent communication methods including chaining subagents, foreground vs background execution, shared memory, message passing, task board patterns, review workflows, delegation protocols, and dispatch strategies
tags:
  [
    communication,
    orchestration,
    shared-memory,
    message-passing,
    task-board,
    background,
    review-workflow,
    delegation-protocol,
    context-bundling,
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

## Question-First Delegation Protocol

Before an agent starts work, it asks clarifying questions. The controller answers all questions before giving the "proceed" signal. This prevents wasted work from misunderstood tasks.

### Protocol Steps

```text
1. Controller sends task description to agent
2. Agent reads the task, identifies ambiguities
3. Agent returns a list of clarifying questions (does NOT start work)
4. Controller answers all questions
5. Controller sends explicit "proceed" signal
6. Agent begins implementation with full understanding
```

### When to Use Question-First

| Use Question-First                           | Skip It (Direct Delegation)             |
| -------------------------------------------- | --------------------------------------- |
| Task has ambiguous requirements              | Task is mechanical and fully specified  |
| Multiple valid interpretations exist         | Agent has done identical work before    |
| Wrong interpretation wastes significant work | Cost of redo is low (small edits)       |
| Cross-cutting concerns need clarification    | Batch operations with a proven template |

### Agent Prompt for Question-First

```yaml
---
name: cautious-implementer
description: Asks clarifying questions before starting work. Use for ambiguous tasks.
tools: Read, Write, Edit, Glob, Grep
---

Before starting ANY implementation:

1. Read the task description and all referenced files
2. List every assumption you are making
3. Ask clarifying questions for anything ambiguous
4. WAIT for answers before writing any code

Only begin implementation after receiving explicit confirmation.
Do NOT guess at requirements — ask instead.
```

## Context Bundling for Subagents

Provide full task text plus surrounding context rather than just a task title. Subagents start with empty context and cannot see the main conversation, so they need everything up front.

### What to Include

| Context Element           | Example                                                     | Why                                           |
| ------------------------- | ----------------------------------------------------------- | --------------------------------------------- |
| Full task description     | "Add rate limiting to the /api/users endpoint"              | The actual work to do                         |
| Where it fits in the plan | "This is step 3 of 5 in the API hardening initiative"       | Helps agent make consistent design decisions  |
| Related decisions         | "We chose token bucket over sliding window in step 1"       | Prevents agent from re-debating settled items |
| Relevant file paths       | "Rate limiter config is at src/middleware/rate-limit.ts"    | Saves exploration time                        |
| Constraints               | "Must not break existing /api/users tests in users.test.ts" | Prevents regressions                          |
| Expected output format    | "Return a summary: files changed, tests added, edge cases"  | Structures the response                       |

### Minimal vs Bundled Delegation

```text
BAD (minimal context):
"Add rate limiting to the users endpoint"

GOOD (bundled context):
"Add rate limiting to the /api/users endpoint.

Context: This is part of the API hardening initiative. In step 1, we chose
token bucket algorithm (see src/middleware/rate-limit.ts for the base
implementation). Step 2 added rate limiting to /api/auth.

Requirements:
- 100 requests per minute per API key
- Return 429 with Retry-After header when exceeded
- Add tests in src/middleware/__tests__/rate-limit-users.test.ts

Constraints:
- Do not modify existing tests in users.test.ts
- Follow the same pattern used in the /api/auth rate limiter

Return: summary of files changed, tests added, and any edge cases found."
```

## Two-Stage Review Workflow

After an implementer agent completes work, run two sequential review passes: spec compliance first, then code quality. This catches both requirement misses and code issues without overloading a single reviewer.

### Workflow Steps

```text
1. Implementer agent completes the task
2. Spec compliance reviewer checks:
   - Does the output match all requirements?
   - Are edge cases from the spec handled?
   - Are acceptance criteria satisfied?
3. If spec review fails: implementer fixes, return to step 2
4. Code quality reviewer checks:
   - Is the code clean and idiomatic?
   - Are there performance or security issues?
   - Does it follow project conventions?
5. If quality review fails: implementer fixes, return to step 4
6. Both reviewers approve: work is complete
```

### When to Use Two-Stage vs Single-Pass

| Two-Stage Review                        | Single-Pass Review                     |
| --------------------------------------- | -------------------------------------- |
| Complex requirements with many criteria | Simple, well-defined changes           |
| High-stakes code (auth, payments, data) | Internal tooling, scripts              |
| Spec and quality concerns are distinct  | One reviewer can cover both adequately |
| Multiple agents available for review    | Limited agent budget                   |

### Reviewer Agent Configurations

```yaml
---
name: spec-reviewer
description: Checks implementation against requirements. Use after code changes.
tools: Read, Grep, Glob
model: sonnet
---

You are a spec compliance reviewer. Given an implementation and its requirements:

1. Read the requirements document or task description
2. Read all changed files
3. Check each requirement against the implementation
4. Report: PASS (all requirements met) or FAIL (list unmet requirements)

Do NOT comment on code style or quality. Focus only on whether the
implementation satisfies the stated requirements.
```

```yaml
---
name: quality-reviewer
description: Reviews code quality after spec compliance is confirmed. Use after spec review passes.
tools: Read, Grep, Glob
model: sonnet
---

You are a code quality reviewer. The implementation already passes spec review.

1. Read all changed files
2. Check for: naming, structure, duplication, error handling, performance, security
3. Report: PASS (code is clean) or FAIL (list specific issues to fix)

Do NOT re-check requirements. Focus only on code quality and conventions.
```

## Review Loop Enforcement

When a reviewer finds issues, the implementer fixes them, then the reviewer checks again. This loop repeats until the reviewer approves.

### Loop Structure

```text
Iteration 1: Implementer builds → Reviewer finds 5 issues
Iteration 2: Implementer fixes  → Reviewer finds 2 remaining issues
Iteration 3: Implementer fixes  → Reviewer approves (PASS)
```

### Max Iterations and Escalation

| Iteration | Action                                                          |
| --------- | --------------------------------------------------------------- |
| 1-3       | Normal review loop: fix issues, re-review                       |
| 4         | Escalate: controller reviews the remaining issues directly      |
| 5+        | Abort the loop, merge what is passing, file issues for the rest |

Loops that do not converge after 3-4 iterations usually indicate one of:

- **Ambiguous requirements**: reviewer and implementer interpret specs differently. Fix the spec, not the code.
- **Scope creep**: reviewer keeps finding new issues beyond the original scope. Constrain the review checklist.
- **Model disagreement**: two models produce different opinions on style. Pick one opinion and move on.

### Orchestrating the Loop from Main Conversation

```text
1. Spawn implementer subagent with task
2. Spawn reviewer subagent with implementer's output
3. If reviewer returns FAIL:
   a. Pass failure list back to implementer subagent
   b. Implementer fixes, returns updated output
   c. Spawn reviewer again with updated output
   d. Repeat (max 3-4 iterations)
4. If reviewer returns PASS: done
5. If max iterations reached: escalate or file remaining issues
```

## Parallel vs Sequential Dispatch

When to run agents in parallel versus chaining them sequentially.

### Decision Criteria

| Criterion        | Parallel                          | Sequential                            |
| ---------------- | --------------------------------- | ------------------------------------- |
| Task dependency  | Tasks are independent             | Task B needs Task A's output          |
| File overlap     | Agents touch different files      | Agents may edit the same files        |
| Information flow | No data passes between agents     | Output of one feeds into the next     |
| Time sensitivity | All tasks needed ASAP             | Order matters more than speed         |
| Failure impact   | One failure does not block others | Failure in step N blocks steps N+1... |

### Parallel Dispatch Patterns

Good candidates for parallel execution:

- **Independent research**: "Research auth libraries" + "Research database options" + "Research deployment platforms"
- **Batch operations**: 4 agents each processing a non-overlapping subset of files
- **Multi-module updates**: agent per module when modules do not share interfaces
- **Test + lint + typecheck**: independent validation passes on the same codebase

```text
Main conversation spawns:
  Agent 1 -> Research authentication     (independent)
  Agent 2 -> Research database           (independent)
  Agent 3 -> Research deployment         (independent)
All complete -> Main conversation synthesizes findings
```

### Sequential Dispatch Patterns

Must be sequential when:

- **Review chains**: implement -> spec review -> quality review
- **Dependent transforms**: parse data -> validate -> transform -> write
- **Iterative refinement**: draft -> review -> revise -> final review
- **Context-dependent steps**: explore codebase -> design solution -> implement

```text
Main conversation -> Agent A: explore codebase (returns architecture summary)
Main conversation -> Agent B: design solution (receives A's summary)
Main conversation -> Agent C: implement design (receives B's design)
Main conversation -> Agent D: review implementation (receives C's changes)
```

### Hybrid Dispatch

Combine parallel and sequential for complex workflows:

```text
Phase 1 (parallel):
  Agent 1 -> Research frontend options
  Agent 2 -> Research backend options

Phase 2 (sequential, uses Phase 1 results):
  Agent 3 -> Design architecture using research findings

Phase 3 (parallel):
  Agent 4 -> Implement frontend
  Agent 5 -> Implement backend

Phase 4 (sequential):
  Agent 6 -> Integration review
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
| Review loop diverges   | Escalate after 3-4 iterations; fix spec or constrain scope   |
