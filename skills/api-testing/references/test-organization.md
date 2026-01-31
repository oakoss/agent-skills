---
title: Test Organization
description: API test structure, fixtures, factories, setup/teardown patterns, database seeding, and test isolation strategies
tags:
  [
    organization,
    fixtures,
    factories,
    setup,
    teardown,
    isolation,
    database,
    seed,
  ]
---

# Test Organization

## Directory Structure

Organize API tests alongside or mirroring the source structure:

```sh
src/
  routes/
    users.ts
    posts.ts
tests/
  setup.ts              # Global test setup (MSW server, DB connection)
  helpers/
    request.ts          # Shared supertest helpers
    factories.ts        # Test data factories
    fixtures.ts         # Static test data
  api/
    users.test.ts       # Tests for /api/users
    posts.test.ts       # Tests for /api/posts
  mocks/
    handlers/
      users.ts          # MSW handlers for user endpoints
      posts.ts          # MSW handlers for post endpoints
    handlers.ts         # Combined handler exports
    server.ts           # MSW server instance
```

## Global Test Setup

Create a setup file that initializes shared resources:

```ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

beforeAll(async () => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(async () => {
  server.close();
});
```

Register in `vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    setupFiles: ['./tests/setup.ts'],
    testTimeout: 10_000,
  },
});
```

## Test Data Factories

Factories generate test data with sensible defaults and allow overrides:

```ts
type User = {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  createdAt: string;
};

let counter = 0;

function createUser(overrides: Partial<User> = {}): User {
  counter += 1;
  return {
    id: `user-${counter}`,
    name: `User ${counter}`,
    email: `user${counter}@example.com`,
    role: 'user',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

function createUsers(count: number, overrides: Partial<User> = {}): User[] {
  return Array.from({ length: count }, () => createUser(overrides));
}
```

Usage in tests:

```ts
it('returns admin users only', async () => {
  const admin = createUser({ role: 'admin' });
  const regular = createUser({ role: 'user' });

  server.use(
    http.get('/api/users', ({ request }) => {
      const url = new URL(request.url);
      const role = url.searchParams.get('role');

      const users = [admin, regular].filter((u) => !role || u.role === role);

      return HttpResponse.json(users);
    }),
  );

  const response = await request(app)
    .get('/api/users')
    .query({ role: 'admin' })
    .expect(200);

  expect(response.body).toHaveLength(1);
  expect(response.body[0].role).toBe('admin');
});
```

## Static Fixtures

Use fixtures for stable test data that does not change between tests:

```ts
export const fixtures = {
  validUser: {
    name: 'Alice Smith',
    email: 'alice@example.com',
  },
  invalidUser: {
    name: '',
    email: 'not-an-email',
  },
  validPost: {
    title: 'Test Post',
    content: 'This is a test post with sufficient content.',
  },
} as const;
```

Prefer factories for data that needs uniqueness. Use fixtures for validation test cases and error scenarios.

## Shared Request Helpers

Reduce boilerplate with helper functions:

```ts
import request from 'supertest';
import { type Express } from 'express';

export function createAuthenticatedAgent(app: Express, token: string) {
  const agent = request(app);
  const originalGet = agent.get.bind(agent);
  const originalPost = agent.post.bind(agent);

  return {
    get: (url: string) =>
      originalGet(url).set('Authorization', `Bearer ${token}`),
    post: (url: string) =>
      originalPost(url).set('Authorization', `Bearer ${token}`),
  };
}

export async function loginAs(
  app: Express,
  credentials: { email: string; password: string },
) {
  const response = await request(app).post('/api/auth/login').send(credentials);

  return response.body.token as string;
}
```

## Database Setup and Teardown

For tests that hit a real database, isolate state between tests:

```ts
import { beforeEach, afterAll } from 'vitest';
import { db } from '../src/db';
import { migrate } from '../src/db/migrate';

beforeEach(async () => {
  await db.execute('BEGIN');
});

afterEach(async () => {
  await db.execute('ROLLBACK');
});

afterAll(async () => {
  await db.close();
});
```

Transaction rollback ensures each test starts with a clean database state without re-seeding.

### In-Memory Database Alternative

For MongoDB, use `mongodb-memory-server` to avoid external dependencies:

```ts
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';

let mongoServer: MongoMemoryServer;

beforeAll(async () => {
  mongoServer = await MongoMemoryServer.create();
  await mongoose.connect(mongoServer.getUri());
});

afterEach(async () => {
  const collections = await mongoose.connection.db.collections();
  for (const collection of collections) {
    await collection.deleteMany({});
  }
});

afterAll(async () => {
  await mongoose.disconnect();
  await mongoServer.stop();
});
```

## Test Isolation Strategies

| Strategy             | Pros                     | Cons                          | Best For                       |
| -------------------- | ------------------------ | ----------------------------- | ------------------------------ |
| Transaction rollback | Fast, reliable           | Requires transaction support  | SQL databases                  |
| Truncate tables      | Works with any DB        | Slower than rollback          | NoSQL or cross-table relations |
| In-memory DB         | No external dependencies | May differ from production    | CI pipelines, rapid iteration  |
| MSW mocking          | No database needed       | Does not test real DB queries | API contract testing           |
| Docker test DB       | Production-identical     | Slower startup                | Integration test suites        |

## Grouping Related Tests

Use `describe` blocks to group by endpoint and operation:

```ts
describe('/api/users', () => {
  describe('GET /', () => {
    it('returns all users', async () => {
      /* ... */
    });
    it('filters by role', async () => {
      /* ... */
    });
    it('paginates results', async () => {
      /* ... */
    });
  });

  describe('POST /', () => {
    it('creates a user with valid data', async () => {
      /* ... */
    });
    it('rejects invalid email', async () => {
      /* ... */
    });
    it('rejects duplicate email', async () => {
      /* ... */
    });
  });

  describe('GET /:id', () => {
    it('returns the user', async () => {
      /* ... */
    });
    it('returns 404 for unknown id', async () => {
      /* ... */
    });
  });

  describe('DELETE /:id', () => {
    it('requires authentication', async () => {
      /* ... */
    });
    it('requires admin role', async () => {
      /* ... */
    });
    it('deletes the user', async () => {
      /* ... */
    });
  });
});
```

## Parallel vs Sequential Tests

Vitest runs test files in parallel by default. For API tests with shared state:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // Run API test files sequentially if they share a database
    fileParallelism: false,

    // Or use pool threads with single thread
    pool: 'forks',
    poolOptions: {
      forks: { singleFork: true },
    },
  },
});
```

Tests within a single file run sequentially by default. Use `concurrent` for independent tests:

```ts
describe('read-only endpoints', () => {
  it.concurrent('GET /api/users returns 200', async () => {
    /* ... */
  });
  it.concurrent('GET /api/posts returns 200', async () => {
    /* ... */
  });
  it.concurrent('GET /api/tags returns 200', async () => {
    /* ... */
  });
});
```

## Environment Variables

Use Vitest `env` configuration to set test-specific variables:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    env: {
      DATABASE_URL: 'postgresql://localhost:5432/test_db',
      API_SECRET: 'test-secret',
      NODE_ENV: 'test',
    },
  },
});
```

Avoid loading `.env` files in tests. Explicit configuration prevents accidental use of production credentials.
