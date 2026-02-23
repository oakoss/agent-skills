---
title: Vector Search
description: Vector similarity search with F32_BLOB columns, DiskANN indexes, embedding storage, and cosine distance queries
tags:
  [
    vector,
    embedding,
    F32_BLOB,
    vector32,
    vector_distance_cos,
    vector_extract,
    DiskANN,
    similarity,
  ]
---

# Vector Search

Vector similarity search is built natively into Turso and libSQL. No extensions are required.

## Schema Setup

```sql
CREATE TABLE movies (
  id INTEGER PRIMARY KEY,
  title TEXT,
  year INTEGER,
  embedding F32_BLOB(4)
);
```

The `F32_BLOB(n)` type stores n-dimensional float32 vectors. Common dimensions: 384 (MiniLM), 768 (BERT), 1536 (OpenAI ada-002), 3072 (OpenAI text-embedding-3-large).

## Vector Index

Create a DiskANN index for efficient nearest-neighbor search:

```sql
CREATE INDEX movies_idx ON movies (
  libsql_vector_idx(embedding, 'type=diskann', 'metric=cosine')
);
```

Supported metrics: `cosine`, `l2`.

## Inserting Vectors

### SQL

```sql
INSERT INTO movies (title, year, embedding)
VALUES ('Napoleon', 2023, vector32('[0.800, 0.579, 0.481, 0.229]'));
```

### TypeScript with Float32Array

```ts
const embedding = new Float32Array([0.8, 0.579, 0.481, 0.229]);

await client.execute({
  sql: 'INSERT INTO movies (title, year, embedding) VALUES (?, ?, vector32(?))',
  args: ['Napoleon', 2023, `[${embedding.join(',')}]`],
});
```

## Querying Vectors

### Cosine Similarity Search

```sql
SELECT title,
       vector_extract(embedding),
       vector_distance_cos(embedding, vector32('[0.064, 0.777, 0.661, 0.687]')) AS distance
FROM movies
ORDER BY distance ASC
LIMIT 10;
```

Cosine distance: 0 means identical, higher means more different. Always `ORDER BY distance ASC` for nearest neighbors.

### TypeScript Query

```ts
const queryVector = [0.064, 0.777, 0.661, 0.687];

const results = await client.execute({
  sql: `SELECT title, vector_distance_cos(embedding, vector32(?)) AS distance
        FROM movies
        ORDER BY distance ASC
        LIMIT ?`,
  args: [`[${queryVector.join(',')}]`, 10],
});
```

## Vector Functions

| Function                        | Purpose                               |
| ------------------------------- | ------------------------------------- |
| `vector32('[...]')`             | Create float32 vector from text       |
| `vector64('[...]')`             | Create float64 vector                 |
| `vector_extract(col)`           | Extract vector as text representation |
| `vector_distance_cos(col, vec)` | Cosine distance between vectors       |

## Batch Embedding Storage

```ts
const BATCH_SIZE = 50;

async function storeEmbeddings(
  documents: Array<{ text: string; embedding: number[] }>,
) {
  for (let i = 0; i < documents.length; i += BATCH_SIZE) {
    const batch = documents.slice(i, i + BATCH_SIZE).map((doc) => ({
      sql: 'INSERT INTO documents (content, embedding) VALUES (?, vector32(?))',
      args: [doc.text, `[${doc.embedding.join(',')}]`] as (string | number)[],
    }));

    await client.batch(batch, 'write');
  }
}
```

## RAG Pattern

Retrieve relevant documents for augmenting LLM context:

```ts
async function findRelevantDocs(queryEmbedding: number[], limit = 5) {
  const result = await client.execute({
    sql: `SELECT content,
                 vector_distance_cos(embedding, vector32(?)) AS distance
          FROM documents
          WHERE distance < 0.5
          ORDER BY distance ASC
          LIMIT ?`,
    args: [`[${queryEmbedding.join(',')}]`, limit],
  });

  return result.rows.map((row) => ({
    content: row.content as string,
    distance: row.distance as number,
  }));
}
```

## Full Setup Example

```sql
CREATE TABLE documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  content TEXT NOT NULL,
  embedding F32_BLOB(1536)
);

CREATE INDEX documents_idx ON documents (
  libsql_vector_idx(embedding, 'type=diskann', 'metric=cosine')
);
```
