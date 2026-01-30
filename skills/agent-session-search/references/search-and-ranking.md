---
title: Search and Ranking
description: Search modes (lexical, semantic, hybrid), ranking modes with scoring formulas, score components, and aggregation analytics
tags:
  [
    search,
    ranking,
    BM25,
    semantic,
    hybrid,
    RRF,
    recency,
    relevance,
    scoring,
    aggregation,
    analytics,
  ]
---

# Search and Ranking

## Search Modes

Three search modes, selectable with `--mode` flag:

| Mode                  | Algorithm              | Best For                           |
| --------------------- | ---------------------- | ---------------------------------- |
| **lexical** (default) | BM25 full-text         | Exact term matching, code searches |
| **semantic**          | Vector similarity      | Conceptual queries, "find similar" |
| **hybrid**            | Reciprocal Rank Fusion | Balanced precision and recall      |

```bash
cass search "authentication" --mode lexical --robot
cass search "how to handle user login" --mode semantic --robot
cass search "auth error handling" --mode hybrid --robot
```

**Hybrid** combines lexical and semantic using RRF:

```text
RRF_score = Σ 1 / (60 + rank_i)
```

## Ranking Modes

Cycle with `F12` in TUI or use `--ranking` flag:

| Mode              | Formula                       | Best For                   |
| ----------------- | ----------------------------- | -------------------------- |
| **Recent Heavy**  | `relevance*0.3 + recency*0.7` | "What was I working on?"   |
| **Balanced**      | `relevance*0.5 + recency*0.5` | General search             |
| **Relevance**     | `relevance*0.8 + recency*0.2` | "Best explanation of X"    |
| **Match Quality** | Penalizes fuzzy matches       | Precise technical searches |
| **Date Newest**   | Pure chronological            | Recent activity            |
| **Date Oldest**   | Reverse chronological         | "When did I first..."      |

### Score Components

- **Text Relevance (BM25)**: Term frequency, inverse document frequency, length normalization
- **Recency**: Exponential decay (today ~1.0, last week ~0.7, last month ~0.3)
- **Match Exactness**: Exact phrase=1.0, Prefix=0.9, Suffix=0.8, Substring=0.6, Fuzzy=0.4

### Blended Scoring Formula

```text
Final_Score = BM25_Score × Match_Quality + α × Recency_Factor
```

| Mode            | α Value | Effect                 |
| --------------- | ------- | ---------------------- |
| Recent Heavy    | 1.0     | Recency dominates      |
| Balanced        | 0.4     | Moderate recency boost |
| Relevance Heavy | 0.1     | BM25 dominates         |
| Match Quality   | 0.0     | Pure text matching     |

## Aggregation and Analytics

Aggregate search results server-side to get counts and distributions without transferring full result data:

```bash
# Count results by agent
cass search "error" --robot --aggregate agent

# Multi-field aggregation
cass search "bug" --robot --aggregate agent,workspace,date

# Combine with filters
cass search "TODO" --agent claude --robot --aggregate workspace
```

| Aggregation Field | Description                                            |
| ----------------- | ------------------------------------------------------ |
| `agent`           | Group by agent type (claude_code, codex, cursor, etc.) |
| `workspace`       | Group by workspace/project path                        |
| `date`            | Group by date (YYYY-MM-DD)                             |
| `match_type`      | Group by match quality (exact, prefix, fuzzy)          |

Top 10 buckets returned per field, with `other_count` for remaining items.
