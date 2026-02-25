---
title: Review Workflows and Multi-Model Blending
description: Multi-model blending technique with exact prompts for creating superior hybrid plans
tags: [review, multi-model, blending, prompts, refinement]
---

# Review Workflows and Multi-Model Blending

## Multi-Model Blending

Get competing plans from multiple frontier models, then use a final arbiter to blend:

```text
I asked 3 competing LLMs to do the exact same thing and they came up with
pretty different plans which you can read below. I want you to REALLY carefully
analyze their plans with an open mind and be intellectually honest about what
they did that's better than your plan. Then I want you to come up with the best
possible revisions to your plan that artfully and skillfully blends the "best
of all worlds" to create a true, ultimate, superior hybrid version of the plan
that best achieves our stated goals and will work the best in real-world
practice; you should provide me with a complete series of git-diff style changes
to your original plan to turn it into the new, enhanced plan that integrates the
best of all the plans with every good idea included:

[Paste competing plans here]
```

## When to Blend

- After initial plan is refined (4-5 rounds)
- When different models suggest fundamentally different architectures
- For critical technical decisions where multiple perspectives add value

## Anti-Patterns

| Anti-Pattern                                       | Why It Fails                                 | Instead                                               |
| -------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------- |
| Starting implementation too early                  | 3 hours of planning saves 30 hours of rework | Finish all planning phases first                      |
| Single-round review                                | Improvements continue through round 6+       | Iterate until suggestions plateau                     |
| Skeleton-first coding                              | Loses big-picture coherence                  | One thorough plan, then implement                     |
| Vague next actions                                 | "Continue API" gives no direction            | "Implement POST /api/tasks in src/routes/tasks.ts:47" |
| SESSION.md over 200 lines                          | Defeats the purpose of quick reference       | Collapse completed phases, reference planning docs    |
| Copying code into SESSION.md                       | Bloats the file, goes stale                  | Reference file paths and line numbers                 |
| Duplicating IMPLEMENTATION_PHASES.md in SESSION.md | Maintenance burden, drift                    | Link to sections with anchors                         |
| Phases with 10+ files                              | Exceeds context, causes errors               | Auto-split into sub-phases                            |
| No verification criteria                           | "It works" is not testable                   | Specific status codes, user flows, constraints        |
| Orphan TODOs in plans                              | Never get addressed                          | Every TODO needs a ticket reference                   |
| Planning before prototyping                        | Unknown frameworks need spikes               | Build a spike first for new tech, then plan           |

## Troubleshooting

### Context Cleared Mid-Phase

1. Read SESSION.md -- find "Next Action"
2. Read referenced planning docs for phase spec
3. Check git log for recent checkpoint commits
4. Continue from the documented next action

### Phase Verification Failing

1. Update SESSION.md stage to "Debugging"
2. Document the specific failure in "Current Issue"
3. Fix the issue
4. Return to Verification stage and continue checking criteria

### Plan Feels Incomplete After Refinement

- Run additional review rounds (improvements continue past round 5)
- Try multi-model blending for fresh perspectives
- Check: Does the plan explain WHY, not just WHAT?
- Check: Are user workflows documented end-to-end?

### Phase Too Large to Complete in One Session

- Split using auto-split logic (max 5-8 files, 2-4 hours)
- Create sub-phases (4a, 4b) with their own verification criteria
- Each sub-phase must be independently verifiable
