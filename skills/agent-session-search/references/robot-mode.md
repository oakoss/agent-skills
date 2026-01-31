---
title: Robot Mode
description: Robot mode for AI agent consumption including self-documenting API, forgiving syntax, output formats, and token budget management
tags: [robot, JSON, agent, API, robot-docs, forgiving-syntax, token-budget]
---

# Robot Mode

## Self-Documenting API

CASS teaches agents how to use itself:

```bash
# Topic-based docs (LLM-optimized)
cass robot-docs commands   # all commands and flags
cass robot-docs schemas    # response JSON schemas
cass robot-docs examples   # copy-paste invocations
cass robot-docs exit-codes # error handling
cass robot-docs guide      # quick-start walkthrough
cass robot-docs contracts  # API versioning
cass robot-docs sources    # remote sources guide
```

## Forgiving Syntax (Agent-Friendly)

CASS aggressively normalizes input to maximize acceptance when intent is clear. When corrections are applied, CASS emits a teaching note to stderr so agents learn the canonical syntax.

| What you type            | What CASS understands                        |
| ------------------------ | -------------------------------------------- |
| `cass searxh "error"`    | `cass search "error"` (typo corrected)       |
| `cass -robot -limit=5`   | `cass --robot --limit=5` (single-dash fixed) |
| `cass --Robot --LIMIT 5` | `cass --robot --limit 5` (case normalized)   |
| `cass --limt 5`          | `cass --limit 5` (Levenshtein <=2)           |

## Output Conventions

**Design principle:** stdout = JSON only; diagnostics go to stderr.

```bash
# JSON output for agent consumption
cass search "error" --robot

# Health check with JSON
cass health --json

# View/expand with JSON
cass view /path -n 42 --json
cass expand /path -n 42 -C 5 --json
```

Exit code 0 means success (parse stdout). Non-zero means an error occurred.

## Token Budget Management

LLMs have context limits. Control output size:

| Flag               | Effect                                    |
| ------------------ | ----------------------------------------- |
| `--fields minimal` | Only essential fields (path, line, agent) |
| `--limit 5`        | Cap number of results                     |

Start with `--fields minimal --limit 5` and widen as needed.

## Agent Workflow

Recommended sequence for AI agents:

```bash
# 1. Check if CASS is available and healthy
cass health --json || cass index --full

# 2. Search for relevant past experience
cass search "authentication error" --robot --fields minimal --limit 5

# 3. Get more context on a promising result
cass expand /path/to/session.jsonl -n 42 -C 5 --json

# 4. View full source if needed
cass view /path/to/session.jsonl -n 42 --json
```

Always check health first. If CASS is not installed, skip gracefully.
