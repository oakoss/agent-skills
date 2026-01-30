---
title: Robot Mode
description: Robot mode for AI agent consumption including self-documenting API, forgiving syntax, output formats, token budget management, and pipeline mode
tags:
  [
    robot,
    JSON,
    agent,
    API,
    capabilities,
    introspect,
    robot-docs,
    forgiving-syntax,
    aliases,
    token-budget,
    pipeline,
    JSONL,
  ]
---

# Robot Mode

## Self-Documenting API

CASS teaches agents how to use itself:

```bash
# Quick capability check
cass capabilities --json
# Returns: features, connectors, limits

# Full API schema
cass introspect --json
# Returns: all commands, arguments, response shapes

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

CASS auto-corrects common mistakes:

| What you type            | What CASS understands                        |
| ------------------------ | -------------------------------------------- |
| `cass searxh "error"`    | `cass search "error"` (typo corrected)       |
| `cass -robot -limit=5`   | `cass --robot --limit=5` (single-dash fixed) |
| `cass --Robot --LIMIT 5` | `cass --robot --limit 5` (case normalized)   |
| `cass find "auth"`       | `cass search "auth"` (alias resolved)        |
| `cass --limt 5`          | `cass --limit 5` (Levenshtein <=2)           |

### Command Aliases

- `find`, `query`, `q`, `lookup`, `grep` → `search`
- `ls`, `list`, `info`, `summary` → `stats`
- `st`, `state` → `status`
- `reindex`, `idx`, `rebuild` → `index`
- `show`, `get`, `read` → `view`
- `docs`, `help-robot`, `robotdocs` → `robot-docs`

## Output Formats

```bash
# Pretty-printed JSON (default)
cass search "error" --robot

# Streaming JSONL (header + one hit per line)
cass search "error" --robot-format jsonl

# Compact single-line JSON
cass search "error" --robot-format compact

# With performance metadata
cass search "error" --robot --robot-meta
```

**Design principle:** stdout = JSON only; diagnostics go to stderr.

## Token Budget Management

LLMs have context limits. Control output size:

| Flag                           | Effect                                     |
| ------------------------------ | ------------------------------------------ |
| `--fields minimal`             | Only `source_path`, `line_number`, `agent` |
| `--fields summary`             | Adds `title`, `score`                      |
| `--fields score,title,snippet` | Custom field selection                     |
| `--max-content-length 500`     | Truncate long fields (UTF-8 safe)          |
| `--max-tokens 2000`            | Soft budget (~4 chars/token)               |
| `--limit 5`                    | Cap number of results                      |

Truncated fields include `*_truncated: true` indicator.

## Pipeline Mode (Chained Search)

Chain searches by piping session paths:

```bash
# Find sessions mentioning "auth", then search within those for "token"
cass search "authentication" --robot-format sessions | \
  cass search "refresh token" --sessions-from - --robot

# Build a filtered corpus from today's work
cass search --today --robot-format sessions > today_sessions.txt
cass search "bug fix" --sessions-from today_sessions.txt --robot
```

Use cases:

- **Drill-down**: Broad search → narrow within results
- **Cross-reference**: Find sessions with term A, then find term B within them
- **Corpus building**: Save session lists for repeated searches
