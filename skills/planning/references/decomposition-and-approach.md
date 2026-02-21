---
title: Decomposition and Approach
description: Goal decomposition, approach comparison, spike/prototype patterns, scope negotiation, and dependency mapping for implementation planning
tags:
  [
    decomposition,
    approach-comparison,
    decision-matrix,
    spike,
    prototype,
    scope,
    mvp,
    dependencies,
    critical-path,
  ]
---

# Decomposition and Approach

## Goal Decomposition

Breaking "build feature X" into concrete, ordered steps. Start from the desired outcome and work backward to identify what must exist.

### The Decomposition Process

1. **Define the outcome** -- what does "done" look like from the user's perspective?
2. **Identify the layers** -- which systems, modules, or files are involved?
3. **Extract prerequisites** -- what must exist before each piece can be built?
4. **Order by dependency** -- what blocks what?
5. **Size the steps** -- each step should be completable and testable independently

### Example: Adding User Notifications

Starting point: "Users should receive notifications when their order ships."

**Step 1 -- Define the outcome:**

- User sees a notification in the UI when their order status changes to "shipped"
- Notification persists until dismissed

**Step 2 -- Identify the layers:**

```text
Database        -> notifications table, migration
Backend API     -> notification creation, retrieval endpoints
Event system    -> order status change triggers notification
Frontend        -> notification display component, polling/websocket
```

**Step 3 -- Extract prerequisites:**

```text
Migration must run before API can store notifications
API must exist before frontend can fetch notifications
Event hook must exist before notifications are created automatically
```

**Step 4 -- Order by dependency:**

```text
1. Database migration (notifications table)
2. Notification API endpoints (create, list, dismiss)
3. Order status change event hook
4. Frontend notification component and data fetching
```

**Step 5 -- Size the steps:**

Each step above is independently deployable and testable. The migration can ship without the API. The API can ship without the frontend. The event hook can be tested against the API directly.

### Decomposition Patterns

| Pattern        | When to use                    | How it works                                           |
| -------------- | ------------------------------ | ------------------------------------------------------ |
| Layer-by-layer | Full-stack features            | Database, then API, then UI                            |
| Outside-in     | UI-driven features             | Start with the interface, stub dependencies, fill in   |
| Inside-out     | Core logic changes             | Start with the domain model, build outward             |
| Vertical slice | Features that touch all layers | Build one thin path end-to-end, then widen             |
| Risk-first     | High-uncertainty features      | Build the riskiest piece first to validate feasibility |

## Approach Comparison

When multiple implementation paths exist, create a decision matrix to choose systematically.

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

Higher complexity scores mean lower complexity (the scoring reflects desirability, not raw magnitude).

### When to Use Each Approach Style

| Situation                                 | Recommended approach                              |
| ----------------------------------------- | ------------------------------------------------- |
| Tight deadline, well-understood problem   | Extend existing code or use a third-party library |
| Long-term investment, core business logic | Build new, optimized for maintainability          |
| Uncertain requirements                    | Prototype first, then decide                      |
| Team lacks domain expertise               | Third-party or well-documented existing solution  |
| Performance-critical path                 | Build new with benchmarking from the start        |

### Documenting the Decision

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

### When to Spike

- The team has never used this technology/pattern before
- Performance characteristics are unknown and critical
- Integration with a third-party system is untested
- The problem has multiple viable solutions and the best one is unclear
- Data migration complexity is uncertain

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

Separating what must ship from what can ship later. Every feature has an MVP core and enhancement layers.

### The MoSCoW Method Applied

```text
Feature: User notification system

Must have (MVP):
  - Notifications created on order ship
  - Notification list visible in UI
  - Mark as read/dismiss

Should have (v1.1):
  - Email notification option
  - Notification preferences
  - Batch notification grouping

Could have (future):
  - Push notifications
  - Notification templates
  - Scheduled notifications

Won't have (out of scope):
  - Real-time websocket delivery (polling is sufficient for v1)
  - SMS notifications
  - Third-party integrations
```

### Phasing Delivery

Each phase should be independently shippable and deliver user value:

```text
Phase 1 (MVP):     Store and display notifications        -> Users see shipping updates
Phase 2 (Polish):  Preferences and email option            -> Users control notification behavior
Phase 3 (Scale):   Batching and push notifications         -> Better experience at higher volume
```

### Negotiation Tactics

| Situation                         | Tactic                                                      |
| --------------------------------- | ----------------------------------------------------------- |
| Stakeholder wants everything      | Show the phased plan, each phase delivers value             |
| Deadline is immovable             | Reduce scope to MVP, defer enhancements                     |
| Requirements are vague            | Define MVP explicitly, get sign-off before building         |
| Scope creep during implementation | Reference the original plan, create issues for new requests |

## Dependency Mapping

Understanding what blocks what prevents wasted effort and enables parallel work.

### Building a Dependency Graph

List all tasks, then for each task ask: "What must be true before I can start this?"

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

The critical path is the longest chain of dependent tasks. It determines the minimum project duration.

```text
Critical path: A -> B -> D -> F  (4 sequential steps)
Parallel path:  A -> C -> E      (3 steps, runs alongside)
```

Optimization: focus effort on critical path tasks. Delays on the parallel path have slack before they impact the timeline.

### Identifying Hidden Dependencies

Common hidden dependencies that block progress:

| Hidden dependency              | How to discover                                    |
| ------------------------------ | -------------------------------------------------- |
| Database migration approvals   | Check team deployment process early                |
| API contract changes           | Review downstream consumers before changing        |
| Shared component modifications | Search for all usages before modifying             |
| Environment configuration      | Verify staging/production parity before assuming   |
| Third-party API rate limits    | Read documentation and test in sandbox             |
| Feature flag infrastructure    | Confirm the flagging system supports your use case |
