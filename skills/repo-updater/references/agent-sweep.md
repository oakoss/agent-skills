---
title: Agent Sweep
description: RU agent-sweep command for automated dirty repo processing with three-phase workflow, preflight checks, security guardrails, and execution modes
tags: [agent-sweep, automation, preflight, security, denylist]
---

# Agent Sweep

Orchestrate AI coding agents to automatically process repositories with uncommitted changes.

## Basic Usage

```bash
ru agent-sweep                    # Process all dirty repos
ru agent-sweep --dry-run          # Preview what would be processed
ru agent-sweep -j4                # 4 repos in parallel
ru agent-sweep --repos="myproject*"  # Filter to specific repos
ru agent-sweep --with-release     # Include release step
ru agent-sweep --resume           # Resume interrupted sweep
ru agent-sweep --restart          # Start fresh
```

## Three-Phase Workflow

**Phase 1: Planning** (`--phase1-timeout`, default 300s)

- Claude Code analyzes uncommitted changes
- Determines which files should be staged (respecting denylist)
- Generates structured commit message

**Phase 2: Commit** (`--phase2-timeout`, default 600s)

- Validates the plan (file existence, denylist compliance)
- Stages approved files, creates commit
- Runs quality gates
- Optionally pushes to remote

**Phase 3: Release** (`--phase3-timeout`, default 300s, requires `--with-release`)

- Analyzes commit history since last tag
- Determines version bump (patch/minor/major)
- Creates git tag and optionally GitHub release

## Execution Modes

```bash
--execution-mode=agent  # Full AI-driven workflow (default)
--execution-mode=plan   # Phase 1 only: generate plan, stop
--execution-mode=apply  # Phase 2+3: execute existing plan
```

## Preflight Checks

Each repo is validated before spawning an agent:

| Check                 | Skip Reason                |
| --------------------- | -------------------------- |
| Is git repository     | `not_a_git_repo`           |
| Git email configured  | `git_email_not_configured` |
| Not a shallow clone   | `shallow_clone`            |
| No rebase in progress | `rebase_in_progress`       |
| No merge in progress  | `merge_in_progress`        |
| Not detached HEAD     | `detached_HEAD`            |
| Has upstream branch   | `no_upstream_branch`       |
| Not diverged          | `diverged_from_upstream`   |

## Security Guardrails

### File Denylist

Never committed regardless of agent output:

| Category            | Patterns                                                 |
| ------------------- | -------------------------------------------------------- |
| **Secrets**         | `.env`, `*.pem`, `*.key`, `id_rsa*`, `credentials.json`  |
| **Build artifacts** | `node_modules`, `__pycache__`, `dist`, `build`, `target` |
| **Logs/temp**       | `*.log`, `*.tmp`, `*.swp`, `.DS_Store`                   |
| **IDE files**       | `.idea`, `.vscode`, `*.iml`                              |

### Secret Scanning

```bash
--secret-scan=none   # Disable
--secret-scan=warn   # Warn but continue (default)
--secret-scan=block  # Block push on detection
```

## Exit Codes

| Code | Meaning                                  |
| ---- | ---------------------------------------- |
| `0`  | All repos processed successfully         |
| `1`  | Some repos failed (agent error, timeout) |
| `2`  | Quality gate failures (secrets, tests)   |
| `3`  | System error (ntm, tmux missing)         |
| `4`  | Invalid arguments                        |
| `5`  | Interrupted (use `--resume`)             |
