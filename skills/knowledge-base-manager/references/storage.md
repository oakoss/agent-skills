---
title: Storage and Retrieval
description: Database selection criteria, vector store setup with pgvector, hybrid storage patterns, technology comparison, and index tuning
tags:
  [
    knowledge-base,
    storage,
    vector-db,
    graph-db,
    search,
    retrieval,
    pgvector,
    pinecone,
    hnsw,
  ]
---

# Storage and Retrieval

## Technology Stacks

| Stack          | Vector DB                    | Graph DB        | Embeddings     | Search                    |
| -------------- | ---------------------------- | --------------- | -------------- | ------------------------- |
| Document-based | Pinecone, Weaviate, pgvector | —               | OpenAI, Cohere | Semantic + keyword hybrid |
| Entity-based   | —                            | Neo4j, ArangoDB | —              | Cypher, AQL               |
| Hybrid         | Any vector DB                | Any graph DB    | OpenAI, Cohere | Combined queries          |

## Selection Criteria

Choose storage based on the architecture decision from [Architecture and Types](architecture.md):

| Architecture   | Primary concern                | Key trade-off                                      |
| -------------- | ------------------------------ | -------------------------------------------------- |
| Document-based | Query latency, embedding cost  | Easy to add content vs hard to query relationships |
| Entity-based   | Graph modeling complexity      | Powerful traversal vs upfront schema design        |
| Hybrid         | Synchronization between stores | Combined strengths vs operational complexity       |

## Technology Comparison

| Feature        | pgvector            | Pinecone          | Weaviate            | Chroma            |
| -------------- | ------------------- | ----------------- | ------------------- | ----------------- |
| Hosting        | Self-hosted         | Managed           | Both                | Self-hosted       |
| Max vectors    | Limited by Postgres | Billions          | Billions            | Millions          |
| Cost model     | Infrastructure only | Per-vector/query  | Per-node or managed | Free / open       |
| Metadata       | Full SQL filtering  | Key-value filters | GraphQL-style       | Key-value filters |
| Best for       | Existing Postgres   | Managed scale     | Multi-modal search  | Local dev / POC   |
| Index types    | HNSW, IVFFlat       | Proprietary       | HNSW                | HNSW              |
| Backup/Restore | Postgres native     | Managed           | Snapshots           | Persistence dir   |
| Transactions   | Full ACID           | None              | None                | None              |

## Vector Store Setup: pgvector

### Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE kb_documents (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content       TEXT NOT NULL,
  embedding     vector(1536),
  metadata      JSONB NOT NULL DEFAULT '{}',
  source_url    TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON kb_documents
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 200);

CREATE INDEX ON kb_documents USING gin (metadata);
CREATE INDEX ON kb_documents USING gin (to_tsvector('english', content));
```

### Insert and Query Functions

```ts
import { pool } from './db';

interface KBDocument {
  id: string;
  content: string;
  embedding: number[];
  metadata: Record<string, unknown>;
  sourceUrl?: string;
}

async function insertDocument(doc: Omit<KBDocument, 'id'>): Promise<string> {
  const { rows } = await pool.query(
    `INSERT INTO kb_documents (content, embedding, metadata, source_url)
     VALUES ($1, $2::vector, $3, $4)
     RETURNING id`,
    [doc.content, JSON.stringify(doc.embedding), doc.metadata, doc.sourceUrl],
  );
  return rows[0].id;
}

async function searchByVector(
  queryEmbedding: number[],
  limit = 10,
  metadataFilter?: Record<string, unknown>,
): Promise<(KBDocument & { similarity: number })[]> {
  let whereClause = '';
  const params: unknown[] = [JSON.stringify(queryEmbedding), limit];

  if (metadataFilter) {
    whereClause = 'WHERE metadata @> $3';
    params.push(JSON.stringify(metadataFilter));
  }

  const { rows } = await pool.query(
    `SELECT id, content, metadata, source_url AS "sourceUrl",
            1 - (embedding <=> $1::vector) AS similarity
     FROM kb_documents
     ${whereClause}
     ORDER BY embedding <=> $1::vector
     LIMIT $2`,
    params,
  );
  return rows;
}
```

## Document Store Schema

For structured documents with full-text search:

```ts
interface DocumentEntry {
  id: string;
  title: string;
  content: string;
  contentHash: string;
  category: string;
  tags: string[];
  source: {
    url: string;
    author: string;
    fetchedAt: string;
  };
  version: number;
  createdAt: string;
  updatedAt: string;
}
```

### Full-Text Search Query

```sql
SELECT id, title,
       ts_rank(to_tsvector('english', content), query) AS rank
