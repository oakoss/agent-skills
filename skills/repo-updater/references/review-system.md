---
title: Review System
description: RU AI-assisted review orchestration with two-phase workflow, priority scoring algorithm, session drivers, and cost budget controls
tags: [review, ai-review, priority-scoring, session-drivers, cost-budgets]
---

# Review System

## Two-Phase Review Workflow

### Phase 1: Discovery (`--plan`)

- Queries GitHub for open issues and PRs across all repos
- Scores items by priority using label analysis and age
- Creates isolated git worktrees for safe review
- Spawns Claude Code sessions in terminal multiplexer

### Phase 2: Application (`--apply`)

- Reviews proposed changes from discovery phase
- Runs quality gates (ShellCheck, tests, lint)
- Optionally pushes approved changes (`--push`)

```bash
ru review --plan                # Discover and plan reviews
ru review --apply --push        # After reviewing AI suggestions
```

## Priority Scoring Algorithm

| Factor         | Points | Logic                                   |
| -------------- | ------ | --------------------------------------- |
| **Type**       | 0-20   | PRs: +20, Issues: +10, Draft PRs: -15   |
| **Labels**     | 0-50   | security/critical: +50, bug/urgent: +30 |
| **Age (bugs)** | 0-50   | >60 days: +50, >30 days: +30            |
| **Recency**    | 0-15   | Updated <3 days: +15, <7 days: +10      |
| **Staleness**  | -20    | Recently reviewed: -20                  |

Priority levels: CRITICAL (≥150), HIGH (≥100), NORMAL (≥50), LOW (<50)

## Session Drivers

| Driver  | Description                    | Best For              |
| ------- | ------------------------------ | --------------------- |
| `auto`  | Auto-detect best available     | Default               |
| `ntm`   | Named Tmux Manager integration | Multi-agent workflows |
| `local` | Direct tmux sessions           | Simple setups         |

```bash
ru review --mode=ntm --plan
ru review -j 4 --plan           # Parallel sessions
```

## Cost Budgets

```bash
ru review --max-repos=10 --plan
ru review --max-runtime=30 --plan    # Minutes
ru review --skip-days=14 --plan      # Skip recently reviewed
ru review --analytics                # View past review stats
```
