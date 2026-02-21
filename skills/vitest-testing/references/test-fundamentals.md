---
title: Test Fundamentals
description: Core test structure with describe/it, assertions with expect, lifecycle hooks, and parameterized testing with test.each
tags:
  [
    describe,
    it,
    test,
    expect,
    assertions,
    lifecycle,
    beforeEach,
    afterEach,
    test.each,
    test.concurrent,
  ]
---

# Test Fundamentals

## Test Structure

Organize tests with `describe` blocks and individual test cases with `test` or `it`:

```ts
import { describe, expect, it, test } from 'vitest';

describe('Calculator', () => {
  it('adds two numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  test('subtracts two numbers', () => {
    expect(subtract(5, 3)).toBe(2);
  });
});
```

Both `test` and `it` are aliases. Use whichever reads better for your test descriptions.

## Nested Describe Blocks

Group related tests hierarchically:

```ts
describe('User authentication', () => {
  describe('login', () => {
    it('succeeds with valid credentials', () => {
      expect(login('user', 'pass')).toBe(true);
    });

    it('fails with invalid credentials', () => {
      expect(login('user', 'wrong')).toBe(false);
    });
  });

  describe('logout', () => {
    it('clears session', () => {
      logout();
      expect(getSession()).toBeNull();
    });
  });
});
```

## Basic Assertions

Common matchers for different value types:

```ts
expect(2 + 2).toBe(4);
expect(user.name).toBe('Alice');

expect({ name: 'Alice' }).toEqual({ name: 'Alice' });
expect([1, 2, 3]).toEqual([1, 2, 3]);

expect(result).toBeTruthy();
expect(result).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

expect('hello world').toContain('world');
expect([1, 2, 3]).toContain(2);

expect(number).toBeGreaterThan(5);
expect(number).toBeGreaterThanOrEqual(5);
expect(number).toBeLessThan(10);
expect(number).toBeLessThanOrEqual(10);

expect(() => throwError()).toThrow();
expect(() => throwError()).toThrow('Error message');
expect(() => throwError()).toThrow(CustomError);
```

Use `toBe` for primitive values (numbers, strings, booleans). Use `toEqual` for objects and arrays (deep equality).

## Async Assertions

Test promises and async functions:

```ts
test('resolves to value', async () => {
  await expect(fetchData()).resolves.toBe('data');
});

test('rejects with error', async () => {
  await expect(fetchData()).rejects.toThrow('Network error');
});

test('async/await pattern', async () => {
  const result = await fetchData();
  expect(result).toBe('data');
});
```

## Lifecycle Hooks

Set up and tear down test state:

```ts
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

describe('Database operations', () => {
  let db: Database;

  beforeEach(async () => {
    db = await createTestDatabase();
    await db.seed();
  });

  afterEach(async () => {
    await db.cleanup();
  });

  it('inserts record', async () => {
    await db.insert({ name: 'Alice' });
    expect(await db.count()).toBe(1);
  });

  it('deletes record', async () => {
    await db.insert({ name: 'Alice' });
    await db.delete({ name: 'Alice' });
    expect(await db.count()).toBe(0);
  });
});
```

Lifecycle hooks:

- `beforeEach` runs before each test
- `afterEach` runs after each test
- `beforeAll` runs once before all tests in a describe block
- `afterAll` runs once after all tests in a describe block

## Suite-Level Hooks

Run expensive setup once per suite:

```ts
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

describe('API integration', () => {
  let server: TestServer;

  beforeAll(async () => {
    server = await startTestServer();
  });

  afterAll(async () => {
    await server.stop();
  });

  it('responds to GET /users', async () => {
    const response = await fetch(`${server.url}/users`);
    expect(response.ok).toBe(true);
  });
});
```

## Parameterized Tests with test.each

Run the same test with different inputs:

```ts
test.each([
  { a: 1, b: 1, expected: 2 },
  { a: 1, b: 2, expected: 3 },
  { a: 2, b: 1, expected: 3 },
])('adds $a + $b to equal $expected', ({ a, b, expected }) => {
  expect(a + b).toBe(expected);
});
```

Using array syntax:

```ts
test.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('adds %i + %i to equal %i', (a, b, expected) => {
  expect(a + b).toBe(expected);
});
```

