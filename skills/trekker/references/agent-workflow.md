---
title: Agent Workflow
description: Session management, checkpoint patterns, comment conventions, planning workflow, and search-first patterns for Trekker
tags:
  [
    workflow,
    session,
    checkpoint,
    context,
    agent,
    comments,
    memory,
    planning,
    search,
  ]
---

# Agent Workflow

## Session Start

Check for in-progress work before picking new tasks:

```bash
trekker --toon task list --status in_progress
```

If a task is found, read its comments for context recovery:

```bash
trekker --toon comment list TREK-1
trekker --toon history --entity TREK-1
```

If no in-progress tasks, find unblocked work:

```bash
trekker --toon ready
```

## Search Before Creating

Always search before creating a task to avoid duplicates:

```bash
trekker --toon search "auth middleware" --type task
```

If no match, create the task. Use single keywords for broader matches:

```bash
trekker --toon search "auth" --type task
trekker --toon search "middleware" --type task
```

## Planning Before Coding

For multi-step work, create an epic and break it into tasks before writing code:

```bash
trekker epic create -t "Implement JWT Authentication" -d "Goal: Secure all API endpoints with JWT tokens.
Success: All /api/* routes require valid token.
Approach: Add auth middleware, login/logout endpoints, bcrypt password hashing.
Files: src/middleware/, src/routes/auth/, src/models/user.ts" -p 1
```

Break down into tasks with dependencies:

```bash
trekker task create -t "Create user model" -d "Define User schema with email and password hash" -e EPIC-1 -p 1
trekker task create -t "Add auth middleware" -d "JWT verification middleware for Authorization header" -e EPIC-1 -p 1
trekker task create -t "Add login endpoint" -d "POST /auth/login with bcrypt verification" -e EPIC-1 -p 1
trekker dep add TREK-3 TREK-1
trekker dep add TREK-2 TREK-1
```

Then use `trekker ready` to work tasks in dependency order.

## Working on a Task

Claim the task, then add analysis comments as you work:

```bash
trekker task update TREK-1 -s in_progress
trekker comment add TREK-1 -a "agent" -c "Analysis: found root cause in src/auth.ts line 42"
```

## Comment Prefixes

Use structured prefixes for consistent, parseable comments:

| Prefix        | When to use                                           |
| ------------- | ----------------------------------------------------- |
| `Analysis:`   | Initial investigation findings                        |
| `Progress:`   | Incremental work updates                              |
| `Summary:`    | Final summary before completing a task                |
| `Checkpoint:` | Context preservation before session end or compaction |
| `Blocked:`    | Explain what is blocking progress                     |
| `Handoff:`    | Context for another agent picking up work             |

```bash
trekker comment add TREK-1 -a "agent" -c "Analysis: the rate limiter reads user tier from req.user, so auth middleware must run first"
trekker comment add TREK-1 -a "agent" -c "Progress: auth middleware done, starting tests"
trekker comment add TREK-1 -a "agent" -c "Blocked: waiting on TREK-4 (database migration) before integration tests"
```

## Completing a Task

Always add a `Summary:` comment before marking complete:

```bash
trekker comment add TREK-1 -a "agent" -c "Summary: implemented JWT validation in src/middleware/auth.ts, added tests in tests/auth.test.ts"
trekker task update TREK-1 -s completed
```

Check if all epic tasks are done:

```bash
trekker --toon epic show EPIC-1
```

If all tasks complete, close the epic:

```bash
trekker epic complete EPIC-1
```

## Checkpoint Comments

Before a context reset or session end, persist your progress:

```bash
trekker comment add TREK-1 -a "agent" -c "Checkpoint: completed auth middleware and unit tests. Next: integration tests for /api/login endpoint. Files: src/middleware/auth.ts, tests/auth.test.ts"
```

Include in every checkpoint:

- What was completed
- What comes next
- Which files were touched or need changes

## Status Guide

| Status        | When to use                                             |
| ------------- | ------------------------------------------------------- |
| `todo`        | Task created, not started                               |
| `in_progress` | Actively working on it                                  |
| `completed`   | Done, verified, summary comment added                   |
| `wont_fix`    | Decided this will never be done (invalid, out of scope) |
| `archived`    | Deferred, superseded, or no longer relevant             |

## Writing Effective Descriptions

### Epic Descriptions

Include goal, success criteria, approach, and key files:

```bash
trekker epic create -t "Implement JWT Authentication" -d "Goal: Secure all API endpoints with JWT tokens.
Success: All /api/* routes require valid token.
Approach: Add auth middleware, login/logout endpoints, bcrypt password hashing.
Files: src/middleware/, src/routes/auth/, src/models/user.ts" -p 1
```

### Task Descriptions

Include specific steps, files, and acceptance criteria:

```bash
trekker task create -t "Add auth middleware" -d "Create JWT verification middleware.
Steps:
1. Create src/middleware/auth.ts
2. Verify token from Authorization header
3. Attach decoded user to request
4. Return 401 for invalid/missing tokens
Accept: All /api/* routes protected, tests pass" -e EPIC-1 -p 1 --tags "auth,middleware"
```

## Dependency Workflow

Create tasks with dependencies to enforce execution order:

```bash
trekker task create -t "Create user model" -d "Define User schema with email and password hash"
trekker task create -t "Add login endpoint" -d "POST /auth/login with bcrypt verification"
trekker dep add TREK-2 TREK-1
```

Check what blocks a task:

```bash
trekker dep list TREK-2
```

## Multi-Agent Handoff

When handing work to another agent, leave a comment with full context:

```bash
trekker comment add TREK-1 -a "agent-1" -c "Handoff: auth middleware done and tested. Remaining: rate limiting (see TREK-3), CORS config needs update in src/server.ts. Blocked by: TREK-4 (database migration)."
```
