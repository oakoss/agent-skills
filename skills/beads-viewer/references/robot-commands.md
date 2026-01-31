---
title: Robot Commands
description: BV robot mode commands, output structures, scoping flags, and jq extraction patterns
tags: [robot, commands, json, jq, output, triage, plan, insights, filtering]
---

# Robot Commands

## Triage and Planning

```bash
bv --robot-triage              # Full triage: recommendations, quick_wins, blockers_to_clear
bv --robot-next                # Single top pick with claim command
bv --robot-plan                # Parallel execution tracks with unblocks lists
bv --robot-priority            # Priority misalignment detection
```

## Graph Analysis

```bash
bv --robot-insights            # Full metrics: PageRank, betweenness, HITS, cycles, etc.
bv --robot-label-health        # Per-label health: healthy|warning|critical
bv --robot-label-flow          # Cross-label dependency flow matrix
bv --robot-label-attention     # Attention-ranked labels
```

## History and Changes

```bash
bv --robot-history             # Bead-to-commit correlations
bv --robot-diff --diff-since <ref>  # Changes since ref
```

## Other Commands

```bash
bv --robot-burndown <sprint>   # Sprint burndown, scope changes
bv --robot-forecast <id|all>   # ETA predictions
bv --robot-alerts              # Stale issues, blocking cascades
bv --robot-suggest             # Hygiene: duplicates, missing deps, cycle breaks
bv --robot-graph               # Dependency graph export (JSON, DOT, Mermaid)
bv --export-graph <file.html>  # Self-contained interactive HTML visualization
```

## Scoping and Filtering

```bash
bv --robot-plan --label backend              # Scope to label's subgraph
bv --robot-insights --as-of HEAD~30          # Historical point-in-time
bv --recipe actionable --robot-plan          # Pre-filter: ready to work
bv --recipe high-impact --robot-triage       # Pre-filter: top PageRank
bv --robot-triage --robot-triage-by-track    # Group by parallel work streams
bv --robot-triage --robot-triage-by-label    # Group by domain
```

## Built-in Recipes

| Recipe        | Purpose                            |
| ------------- | ---------------------------------- |
| `default`     | All open issues sorted by priority |
| `actionable`  | Ready to work (no blockers)        |
| `high-impact` | Top PageRank scores                |
| `blocked`     | Waiting on dependencies            |
| `stale`       | Open but untouched for 30+ days    |
| `triage`      | Sorted by computed triage score    |
| `quick-wins`  | Easy P2/P3 items with no blockers  |
| `bottlenecks` | High betweenness nodes             |

## Graph Export Formats

```bash
bv --robot-graph                              # JSON (default)
bv --robot-graph --graph-format=dot           # Graphviz DOT
bv --robot-graph --graph-format=mermaid       # Mermaid diagram
bv --robot-graph --graph-root=bd-123 --graph-depth=3  # Subgraph
bv --export-graph report.html                 # Interactive HTML
```

## Robot Output Structure

All robot JSON includes:

- `data_hash` -- Fingerprint of beads.jsonl (verify consistency)
- `status` -- Per-metric state: `computed|approx|timeout|skipped`
- `as_of` / `as_of_commit` -- Present when using `--as-of`

### --robot-triage Output

```json
{
  "quick_ref": { "open": 45, "blocked": 12, "top_picks": ["..."] },
  "recommendations": [
    {
      "id": "bd-123",
      "score": 0.85,
      "reason": "Unblocks 5 tasks",
      "unblock_info": {}
    }
  ],
  "quick_wins": ["..."],
  "blockers_to_clear": ["..."],
  "project_health": { "distributions": {}, "graph_metrics": {} },
  "commands": { "claim": "bd claim bd-123", "view": "bv --bead bd-123" }
}
```

### --robot-insights Output

```json
{
  "bottlenecks": [{ "id": "bd-123", "value": 0.45 }],
  "keystones": [{ "id": "bd-456", "value": 12.0 }],
  "influencers": ["..."],
  "hubs": ["..."],
  "authorities": ["..."],
  "cycles": [["bd-A", "bd-B", "bd-A"]],
  "clusterDensity": 0.045,
  "status": { "pagerank": "computed", "betweenness": "computed" }
}
```

## jq Quick Reference

```bash
bv --robot-triage | jq '.quick_ref'                        # At-a-glance summary
bv --robot-triage | jq '.recommendations[0]'               # Top recommendation
bv --robot-plan | jq '.plan.summary.highest_impact'        # Best unblock target
bv --robot-insights | jq '.status'                         # Check metric readiness
bv --robot-insights | jq '.cycles'                         # Circular deps (must fix!)
bv --robot-label-health | jq '.results.labels[] | select(.health_level == "critical")'
```
