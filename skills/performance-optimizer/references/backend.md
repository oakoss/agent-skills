---
title: Backend Performance
description: Async background processing with BullMQ queues, API response optimization with compression and pagination, and rate limiting configuration
tags:
  [
    backend,
    background-jobs,
    bullmq,
    queue,
    pagination,
    compression,
    rate-limiting,
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

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';

// General API rate limit
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests, please try again later',
});

app.use('/api/', apiLimiter);

// Stricter limit for expensive endpoints
const authLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5, // 5 requests per hour
  skipSuccessfulRequests: true,
});

app.post('/api/auth/login', authLimiter, loginHandler);
```