Printf formatting tokens: `%s` (string), `%d` (number), `%i` (integer), `%f` (float), `%j` (JSON), `%o` (object), `%%` (literal percent).

## Test Modifiers

Control which tests run:

```ts
test.skip('not ready yet', () => {});

test.only('debug this test', () => {
  expect(debugFeature()).toBe(true);
});

test.todo('implement later');

test.skipIf(process.env.CI === 'true')('local only', () => {});

test.runIf(process.platform === 'darwin')('macOS only', () => {});
```

Modifiers work on describe blocks too:

```ts
describe.skip('entire suite', () => {
  it('will not run', () => {});
});

describe.only('focus on this suite', () => {
  it('will run', () => {});
});
```

## Concurrent Tests

Run tests in parallel for faster execution:

```ts
import { describe, expect, test } from 'vitest';

describe.concurrent('parallel suite', () => {
  test('test 1', async () => {
    await slowOperation();
    expect(result).toBe(true);
  });

  test('test 2', async () => {
    await slowOperation();
    expect(result).toBe(true);
  });
});
```

Or mark individual tests as concurrent:

```ts
test.concurrent('parallel test 1', async () => {
  await slowOperation();
});

test.concurrent('parallel test 2', async () => {
  await slowOperation();
});
```

Concurrent tests require async functions. Use `test.sequential` inside a concurrent suite to force specific tests to run sequentially.

## Test Context

Access test metadata via the context parameter. For reusable setup, prefer `test.extend` fixtures over manual context manipulation — see the fixtures-and-context reference.

## Assertions with Custom Messages

Add context to assertion failures:

```ts
expect(result, 'Expected user to be authenticated').toBe(true);

expect(response.status, `API returned ${response.status}`).toBe(200);
```

## Negation

Invert any matcher with `.not`:

```ts
expect(value).not.toBe(null);
expect(array).not.toContain(item);
expect(fn).not.toThrow();
```

## Soft Assertions

Soft assertions continue executing after failure and collect all failures. The test reports all failing expectations at once instead of stopping at the first failure:

```ts
import { expect, test } from 'vitest';

test('validates all fields', () => {
  const user = getUser();

  expect.soft(user.name).toBe('Alice');
  expect.soft(user.email).toContain('@');
  expect.soft(user.age).toBeGreaterThan(0);
});
```

## Poll Assertions

`expect.poll()` retries the callback until the assertion passes or times out. Useful for testing async state changes without manual retry loops:

```ts
test('waits for value', async () => {
  await expect.poll(() => fetchStatus()).toBe('ready');

  await expect
    .poll(() => getCount(), { interval: 100, timeout: 5000 })
    .toBeGreaterThan(0);
});
```

## In-Test Cleanup Hooks

`onTestFinished` runs after each test completes (pass or fail) — useful for cleanup without `afterEach`. `onTestFailed` runs only on failure — useful for diagnostics. Both are scoped to the current test:

```ts
import { expect, onTestFailed, onTestFinished, test } from 'vitest';

test('with cleanup', () => {
  const resource = acquireResource();

  onTestFinished(() => {
    resource.release();
  });

  onTestFailed((result) => {
    console.log('Failed:', result.errors);
  });

  expect(resource.isActive()).toBe(true);
});
```

## Type Assertions

Test TypeScript types at compile time:

```ts
import { expectTypeOf } from 'vitest';

expectTypeOf({ a: 1 }).toEqualTypeOf<{ a: number }>();
expectTypeOf('test').toBeString();
expectTypeOf(123).toBeNumber();
expectTypeOf<Promise<string>>().resolves.toBeString();
```

## Asymmetric Matchers

Match partial values in assertions:

```ts
expect(user).toEqual({
  id: expect.any(String),
  name: 'Alice',
  createdAt: expect.any(Date),
});

expect(response).toMatchObject({
  status: 200,
  data: expect.objectContaining({
    userId: '123',
  }),
});

expect(array).toEqual(
  expect.arrayContaining([expect.objectContaining({ name: 'Alice' })]),
);

expect(url).toMatch(/^https?:\/\//);
expect(email).toMatch(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/);
```
