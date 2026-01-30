---
title: Command Reference
description: Complete CLI command reference for CASS including indexing, search, session analysis, export, timeline, and status/diagnostics commands
tags:
  [
    commands,
    CLI,
    search,
    index,
    export,
    timeline,
    status,
    diagnostics,
    health,
    view,
    expand,
  ]
---

# Command Reference

## Indexing

```bash
# Full rebuild of DB and search index
cass index --full

# Incremental update (since last scan)
cass index

# Watch mode: auto-reindex on file changes
cass index --watch

# Force rebuild even if schema unchanged
cass index --full --force-rebuild

# Safe retries with idempotency key (24h TTL)
cass index --full --idempotency-key "build-$(date +%Y%m%d)"

# JSON output with stats
cass index --full --json
```

## Search

```bash
# Basic search (JSON output required for agents!)
cass search "query" --robot

# With filters
cass search "error" --robot --agent claude --days 7
cass search "bug" --robot --workspace /path/to/project
cass search "panic" --robot --today

# Time filters
cass search "auth" --robot --since 2024-01-01 --until 2024-01-31
cass search "test" --robot --yesterday
cass search "fix" --robot --week

# Wildcards
cass search "auth*" --robot          # prefix: authentication, authorize
cass search "*tion" --robot          # suffix: authentication, exception
cass search "*config*" --robot       # substring: misconfigured

# Token budget management (critical for LLMs!)
cass search "error" --robot --fields minimal              # path, line, agent only
cass search "error" --robot --fields summary              # adds title, score
cass search "error" --robot --max-content-length 500      # truncate fields
cass search "error" --robot --max-tokens 2000             # soft budget (~4 chars/token)
cass search "error" --robot --limit 5                     # cap results

# Pagination (cursor-based)
cass search "TODO" --robot --robot-meta --limit 20
# Use _meta.next_cursor from response:
cass search "TODO" --robot --robot-meta --limit 20 --cursor "eyJ..."

# Match highlighting
cass search "authentication error" --robot --highlight

# Query analysis/debugging
cass search "auth*" --robot --explain    # parsed query, cost estimates
cass search "auth error" --robot --dry-run  # validate without executing

# Aggregations (server-side counts)
cass search "error" --robot --aggregate agent,workspace,date

# Request correlation
cass search "bug" --robot --request-id "req-12345"

# Source filtering (for multi-machine setups)
cass search "auth" --robot --source laptop
cass search "error" --robot --source remote

# Traceability (for debugging agent pipelines)
cass search "error" --robot --trace-file /tmp/cass-trace.json
```

## Session Analysis

```bash
# Export conversation to markdown/HTML/JSON
cass export /path/to/session.jsonl --format markdown -o conversation.md
cass export /path/to/session.jsonl --format html -o conversation.html
cass export /path/to/session.jsonl --format json --include-tools

# Expand context around a line (from search result)
cass expand /path/to/session.jsonl -n 42 -C 5 --json
# Shows 5 messages before and after line 42

# View source at line
cass view /path/to/session.jsonl -n 42 --json

# Activity timeline
cass timeline --today --json --group-by hour
cass timeline --days 7 --json --agent claude
cass timeline --since 7d --json

# Find related sessions for a file
cass context /path/to/source.ts --json
```

## Status and Diagnostics

```bash
# Quick health (<50ms)
cass health
cass health --json

# Full status snapshot
cass status --json
cass state --json  # alias

# Statistics
cass stats --json
cass stats --by-source  # for multi-machine

# Full diagnostics
cass diag --verbose
```

## Use Cases

```bash
# "I solved this before..."
cass search "TypeError: Cannot read property" --robot --days 30

# Cross-agent learning (what has ANY agent said about X?)
cass search "authentication" --robot --workspace /path/to/project

# Agent-to-agent handoff
cass search "database migration" --robot --fields summary

# Daily review
cass timeline --today --json
```
