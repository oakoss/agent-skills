---
title: Advanced Patterns
description: Snapshot testing, concurrent test execution, in-source testing, type testing, benchmarking, and custom matchers
tags:
  [
    snapshots,
    concurrent,
    in-source,
    type-testing,
    benchmarks,
    custom-matchers,
    test.concurrent,
    expect.extend,
  ]
---

# Advanced Patterns

## Snapshot Testing

Capture and compare output snapshots:

```ts
import { expect, test } from 'vitest';

test('matches snapshot', () => {
  const output = generateOutput({ name: 'Alice', age: 30 });

  expect(output).toMatchSnapshot();
});
```

First run creates `__snapshots__/test-file.test.ts.snap`:

```text
exports['matches snapshot 1'] = `
{
  "name": "Alice",
  "age": 30,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
`;
```

Subsequent runs compare against saved snapshot.

## Inline Snapshots

Store snapshots in test file:

```ts
test('inline snapshot', () => {
  const user = { name: 'Alice', age: 30 };

  expect(user).toMatchInlineSnapshot(`
    {
      "name": "Alice",
      "age": 30,
    }
  `);
});
```

Vitest updates the test file on first run or with `--update` flag.

## Updating Snapshots

Update snapshots when output changes:

```bash
vitest -u
vitest --update
```

Update specific test:

```bash
vitest -u src/components/Button.test.tsx
```

## Property Matchers in Snapshots

Ignore dynamic values:

```ts
test('snapshot with dynamic values', () => {
  const user = {
    id: generateId(),
    name: 'Alice',
    createdAt: new Date(),
  };

  expect(user).toMatchSnapshot({
    id: expect.any(String),
    createdAt: expect.any(Date),
  });
});
```

## Concurrent Tests

Run tests in parallel for faster execution:

```ts
import { describe, expect, test } from 'vitest';

describe.concurrent('parallel suite', () => {
  test('test 1', async () => {
    const result = await fetchData('1');
    expect(result).toBeDefined();
  });

  test('test 2', async () => {
    const result = await fetchData('2');
    expect(result).toBeDefined();
  });

  test('test 3', async () => {
    const result = await fetchData('3');
    expect(result).toBeDefined();
  });
});
```

All tests in the suite run concurrently.

## Individual Concurrent Tests

Mark specific tests as concurrent:

```ts
test.concurrent('parallel 1', async () => {
  await slowOperation();
});

test.concurrent('parallel 2', async () => {
  await slowOperation();
});

test('sequential', () => {
  expect(true).toBe(true);
});
```

## Concurrent Limits

Limit concurrent test execution:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    maxConcurrency: 5,
  },
});
```

## Sequential Tests

Force sequential execution in concurrent suite:

```ts
describe.concurrent('suite', () => {
  test('runs in parallel', async () => {});

  test.sequential('runs after parallel', async () => {});

  test.sequential('runs after previous sequential', async () => {});
});
```

## In-Source Testing

Write tests alongside source code:

```ts
export function add(a: number, b: number) {
  return a + b;
}

if (import.meta.vitest) {
  const { describe, expect, it } = import.meta.vitest;

  describe('add', () => {
    it('adds positive numbers', () => {
      expect(add(1, 2)).toBe(3);
    });

    it('adds negative numbers', () => {
      expect(add(-1, -2)).toBe(-3);
    });
  });
}
```

Enable in `vitest.config.ts`:

```ts
export default defineConfig({
  test: {
    includeSource: ['src/**/*.ts'],
  },
  define: {
    'import.meta.vitest': 'undefined',
  },
});
```

Benefits: tests stay close to code, easy to maintain, tree-shaken in production.

## Type Testing

Test TypeScript types at compile time:

```ts
import { expectTypeOf } from 'vitest';

test('type assertions', () => {
  expectTypeOf({ a: 1, b: 'test' }).toEqualTypeOf<{ a: number; b: string }>();

  expectTypeOf('test').toBeString();
  expectTypeOf(123).toBeNumber();
  expectTypeOf(true).toBeBoolean();
  expectTypeOf(null).toBeNull();
  expectTypeOf(undefined).toBeUndefined();

  expectTypeOf([1, 2, 3]).toBeArray();
  expectTypeOf({}).toBeObject();
  expectTypeOf(() => {}).toBeFunction();

  expectTypeOf<Promise<string>>().resolves.toBeString();

  expectTypeOf<string | number>().toMatchTypeOf<string>();
});
```

## Assert Types

Runtime and compile-time assertions:

```ts
import { assertType } from 'vitest';

test('assert type', () => {
  const value: unknown = 'hello';

  if (typeof value === 'string') {
    assertType<string>(value);
    expect(value.toUpperCase()).toBe('HELLO');
  }
});
```

## Custom Matchers

Extend expect with custom matchers:

```ts
import { expect } from 'vitest';

interface CustomMatchers<R = unknown> {
  toBeWithinRange(floor: number, ceiling: number): R;
}

declare module 'vitest' {
  interface Assertion<T = any> extends CustomMatchers<T> {}
  interface AsymmetricMatchersContaining extends CustomMatchers {}
}

expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        pass
          ? `expected ${received} not to be within range ${floor} - ${ceiling}`
          : `expected ${received} to be within range ${floor} - ${ceiling}`,
    };
  },
});

test('custom matcher', () => {
  expect(10).toBeWithinRange(5, 15);
  expect(20).not.toBeWithinRange(5, 15);
});
```

## Benchmarking

Measure performance:

```ts
import { bench, describe } from 'vitest';

describe('sorting algorithms', () => {
  bench('sort with Array.sort', () => {
    const arr = Array.from({ length: 1000 }, () => Math.random());
    arr.sort();
  });

  bench('sort with custom quicksort', () => {
    const arr = Array.from({ length: 1000 }, () => Math.random());
    quicksort(arr);
  });
});
```

Run benchmarks:

```bash
vitest bench
```

## Benchmark Options

Configure benchmark behavior:

```ts
bench(
  'operation',
  () => {
    heavyOperation();
  },
  {
    time: 1000,
    iterations: 100,
    warmupIterations: 10,
    warmupTime: 100,
  },
);
```

## Test Context

Share data between hooks and tests:

```ts
import { beforeEach, expect, it } from 'vitest';

interface LocalTestContext {
  server: TestServer;
  user: User;
}

beforeEach<LocalTestContext>(async (context) => {
  context.server = await startTestServer();
  context.user = await createTestUser();
});

it<LocalTestContext>('makes request', async ({ server, user }) => {
  const response = await server.get('/profile', { userId: user.id });
  expect(response.status).toBe(200);
});
```

## Conditional Tests

Run tests based on environment:

```ts
test.skipIf(process.env.CI === 'true')('runs locally only', () => {});
test.runIf(process.platform === 'darwin')('macOS only', () => {});
```

## Shuffle Tests

Randomize test order to detect dependencies:

```ts
describe.shuffle('random order', () => {
  test('test 1', () => {});
  test('test 2', () => {});
});
```
