---
title: Phase-Based Implementation Planning
description: Structuring implementation into phases with verification criteria, file-level detail, and auto-split rules
tags: [phases, implementation, verification, file-map, auto-split]
---

# Phase-Based Implementation Planning

## Phase Structure

Generate structured docs starting with IMPLEMENTATION_PHASES.md. Every phase MUST have:

1. **Type** -- Infrastructure / Database / API / UI / Integration / Testing
2. **Estimated duration** -- in hours
3. **Files** -- specific files created or modified
4. **Task list** -- ordered checklist with clear actions
5. **Verification criteria** -- checkbox list of tests to confirm phase works
6. **Exit criteria** -- clear definition of "done"

## Context-Safe Sizing Rules

- Max 5-8 files touched per phase
- Max 2 cross-phase dependencies
- Implementation + verification + fixes should fit in one 2-4 hour session

## Auto-Split When Violated

```text
Phase 4 "Complete User Management" is too large (12 files, 8-10 hours).

Suggested split:
- Phase 4a: User CRUD API (5 files, 4 hours)
- Phase 4b: User Profile UI (6 files, 5 hours)
```

## Verification Requirements by Type

- **API**: Test all HTTP status codes (200, 400, 401, 404, 500)
- **UI**: Test user flows, form validation, error states
- **Database**: Test CRUD, constraints, relationships
- **Integration**: Test service connectivity, webhooks, error handling

## Logical Phase Order

Infrastructure -> Database -> API -> UI -> Integration -> Testing

## File-Level Detail in Phases

Include for API, UI, and Integration phases:

**File map:**

```markdown
- `src/routes/tasks.ts` (~150 lines) - CRUD endpoints
  - Purpose, key exports, dependencies, used by
- `src/lib/schemas.ts` (~80 lines) - Validation schemas
```

**Data flow (Mermaid):**

```markdown
sequenceDiagram
Client->>Worker: POST /api/tasks
Worker->>Auth: authenticateUser()
Worker->>D1: INSERT INTO tasks
D1->>Worker: task record
Worker->>Client: 201 + JSON
```

**Dependencies and gotchas:**

```markdown
**Internal**: auth.ts, schemas.ts, D1 binding
**External**: zod, hono, @clerk/backend
**Gotchas**: Ownership checks on PATCH/DELETE, pagination (50 max), soft delete
```

## Approach Comparison

When multiple implementation paths exist, use a decision matrix to choose systematically.

### Decision Matrix

Score each approach (1-5) against weighted criteria:

```text
Criteria (weight)        | Approach A: New Service | Approach B: Extend Existing | Approach C: Third-Party
-------------------------|------------------------|-----------------------------|------------------------
Complexity (3)           | 2                      | 4                           | 5
Maintainability (3)      | 5                      | 3                           | 2
Performance (2)          | 4                      | 3                           | 4
Team familiarity (2)     | 2                      | 5                           | 3
Time to ship (2)         | 2                      | 4                           | 5
Operational cost (1)     | 2                      | 5                           | 3
-------------------------|------------------------|-----------------------------|------------------------
Weighted total           | 40                     | 48                          | 46
```

Higher complexity scores mean lower complexity (scoring reflects desirability, not raw magnitude).

Record the decision so future developers understand the trade-offs:

```text
Decision: Extend the existing notification service (Approach B)
Rationale: Team familiarity is high, shipping timeline is tight,
           and the existing service handles 80% of the requirements.
Trade-offs accepted: Maintainability score is lower; plan a refactor
                     if notification types exceed 5.
Revisit trigger: If latency exceeds 200ms p99 or notification types > 5.
```

## Spike / Prototype Pattern

A spike is a timeboxed experiment to answer a specific technical question before committing to an approach.

### Spike Structure

```text
Question:    Can we render 10,000 rows with virtual scrolling under 16ms per frame?
Timebox:     4 hours
Approach:    Build minimal prototype with react-window, measure with React Profiler
Success:     < 16ms render, < 50MB memory at 10k rows
Failure:     Exceeds thresholds -> evaluate canvas-based rendering
Deliverable: Written summary with measurements, not production code
```

### Spike Rules

1. **Timebox strictly** -- if the timebox expires without an answer, that itself is a finding
2. **Answer one question** -- resist scope creep during the spike
3. **Throw away the code** -- spike code is for learning, not shipping
4. **Document the result** -- measurements, findings, and recommendation
5. **Decide immediately** -- the spike should unblock a decision, not create more questions

## Scope Negotiation

### MoSCoW Prioritization

```text
Must have (MVP):
  - Core functionality required for launch
  - Without these, the feature has no value

Should have (v1.1):
  - Important but not blocking launch
  - First enhancements after MVP ships

Could have (future):
  - Nice-to-have improvements
  - Build only after must/should are stable

Won't have (out of scope):
  - Explicitly excluded from this effort
  - Prevents scope creep by naming what is deferred
```

Each phase should be independently shippable and deliver user value.

## Dependency Mapping

Understanding what blocks what prevents wasted effort and enables parallel work.

### Building a Dependency Graph

List all tasks, then for each ask: "What must be true before I can start this?"

```text
Task                          | Depends on           | Blocks
------------------------------|----------------------|------------------
A. Database migration         | Nothing              | B, C
B. Notification API           | A                    | D, E
C. Event hook integration     | A                    | E
D. Frontend component         | B                    | F
E. End-to-end test            | B, C                 | Nothing
F. UI integration test        | D                    | Nothing
```

### Critical Path

The critical path is the longest chain of dependent tasks -- it determines the minimum project duration.

```text
Critical path: A -> B -> D -> F  (4 sequential steps)
Parallel path:  A -> C -> E      (3 steps, runs alongside)
```

Focus effort on critical path tasks. Delays on the parallel path have slack before they impact the timeline.

## Risk Assessment

### Probability x Impact Matrix

Rate each risk on two axes (1-5 scale), then multiply for a risk score:

```text
Risk                              | Probability | Impact | Score | Priority
----------------------------------|-------------|--------|-------|----------
API response too slow for UI      | 3           | 4      | 12    | High
Migration corrupts existing data  | 2           | 5      | 10    | High
Third-party SDK breaks on update  | 3           | 3      | 9     | Medium
New component causes layout shift | 4           | 2      | 8     | Medium
Feature flag system has edge case | 2           | 2      | 4     | Low
```

Focus mitigation effort on high-score risks first.

### Mitigation Strategies

| Strategy       | When to use                               | Rollback approach                    |
| -------------- | ----------------------------------------- | ------------------------------------ |
| Feature flags  | New features that may cause regression    | Disable flag, no deployment needed   |
| Staged rollout | Any production deployment                 | Stop rollout, revert canary instance |
| Rollback plan  | Database migrations, API contract changes | Reverse migration or API versioning  |

### Time Estimation

**Three-point estimation:** For each task, estimate optimistic, likely, and pessimistic durations:

```text
Task: Build notification API

Optimistic:   2 days (everything works first try)
Likely:       4 days (normal iteration and testing)
Pessimistic:  8 days (unexpected integration issues)

Expected:     (2 + 4*4 + 8) / 6 = 4.3 days
```

**Reference class forecasting:** Look at similar past work. If "add a new API endpoint" has historically taken 3-5 days, use that range regardless of how simple the new endpoint seems.

## Status Icons

| Icon        | Meaning               |
| ----------- | --------------------- |
| Pending     | Not started           |
| In Progress | Active work           |
| Complete    | Done                  |
| Blocked     | Waiting on dependency |
