---
title: Session Management and Context Tracking
description: SESSION.md structure, session lifecycle, git checkpoints, and context management across sessions
tags: [session, context, checkpoint, git, lifecycle]
---

# Session Management and Context Tracking

## SESSION.md Purpose

SESSION.md is a navigation hub in the project root (<200 lines). It references planning docs and tracks current progress.

## Phases vs Sessions

- **Phases** (IMPLEMENTATION_PHASES.md): Units of WORK. Have verification/exit criteria. May span multiple sessions.
- **Sessions** (SESSION.md): Units of CONTEXT. Complete before clearing context. Can cover part of a phase or multiple small phases.

## Stages Within a Phase

1. **Implementation** -- writing code
2. **Verification** -- testing against criteria
3. **Debugging** -- fixing issues

## SESSION.md Template

```markdown
# Session State

**Current Phase**: Phase 3
**Current Stage**: Implementation
**Last Checkpoint**: abc1234 (2025-10-23)
**Planning Docs**: `docs/IMPLEMENTATION_PHASES.md`, `docs/ARCHITECTURE.md`

---

## Phase 1: Setup [Complete]

**Completed**: 2025-10-15 | **Checkpoint**: abc1234
**Summary**: Vite + React + Tailwind v4 + D1 binding

## Phase 2: Database [Complete]

**Completed**: 2025-10-18 | **Checkpoint**: def5678
**Summary**: D1 schema + migrations + seed data

## Phase 3: Tasks API [In Progress]

**Type**: API | **Started**: 2025-10-23
**Spec**: `docs/IMPLEMENTATION_PHASES.md#phase-3`

**Progress**:

- [x] GET /api/tasks endpoint (commit: ghi9012)
- [x] POST /api/tasks endpoint (commit: jkl3456)
- [ ] PATCH /api/tasks/:id <-- CURRENT
- [ ] DELETE /api/tasks/:id
- [ ] Verify all endpoints

**Next Action**: Implement PATCH /api/tasks/:id in src/routes/tasks.ts:47

**Key Files**: `src/routes/tasks.ts`, `src/lib/schemas.ts`

## Phase 4: Task UI [Pending]

**Spec**: `docs/IMPLEMENTATION_PHASES.md#phase-4`
```

## Git Checkpoints

```text
checkpoint: Phase [N] [Status] - [Brief Description]

Phase: [N] - [Name]
Status: [Complete/In Progress/Paused]
Session: [What was accomplished this session]

Files Changed:
- path/to/file.ts (what changed)

Next: [Concrete next action]
```

**Expected uncommitted files** (no warning needed):

- **SESSION.md** -- checkpoint hash updated post-commit, always uncommitted between sessions (by design)
- **CLAUDE.md** -- often updated during dev

**Warning triggers** (unexpected uncommitted):

- Source files (.ts, .tsx, .js)
- Config files (vite.config.ts, wrangler.jsonc)
- Planning docs (IMPLEMENTATION_PHASES.md, ARCHITECTURE.md)

## Context Management

**Context full mid-phase**: Update SESSION.md -> checkpoint -> clear context -> read SESSION.md + planning docs -> continue from "Next Action"

**Phase complete**: Check verification criteria -> mark complete -> checkpoint -> start next phase

**Troubleshooting**: Update stage to "Debugging" -> document "Current Issue" -> when fixed, return to Verification or Implementation
