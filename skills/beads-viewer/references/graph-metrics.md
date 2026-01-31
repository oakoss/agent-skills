---
title: Graph Metrics
description: The 9 graph metrics BV computes, two-phase analysis model, and metric interpretation recipes
tags:
  [
    pagerank,
    betweenness,
    hits,
    critical-path,
    eigenvector,
    cycles,
    density,
    topo-sort,
    metrics,
  ]
---

# Graph Metrics

## The 9 Graph Metrics

BV computes these metrics to surface hidden project dynamics:

| Metric            | What It Measures                | Key Insight                   |
| ----------------- | ------------------------------- | ----------------------------- |
| **PageRank**      | Recursive dependency importance | Foundational blockers         |
| **Betweenness**   | Shortest-path traffic           | Bottlenecks and bridges       |
| **HITS**          | Hub/Authority duality           | Epics vs utilities            |
| **Critical Path** | Longest dependency chain        | Keystones with zero slack     |
| **Eigenvector**   | Influence via neighbors         | Strategic dependencies        |
| **Degree**        | Direct connection counts        | Immediate blockers/blocked    |
| **Density**       | Edge-to-node ratio              | Project coupling health       |
| **Cycles**        | Circular dependencies           | Structural errors (must fix!) |
| **Topo Sort**     | Valid execution order           | Work queue foundation         |

## Two-Phase Analysis

BV uses async computation with timeouts:

- **Phase 1 (instant):** degree, topo sort, density
- **Phase 2 (500ms timeout):** PageRank, betweenness, HITS, eigenvector, cycles

Always check the `status` field in output. For large graphs (>500 nodes), some metrics may be `approx` or `skipped`.

### Status Field Values

| Status     | Meaning                                       |
| ---------- | --------------------------------------------- |
| `computed` | Full precision result                         |
| `approx`   | Approximation due to graph size               |
| `timeout`  | Exceeded 500ms budget, result unavailable     |
| `skipped`  | Metric not applicable (e.g., cycles in a DAG) |

## Performance Characteristics

- Phase 1 metrics (degree, topo, density): instant for any graph size
- Phase 2 metrics (PageRank, betweenness, etc.): 500ms timeout budget
- Results cached by `data_hash` fingerprint of beads.jsonl
- Prefer `--robot-plan` over `--robot-insights` when speed matters

## Interpreting Metrics

### Finding Bottlenecks

High betweenness centrality indicates beads that sit on many shortest paths between other beads. Completing these first maximizes unblocking impact.

```bash
bv --robot-insights | jq '.bottlenecks[:5]'
```

### Finding Foundational Work

High PageRank scores indicate beads with deep recursive dependency chains. These are the foundational pieces many other tasks ultimately depend on.

```bash
bv --recipe high-impact --robot-triage
```

### Detecting Structural Problems

Cycles are circular dependencies that make execution order impossible to determine. These must be resolved before planning work.

```bash
bv --robot-insights | jq '.cycles'
```

### Understanding Project Coupling

Cluster density measures the edge-to-node ratio. High density suggests tight coupling; low density suggests independent work streams.

```bash
bv --robot-insights | jq '.clusterDensity'
```

### Hub vs Authority Analysis

HITS distinguishes between hubs (epics that depend on many tasks) and authorities (utility tasks that many items depend on). Use this to identify strategic epics and critical shared work.

```bash
bv --robot-insights | jq '{ hubs: .hubs[:3], authorities: .authorities[:3] }'
```

### Label Health Assessment

Per-label health scoring identifies which project areas need attention:

```bash
bv --robot-label-health | jq '.results.labels[] | select(.health_level == "critical")'
bv --robot-label-attention | jq '.results[:5]'
```
