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

## Subtasks

```bash
trekker subtask create TREK-1 -t "Title" [-d "desc"] [-p 0-5] [-s <status>]
trekker subtask list TREK-1
trekker subtask update TREK-2 [-t "Title"] [-d "desc"] [-p 0-5] [-s <status>]
trekker subtask delete TREK-2
```

Subtasks share the same status values and ID namespace (`TREK-n`) as tasks.

## Comments

Comments serve as external memory for agents across sessions:

```bash
trekker comment add TREK-1 -a "agent" -c "Analysis: found the root cause in auth.ts"
trekker comment list TREK-1
trekker comment update CMT-1 -c "Updated analysis"
trekker comment delete CMT-1
```

The `-a` flag sets the author name. Use it to identify which agent or user wrote the comment.

## Dependencies

```bash
trekker dep add TREK-2 TREK-1
trekker dep remove TREK-2 TREK-1
trekker dep list TREK-1
```

`dep add TREK-2 TREK-1` means "TREK-2 depends on TREK-1" — TREK-1 must complete before TREK-2 can start.

## Search

Full-text search across all entity types using FTS5:

```bash
trekker search "auth" [--type epic,task,subtask,comment] [--status <status>] [--limit 20] [--page 1]
```

Supports FTS5 query syntax for advanced matching.

Use `--rebuild-index` to rebuild the search index if results seem stale.

## History

Audit log of all creates, updates, and deletes:

```bash
trekker history [--entity TREK-1] [--type task] [--action create,update,delete] [--since 2025-01-01] [--until 2025-12-31] [--limit 50] [--page 1]
```

## Unified List

View epics, tasks, and subtasks in a single output:

```bash
trekker list [--type epic,task,subtask] [--status <statuses>] [--priority 0,1] [--since <date>] [--until <date>] [--sort priority:asc,created:desc] [--limit 50] [--page 1]
```

## Ready Tasks

Show unblocked tasks with `todo` status, ready to pick up:

```bash
trekker ready
```

Equivalent to filtering for tasks that have no incomplete dependencies and are in `todo` status.

## Token-Efficient Output

Add `--toon` immediately after `trekker` for compact output suitable for LLM contexts:

```bash
trekker --toon task list --status in_progress
trekker --toon epic show EPIC-1
trekker --toon search "auth"
```
