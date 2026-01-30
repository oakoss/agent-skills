---
name: planning
description: |
  Comprehensive planning methodology and session management for software projects.
  Covers markdown plan creation, iterative refinement, multi-model blending,
  phase-based implementation docs, and cross-session progress tracking.

  Use when: starting new projects, adding major features, breaking large work
  into phases, resuming after context clears, or managing multi-phase implementations.
---

# Planning Skill

Plan-first development methodology with session tracking. Spend 80%+ of time on planning -- planning tokens are cheaper than implementation tokens, and models reason better about detailed plans that fit their context window.

## Quick Reference

| Command             | Purpose                                                                        |
| ------------------- | ------------------------------------------------------------------------------ |
| `/plan-project`     | Generate IMPLEMENTATION_PHASES.md + SESSION.md + git commit for NEW projects   |
| `/plan-feature`     | Generate phases for EXISTING projects, integrate into IMPLEMENTATION_PHASES.md |
| `/wrap-session`     | Update SESSION.md, create checkpoint commit, output summary                    |
| `/continue-session` | Load context, show summary, continue from "Next Action"                        |

| Planning Phase          | Description                                    |
| ----------------------- | ---------------------------------------------- |
| 1. Initial plan         | Write goals, intent, workflows, tech stack     |
| 2. Iterative refinement | 4-5 rounds of review until suggestions plateau |
| 3. Multi-model blend    | Get competing plans, merge best-of-all-worlds  |
| 4. Convert to beads     | Self-contained tasks with dependency structure |
| 5. Polish beads         | 6+ rounds of cross-model review                |

| Phase Type     | Scope                                 | Max Files | Duration  |
| -------------- | ------------------------------------- | --------- | --------- |
| Infrastructure | Scaffolding, build config, deployment | 3-5       | 1-3 hours |
| Database       | Migrations, schema, seed data         | 2-4       | 2-4 hours |
| API            | Routes, middleware, validation        | 3-6       | 3-6 hours |
| UI             | Components, forms, state, styling     | 4-8       | 4-8 hours |
| Integration    | Third-party services, webhooks        | 2-4       | 3-5 hours |
| Testing        | E2E tests, integration tests          | varies    | 3-6 hours |

| Session Lifecycle | Action                                                       |
| ----------------- | ------------------------------------------------------------ |
| Start             | Read SESSION.md, check "Next Action", continue               |
| Work              | Implement, verify, debug (repeat)                            |
| Wrap              | Update SESSION.md, git checkpoint, set "Next Action"         |
| Resume            | Read SESSION.md + planning docs, continue from "Next Action" |

## Common Mistakes

| Mistake                                             | Correct Pattern                                                                               |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Starting implementation before planning is complete | Spend 80%+ of time on planning; finish all refinement rounds before writing code              |
| Writing vague next actions like "continue API work" | Be specific: "Implement PATCH /api/tasks/:id in src/routes/tasks.ts:47"                       |
| Keeping SESSION.md over 200 lines                   | Collapse completed phases to summaries; reference IMPLEMENTATION_PHASES.md for details        |
| Creating phases with 10+ files                      | Auto-split into sub-phases of 5-8 files that fit in one 2-4 hour session                      |
| Single-round plan review                            | Iterate 4-5 rounds until suggestions plateau; use multi-model blending for fresh perspectives |

## Delegation

- **Explore existing codebase for architecture decisions**: Use `Explore` agent to survey file structure, patterns, and dependencies before planning
- **Execute phase implementation with verification**: Use `Task` agent to implement individual phases, run verification criteria, and create checkpoint commits
- **Design architecture and decompose into phases**: Use `Plan` agent to create IMPLEMENTATION_PHASES.md with dependency ordering and gate criteria

## References

- [Planning process and iterative refinement](references/planning-process.md)
- [Session management and context tracking](references/session-management.md)
- [Phase-based implementation planning](references/phase-planning.md)
- [Review workflows and multi-model blending](references/review-workflows.md)
- [Decision tracking and conditional documents](references/decision-tracking.md)
