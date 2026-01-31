---
title: Testing
description: bun:test runner, describe blocks, expect assertions, mocking, spyOn, snapshots, lifecycle hooks, and CLI usage
tags:
  [
    bun:test,
    test,
    describe,
    expect,
    mock,
    spyOn,
    snapshot,
    lifecycle,
    coverage,
    watch,
  ]
---

# Testing

## Basic Tests

```ts
import { test, expect } from 'bun:test';

test('arithmetic', () => {
  expect(2 + 2).toBe(4);
});

test('async fetch', async () => {
  const response = await fetch('https://api.example.com/health');
  expect(response.ok).toBe(true);
});
```

## Describe Blocks

```ts
import { describe, test, expect } from 'bun:test';

describe('Math operations', () => {
  test('addition', () => {
    expect(1 + 1).toBe(2);
  });

  test('multiplication', () => {
    expect(2 * 3).toBe(6);
  });

  describe('nested: division', () => {
    test('basic division', () => {
      expect(10 / 2).toBe(5);
    });
  });
});
```

## Lifecycle Hooks

```ts
import {
  describe,
  test,
  expect,
  beforeAll,
  afterAll,
  beforeEach,
  afterEach,
} from 'bun:test';
import { Database } from 'bun:sqlite';

describe('database tests', () => {
  let db: Database;

  beforeAll(() => {
    db = new Database(':memory:');
    db.exec('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)');
  });

  afterAll(() => {
    db.close();
  });

  beforeEach(() => {
    db.exec("INSERT INTO users (name) VALUES ('Alice')");
  });

  afterEach(() => {
    db.exec('DELETE FROM users');
  });

  test('user exists', () => {
    const user = db.query('SELECT * FROM users WHERE name = ?').get('Alice');
    expect(user).toBeDefined();
  });
});
```

## Assertions

### Common Matchers

```ts
import { test, expect } from 'bun:test';

test('matchers', () => {
  expect(42).toBe(42);
  expect({ a: 1 }).toEqual({ a: 1 });
  expect(10).toBeGreaterThan(5);
  expect(3).toBeLessThanOrEqual(3);
  expect('hello world').toContain('world');
  expect('hello').toMatch(/^hel/);
  expect(null).toBeNull();
  expect(undefined).toBeUndefined();
  expect(1).toBeDefined();
  expect(true).toBeTruthy();
  expect(0).toBeFalsy();
  expect([1, 2, 3]).toHaveLength(3);
  expect({ name: 'Alice' }).toHaveProperty('name');
  expect({ name: 'Alice' }).toHaveProperty('name', 'Alice');
});
```

### Error Assertions

```ts
import { test, expect } from 'bun:test';

test('throws', () => {
  expect(() => {
    throw new Error('fail');
  }).toThrow('fail');

  expect(() => {
    throw new TypeError('type error');
  }).toThrow(TypeError);
});
```

### Async Assertions

```ts
import { test, expect } from 'bun:test';

test('resolves', async () => {
  await expect(Promise.resolve(42)).resolves.toBe(42);
});

test('rejects', async () => {
  await expect(Promise.reject(new Error('oops'))).rejects.toThrow('oops');
});
```

### Negation

```ts
import { test, expect } from 'bun:test';

test('negation', () => {
  expect(1).not.toBe(2);
  expect('hello').not.toContain('xyz');
  expect(null).not.toBeDefined();
});
```

## Mocking

### Mock Functions

```ts
import { test, expect, mock } from 'bun:test';

test('mock function', () => {
  const fn = mock((x: number) => x * 2);

  fn(5);
  fn(10);

  expect(fn).toHaveBeenCalledTimes(2);
  expect(fn).toHaveBeenCalledWith(5);
  expect(fn.mock.calls).toEqual([[5], [10]]);
  expect(fn.mock.results[0].value).toBe(10);
});
```

### Mock Return Values

