---
title: Command Reference
description: Complete CLI command reference for CASS including indexing, search, session viewing, export, and diagnostics
tags: [commands, CLI, search, index, export, diagnostics, health, view, expand]
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

# Search modes
cass search "authentication" --mode lexical --robot
cass search "how to handle user login" --mode semantic --robot
cass search "auth error handling" --mode hybrid --robot

# Token budget management (critical for LLMs!)
cass search "error" --robot --fields minimal              # path, line, agent only
cass search "error" --robot --limit 5                     # cap results

# Match highlighting
cass search "authentication error" --robot --highlight
```

## Session Viewing and Export

```bash
# Expand context around a line (from search result)
cass expand /path/to/session.jsonl -n 42 -C 5 --json
# Shows 5 messages before and after line 42

# View source at line
cass view /path/to/session.jsonl -n 42 --json

# Export conversation as self-contained HTML
cass export-html /path/to/session.jsonl
cass export-html /path/to/session.jsonl --encrypt --password "secret"
cass export-html /path/to/session.jsonl --output-dir ./exports --open
```

## Status and Diagnostics

```bash
# Quick health check
cass health
cass health --json

# Self-documenting API for agents
cass robot-docs guide      # quick-start walkthrough
cass robot-docs commands   # all commands and flags
cass robot-docs schemas    # response JSON schemas
cass robot-docs exit-codes # error handling
cass robot-docs examples   # copy-paste invocations
cass robot-docs contracts  # API versioning
cass robot-docs sources    # remote sources guide
```

## Use Cases

```bash
# "I solved this before..."
cass search "TypeError: Cannot read property" --robot --days 30

# Cross-agent learning (what has ANY agent said about X?)
cass search "authentication" --robot --workspace /path/to/project

# Agent-to-agent handoff
cass search "database migration" --robot --fields minimal

# Daily review
cass search "--today" --robot
```
