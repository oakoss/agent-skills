---
title: Commands
description: Complete CLI command reference for Trekker epics, tasks, subtasks, comments, dependencies, search, and history
tags:
  [
    cli,
    commands,
    epic,
    task,
    subtask,
    comment,
    dependency,
    search,
    history,
    list,
  ]
---

# Commands

## Initialization

```bash
trekker init
```

Creates `.trekker/trekker.db` in the current directory.

```bash
trekker wipe -y
```

Destroys all data. Use `-y` to skip confirmation.

## Epics

```bash
trekker epic create -t "Title" [-d "description"] [-p 0-5] [-s <status>]
trekker epic list [--status <status>]
trekker epic show EPIC-1
trekker epic update EPIC-1 [-t "Title"] [-d "desc"] [-p 0-5] [-s <status>]
trekker epic complete EPIC-1
trekker epic delete EPIC-1
```

`epic complete` sets the epic to `completed` and archives all child tasks and subtasks.

Epic statuses: `todo`, `in_progress`, `completed`, `archived`

Common usage:

```bash
trekker epic create -t "Implement user auth" -d "JWT-based auth for all API endpoints" -p 1
trekker --toon epic list
trekker --toon epic list --status in_progress
trekker --toon epic show EPIC-1
trekker epic update EPIC-1 -s in_progress
trekker epic update EPIC-1 -d "Updated scope: OAuth2 + JWT for API endpoints"
trekker epic complete EPIC-1
```

## Tasks

```bash
trekker task create -t "Title" [-d "desc"] [-p 0-5] [-s <status>] [-e EPIC-1] [--tags "a,b"]
trekker task list [--status <status>] [--epic EPIC-1]
trekker task show TREK-1
trekker task update TREK-1 [-t "Title"] [-d "desc"] [-p 0-5] [-s <status>] [--tags "a,b"] [-e EPIC-1] [--no-epic]
trekker task delete TREK-1
```

Task statuses: `todo`, `in_progress`, `completed`, `wont_fix`, `archived`

Use `--no-epic` to unlink a task from its epic.

Common usage:

```bash
trekker task create -t "Add login endpoint" -d "POST /auth/login with bcrypt" -e EPIC-1 -p 1 --tags "auth,api"
trekker --toon task list
trekker --toon task list --status todo
trekker --toon task list --status in_progress
trekker --toon task list --epic EPIC-1
trekker --toon task show TREK-1
trekker task update TREK-1 -s in_progress
trekker task update TREK-1 -s completed
trekker task update TREK-1 -p 0 --tags "auth,api,urgent"
trekker task update TREK-1 -d "Updated: also handle refresh tokens"
trekker task update TREK-1 -e EPIC-2
trekker task update TREK-1 --no-epic
trekker task update TREK-1 -s wont_fix
trekker task update TREK-1 -s archived
```

## Subtasks

```bash
trekker subtask create TREK-1 -t "Title" [-d "desc"] [-p 0-5] [-s <status>]
trekker subtask list TREK-1
trekker subtask update TREK-2 [-t "Title"] [-d "desc"] [-p 0-5] [-s <status>]
trekker subtask delete TREK-2
```

Subtasks share the same status values and ID namespace (`TREK-n`) as tasks.

Common usage:

```bash
trekker subtask create TREK-1 -t "Write unit tests" -d "Cover login and logout flows" -p 2
trekker subtask create TREK-1 -t "Add input validation" -p 1
trekker --toon subtask list TREK-1
trekker subtask update TREK-3 -s in_progress
trekker subtask update TREK-3 -s completed
```

## Comments

Comments serve as external memory for agents across sessions:

```bash
trekker comment add TREK-1 -a "agent" -c "Analysis: found the root cause in auth.ts"
trekker comment list TREK-1
trekker comment update CMT-1 -c "Updated analysis"
trekker comment delete CMT-1
```

The `-a` flag sets the author name. Use it to identify which agent or user wrote the comment.

Common usage:

