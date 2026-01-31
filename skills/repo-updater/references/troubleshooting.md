---
title: Troubleshooting
description: RU common issues and fixes, debug mode, preflight failure debugging, ntm integration reference, and flywheel integration points
tags: [troubleshooting, debug, ntm, integration, preflight]
---

# Troubleshooting

## Common Issues

| Issue                    | Fix                                   |
| ------------------------ | ------------------------------------- |
| `gh: command not found`  | `brew install gh && gh auth login`    |
| `gh: auth required`      | `gh auth login` or set `GH_TOKEN`     |
| `Cannot fast-forward`    | Use `--rebase` or push first          |
| `dirty working tree`     | Commit changes or use `--autostash`   |
| `diverged_from_upstream` | `git fetch && git rebase origin/main` |

## Debug Mode

```bash
# View latest run log
cat ~/.local/state/ru/logs/latest/run.log

# View specific repo log
cat ~/.local/state/ru/logs/latest/repos/mcp_agent_mail.log

# Run with verbose output
ru agent-sweep --verbose --debug
```

## Preflight Failure Debugging

```bash
# View why repos were skipped
ru agent-sweep --json 2>/dev/null | jq '.repos[] | select(.status == "skipped")'
```

## ntm Integration

When ntm (Named Tmux Manager) is available, RU uses its robot mode API:

| Function                | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `ntm --robot-spawn`     | Create Claude Code session in new tmux pane  |
| `ntm --robot-send`      | Send prompts with chunking for long messages |
| `ntm --robot-wait`      | Block until session completes with timeout   |
| `ntm --robot-activity`  | Query real-time session state                |
| `ntm --robot-status`    | Get status of all managed sessions           |
| `ntm --robot-interrupt` | Send Ctrl+C to interrupt long operations     |

## Flywheel Integration

| Tool           | Integration                                              |
| -------------- | -------------------------------------------------------- |
| **Agent Mail** | Notify agents when repos are updated; coordinate reviews |
| **BV**         | Track repo sync as recurring beads                       |
| **CASS**       | Search past sync sessions and agent-sweep logs           |
| **NTM**        | Robot mode API for session orchestration                 |
| **DCG**        | RU runs inside DCG sandbox protection                    |

## Architecture Notes

- ~17,700 LOC pure Bash, no external dependencies beyond git, curl, gh
- Work-stealing queue for parallel sync with atomic dequeue
- Portable locking via `mkdir` (works on all POSIX systems)
- Path security validation prevents traversal attacks
- Retry with exponential backoff for network operations

## Installation

```bash
brew install dicklesworthstone/tap/ru
ru doctor
```

Alternative (curl):

```bash
curl -fsSL "https://raw.githubusercontent.com/Dicklesworthstone/repo_updater/main/install.sh?ru_cb=$(date +%s)" | bash
ru doctor
```
