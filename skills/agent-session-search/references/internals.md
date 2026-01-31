---
title: Internals
description: Deduplication strategy, performance characteristics, watch mode, and semantic search architecture
tags:
  [
    deduplication,
    performance,
    latency,
    memory,
    watch,
    semantic-search,
    MiniLM,
    vector,
    FastEmbed,
    Tantivy,
  ]
---

# Internals

## Architecture

CASS uses a dual storage strategy:

- **SQLite** (WAL mode): Source of truth with ACID compliance and FTS5 for fallback search
- **Tantivy**: Speed layer with schema v4, edge n-grams for fast prefix matching

## Deduplication Strategy

CASS uses multi-layer deduplication:

1. **Message Hash**: SHA-256 of `(role + content + timestamp)` -- identical messages stored once
2. **Conversation Fingerprint**: Hash of first N message hashes -- detects duplicate files
3. **Search-Time Dedup**: Results deduplicated by content similarity

**Noise Filtering:**

- Empty messages and pure whitespace
- System prompts (unless searching for them)
- Repeated tool acknowledgments

## Performance Characteristics

| Operation              | Latency  |
| ---------------------- | -------- |
| Prefix search (cached) | 2-8ms    |
| Prefix search (cold)   | 40-60ms  |
| Substring search       | 80-200ms |
| Full reindex           | 5-30s    |
| Incremental reindex    | 50-500ms |
| Health check           | <50ms    |

**Memory:** 70-140MB typical (50K messages)
**Disk:** ~600 bytes/message (including n-gram overhead)

## Watch Mode

Real-time index updates:

```bash
cass index --watch
```

- **Debounce:** 2 seconds (wait for burst to settle)
- **Max wait:** 5 seconds (force flush during continuous activity)
- **Incremental:** Only re-scans modified files

The TUI automatically starts watch mode in background.

## Semantic Search

Local-only semantic search using MiniLM via FastEmbed (384-dimensional vectors, no cloud dependency):

- Primary model: MiniLM (~23MB, auto-downloaded on first use via FastEmbed)
- Fallback: Hash-based embedder (FNV-1a deterministic hashing) for approximate similarity when MiniLM unavailable

Vector index stored in CVVI format (Custom Vector Versioned Index) with:

- F32/F16 precision support
- Content deduplication via SHA-256
- Memory-mapped loading for efficiency
