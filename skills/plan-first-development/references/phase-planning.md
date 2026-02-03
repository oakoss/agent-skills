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

## Status Icons

| Icon        | Meaning               |
| ----------- | --------------------- |
| Pending     | Not started           |
| In Progress | Active work           |
| Complete    | Done                  |
| Blocked     | Waiting on dependency |
