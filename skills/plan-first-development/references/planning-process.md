---
title: Planning Process and Iterative Refinement
description: Creating initial plans, iterative refinement with exact prompts, and achieving steady-state quality
tags: [planning, refinement, prompts, initial-plan, iteration]
---

# Planning Process and Iterative Refinement

## Why Planning Matters

- **Measure twice, cut once** -- becomes "Check your plan N times, implement once"
- A very big, complex markdown plan is still shorter than a few substantive code files
- Front-loading human input in planning enables removing yourself from implementation
- The code will be written ridiculously quickly when you start enough agents with a solid plan

## Creating the Initial Plan

Write the plan in a frontier model (GPT Pro Extended Reasoning, Opus 4.5). Include:

1. **Goals and intent** -- what you are really trying to accomplish
2. **Workflows** -- how the software works from the user's perspective
3. **Tech stack** -- be specific (e.g., "TypeScript, TanStack Start, Tailwind v4")
4. **Architecture decisions** -- high-level structure and patterns
5. **The "why"** -- the more the model understands your end goal, the better it performs

You do not even need to write the initial markdown plan yourself. You can write it with a frontier model, just explaining what you want to make.

## Iterative Refinement

Paste the entire plan into GPT Pro with Extended Reasoning and use this prompt:

```text
Carefully review this entire plan for me and come up with your best revisions
in terms of better architecture, new features, changed features, etc. to make
it better, more robust/reliable, more performant, more compelling/useful, etc.
For each proposed change, give me your detailed analysis and
rationale/justification for why it would make the project better along with the
git-diff style change versus the original plan shown below:

<PASTE YOUR EXISTING COMPLETE PLAN HERE>
```

Then integrate revisions via Claude Code:

````text
OK, now integrate these revisions to the markdown plan in-place; use ultrathink
and be meticulous. At the end, you can tell me which changes you wholeheartedly
agree with, which you somewhat agree with, and which you disagree with:

```[Pasted text from GPT Pro]```
````

### Repeat Until Steady-State

- Start fresh conversations for each round
- After 4-5 rounds, suggestions become very incremental
- You will see massive improvements from v2 to v3, continuing to the end
- This phase can take 2-3 hours for complex features -- this is normal

## Planning Workflow for New Projects

1. **Ask** 3-5 clarifying questions (auth, data, features, scope, timeline)
2. **Wait** for user answers
3. **Create** planning docs immediately
4. **Output** all docs for review
5. **Confirm** user is satisfied
6. **Suggest** creating SESSION.md and starting Phase 1

## Good Plan vs Great Plan

| Good Plan               | Great Plan                                |
| ----------------------- | ----------------------------------------- |
| Describes what to build | Explains WHY you are building it          |
| Lists features          | Details user workflows and interactions   |
| Mentions tech stack     | Justifies tech choices with tradeoffs     |
| Has tasks               | Has tasks with dependencies and rationale |
| ~500 lines              | ~3,500+ lines after refinement            |

## When to Plan vs Just Build

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

## Goal Decomposition

Breaking "build feature X" into concrete, ordered steps. Start from the desired outcome and work backward.

### The Decomposition Process

1. **Define the outcome** -- what does "done" look like from the user's perspective?
2. **Identify the layers** -- which systems, modules, or files are involved?
3. **Extract prerequisites** -- what must exist before each piece can be built?
4. **Order by dependency** -- what blocks what?
5. **Size the steps** -- each step should be completable and testable independently

### Decomposition Patterns

| Pattern        | When to use                    | How it works                                           |
| -------------- | ------------------------------ | ------------------------------------------------------ |
| Layer-by-layer | Full-stack features            | Database, then API, then UI                            |
| Outside-in     | UI-driven features             | Start with the interface, stub dependencies, fill in   |
| Inside-out     | Core logic changes             | Start with the domain model, build outward             |
| Vertical slice | Features that touch all layers | Build one thin path end-to-end, then widen             |
| Risk-first     | High-uncertainty features      | Build the riskiest piece first to validate feasibility |

## Essential Plan Elements

1. **Self-contained** -- never need external docs to understand
2. **Granular** -- complex features broken into specific subtasks
3. **Dependency-aware** -- what blocks what
4. **Justified** -- includes reasoning, not just instructions
5. **User-focused** -- each piece serves the end user
