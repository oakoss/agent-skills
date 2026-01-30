# Beads Issue Tracking

Rules for using beads (`bd`) for issue tracking in this project.

## Dependency Direction (Critical)

The `bd dep add` command uses the format:

```bash
bd dep add <issue> <depends-on>
```

**Read it as:** "issue DEPENDS ON depends-on" or "depends-on BLOCKS issue"

### Mental Model: Arrows Point to Blockers

Think of dependencies as arrows pointing TO what blocks you:

```text
Task A ───depends-on───> Task B
(Task A depends on Task B)
(Task B blocks Task A)
(Task B must complete before Task A can start)
```

### Common Pattern: Epic with Tasks

An epic depends on its tasks (tasks block the epic):

```bash
# Create epic and tasks
bd create --title="Epic: Improve auth" --type=epic
bd create --title="Add OAuth support" --type=task
bd create --title="Add MFA support" --type=task

# Epic depends on tasks (tasks block epic)
bd dep add <epic-id> <task-1-id>
bd dep add <epic-id> <task-2-id>
```

Result: The epic is blocked until both tasks complete.

### Common Mistake to Avoid

```bash
# WRONG - This says "task depends on epic"
bd dep add <task-id> <epic-id>

# CORRECT - Epic depends on task
bd dep add <epic-id> <task-id>
```

### Verification

After adding dependencies, verify with:

```bash
bd show <epic-id>
```

Check the output:

- **Blocked by:** Should list the tasks (what must complete first)
- **Blocks:** Should be empty or list higher-level work

## Issue Status Flow

```text
open → in_progress → closed
```

- `bd update <id> --status=in_progress` - Claim work
- `bd close <id>` - Mark complete

## Priority Values

Use numeric priorities (0-4), NOT text like "high"/"medium"/"low":

| Value | Meaning  |
| ----- | -------- |
| 0     | Critical |
| 1     | High     |
| 2     | Medium   |
| 3     | Low      |
| 4     | Backlog  |

```bash
bd create --title="Fix crash" --priority=0
bd create --title="Nice to have" --priority=4
```

## Session Workflow

### Starting Work

```bash
bd ready           # Find unblocked work
bd show <id>       # Review details
bd update <id> --status=in_progress
```

### Ending Session

```bash
bd close <completed-ids>    # Close finished work
bd sync --from-main         # Pull beads updates
git add . && git commit     # Commit changes
```
