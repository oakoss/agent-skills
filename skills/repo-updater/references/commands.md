---
title: Commands
description: RU CLI command reference for sync, status, repo management, diagnostics, and output modes with JSON and NDJSON examples
tags: [cli, commands, sync, status, json, ndjson, jq]
---

# Commands

## Sync (Primary Use Case)

```bash
ru sync              # Sync all configured repos
ru sync -j8          # Parallel sync (much faster)
ru sync --dry-run    # See what would happen
ru sync --resume     # Resume interrupted sync
ru sync --json 2>/dev/null | jq '.summary'  # JSON output
```

## Status (Read-Only Check)

```bash
ru status            # Check all repos without modifying
ru status --json     # JSON output
```

## Repo Management

```bash
ru init                            # Initialize configuration
ru add owner/repo                  # Add repo
ru add https://github.com/owner/repo
ru add owner/repo@branch as custom-name
ru remove owner/repo               # Remove from list
ru list                            # List configured repos
ru prune                           # Preview orphaned repos
ru prune --delete                  # Remove orphans
ru prune --archive                 # Archive orphans
```

## Diagnostics

```bash
ru doctor      # System health check
ru self-update # Update ru itself
```

## JSON Output Mode

```bash
ru sync --json 2>/dev/null
```

```json
{
  "version": "1.2.0",
  "timestamp": "2025-01-03T14:30:00Z",
  "summary": {
    "total": 47,
    "cloned": 8,
    "updated": 34,
    "current": 3,
    "conflicts": 2
  },
  "repos": []
}
```

## NDJSON Results Logging

```json
{"repo":"mcp_agent_mail","action":"pull","status":"updated","duration":2}
{"repo":"beads_viewer","action":"clone","status":"cloned","duration":5}
```

## jq Examples

```bash
# Get paths of all cloned repos
ru sync --json 2>/dev/null | jq -r '.repos[] | select(.action=="clone") | .path'

# Count by status
cat ~/.local/state/ru/logs/latest/results.ndjson | jq -s 'group_by(.status) | map({status: .[0].status, count: length})'
```
