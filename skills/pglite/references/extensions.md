---
title: Extensions
description: Loading and using PGlite extensions including pgvector, pg_trgm, pgcrypto, uuid-ossp, pg_uuidv7, hstore, ltree, bloom, and full-text search
tags:
  [
    extensions,
    pgvector,
    pg_trgm,
    pgcrypto,
    uuid,
    hstore,
    ltree,
    bloom,
    full-text-search,
    vector,
  ]
---

# Extensions

## Loading Extensions

Extensions must be declared at construction time in the `extensions` option. They cannot be added after the instance is created.

```ts
import { PGlite } from '@electric-sql/pglite';
import { vector } from '@electric-sql/pglite/vector';
import { pg_trgm } from '@electric-sql/pglite/contrib/pg_trgm';
import { uuid_ossp } from '@electric-sql/pglite/contrib/uuid_ossp';

const db = await PGlite.create({
  extensions: {
    vector,
    pg_trgm,
    uuid_ossp,
  },
});
```

After creating the instance, enable each extension with `CREATE EXTENSION`:

```ts
await db.exec('CREATE EXTENSION IF NOT EXISTS vector');
await db.exec('CREATE EXTENSION IF NOT EXISTS pg_trgm');
await db.exec('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"');
```

## Extension Import Paths

| Extension   | Import Path                                      |
| ----------- | ------------------------------------------------ |
| `vector`    | `@electric-sql/pglite/vector`                    |
| `pg_trgm`   | `@electric-sql/pglite/contrib/pg_trgm`           |
| `pgcrypto`  | `@electric-sql/pglite/contrib/pgcrypto`          |
| `uuid-ossp` | `@electric-sql/pglite/contrib/uuid_ossp`         |
| `pg_uuidv7` | `@electric-sql/pglite-uuidv7` (separate package) |
| `hstore`    | `@electric-sql/pglite/contrib/hstore`            |
| `ltree`     | `@electric-sql/pglite/contrib/ltree`             |
| `bloom`     | `@electric-sql/pglite/contrib/bloom`             |
| `live`      | `@electric-sql/pglite/live`                      |

## pgvector: Vector Similarity Search

Store and query vector embeddings with exact and approximate nearest neighbor search.

```ts
import { PGlite } from '@electric-sql/pglite';
import { vector } from '@electric-sql/pglite/vector';

const db = await PGlite.create({ extensions: { vector } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS vector;

  CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536)
  );

  CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops);
`);

await db.query('INSERT INTO documents (content, embedding) VALUES ($1, $2)', [
  'Hello world',
  '[0.1, 0.2, ...]',
]);

const similar = await db.query<{ id: number; content: string }>(
  `SELECT id, content
   FROM documents
   ORDER BY embedding <=> $1
   LIMIT 5`,
  ['[0.1, 0.2, ...]'],
);
```

Distance operators:

| Operator | Distance Type  |
| -------- | -------------- |
| `<->`    | L2 (Euclidean) |
| `<=>`    | Cosine         |
| `<#>`    | Inner product  |

## pg_trgm: Trigram Similarity

Fuzzy text matching using trigram decomposition.

```ts
import { PGlite } from '@electric-sql/pglite';
import { pg_trgm } from '@electric-sql/pglite/contrib/pg_trgm';

const db = await PGlite.create({ extensions: { pg_trgm } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS pg_trgm;

  CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
  );

  CREATE INDEX idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
`);

const results = await db.query<{
  id: number;
  name: string;
  similarity: number;
}>(
  `SELECT id, name, similarity(name, $1) AS similarity
   FROM products
   WHERE name % $1
   ORDER BY similarity DESC
   LIMIT 10`,
  ['laptop'],
);
```

## pgcrypto: Cryptographic Functions

Hashing, encryption, and random data generation.

```ts
import { PGlite } from '@electric-sql/pglite';
import { pgcrypto } from '@electric-sql/pglite/contrib/pgcrypto';

const db = await PGlite.create({ extensions: { pgcrypto } });

await db.exec('CREATE EXTENSION IF NOT EXISTS pgcrypto');

const hash = await db.query<{ digest: string }>(
  "SELECT encode(digest($1, 'sha256'), 'hex') as digest",
  ['my secret data'],
);

const uuid = await db.query<{ id: string }>('SELECT gen_random_uuid() as id');
```

## uuid-ossp: UUID Generation

```ts
import { PGlite } from '@electric-sql/pglite';
import { uuid_ossp } from '@electric-sql/pglite/contrib/uuid_ossp';

const db = await PGlite.create({ extensions: { uuid_ossp } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

  CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL
  );
`);
```

## pg_uuidv7: UUIDv7 with Timestamp Ordering

UUIDv7 embeds a timestamp for natural sort ordering. Requires a separate package.

```bash
npm install @electric-sql/pglite-uuidv7
```

```ts
import { PGlite } from '@electric-sql/pglite';
import { pg_uuidv7 } from '@electric-sql/pglite-uuidv7';

const db = await PGlite.create({ extensions: { pg_uuidv7 } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS pg_uuidv7;

  CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    name TEXT NOT NULL
  );
`);
```

## hstore: Key-Value Store

Store sets of key-value pairs in a single column.

```ts
import { PGlite } from '@electric-sql/pglite';
import { hstore } from '@electric-sql/pglite/contrib/hstore';

const db = await PGlite.create({ extensions: { hstore } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS hstore;

  CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    config hstore
  );
`);

await db.query('INSERT INTO settings (config) VALUES ($1::hstore)', [
  '"theme"=>"dark","lang"=>"en"',
]);

const result = await db.query<{ value: string }>(
  "SELECT config -> 'theme' as value FROM settings WHERE id = $1",
  [1],
);
```

## ltree: Hierarchical Labels

Store and query hierarchical tree-like data.

```ts
import { PGlite } from '@electric-sql/pglite';
import { ltree } from '@electric-sql/pglite/contrib/ltree';

const db = await PGlite.create({ extensions: { ltree } });

await db.exec(`
  CREATE EXTENSION IF NOT EXISTS ltree;

  CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    path ltree NOT NULL
  );

  CREATE INDEX idx_categories_path ON categories USING gist (path);
`);

await db.exec(`
  INSERT INTO categories (path) VALUES
    ('root'),
    ('root.electronics'),
    ('root.electronics.phones'),
    ('root.electronics.laptops')
`);

const descendants = await db.query<{ id: number; path: string }>(
  "SELECT * FROM categories WHERE path <@ 'root.electronics'",
);
```

## Full-Text Search

Postgres built-in full-text search works out of the box without additional extensions.

```ts
import { PGlite } from '@electric-sql/pglite';

const db = await PGlite.create();

await db.exec(`
  CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    search_vector tsvector GENERATED ALWAYS AS (
      setweight(to_tsvector('english', title), 'A') ||
      setweight(to_tsvector('english', body), 'B')
    ) STORED
  );

  CREATE INDEX idx_articles_search ON articles USING gin (search_vector);
`);

const results = await db.query<{ id: number; title: string; rank: number }>(
  `SELECT id, title, ts_rank(search_vector, query) AS rank
   FROM articles, plainto_tsquery('english', $1) query
   WHERE search_vector @@ query
   ORDER BY rank DESC
   LIMIT 10`,
  ['postgres embedded browser'],
);
```
