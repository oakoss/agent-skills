---
name: trekker
description: |
  Trekker CLI task tracking for AI coding agents. Covers epics, tasks, subtasks, dependencies, comments, full-text search, history audit log, and kanban-style workflow with local SQLite storage.

  Use when creating task trackers, managing agent work sessions, tracking epics and dependencies, or implementing local-first issue tracking with Trekker CLI.
license: MIT
metadata:
  author: oakoss
  version: '1.0'
  runtime: bun
  storage: .trekker/trekker.db
---

# Trekker

## Overview

Trekker is a CLI-based issue tracker designed for AI coding agents. It stores data locally in SQLite (`.trekker/trekker.db`) and supports epics, tasks, subtasks, dependencies, comments, full-text search, and an audit history log. Use `--toon` on any command for token-efficient output.

**When to use:** Agent work session tracking, local task management, kanban-style workflows, dependency-aware task ordering, checkpoint comments for context persistence across sessions.

**When NOT to use:** Team-wide project management (use GitHub Issues/Linear), real-time collaboration, remote-first workflows, CI/CD-integrated issue tracking.

## Quick Reference

| Pattern         | Command                                              | Key Points                               |
| --------------- | ---------------------------------------------------- | ---------------------------------------- |
| Initialize      | `trekker init`                                       | Creates `.trekker/` in current directory |
| Create epic     | `trekker epic create -t "Title" -d "desc" -p 2`      | Groups related tasks                     |
| Create task     | `trekker task create -t "Title" -d "desc" -e EPIC-1` | `-e` links to epic                       |
| Create subtask  | `trekker subtask create TREK-1 -t "Title"`           | Requires parent task ID                  |
| Start work      | `trekker task update TREK-1 -s in_progress`          | Always set before working                |
| Complete task   | `trekker task update TREK-1 -s completed`            | Add summary comment first                |
| Complete epic   | `trekker epic complete EPIC-1`                       | Archives all child tasks                 |
| Add dependency  | `trekker dep add TREK-2 TREK-1`                      | TREK-2 depends on TREK-1                 |
| Add comment     | `trekker comment add TREK-1 -a "agent" -c "content"` | External memory for agents               |
| Search          | `trekker search "query" --type task`                 | FTS5 full-text search                    |
| Audit history   | `trekker history --entity TREK-1`                    | All changes to an entity                 |
| Unified list    | `trekker list --status in_progress`                  | Epics, tasks, and subtasks               |
| Ready tasks     | `trekker ready`                                      | Unblocked todo tasks, ready to start     |
| Token-efficient | `trekker --toon task list`                           | Compact output format                    |

## Status Values

| Entity           | Statuses                                                   |
| ---------------- | ---------------------------------------------------------- |
| Tasks / Subtasks | `todo`, `in_progress`, `completed`, `wont_fix`, `archived` |
| Epics            | `todo`, `in_progress`, `completed`, `archived`             |

## Priority Scale

| Value | Meaning          |
| ----- | ---------------- |
| 0     | Critical         |
| 1     | High             |
| 2     | Medium (default) |
| 3     | Low              |
| 4     | Backlog          |
| 5     | Someday          |

## Common Mistakes

| Mistake                                             | Correct Pattern                                                               |
| --------------------------------------------------- | ----------------------------------------------------------------------------- |
| Creating task without searching first               | Always `trekker search "keyword"` before creating to avoid duplicates         |
| Completing task without summary comment             | Add `Summary:` comment with what was done and which files changed             |
| Not using `--toon` flag                             | Always use `--toon` to reduce token usage in agent contexts                   |
| Forgetting to set `in_progress` before working      | Set status before starting so other agents know the task is claimed           |
| Using `epic delete` to finish an epic               | Use `trekker epic complete EPIC-n` to complete and archive all tasks          |
| Dependency direction reversed                       | `dep add TREK-2 TREK-1` means TREK-2 depends on TREK-1 (TREK-1 blocks TREK-2) |
| Not adding checkpoint comments before context reset | Add `Checkpoint:` comment with done items, next steps, and affected files     |
| Coding before planning                              | Create epic and break into tasks with dependencies before writing code        |
| Vague task descriptions                             | Include implementation steps, files to modify, and acceptance criteria        |
| Searching without type filter                       | Use `--type task` or `--status in_progress` to narrow results                 |
| Using `wont_fix` when task is just deferred         | `wont_fix` = will never do; use `archived` for deferred or superseded work    |

## Delegation

- **Task discovery and prioritization**: Use `Explore` agent to scan codebase and identify work
- **Multi-task execution**: Use `Task` agent for parallel subtask completion

## References

- [Agent workflow and session management](references/agent-workflow.md)
- [Commands and CLI usage](references/commands.md)
