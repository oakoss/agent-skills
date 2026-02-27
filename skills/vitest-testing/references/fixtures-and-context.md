---
title: Fixtures and Context
description: Test fixtures with test.extend, fixture scoping, auto fixtures, composable fixtures, test.override, and config-injected fixtures
tags:
  [fixtures, test.extend, scope, auto, inject, provide, test.override, context]
---

# Fixtures and Context

## Basic `test.extend`

Define reusable, typed fixtures with automatic setup and teardown:

```ts
import { test as base, expect } from 'vitest';

interface TodoFixtures {
  db: Database;
  todos: TodoService;
}

const test = base.extend<TodoFixtures>({
  db: async ({}, use) => {
    const db = await createTestDatabase();
    await use(db);
    await db.close();
  },

  todos: async ({ db }, use) => {
    const service = new TodoService(db);
    await use(service);
  },
});

test('creates a todo', async ({ todos }) => {
  const todo = await todos.create({ title: 'Write tests' });
  expect(todo.title).toBe('Write tests');
});

test('lists todos', async ({ todos }) => {
  await todos.create({ title: 'First' });
  await todos.create({ title: 'Second' });
  const all = await todos.list();
  expect(all).toHaveLength(2);
});
```

Each test gets a fresh `db` and `todos` instance. Teardown runs automatically after `use()` returns.

## Fixture Scoping

Control how often fixtures are created:

### Per-Test Scope (Default)

```ts
const test = base.extend<{ server: TestServer }>({
  server: async ({}, use) => {
    const server = await startServer();
    await use(server);
    await server.close();
  },
});
```

A new `server` is created and destroyed for every test.

### Per-File Scope

Share a fixture across all tests in a file:

```ts
const test = base.extend<{ server: TestServer }>({
  server: [
    async ({}, use) => {
      const server = await startServer();
      await use(server);
      await server.close();
    },
    { scope: 'file' },
  ],
});
```

The server starts once before the first test and closes after the last test in the file.

### Per-Worker Scope

Share across all files in a worker thread:

```ts
const test = base.extend<{ browser: Browser }>({
  browser: [
    async ({}, use) => {
      const browser = await chromium.launch();
      await use(browser);
      await browser.close();
    },
    { scope: 'worker' },
  ],
});
```

## Auto Fixtures

Fixtures with `auto: true` run for every test without being referenced in test parameters:

```ts
const test = base.extend<{ logging: void }>({
  logging: [
    async ({}, use) => {
      console.log('Test starting');
      await use();
      console.log('Test finished');
    },
    { auto: true },
  ],
});

test('runs with auto logging', () => {
  expect(true).toBe(true);
});
```

Combine `auto` with scoping:

```ts
const test = base.extend<{ globalSetup: void }>({
  globalSetup: [
    async ({}, use) => {
      await seedDatabase();
      await use();
      await cleanDatabase();
    },
    { auto: true, scope: 'worker' },
  ],
});
```

## Composing Fixtures

Build fixture layers by extending from an already-extended test:

```ts
import { test as base, expect } from 'vitest';

interface AuthFixtures {
  auth: AuthService;
  token: string;
}

const authTest = base.extend<AuthFixtures>({
  auth: async ({}, use) => {
    const auth = new AuthService();
    await use(auth);
  },

  token: async ({ auth }, use) => {
    const token = await auth.createToken({ userId: 'test-user' });
    await use(token);
  },
});

interface ApiFixtures {
  api: ApiClient;
}

const test = authTest.extend<ApiFixtures>({
  api: async ({ token }, use) => {
    const client = new ApiClient({ token });
    await use(client);
    await client.disconnect();
  },
});

test('fetches user profile', async ({ api }) => {
  const profile = await api.get('/profile');
  expect(profile.userId).toBe('test-user');
});
```

The `api` fixture receives `token` from the auth layer automatically.

## `test.override`

Override fixture values within a `describe` block:

```ts
import { describe, expect } from 'vitest';

const test = base.extend<{ locale: string }>({
  locale: async ({}, use) => {
    await use('en-US');
  },
});

test('default locale', ({ locale }) => {
  expect(locale).toBe('en-US');
});

describe('French locale', () => {
  test.override({ locale: 'fr-FR' });

  test('uses french locale', ({ locale }) => {
    expect(locale).toBe('fr-FR');
  });
});
```

`test.override` must be called at the top level of a `describe` block. It overrides fixture values for all tests in that suite.

## Injected Fixtures from Config

Pass values from `vitest.config.ts` into tests with `provide` and `inject`:

### Config Side

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    provide: {
      apiBaseUrl: 'http://localhost:3000',
      dbConnectionString: 'postgresql://test@localhost/testdb',
    },
  },
});
```

### Declare Types

```ts
declare module 'vitest' {
  export interface ProvidedContext {
    apiBaseUrl: string;
    dbConnectionString: string;
  }
}
```

### Test Side

```ts
import { inject, test, expect } from 'vitest';

test('uses injected config', () => {
  const baseUrl = inject('apiBaseUrl');
  expect(baseUrl).toBe('http://localhost:3000');
});
```

### Using Injected Values in Fixtures

```ts
import { inject, test as base } from 'vitest';

const test = base.extend<{ api: ApiClient }>({
  api: async ({}, use) => {
    const baseUrl = inject('apiBaseUrl');
    const client = new ApiClient(baseUrl);
    await use(client);
  },
});
```

## Migration from `beforeEach`

### Before: Manual Setup/Teardown

```ts
import { afterEach, beforeEach, expect, test } from 'vitest';

let db: Database;
let service: UserService;

beforeEach(async () => {
  db = await createTestDatabase();
  service = new UserService(db);
});

afterEach(async () => {
  await db.close();
});

test('creates user', async () => {
  const user = await service.create({ name: 'Alice' });
  expect(user.name).toBe('Alice');
});

test('finds user', async () => {
  await service.create({ name: 'Bob' });
  const found = await service.findByName('Bob');
  expect(found).toBeDefined();
});
```

### After: Fixtures

```ts
import { test as base, expect } from 'vitest';

interface UserFixtures {
  db: Database;
  users: UserService;
}

const test = base.extend<UserFixtures>({
  db: async ({}, use) => {
    const db = await createTestDatabase();
    await use(db);
    await db.close();
  },

  users: async ({ db }, use) => {
    await use(new UserService(db));
  },
});

test('creates user', async ({ users }) => {
  const user = await users.create({ name: 'Alice' });
  expect(user.name).toBe('Alice');
});

test('finds user', async ({ users }) => {
  await users.create({ name: 'Bob' });
  const found = await users.findByName('Bob');
  expect(found).toBeDefined();
});
```

Advantages of fixtures over `beforeEach`:

- **No shared mutable state** — each test declares what it needs via parameters
- **Automatic teardown** — cleanup runs after `use()` without separate `afterEach`
- **Composable** — layer fixtures by extending from other extended tests
- **Type-safe** — TypeScript infers fixture types from the definition
- **Lazy** — fixtures only run when a test references them by name
- **Scoped** — choose per-test, per-file, or per-worker lifecycle

## Fixture with Parameterized Tests

Use `test.for` (not `test.each`) to combine fixtures with parameterized data. `test.for` provides `TestContext` as the second argument, giving access to fixtures:

```ts
const test = base.extend<{ parser: Parser }>({
  parser: async ({}, use) => {
    const parser = new Parser({ strict: true });
    await use(parser);
  },
});

test.for([
  { input: '42', expected: 42 },
  { input: '3.14', expected: 3.14 },
  { input: '-1', expected: -1 },
])('parses "$input"', ({ input, expected }, { parser }) => {
  expect(parser.parse(input)).toBe(expected);
});
```

`test.each` does not support fixture context — always use `test.for` when combining parameterized data with fixtures.
