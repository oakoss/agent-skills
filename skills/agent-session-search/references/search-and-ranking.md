---
title: Search and Ranking
description: Search modes (lexical, semantic, hybrid), ranking modes with scoring, and match types
tags:
  [search, ranking, BM25, semantic, hybrid, RRF, recency, relevance, scoring]
---

# Search and Ranking

## Search Modes

Three search modes, selectable with `--mode` flag:

| Mode                  | Algorithm                                | Best For                           |
| --------------------- | ---------------------------------------- | ---------------------------------- |
| **lexical** (default) | BM25 full-text via Tantivy               | Exact term matching, code searches |
| **semantic**          | Vector similarity (MiniLM via FastEmbed) | Conceptual queries, "find similar" |
| **hybrid**            | Reciprocal Rank Fusion                   | Balanced precision and recall      |

```bash
cass search "authentication" --mode lexical --robot
cass search "how to handle user login" --mode semantic --robot
cass search "auth error handling" --mode hybrid --robot
```

**Hybrid** combines lexical and semantic using RRF:

```text
RRF_score = Sigma 1 / (60 + rank_i)
```

Semantic mode requires MiniLM model files (~23MB). When MiniLM is not available, CASS falls back to a hash-based embedder (FNV-1a deterministic hashing) for approximate similarity.

## Ranking Modes

Cycle with `F12` in TUI or use `--ranking` flag:

| Mode              | Effect                                |
| ----------------- | ------------------------------------- |
| **Recent Heavy**  | Recency dominates                     |
| **Balanced**      | Equal weight to relevance and recency |
| **Relevance**     | BM25 score dominates                  |
| **Match Quality** | Penalizes fuzzy matches               |
| **Date Newest**   | Pure chronological                    |
| **Date Oldest**   | Reverse chronological                 |

### Score Components

- **Text Relevance (BM25)**: Term frequency, inverse document frequency, length normalization
- **Recency**: Exponential decay based on age
- **Match Exactness**: Exact > Prefix > Suffix > Substring > Fuzzy

## Match Types

Results include a `match_type` field indicating how the query matched:

| Type        | Meaning                               |
| ----------- | ------------------------------------- |
| `exact`     | Verbatim match                        |
| `prefix`    | Via prefix expansion (edge n-grams)   |
| `suffix`    | Via suffix pattern                    |
| `substring` | Via substring pattern                 |
| `fuzzy`     | Auto-fallback when results are sparse |
