---
title: Assertion Patterns
description: Response assertions for status codes, headers, body content, error responses, and schema validation with Zod
tags: [assertions, status-code, headers, body, schema, zod, validation, error]
---

# Assertion Patterns

## Status Code Assertions

Supertest supports chained status code checks:

```ts
await request(app).get('/api/users').expect(200);
await request(app).post('/api/users').send(data).expect(201);
await request(app).delete('/api/users/1').expect(204);
await request(app).get('/api/missing').expect(404);
await request(app).post('/api/users').send({}).expect(422);
```

For programmatic assertions, use the response object:

```ts
const response = await request(app).get('/api/users');
expect(response.status).toBe(200);
expect(response.statusCode).toBe(200);
```

## Header Assertions

Assert exact values or patterns:

```ts
await request(app)
  .get('/api/users')
  .expect('Content-Type', /application\/json/)
  .expect('Cache-Control', 'no-store');
```

Check custom headers from the response object:

```ts
const response = await request(app).get('/api/items');
expect(response.headers['x-total-count']).toBe('42');
expect(response.headers['x-request-id']).toBeDefined();
```

## CORS Header Assertions

```ts
it('includes CORS headers', async () => {
  const response = await request(app)
    .options('/api/users')
    .set('Origin', 'https://example.com')
    .set('Access-Control-Request-Method', 'GET');

  expect(response.headers['access-control-allow-origin']).toBe(
    'https://example.com',
  );
  expect(response.headers['access-control-allow-methods']).toContain('GET');
});
```

## Response Body Assertions

### Exact Match

```ts
await request(app)
  .get('/api/config')
  .expect(200)
  .expect({ theme: 'dark', language: 'en' });
```

### Partial Match with expect.objectContaining

```ts
const response = await request(app).get('/api/users/1').expect(200);

expect(response.body).toEqual(
  expect.objectContaining({
    name: 'Alice',
    email: 'alice@example.com',
  }),
);
```

### Array Assertions

```ts
const response = await request(app).get('/api/users').expect(200);

expect(response.body).toHaveLength(3);

expect(response.body).toEqual(
  expect.arrayContaining([expect.objectContaining({ name: 'Alice' })]),
);

expect(response.body).toSatisfy((users: { role: string }[]) =>
  users.every((u) => u.role === 'user'),
);
```

### Nested Object Assertions

```ts
const response = await request(app).get('/api/users/1/profile').expect(200);

expect(response.body).toEqual({
  user: expect.objectContaining({
    id: expect.any(String),
    name: expect.any(String),
    address: expect.objectContaining({
      city: expect.any(String),
      country: expect.any(String),
    }),
  }),
  metadata: expect.objectContaining({
    createdAt: expect.stringMatching(/^\d{4}-\d{2}-\d{2}/),
  }),
});
```

## Callback-Style Assertions

Supertest `.expect()` accepts a callback for custom logic:

```ts
await request(app)
  .get('/api/users')
  .expect(200)
  .expect((res) => {
    expect(res.body.length).toBeGreaterThan(0);
    expect(res.body[0]).toHaveProperty('id');
    expect(res.body[0]).toHaveProperty('name');
  });
```

## Schema Validation with Zod

Define response schemas and validate against them:

```ts
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  email: z.string().email(),
  role: z.enum(['admin', 'user']),
  createdAt: z.string().datetime(),
});

const UsersResponseSchema = z.array(UserSchema);

it('returns valid user data', async () => {
  const response = await request(app).get('/api/users').expect(200);

  const result = UsersResponseSchema.safeParse(response.body);
  expect(result.success).toBe(true);
});
```

### Custom Vitest Matcher for Zod

Create a reusable matcher:

```ts
import { type ZodSchema } from 'zod';
import { expect } from 'vitest';

expect.extend({
  toMatchSchema(received: unknown, schema: ZodSchema) {
    const result = schema.safeParse(received);

    if (result.success) {
      return {
        pass: true,
        message: () => 'Expected data not to match schema',
      };
    }

    return {
      pass: false,
      message: () =>
        `Schema validation failed:\n${result.error.issues
          .map((i) => `  - ${i.path.join('.')}: ${i.message}`)
          .join('\n')}`,
    };
  },
});

declare module 'vitest' {
  interface Assertion {
    toMatchSchema(schema: ZodSchema): void;
  }
}
```

