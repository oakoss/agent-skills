---
title: Testing Patterns
description: Testing tRPC procedures with createCaller, integration testing with adapters, and mocking context
tags:
  [
    testing,
    createCaller,
    createCallerFactory,
    vitest,
    mock-context,
    integration-test,
  ]
---

# Testing Patterns

## Unit Testing with createCallerFactory

The recommended approach for testing individual procedures:

```ts
import { describe, expect, it } from 'vitest';
import { appRouter, createCaller } from '../routers/_app';

describe('user router', () => {
  it('creates a user', async () => {
    const caller = createCaller({
      session: null,
      db: testDb,
    });

    const user = await caller.user.create({
      name: 'Alice',
      email: 'alice@example.com',
    });

    expect(user).toMatchObject({
      name: 'Alice',
      email: 'alice@example.com',
    });
    expect(user.id).toBeDefined();
  });

  it('lists users', async () => {
    const caller = createCaller({
      session: null,
      db: testDb,
    });

    const users = await caller.user.list();
    expect(users).toBeInstanceOf(Array);
  });
});
```

## Testing Protected Procedures

Mock the auth context to test procedures behind middleware:

```ts
import { describe, expect, it } from 'vitest';
import { TRPCError } from '@trpc/server';

describe('protected routes', () => {
  it('rejects unauthenticated requests', async () => {
    const caller = createCaller({
      session: null,
      db: testDb,
    });

    await expect(caller.post.create({ title: 'Test' })).rejects.toThrow(
      TRPCError,
    );
    await expect(caller.post.create({ title: 'Test' })).rejects.toMatchObject({
      code: 'UNAUTHORIZED',
    });
  });

  it('allows authenticated requests', async () => {
    const caller = createCaller({
      session: { user: { id: 'user-1', role: 'user' } },
      db: testDb,
    });

    const post = await caller.post.create({ title: 'Test Post' });
    expect(post.title).toBe('Test Post');
    expect(post.authorId).toBe('user-1');
  });
});
```

## Testing Input Validation

```ts
import { describe, expect, it } from 'vitest';
import { TRPCError } from '@trpc/server';

describe('input validation', () => {
  it('rejects invalid email', async () => {
    const caller = createCaller({ session: null, db: testDb });

    await expect(
      caller.user.create({ name: 'Alice', email: 'not-an-email' }),
    ).rejects.toThrow(TRPCError);
  });

  it('rejects empty name', async () => {
    const caller = createCaller({ session: null, db: testDb });

    await expect(
      caller.user.create({ name: '', email: 'alice@example.com' }),
    ).rejects.toThrow(TRPCError);
  });
});
```

## Integration Testing with HTTP

Test the full request/response cycle:

```ts
import { describe, expect, it, beforeAll, afterAll } from 'vitest';
import { createHTTPServer } from '@trpc/server/adapters/standalone';
import { createTRPCClient, httpBatchLink } from '@trpc/client';
import { type AppRouter, appRouter } from '../routers/_app';

describe('API integration', () => {
  let server: ReturnType<typeof createHTTPServer>;
  let client: ReturnType<typeof createTRPCClient<AppRouter>>;

  beforeAll(() => {
    server = createHTTPServer({
      router: appRouter,
      createContext: () => ({ session: null, db: testDb }),
    });
    server.listen(0);
    const { port } = server.server.address() as { port: number };

    client = createTRPCClient<AppRouter>({
      links: [httpBatchLink({ url: `http://localhost:${port}` })],
    });
  });

  afterAll(() => {
    server.server.close();
  });

  it('creates and retrieves a user', async () => {
    const created = await client.user.create.mutate({
      name: 'Bob',
      email: 'bob@example.com',
    });

    const fetched = await client.user.byId.query(created.id);
    expect(fetched).toMatchObject({ name: 'Bob' });
  });
});
```

## Testing with a Helper Factory

Create a reusable test helper:

```ts
import { createCaller } from '../routers/_app';

function createTestCaller(overrides?: Partial<Context>) {
  return createCaller({
    session: null,
    db: testDb,
    ...overrides,
  });
}

function createAuthenticatedCaller(
  user: { id: string; role: string } = { id: 'test-user', role: 'user' },
) {
  return createTestCaller({
    session: { user },
  });
}
```

```ts
describe('admin routes', () => {
  it('allows admin access', async () => {
    const caller = createAuthenticatedCaller({ id: 'admin-1', role: 'admin' });
    const users = await caller.admin.listAllUsers();
    expect(users).toBeDefined();
  });

  it('blocks non-admin access', async () => {
    const caller = createAuthenticatedCaller({ id: 'user-1', role: 'user' });
    await expect(caller.admin.listAllUsers()).rejects.toMatchObject({
      code: 'FORBIDDEN',
    });
  });
});
```

## Testing Error Formatting

```ts
import { describe, expect, it } from 'vitest';

describe('error formatting', () => {
  it('returns Zod errors for invalid input', async () => {
    const caller = createCaller({ session: null, db: testDb });

    try {
      await caller.user.create({ name: '', email: 'invalid' });
    } catch (err) {
      expect(err).toBeInstanceOf(TRPCError);
      expect((err as TRPCError).code).toBe('BAD_REQUEST');
    }
  });
});
```
