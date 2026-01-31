---
title: Agent Integration
description: bd CLI commands, robot mode for agents, Agent Mail integration, and test coverage bead creation
tags: [bd, bv, cli, robot-mode, agent-mail, test-coverage, swarm]
---

# Agent Integration

## bd CLI Basics

```bash
bd init

bd create "Implement user authentication" -t feature -p 1

bd depend BD-123 BD-100  # BD-123 depends on BD-100

bd update BD-123 --status in_progress

bd close BD-123 --reason "Completed and tested"

bd ready --json
```

Key commands:

| Command                                 | Purpose                                  |
| --------------------------------------- | ---------------------------------------- |
| `bd init`                               | Initialize beads in a project            |
| `bd create "title" -t type -p priority` | Create a new bead                        |
| `bd depend <issue> <depends-on>`        | Declare that issue depends on depends-on |
| `bd update <id> --status <status>`      | Change bead status                       |
| `bd close <id> --reason "reason"`       | Close a completed bead                   |
| `bd ready --json`                       | List beads with no unresolved blockers   |

## Robot Mode for Agents

**Never run bare `bv`** -- it launches an interactive TUI that blocks agents. Always use `--robot-*` flags.

```bash
bv --robot-triage

bv --robot-next

bv --robot-plan

bv --robot-insights
```

| Flag               | Output                                        |
| ------------------ | --------------------------------------------- |
| `--robot-triage`   | Triage recommendations for all open beads     |
| `--robot-next`     | The single highest-priority unblocked bead    |
| `--robot-plan`     | Parallel execution tracks for swarm agents    |
| `--robot-insights` | Graph analysis: PageRank, bottlenecks, cycles |

Check for cycles before implementation:

```bash
bv --robot-insights | jq '.Cycles'
```

An empty result means the dependency graph is clean.

## Agent Mail Integration

When multiple agents work on beads in parallel, use Agent Mail conventions to coordinate.

### Conventions

- Use the bead ID as the Mail `thread_id`: `send_message(..., thread_id="bd-123")`
- Prefix subjects with the bead ID: `[bd-123] Starting auth refactor`
- Include the bead ID in file reservation reasons: `file_reservation_paths(..., reason="bd-123")`

### Typical Agent Flow

```bash
bd ready --json
```

```text
file_reservation_paths(project_key, agent_name, ["src/**"], reason="bd-123")
```

```text
send_message(..., thread_id="bd-123", subject="[bd-123] Starting work")
```

Work on the bead, then complete:

```bash
bd close bd-123 --reason "Completed"
```

```text
release_file_reservations(project_key, agent_name)
```

## Test Coverage Beads

Use the following prompt to audit test coverage and create beads for any gaps.

```text
Do we have full unit test coverage without using mocks/fake stuff? What about complete e2e integration test scripts with great, detailed logging? If not, then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid with detailed comments.
```

This prompt:

- Audits existing test coverage across the project
- Identifies gaps in both unit tests and e2e tests
- Creates granular beads for missing test coverage with full dependency structure
- Emphasizes real implementations over mocks and detailed logging for debugging
