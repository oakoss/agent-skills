---
title: Supertest Patterns
description: Integration testing with supertest for Express, Fastify, and Hono applications including request chaining, authentication, and file uploads
tags:
  [supertest, express, fastify, hono, integration-test, request, response, http]
---

# Supertest Patterns

## Express Integration

Supertest accepts an Express app instance directly. No need to call `app.listen()` in tests:

```ts
import request from 'supertest';
import { createApp } from '../src/app';

const app = createApp();

describe('GET /api/users', () => {
  it('returns a list of users', async () => {
    const response = await request(app)
      .get('/api/users')
      .expect('Content-Type', /json/)
      .expect(200);

    expect(response.body).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          id: expect.any(String),
          name: expect.any(String),
        }),
      ]),
    );
  });
});
```

Export a factory function (`createApp`) rather than a singleton to ensure test isolation.

## Fastify Integration

Fastify provides a built-in `inject` method that avoids starting a real server. Prefer `inject` over supertest when possible:

```ts
import Fastify from 'fastify';
import { userRoutes } from '../src/routes/users';

describe('GET /api/users', () => {
  const app = Fastify();

  beforeAll(async () => {
    app.register(userRoutes);
    await app.ready();
  });

  afterAll(async () => {
    await app.close();
  });

  it('returns users', async () => {
    const response = await app.inject({
      method: 'GET',
      url: '/api/users',
    });

    expect(response.statusCode).toBe(200);
    expect(response.json()).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ id: expect.any(String) }),
      ]),
    );
  });
});
```

If you must use supertest with Fastify, pass `fastify.server` (not the Fastify instance):

```ts
import request from 'supertest';

beforeAll(async () => {
  await app.ready();
});

it('works with supertest', async () => {
  await request(app.server).get('/api/users').expect(200);
});
```

## Hono Integration

Hono provides `app.request()` and a type-safe `testClient`:

```ts
import { Hono } from 'hono';
import { testClient } from 'hono/testing';

const app = new Hono()
  .get('/api/users', (c) => c.json([{ id: '1', name: 'Alice' }]))
  .post('/api/users', async (c) => {
    const body = await c.req.json();
    return c.json({ id: '2', ...body }, 201);
  });

describe('User API', () => {
  const client = testClient(app);

  it('lists users', async () => {
    const response = await client.api.users.$get();
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toHaveLength(1);
  });

  it('creates a user', async () => {
    const response = await client.api.users.$post({
      json: { name: 'Bob' },
    });

    expect(response.status).toBe(201);
  });
});
```

Chain route definitions on the Hono instance so `testClient` infers types correctly.

## Request Chaining

Supertest supports fluent chaining for building requests:

```ts
it('creates a resource with authentication', async () => {
  const response = await request(app)
    .post('/api/posts')
    .set('Authorization', `Bearer ${token}`)
    .set('Accept', 'application/json')
    .send({ title: 'New Post', content: 'Body text' })
    .expect('Content-Type', /json/)
    .expect(201);

  expect(response.body.id).toBeDefined();
  expect(response.body.title).toBe('New Post');
});
```

Order does not matter for `.set()` and `.send()`, but `.expect()` assertions run after the request completes.

## Cookie and Session Persistence

Use `request.agent()` to maintain cookies across requests:

```ts
describe('authenticated flow', () => {
  const agent = request.agent(app);

  it('logs in and accesses protected resource', async () => {
    await agent
      .post('/api/login')
      .send({ email: 'user@example.com', password: 'password' })
      .expect(200);

    await agent
      .get('/api/profile')
      .expect(200)
      .expect((res) => {
        expect(res.body.email).toBe('user@example.com');
      });
  });
});
```

## Query Parameters

```ts
it('filters by status', async () => {
  await request(app)
    .get('/api/orders')
    .query({ status: 'pending', page: 1, limit: 10 })
    .expect(200)
    .expect((res) => {
      expect(res.body.data).toSatisfy((items: unknown[]) =>
        items.every((item: any) => item.status === 'pending'),
      );
    });
});
```

## File Uploads

```ts
it('uploads an avatar image', async () => {
  await request(app)
    .post('/api/users/1/avatar')
    .set('Authorization', `Bearer ${token}`)
    .attach('avatar', Buffer.from('fake-image'), 'avatar.png')
    .expect(200)
    .expect((res) => {
      expect(res.body.avatarUrl).toMatch(/\.png$/);
    });
});
```

## Testing Different HTTP Methods

```ts
describe('REST operations', () => {
  let createdId: string;

  it('POST creates resource', async () => {
    const res = await request(app)
      .post('/api/items')
      .send({ name: 'Widget' })
      .expect(201);

    createdId = res.body.id;
  });

  it('GET retrieves resource', async () => {
    await request(app)
      .get(`/api/items/${createdId}`)
      .expect(200)
      .expect((res) => {
        expect(res.body.name).toBe('Widget');
      });
  });

  it('PATCH updates resource', async () => {
    await request(app)
      .patch(`/api/items/${createdId}`)
      .send({ name: 'Updated Widget' })
      .expect(200);
  });

  it('DELETE removes resource', async () => {
    await request(app).delete(`/api/items/${createdId}`).expect(204);
  });
});
```

## Testing Middleware

Test middleware effects through endpoints rather than testing middleware in isolation:

```ts
describe('rate limiting middleware', () => {
  it('allows requests under the limit', async () => {
    await request(app).get('/api/data').expect(200);
  });

  it('returns 429 when rate limit exceeded', async () => {
    const requests = Array.from({ length: 101 }, () =>
      request(app).get('/api/data'),
    );

    const responses = await Promise.all(requests);
    const tooMany = responses.filter((r) => r.status === 429);

    expect(tooMany.length).toBeGreaterThan(0);
  });
});
```

## Error Response Testing

```ts
it('returns 404 for missing resource', async () => {
  await request(app)
    .get('/api/items/nonexistent')
    .expect(404)
    .expect((res) => {
      expect(res.body).toEqual({
        error: 'Not Found',
        message: expect.any(String),
      });
    });
});

it('returns 422 for invalid input', async () => {
  await request(app)
    .post('/api/items')
    .send({ name: '' })
    .expect(422)
    .expect((res) => {
      expect(res.body.errors).toBeDefined();
    });
});
```

## Common Patterns Table

| Pattern            | Supertest                 | Fastify inject                        | Hono testClient                |
| ------------------ | ------------------------- | ------------------------------------- | ------------------------------ |
| GET request        | `request(app).get(url)`   | `app.inject({ method: 'GET', url })`  | `client.path.$get()`           |
| POST with JSON     | `.post(url).send(body)`   | `inject({ method: 'POST', payload })` | `client.path.$post({ json })`  |
| Set header         | `.set('Key', 'value')`    | `inject({ headers: { key: val } })`   | Pass in request init           |
| Assert status      | `.expect(200)`            | `expect(res.statusCode).toBe(200)`    | `expect(res.status).toBe(200)` |
| Assert JSON        | `.expect({ key: 'val' })` | `expect(res.json())`                  | `await res.json()`             |
| Cookie persistence | `request.agent(app)`      | Manual cookie forwarding              | Manual cookie forwarding       |
