---
name: planning
description: |
  Research-driven implementation planning for complex software tasks. Covers goal decomposition, approach selection, risk assessment, dependency mapping, and phased execution strategies.

  Use when breaking down complex features, choosing between implementation approaches, planning multi-file changes, assessing technical risks, or designing phased rollout strategies.
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Planning

## Overview

Planning is a structured process for breaking down complex software tasks into concrete, sequenced steps before writing code. It covers goal decomposition, approach comparison, risk assessment, dependency mapping, and phased execution.

**When to use:** Multi-file features, architectural changes, unfamiliar codebases, tasks with multiple viable approaches, work that spans multiple sessions, or anything where the wrong approach wastes significant time.

**When NOT to use:** Single-file fixes, well-understood patterns, trivial bug fixes, one-line changes, or tasks where the implementation path is obvious.

## Quick Reference

| Pattern             | Purpose                                    | Key Points                                                     |
| ------------------- | ------------------------------------------ | -------------------------------------------------------------- |
| Goal decomposition  | Break vague requirements into steps        | Start from desired outcome, work backward to concrete tasks    |
| Approach comparison | Choose between implementation options      | Score on complexity, maintainability, performance, familiarity |
| Risk matrix         | Identify what could go wrong               | Probability x impact, focus on high-risk items first           |
| Dependency mapping  | Find what blocks what                      | Identify critical path, parallelize independent work           |
| Spike/prototype     | Validate assumptions before committing     | Timebox strictly, answer a specific question, then discard     |
| Phased execution    | Ship incrementally with value at each step | Each phase is independently deployable and testable            |
| Scope negotiation   | Separate MVP from nice-to-have             | Define what ships first, defer enhancements explicitly         |

## Decision Trees

**When to plan vs just build:**

| Signal                                  | Action     |
| --------------------------------------- | ---------- |
| Touches 1-2 files, clear pattern exists | Just build |
| Touches 3+ files or modules             | Plan first |
| Unfamiliar codebase or library          | Plan first |
| Multiple viable approaches              | Plan first |
| Architectural or data model changes     | Plan first |
| Performance-critical path               | Plan first |
| Well-understood bug fix                 | Just build |
| Refactor with existing test coverage    | Light plan |
| Cross-team or cross-service changes     | Plan first |
| Reversible change with feature flag     | Light plan |

**Planning depth by complexity:**

| Complexity | Planning depth                                       |
| ---------- | ---------------------------------------------------- |
| Low        | Mental model, no written plan needed                 |
| Medium     | Quick decomposition, list dependencies               |
| High       | Full decomposition, approach comparison, risk matrix |
| Very high  | Spike first, then full plan with phased execution    |

## Common Mistakes

| Mistake                                    | Correct Pattern                                                |
| ------------------------------------------ | -------------------------------------------------------------- |
| Jumping to code without reading            | Explore existing code first, understand patterns and contracts |
| Planning at line-level granularity         | Plan at task level, let implementation details emerge          |
| Not validating assumptions early           | Run a spike or prototype for the riskiest assumption first     |
| Ignoring existing codebase patterns        | Search for prior art, follow established conventions           |
| Over-planning simple tasks                 | Match planning depth to complexity, skip for trivial work      |
| Planning without time constraints          | Timebox planning itself, set a deadline to start building      |
| Treating the plan as immutable             | Revisit and adjust the plan as new information emerges         |
| Skipping dependency identification         | Map blockers before starting, avoid blocked-path surprises     |
| Planning in isolation                      | Validate approach with stakeholders before deep investment     |
| Estimating without accounting for unknowns | Add buffers for integration, testing, and unforeseen issues    |

## Delegation

- **Codebase research**: Use `Explore` agent to understand existing patterns, find prior art, and map dependencies
- **Implementation work**: Use `Task` agent to execute planned steps
- **Architecture decisions**: Use `Plan` agent for high-level design choices

> If the `vitest-testing` skill is available, delegate test strategy planning to it.
> If the `typescript-eslint` skill is available, delegate linting and code quality checks to it.

## References

- [Decomposition, approach comparison, and scope negotiation](references/decomposition-and-approach.md)
- [Risk assessment, mitigation, and phased execution](references/risk-and-execution.md)