Usage:

```ts
it('returns valid user data', async () => {
  const response = await request(app).get('/api/users').expect(200);
  expect(response.body).toMatchSchema(UsersResponseSchema);
});
```

### Shared Schemas Between Source and Tests

Reuse Zod schemas from your application code to ensure test assertions match the actual API contract:

```ts
import { UserResponseSchema } from '../src/schemas/user';

it('conforms to the API contract', async () => {
  const response = await request(app).get('/api/users/1').expect(200);
  expect(() => UserResponseSchema.parse(response.body)).not.toThrow();
});
```

## Error Response Assertions

### Standard Error Format

```ts
const ErrorResponseSchema = z.object({
  error: z.string(),
  message: z.string(),
  statusCode: z.number(),
});

it('returns structured error for invalid input', async () => {
  const response = await request(app)
    .post('/api/users')
    .send({ email: 'invalid' })
    .expect(422);

  expect(response.body).toMatchObject({
    error: 'Validation Error',
    statusCode: 422,
  });
  expect(response.body.message).toBeDefined();
});
```

### Validation Error Details

```ts
it('returns field-level validation errors', async () => {
  const response = await request(app)
    .post('/api/users')
    .send({ name: '', email: 'bad' })
    .expect(422);

  expect(response.body.errors).toEqual(
    expect.arrayContaining([
      expect.objectContaining({
        field: 'name',
        message: expect.any(String),
      }),
      expect.objectContaining({
        field: 'email',
        message: expect.any(String),
      }),
    ]),
  );
});
```

## Pagination Assertions

```ts
it('returns paginated results', async () => {
  const response = await request(app)
    .get('/api/posts')
    .query({ page: 2, limit: 10 })
    .expect(200);

  expect(response.body).toEqual(
    expect.objectContaining({
      data: expect.any(Array),
      meta: expect.objectContaining({
        page: 2,
        limit: 10,
        total: expect.any(Number),
        totalPages: expect.any(Number),
      }),
    }),
  );

  expect(response.body.data.length).toBeLessThanOrEqual(10);
});
```

## Authentication and Authorization Assertions

```ts
describe('protected endpoints', () => {
  it('returns 401 without token', async () => {
    await request(app).get('/api/admin/users').expect(401);
  });

  it('returns 403 with insufficient permissions', async () => {
    await request(app)
      .get('/api/admin/users')
      .set('Authorization', `Bearer ${userToken}`)
      .expect(403);
  });

  it('returns 200 with admin token', async () => {
    await request(app)
      .get('/api/admin/users')
      .set('Authorization', `Bearer ${adminToken}`)
      .expect(200);
  });
});
```

## Timing Assertions

```ts
it('responds within acceptable time', async () => {
  const start = performance.now();

  await request(app).get('/api/health').expect(200);

  const duration = performance.now() - start;
  expect(duration).toBeLessThan(200);
});
```

## Common Assertion Patterns Table

| What to Assert    | Supertest Chain                   | Vitest Expect                                         |
| ----------------- | --------------------------------- | ----------------------------------------------------- |
| Status code       | `.expect(200)`                    | `expect(res.status).toBe(200)`                        |
| Content-Type      | `.expect('Content-Type', /json/)` | `expect(res.headers['content-type']).toMatch(/json/)` |
| Exact body        | `.expect({ key: 'val' })`         | `expect(res.body).toEqual({ key: 'val' })`            |
| Body shape        | callback in `.expect()`           | `expect(res.body).toMatchObject({})`                  |
| Array length      | callback in `.expect()`           | `expect(res.body).toHaveLength(n)`                    |
| Property exists   | callback in `.expect()`           | `expect(res.body).toHaveProperty('key')`              |
| Schema validation | N/A                               | `expect(res.body).toMatchSchema(schema)`              |
| Header exists     | `.expect('X-Key', /.*/)`          | `expect(res.headers['x-key']).toBeDefined()`          |
