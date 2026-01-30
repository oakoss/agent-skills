---
title: Database Optimization
description: Strategic indexing, N+1 query elimination, query optimization patterns, and connection pooling configuration for PostgreSQL and MongoDB
tags:
  [
    database,
    indexing,
    n-plus-one,
    query-optimization,
    connection-pooling,
    postgresql,
    mongodb,
  ]
---

# Database Optimization

## Strategic Indexes

```sql
-- Before: Table scan (slow)
SELECT * FROM users WHERE email = 'user@example.com';
-- Execution time: 2000ms on 1M rows

-- After: Index scan (fast)
CREATE INDEX idx_users_email ON users(email);
SELECT * FROM users WHERE email = 'user@example.com';
-- Execution time: 5ms

-- Composite index for multi-column queries
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at DESC);
SELECT * FROM posts WHERE user_id = 123 ORDER BY created_at DESC;

-- Partial index for filtered queries
CREATE INDEX idx_active_users ON users(created_at) WHERE is_active = true;
```

## Eliminate N+1 Queries

```typescript
// N+1 query problem (101 database queries)
const users = await User.findAll(); // 1 query
for (const user of users) {
  user.posts = await Post.findAll({ where: { userId: user.id } }); // N queries
}

// Eager loading (2 queries)
const users = await User.findAll({
  include: [{ model: Post }],
});

// DataLoader (batching + caching)
const userLoader = new DataLoader(async (userIds) => {
  const users = await User.findAll({ where: { id: userIds } });
  return userIds.map((id) => users.find((u) => u.id === id));
});
```

## Query Optimization

```sql
-- Avoid SELECT *
SELECT id, name, email FROM users WHERE id = 1;

-- Use LIMIT
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20;

-- Avoid functions in WHERE clause (can't use index)
-- Bad:  SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
-- Good: SELECT * FROM users WHERE email = 'user@example.com';
-- Store email as lowercase, or use generated column + index
```

## Connection Pooling

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  max: 20, // Maximum connections
  min: 5, // Minimum connections
  idleTimeoutMillis: 30000, // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Error if can't connect in 2s
});

// Always release connections
const client = await pool.connect();
try {
  const result = await client.query('SELECT * FROM users');
  return result.rows;
} finally {
  client.release();
}
```