FROM kb_documents, plainto_tsquery('english', $1) query
WHERE to_tsvector('english', content) @@ query
ORDER BY rank DESC
LIMIT $2;
```

## Hybrid Storage Pattern

Combine vector similarity, full-text search, and metadata filtering in a single query using Reciprocal Rank Fusion (RRF):

```ts
interface HybridSearchOptions {
  query: string;
  queryEmbedding: number[];
  metadataFilter?: Record<string, unknown>;
  limit?: number;
  vectorWeight?: number;
  textWeight?: number;
}

async function hybridSearch(opts: HybridSearchOptions) {
  const {
    query,
    queryEmbedding,
    metadataFilter,
    limit = 10,
    vectorWeight = 0.7,
    textWeight = 0.3,
  } = opts;

  const filterClause = metadataFilter ? 'AND metadata @> $4::jsonb' : '';
  const params: unknown[] = [JSON.stringify(queryEmbedding), query, limit];
  if (metadataFilter) params.push(JSON.stringify(metadataFilter));

  const { rows } = await pool.query(
    `WITH vector_results AS (
       SELECT id, content, metadata,
              ROW_NUMBER() OVER (ORDER BY embedding <=> $1::vector) AS vrank
       FROM kb_documents
       WHERE embedding IS NOT NULL ${filterClause}
       LIMIT 50
     ),
     text_results AS (
       SELECT id, content, metadata,
              ROW_NUMBER() OVER (
                ORDER BY ts_rank(to_tsvector('english', content),
                                 plainto_tsquery('english', $2)) DESC
              ) AS trank
       FROM kb_documents
       WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $2)
             ${filterClause}
       LIMIT 50
     )
     SELECT COALESCE(v.id, t.id) AS id,
            COALESCE(v.content, t.content) AS content,
            COALESCE(v.metadata, t.metadata) AS metadata,
            (COALESCE($5::float / (60 + v.vrank), 0) +
             COALESCE($6::float / (60 + t.trank), 0)) AS rrf_score
     FROM vector_results v
     FULL OUTER JOIN text_results t ON v.id = t.id
     ORDER BY rrf_score DESC
     LIMIT $3`,
    [...params, vectorWeight, textWeight],
  );
  return rows;
}
```

## Index Tuning

### HNSW Parameters

| Parameter         | Default | Effect                                   | Guidance                       |
| ----------------- | ------- | ---------------------------------------- | ------------------------------ |
| `m`               | 16      | Max connections per node                 | 12-48; higher = better recall  |
| `ef_construction` | 64      | Build-time search width                  | 100-400; higher = slower build |
| `ef_search`       | 40      | Query-time search width (SET at runtime) | 100-400; higher = slower query |

```sql
SET hnsw.ef_search = 200;
```

### IVFFlat Trade-offs

| Parameter | Effect                          | Guidance                            |
| --------- | ------------------------------- | ----------------------------------- |
| `lists`   | Number of clusters              | sqrt(row_count) to row_count / 1000 |
| `probes`  | Clusters searched at query time | 1-20; higher = better recall        |

IVFFlat is faster to build but less accurate than HNSW. Use IVFFlat for datasets that change frequently (rebuild is cheaper). Use HNSW for stable datasets where recall matters.

```sql
CREATE INDEX ON kb_documents
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

SET ivfflat.probes = 10;
```

## Implementation Steps

1. Choose database(s) based on KB type
2. Create schema with vector, full-text, and metadata indexes
3. Implement insert and query functions with proper parameterization
4. Add caching and optimization for common access patterns
5. Target <100ms median query time
6. Monitor index performance and tune parameters based on recall benchmarks

> For document-based implementation details (chunking, embeddings, vector store configuration), use the `rag-implementer` skill. For entity-based implementation details (ontology design, entity extraction, graph database setup), use the `knowledge-graph-builder` skill.
