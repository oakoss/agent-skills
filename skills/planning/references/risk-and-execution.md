---
title: Risk and Execution
description: Risk assessment matrices, mitigation strategies, phased execution patterns, validation checkpoints, and time estimation guidance
tags:
  [
    risk-assessment,
    mitigation,
    feature-flags,
    rollback,
    phased-execution,
    validation,
    estimation,
    staged-rollout,
  ]
---

# Risk and Execution

## Risk Assessment

Every plan carries technical risks. Identifying them early lets you mitigate before they become blockers.

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

### Common Technical Risk Categories

| Category       | Examples                                                                 |
| -------------- | ------------------------------------------------------------------------ |
| Performance    | Slow queries, rendering bottlenecks, memory leaks, payload size          |
| Security       | Auth bypass, injection, data exposure, CORS misconfiguration             |
| Compatibility  | Browser support, API versioning, dependency conflicts, OS differences    |
| Data integrity | Migration failures, race conditions, cache inconsistency, partial writes |
| Integration    | Third-party API changes, rate limits, downtime, contract mismatches      |
| Scalability    | Connection pool exhaustion, queue backpressure, storage growth           |
| Operability    | Missing monitoring, unclear error messages, no rollback path             |

### Risk Discovery Techniques

| Technique             | When to use                          | How it works                                    |
| --------------------- | ------------------------------------ | ----------------------------------------------- |
| Pre-mortem            | Before starting implementation       | Imagine the project failed, list reasons why    |
| Assumption listing    | When requirements seem clear         | List every assumption, mark which are validated |
| Dependency audit      | When using third-party code          | Check maintenance status, license, alternatives |
| Load estimation       | When building for production traffic | Calculate expected load, identify bottlenecks   |
| Failure mode analysis | When building critical paths         | For each component, ask "what if this fails?"   |

## Mitigation Strategies

For each identified risk, define a concrete mitigation plan.

### Feature Flags

Deploy code without exposing it to users. Gradually enable for testing, then broader rollout.

```text
Risk:       New notification system causes performance regression
Mitigation: Deploy behind feature flag, enable for internal users first

Rollout plan:
  1. Deploy with flag OFF (code in production, not active)
  2. Enable for internal team (validate functionality)
  3. Enable for 5% of users (monitor performance metrics)
  4. Enable for 25%, 50%, 100% (with 24h soak at each stage)

Rollback: Disable flag immediately, no deployment needed
```

### Staged Rollout

Ship to a subset of users or environments before full deployment.

```text
Stage 1: Staging environment     -> Full integration testing
Stage 2: Canary (1 instance)     -> Monitor error rates and latency
Stage 3: 10% of production       -> Compare metrics against baseline
Stage 4: Full production         -> Continue monitoring for 48h
```

### Rollback Plans

Every deployment should have a defined rollback path before it ships.

| Change type          | Rollback strategy                                           |
| -------------------- | ----------------------------------------------------------- |
| Feature code         | Feature flag off, or revert deployment                      |
| Database migration   | Write reverse migration before deploying forward migration  |
| API contract change  | Version the API, keep old version running during transition |
| Configuration change | Store previous config, script the rollback                  |
| Data migration       | Backup before migration, validate with checksums            |
| Infrastructure       | Use infrastructure-as-code, revert to previous state        |

### Mitigation Plan Template

```text
Risk:         [Description of what could go wrong]
Probability:  [1-5]
Impact:       [1-5]
Mitigation:   [What you will do to reduce probability or impact]
Detection:    [How you will know if the risk materializes]
Response:     [What you will do if it happens despite mitigation]
Owner:        [Who is responsible for monitoring this risk]
```

## Phased Execution

Break work into shippable increments. Each phase delivers value independently.

### Designing Phases

Each phase must satisfy three criteria:

1. **Independently deployable** -- can ship without the next phase
2. **Delivers user value** -- users benefit from this phase alone
3. **Validates assumptions** -- confirms or adjusts the plan for later phases

### Phase Structure

```text
Phase 1: Foundation
  Goal:       Core data model and basic API
  Delivers:   Backend team can build against the API
  Validates:  Data model supports all planned features
  Duration:   3-5 days
  Gate:       API contract review, migration tested on staging

Phase 2: Core Feature
  Goal:       Primary user-facing functionality
  Delivers:   Users can perform the core workflow
  Validates:  UI patterns work, performance is acceptable
  Duration:   5-8 days
  Gate:       QA sign-off, performance benchmarks pass

Phase 3: Polish and Edge Cases
  Goal:       Error handling, edge cases, accessibility
  Delivers:   Production-quality experience
  Validates:  System handles failure modes gracefully
  Duration:   3-5 days
  Gate:       Accessibility audit, error monitoring configured
```

