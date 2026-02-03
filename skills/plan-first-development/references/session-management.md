---
title: Session Management and Context Tracking
description: SESSION.md structure, session lifecycle, git checkpoint format, handoff protocol, and context management across sessions
tags: [session, context, checkpoint, git, lifecycle, handoff]
---

# Session Management and Context Tracking

## SESSION.md Purpose

SESSION.md is a navigation hub in the project root (<200 lines). It references planning docs and tracks current progress. Planning docs are the reference material (rarely change); SESSION.md is the living document (updates constantly).

## Phases vs Sessions

- **Phases** (IMPLEMENTATION_PHASES.md): Units of WORK. Have verification/exit criteria. May span multiple sessions.
- **Sessions** (SESSION.md): Units of CONTEXT. Complete before clearing context. Can cover part of a phase or multiple small phases.

**Example**: Phase 3 (Tasks API) -> Session 1 (GET/POST) -> Session 2 (PATCH/DELETE) -> Session 3 (verify complete)

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

**Known Issues**: None

## Phase 4: Task UI [Pending]

**Spec**: `docs/IMPLEMENTATION_PHASES.md#phase-4`
```

## Status Icons

| Icon        | Meaning     |
| ----------- | ----------- |
| Pending     | Not started |
| In Progress | Active work |
| Complete    | Done        |
| Blocked     | Waiting     |

## Stages Within a Phase

Each phase progresses through three stages:

1. **Implementation** -- writing code for tasks
2. **Verification** -- testing against verification criteria from IMPLEMENTATION_PHASES.md
3. **Debugging** -- fixing issues found during verification

Update SESSION.md with the current stage. Example during verification:

```markdown
**Current Stage**: Verification

**Verification Progress**:

- [x] GET /api/tasks returns 200
- [x] POST /api/tasks creates task
- [ ] POST with invalid data returns 400 (currently returns 500)

**Current Issue**: Invalid data returning 500. Check src/middleware/validate.ts
```

## Session Handoff Protocol

### Ending a Session

1. Update SESSION.md with current progress and stage
2. Create a git checkpoint commit (see format below)
3. Set a concrete "Next Action" with file path, line number, and task
4. Push to remote if desired

### Resuming a Session

1. Read SESSION.md -- find "Current Phase", "Current Stage", and "Next Action"
2. Read referenced planning docs for phase spec and verification criteria
3. Check git log for recent checkpoint commits
4. Continue from the documented next action

### Context Full Mid-Phase

When context is filling up before a phase is complete:

1. Update SESSION.md with current progress
2. Create git checkpoint commit (status: In Progress)
3. Clear context
4. Read SESSION.md + planning docs
5. Continue from "Next Action"

### Phase Complete

1. Run all verification criteria from IMPLEMENTATION_PHASES.md
2. Mark phase Complete in SESSION.md
3. Create git checkpoint commit (status: Complete)
4. Move next phase from Pending to In Progress
5. Set "Next Action" for first task of next phase

## Git Checkpoint Format

```text
checkpoint: Phase [N] [Status] - [Brief Description]

Phase: [N] - [Name]
Status: [Complete/In Progress/Paused/Blocked]
Session: [What was accomplished this session]

Files Changed:
- path/to/file.ts (what changed)

Next: [Concrete next action with file path + line number]
```

### Checkpoint Examples

**Phase complete:**

```text
checkpoint: Phase 3 Complete - Tasks API

Phase: 3 - Tasks API
Status: Complete
Session: Completed all CRUD endpoints and verified functionality

Files Changed:
- src/routes/tasks.ts (all CRUD operations)
- src/lib/schemas.ts (task validation)

Next: Phase 4 - Start building Task List UI component
```

**Context full mid-phase:**

```text
checkpoint: Phase 3 In Progress - Endpoints implemented

Phase: 3 - Tasks API
Status: In Progress
Session: Implemented GET and POST endpoints, need PATCH/DELETE

Files Changed:
- src/routes/tasks.ts (GET, POST endpoints)
- src/lib/schemas.ts (task schema)

Next: Implement PATCH /api/tasks/:id in src/routes/tasks.ts:47
```

**Paused for decision:**

```text
checkpoint: Phase 3 Paused - Need design decision

Phase: 3 - Tasks API
Status: Paused
Session: Built endpoints but need to decide on tag filtering approach

Files Changed:
- src/routes/tasks.ts (basic endpoints)

Next: Decide: client-side tag filtering or SQL query parameter? Resume at src/routes/tasks.ts:89
```

### When to Checkpoint

- End of phase (status: Complete)
- Context getting full mid-phase (status: In Progress)
- Pausing for user decision (status: Paused)
- Hitting a blocker (status: Blocked)

### Creating a Checkpoint

```bash
git add path/to/changed/files
git commit -m "$(cat <<'EOF'
checkpoint: Phase 3 In Progress - Endpoints implemented

Phase: 3 - Tasks API
Status: In Progress
Session: Implemented GET and POST endpoints

Files Changed:
- src/routes/tasks.ts (GET, POST endpoints)

Next: Implement PATCH /api/tasks/:id in src/routes/tasks.ts:47
EOF
)"
```

After committing, update SESSION.md with the checkpoint commit hash. This means SESSION.md is always uncommitted when resuming -- this is by design.

## Expected Uncommitted Files

**Normal (no warning needed):**

- **SESSION.md** -- checkpoint hash updated post-commit, always uncommitted between sessions
- **CLAUDE.md** -- often updated during dev

**Warning triggers (unexpected uncommitted):**

- Source files (.ts, .tsx, .js)
- Config files (vite.config.ts, wrangler.jsonc)
- Planning docs (IMPLEMENTATION_PHASES.md, ARCHITECTURE.md)
- New untracked files

## SESSION.md Guidelines

**Do:**

- Collapse completed phases to 2-3 lines (date, checkpoint, summary)
- Use concrete "Next Action" with file path + line number + task
- Reference planning docs instead of duplicating content
- Checkpoint at phase end or when context is full

**Do not:**

- Copy code into SESSION.md (reference file paths instead)
- Duplicate IMPLEMENTATION_PHASES.md content (link with anchors)
- Use vague actions like "continue API work"
- Let SESSION.md exceed 200 lines

## Creating SESSION.md for a New Project

After generating IMPLEMENTATION_PHASES.md:

1. Read IMPLEMENTATION_PHASES.md to extract phase names and types
2. Create SESSION.md in project root
3. Set Phase 1 as In Progress, all others as Pending
4. Expand Phase 1 with task checklist from IMPLEMENTATION_PHASES.md
5. Set concrete "Next Action" for the first task
6. Commit SESSION.md as part of initial project setup
