---
title: Internals
description: Response JSON shapes, deduplication strategy, performance characteristics, watch mode, and optional semantic search with MiniLM
tags:
  [
    response,
    JSON,
    schema,
    deduplication,
    performance,
    latency,
    memory,
    watch,
    semantic-search,
    MiniLM,
    vector,
    embedder,
  ]
---

# Internals

## Response Shapes

### Search Response

```json
{
  "query": "error",
  "limit": 10,
  "count": 5,
  "total_matches": 42,
  "hits": [
    {
      "source_path": "/path/to/session.jsonl",
      "line_number": 123,
      "agent": "claude_code",
      "workspace": "/projects/myapp",
      "title": "Authentication debugging",
      "snippet": "The error occurs when...",
      "score": 0.85,
      "match_type": "exact",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "_meta": {
    "elapsed_ms": 12,
    "cache_hit": true,
    "wildcard_fallback": false,
    "next_cursor": "eyJ...",
    "index_freshness": { "stale": false, "age_seconds": 120 }
  }
}
```

### Aggregation Response

```json
{
  "aggregations": {
    "agent": {
      "buckets": [
        { "key": "claude_code", "count": 120 },
        { "key": "codex", "count": 85 }
      ],
      "other_count": 15
    }
  }
}
```

## Deduplication Strategy

CASS uses multi-layer deduplication:

1. **Message Hash**: SHA-256 of `(role + content + timestamp)` - identical messages stored once
2. **Conversation Fingerprint**: Hash of first N message hashes - detects duplicate files
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

TUI automatically starts watch mode in background.

## Optional Semantic Search

Local-only semantic search using MiniLM (no cloud):

**Required files** (place in data directory):

- `model.onnx`
- `tokenizer.json`
- `config.json`
- `special_tokens_map.json`
- `tokenizer_config.json`

Vector index stored as `vector_index/index-minilm-384.cvvi`.

CASS does NOT auto-download models; you must manually install them.

**Hash Embedder Fallback:** When MiniLM not installed, CASS uses a hash-based embedder for approximate semantic similarity.