```ts
import { test, expect, mock } from 'bun:test';

test('mock return values', () => {
  const fn = mock(() => 'default');

  fn.mockReturnValueOnce('first');
  fn.mockReturnValueOnce('second');

  expect(fn()).toBe('first');
  expect(fn()).toBe('second');
  expect(fn()).toBe('default');
});
```

### spyOn

```ts
import { test, expect, spyOn } from 'bun:test';

test('spy on method', () => {
  const obj = {
    method(x: number) {
      return x + 1;
    },
  };

  const spy = spyOn(obj, 'method');
  obj.method(5);

  expect(spy).toHaveBeenCalled();
  expect(spy).toHaveBeenCalledWith(5);

  spy.mockReturnValue(100);
  expect(obj.method(5)).toBe(100);

  spy.mockRestore();
  expect(obj.method(5)).toBe(6);
});
```

### Module Mocking

```ts
import { test, expect, mock } from 'bun:test';

mock.module('./utils', () => ({
  calculate: () => 42,
}));

test('mocked module', async () => {
  const { calculate } = await import('./utils');
  expect(calculate()).toBe(42);
});
```

## Snapshots

```ts
import { test, expect } from 'bun:test';

test('snapshot', () => {
  const user = { name: 'Alice', role: 'admin' };
  expect(user).toMatchSnapshot();
});

test('inline snapshot', () => {
  const value = { x: 1, y: 2 };
  expect(value).toMatchInlineSnapshot(`
    {
      "x": 1,
      "y": 2,
    }
  `);
});
```

Update snapshots:

```bash
bun test --update-snapshots
```

## Test Modifiers

```ts
import { test, describe } from 'bun:test';

test.skip('not implemented yet', () => {});

test.todo('implement later');

test.only('run only this test', () => {});

describe.skip('skip entire suite', () => {
  test('skipped', () => {});
});
```

## Concurrent Tests

```ts
import { test, expect } from 'bun:test';

test.concurrent('parallel 1', async () => {
  await Bun.sleep(100);
  expect(true).toBe(true);
});

test.concurrent('parallel 2', async () => {
  await Bun.sleep(100);
  expect(true).toBe(true);
});
```

## Timeouts

```ts
import { test, expect } from 'bun:test';

test('slow operation', async () => {
  const result = await slowOperation();
  expect(result).toBeDefined();
}, 10_000);
```

## CLI Commands

```bash
bun test                        # Run all tests
bun test --watch                # Watch mode
bun test --coverage             # Show code coverage
bun test -t "pattern"           # Filter by test name
bun test src/utils              # Run tests in directory
bun test --timeout 30000        # Set global timeout (ms)
bun test --bail                 # Stop after first failure
bun test --bail 5               # Stop after 5 failures
bun test --rerun-each 3         # Run each test 3 times
```

## File Conventions

Bun auto-discovers test files matching these patterns:

- `*.test.ts`, `*.test.tsx`, `*.test.js`, `*.test.jsx`
- `*_test.ts`, `*_test.tsx`, `*_test.js`, `*_test.jsx`
- `*.spec.ts`, `*.spec.tsx`, `*.spec.js`, `*.spec.jsx`

## Coverage

```bash
bun test --coverage
```

Output shows line-by-line coverage per file. Configure thresholds in `bunfig.toml`:

```toml
[test]
coverage = true
coverageThreshold = { line = 80, function = 80, statement = 80 }
coverageReporter = ["text", "lcov"]
```

## Testing HTTP Servers

```ts
import { test, expect, afterAll } from 'bun:test';

const server = Bun.serve({
  port: 0,
  fetch(req) {
    return Response.json({ status: 'ok' });
  },
});

afterAll(() => {
  server.stop();
});

test('health check', async () => {
  const response = await fetch(`${server.url}api/health`);
  expect(response.status).toBe(404);

  const root = await fetch(server.url);
  const body = await root.json();
  expect(body).toEqual({ status: 'ok' });
});
```