```bash
trekker comment add TREK-1 -a "agent" -c "Analysis: login fails because token expiry is not checked"
trekker comment add TREK-1 -a "agent" -c "Progress: added token validation, working on refresh flow"
trekker comment add TREK-1 -a "agent" -c "Blocked: waiting on TREK-2 (user model) before integration tests"
trekker comment add TREK-1 -a "agent" -c "Summary: implemented login endpoint in src/routes/auth.ts, tests in tests/auth.test.ts"
trekker comment add TREK-1 -a "agent" -c "Checkpoint: done login/logout. Next: refresh tokens. Files: src/routes/auth.ts"
trekker comment add TREK-1 -a "agent" -c "Handoff: auth middleware complete. Remaining: rate limiting (TREK-5)"
trekker --toon comment list TREK-1
```

## Dependencies

```bash
trekker dep add TREK-2 TREK-1
trekker dep remove TREK-2 TREK-1
trekker dep list TREK-1
```

`dep add TREK-2 TREK-1` means "TREK-2 depends on TREK-1" — TREK-1 must complete before TREK-2 can start.

Common usage:

```bash
trekker dep add TREK-3 TREK-1
trekker dep add TREK-3 TREK-2
trekker --toon dep list TREK-3
trekker dep remove TREK-3 TREK-2
```

## Search

Full-text search across all entity types using FTS5:

```bash
trekker search "auth" [--type epic,task,subtask,comment] [--status <status>] [--limit 20] [--page 1]
```

Supports FTS5 query syntax for advanced matching.

Use `--rebuild-index` to rebuild the search index if results seem stale.

Common usage:

```bash
trekker --toon search "auth"
trekker --toon search "auth" --type task
trekker --toon search "auth" --type task --status todo
trekker --toon search "login" --type task,subtask
trekker --toon search "middleware" --type comment
trekker --toon search "auth" --limit 10 --page 1
trekker search --rebuild-index "auth"
```

## History

Audit log of all creates, updates, and deletes:

```bash
trekker history [--entity TREK-1] [--type task] [--action create,update,delete] [--since 2025-01-01] [--until 2025-12-31] [--limit 50] [--page 1]
```

Common usage:

```bash
trekker --toon history
trekker --toon history --entity TREK-1
trekker --toon history --entity EPIC-1
trekker --toon history --type task
trekker --toon history --type task --action update
trekker --toon history --action create --since 2025-01-15
trekker --toon history --type comment --entity TREK-1
trekker --toon history --limit 20 --page 1
```

## Unified List

View epics, tasks, and subtasks in a single output:

```bash
trekker list [--type epic,task,subtask] [--status <statuses>] [--priority 0,1] [--since <date>] [--until <date>] [--sort priority:asc,created:desc] [--limit 50] [--page 1]
```

Common usage:

```bash
trekker --toon list
trekker --toon list --status in_progress
trekker --toon list --status todo,in_progress
trekker --toon list --type task --status todo
trekker --toon list --type epic
trekker --toon list --priority 0,1
trekker --toon list --type task --priority 0 --status todo
trekker --toon list --sort priority:asc
trekker --toon list --sort created:desc --limit 10
trekker --toon list --since 2025-01-01 --until 2025-02-01
trekker --toon list --type task,subtask --status completed
```

## Ready Tasks

Show unblocked tasks with `todo` status, ready to pick up:

```bash
trekker ready
```

Equivalent to filtering for tasks that have no incomplete dependencies and are in `todo` status.

Common usage:

```bash
trekker --toon ready
```

## Global Options

**`--toon`** — Add immediately after `trekker` for compact, token-efficient output suitable for LLM contexts:

```bash
trekker --toon task list --status in_progress
trekker --toon epic show EPIC-1
trekker --toon search "auth"
trekker --toon list --status todo
trekker --toon history --entity TREK-1
trekker --toon comment list TREK-1
trekker --toon ready
```

**Pagination** — Commands that return lists (`list`, `search`, `history`) support `--limit` and `--page`. There is no `--offset` flag.

```bash
trekker list --limit 20 --page 1
trekker list --limit 20 --page 2
trekker search "auth" --limit 10 --page 3
trekker history --limit 20 --page 2
```