### Phase Transition Checklist

Before moving to the next phase, verify:

```text
[ ] All phase tasks completed and merged
[ ] Tests passing (unit, integration, e2e as applicable)
[ ] No regressions in existing functionality
[ ] Performance metrics within acceptable range
[ ] Documentation updated if APIs or contracts changed
[ ] Stakeholder review completed (if required)
[ ] Risks reassessed based on new information
```

## Validation Checkpoints

Defined points where you stop, verify progress, and adjust the plan.

### Checkpoint Types

| Checkpoint          | When                         | What to verify                                   |
| ------------------- | ---------------------------- | ------------------------------------------------ |
| Architecture review | After decomposition          | Approach is sound, no major blind spots          |
| Spike complete      | After prototype              | Key assumptions validated, approach confirmed    |
| API contract review | Before frontend work         | Contract is stable, edge cases handled           |
| Integration check   | After connecting systems     | Data flows correctly end-to-end                  |
| Performance gate    | Before scaling up            | Meets latency and throughput requirements        |
| Security review     | Before handling user data    | Auth, input validation, data protection in place |
| Pre-launch review   | Before production deployment | Monitoring, rollback plan, runbook ready         |

### What to Do at a Checkpoint

1. **Measure** -- collect data against success criteria defined in the plan
2. **Compare** -- compare actual progress against expected progress
3. **Decide** -- continue as planned, adjust the plan, or escalate
4. **Update** -- revise remaining phases based on what you learned

### Adjusting the Plan

Plans change as you learn more. This is expected, not a failure.

```text
Original plan:   Build custom charting library
After spike:     Custom library takes 3x longer than estimated
Adjusted plan:   Use existing charting library, customize styling only
What changed:    Spike revealed complexity in SVG rendering edge cases
Impact:          Phase 2 duration reduced from 8 days to 3 days
```

## Time Estimation

Developers consistently underestimate. Understanding why helps produce better estimates.

### Why Estimates Are Wrong

| Bias                  | Description                                         | Counter-strategy                           |
| --------------------- | --------------------------------------------------- | ------------------------------------------ |
| Optimism bias         | Assuming everything will go smoothly                | Multiply initial estimate by 1.5-2x        |
| Anchoring             | First estimate becomes the baseline                 | Estimate independently, then compare       |
| Planning fallacy      | Focusing on best case, ignoring base rates          | Look at how long similar past tasks took   |
| Scope underestimation | Missing tasks that seem small but add up            | Decompose fully, estimate each piece       |
| Integration blindness | Forgetting the cost of connecting pieces            | Add explicit integration and testing steps |
| Context switching     | Not accounting for meetings, reviews, interruptions | Assume 60-70% productive coding time       |

### Estimation Techniques

**Three-point estimation:** For each task, estimate optimistic, likely, and pessimistic durations:

```text
Task: Build notification API

Optimistic:   2 days (everything works first try)
Likely:       4 days (normal iteration and testing)
Pessimistic:  8 days (unexpected integration issues)

Expected:     (2 + 4*4 + 8) / 6 = 4.3 days
```

**Reference class forecasting:** Look at similar past work. If "add a new API endpoint" has historically taken 3-5 days, use that range regardless of how simple the new endpoint seems.

### Adding Buffers

```text
Known work estimate:        20 days
Unknown unknowns (+20-30%): 4-6 days
Integration and testing:    3-5 days
Review and iteration:       2-3 days
---
Total realistic estimate:   29-34 days
```

### Estimation Red Flags

| Red flag                                  | What it means                                 |
| ----------------------------------------- | --------------------------------------------- |
| "It should only take a day"               | Likely underestimated, probe for hidden work  |
| No time allocated for testing             | Testing will happen, planned or not           |
| Estimate assumes no interruptions         | Unrealistic, add context-switching buffer     |
| New technology with zero buffer           | Learning curve is real, add exploration time  |
| "We've done this before" without checking | Past work may have been different in key ways |
| Estimate given without decomposition      | Cannot estimate what you haven't broken down  |
