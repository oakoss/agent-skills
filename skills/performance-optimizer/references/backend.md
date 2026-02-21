---
title: Backend Performance
description: Background processing with BullMQ, API response optimization with compression, pagination, conditional requests, streaming responses, serverless cold start mitigation, and rate limiting
tags:
  [
    backend,
    background-jobs,
    bullmq,
    queue,
    pagination,
    compression,
    rate-limiting,
    serverless,
    cold-start,
    etag,
    streaming,
  ]
---

# Backend Performance

## Async Background Processing

```typescript
// Synchronous (slow response)
app.post('/send-email', async (req, res) => {
  await sendEmail(req.body); // 3 seconds
  res.json({ success: true });
});

// Queue job (fast response)
import { Queue, Worker } from 'bullmq';

const emailQueue = new Queue('emails', {
  connection: { host: 'localhost', port: 6379 },
});

app.post('/send-email', async (req, res) => {
  await emailQueue.add('send', req.body);
  res.json({ success: true, message: 'Email queued' });
});

// Process jobs in background worker
const worker = new Worker(
  'emails',
  async (job) => {
    await sendEmail(job.data);
  },
  { connection: { host: 'localhost', port: 6379 } },
);
```

## API Response Optimization

```typescript
// 1. Compression
import compression from 'compression';
app.use(compression()); // Gzip responses

// 2. Pagination
app.get('/api/posts', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 20;

  const posts = await db.posts.findAll({
    offset: (page - 1) * limit,
    limit: limit,
  });

  res.json({
    data: posts,
    pagination: {
      page,
      limit,
      total: await db.posts.count(),
    },
  });
});

// 3. Field filtering (GraphQL-style)
app.get('/api/users/:id', async (req, res) => {
  const fields = req.query.fields?.split(',') || ['id', 'name', 'email'];

  const user = await db.users.findById(req.params.id, {
    attributes: fields,
  });

  res.json(user);
});
```

## Partial Responses (Sparse Fieldsets)

```ts
// JSON:API sparse fieldsets
app.get('/api/users/:id', async (req, res) => {
  const fields = req.query['fields[user]']?.split(',');
  const defaultFields = ['id', 'name', 'email'];

  const user = await db.users.findById(req.params.id, {
    attributes: fields || defaultFields,
  });

  res.json({ data: user });
});

// GraphQL-style field selection via query param
// GET /api/posts/123?fields=id,title,author.name
app.get('/api/posts/:id', async (req, res) => {
  const fields = req.query.fields?.split(',') || ['*'];
  const post = await db.posts.findById(req.params.id, {
    select: Object.fromEntries(fields.map((f: string) => [f, true])),
  });

  res.json(post);
});
```

## Conditional Requests (ETag / If-None-Match)

```ts
import { createHash } from 'crypto';

function generateETag(data: unknown): string {
  return createHash('md5').update(JSON.stringify(data)).digest('hex');
}

app.get('/api/products/:id', async (req, res) => {
  const product = await db.products.findById(req.params.id);
  const etag = `"${generateETag(product)}"`;

  res.setHeader('ETag', etag);

  if (req.headers['if-none-match'] === etag) {
    return res.status(304).end();
  }

  res.json(product);
});
```

## Streaming Responses

```ts
import { Readable } from 'stream';

app.get('/api/export/users', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Transfer-Encoding', 'chunked');

  res.write('[');
  let first = true;

  const cursor = db.users.find().cursor();
  for await (const user of cursor) {
    if (!first) res.write(',');
    res.write(JSON.stringify(user));
    first = false;
  }

  res.write(']');
  res.end();
});

// Node.js Web Streams API (fetch-compatible)
app.get('/api/stream', (req, res) => {
  const stream = new ReadableStream({
    async pull(controller) {
      const chunk = await getNextChunk();
      if (chunk) {
        controller.enqueue(new TextEncoder().encode(chunk));
      } else {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  });
});
```

## Serverless Optimization

### Cold Start Mitigation

```yaml
# AWS Lambda — provisioned concurrency keeps instances warm
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: nodejs20.x
      MemorySize: 512
      Timeout: 30
      ProvisionedConcurrencyConfig:
        ProvisionedConcurrentExecutions: 5
```

```ts
// Keep-warm pattern: scheduled invocation every 5 minutes
// AWS EventBridge rule
// { "schedule": "rate(5 minutes)", "target": "my-lambda-arn" }

// Handler detects warm-up events and returns early
export const handler = async (event: any) => {
  if (event.source === 'aws.events') {
    return { statusCode: 200, body: 'warm' };
  }
  return processRequest(event);
};
```

```text
Memory/timeout budgeting:
  128 MB  — Simple transforms, redirects
  256 MB  — API handlers, light DB queries
  512 MB  — Image processing, moderate computation
  1024 MB — Heavy computation, ML inference

  Timeout guidelines:
  API Gateway limit: 29s max
  Direct invoke: up to 15 min
  Set timeout to 2x expected P95 duration
```

### Connection Pooling for Serverless

```ts
// RDS Proxy — managed connection pooling for AWS Lambda
// Configure in AWS console, then connect via proxy endpoint
import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.RDS_PROXY_ENDPOINT,
  max: 1, // Single connection per Lambda instance
  ssl: { rejectUnauthorized: false },
});

// Reuse connection across invocations (module-level)
let client: any;

export const handler = async () => {
  if (!client) {
    client = await pool.connect();
  }
  const result = await client.query('SELECT * FROM users LIMIT 10');
  return { statusCode: 200, body: JSON.stringify(result.rows) };
};
```

```text
Serverless connection pooling options:
  AWS RDS Proxy     — Managed, supports PostgreSQL/MySQL
  PgBouncer         — Self-hosted, PostgreSQL only
  Neon              — Serverless Postgres with built-in pooling
  PlanetScale       — Serverless MySQL with HTTP-based queries
```

## Rate Limiting

```ts
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: 'Too many requests, please try again later',
});

app.use('/api/', apiLimiter);

const authLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
});

app.post('/api/auth/login', authLimiter, loginHandler);
```
