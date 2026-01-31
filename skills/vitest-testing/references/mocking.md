---
title: Mocking
description: Mock functions with vi.fn, module mocking with vi.mock, spying with vi.spyOn, auto-mocking, timer control, and mock management
tags:
  [
    vi.fn,
    vi.mock,
    vi.spyOn,
    vi.mocked,
    mocking,
    spies,
    auto-mock,
    timers,
    vi.useFakeTimers,
  ]
---

# Mocking

## Mock Functions with vi.fn

Create spy functions to track calls and control return values:

```ts
import { expect, test, vi } from 'vitest';

test('tracks function calls', () => {
  const mockFn = vi.fn();

  mockFn('arg1', 'arg2');
  mockFn('arg3');

  expect(mockFn).toHaveBeenCalledTimes(2);
  expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
  expect(mockFn).toHaveBeenLastCalledWith('arg3');
});
```

## Mock Return Values

Control what mocks return:

```ts
const mockFn = vi.fn();

mockFn.mockReturnValue(42);
expect(mockFn()).toBe(42);

mockFn.mockReturnValueOnce(1).mockReturnValueOnce(2).mockReturnValue(3);
expect(mockFn()).toBe(1);
expect(mockFn()).toBe(2);
expect(mockFn()).toBe(3);
expect(mockFn()).toBe(3);
```

## Mock Async Functions

Return promises from mocks:

```ts
const mockFetch = vi.fn();

mockFetch.mockResolvedValue({ data: 'success' });
await expect(mockFetch()).resolves.toEqual({ data: 'success' });

mockFetch.mockRejectedValue(new Error('Network error'));
await expect(mockFetch()).rejects.toThrow('Network error');
```

## Mock Implementation

Replace function logic:

```ts
const mockFn = vi.fn();

mockFn.mockImplementation((a, b) => a + b);
expect(mockFn(2, 3)).toBe(5);

mockFn
  .mockImplementationOnce((a, b) => a * b)
  .mockImplementation((a, b) => a - b);
expect(mockFn(2, 3)).toBe(6);
expect(mockFn(5, 3)).toBe(2);
```

## Module Mocking

Replace entire modules with mocks:

```ts
import { expect, test, vi } from 'vitest';

vi.mock('./api', () => ({
  fetchUser: vi.fn().mockResolvedValue({ id: '1', name: 'Alice' }),
  updateUser: vi.fn().mockResolvedValue({ success: true }),
}));

import { fetchUser, updateUser } from './api';

test('uses mocked API', async () => {
  const user = await fetchUser('1');
  expect(user.name).toBe('Alice');

  await updateUser('1', { name: 'Bob' });
  expect(updateUser).toHaveBeenCalledWith('1', { name: 'Bob' });
});
```

`vi.mock` calls are hoisted to the top of the file, so they execute before imports.

## Partial Module Mocking

Mock some exports while keeping others:

```ts
vi.mock('./utils', async () => {
  const actual = await vi.importActual<typeof import('./utils')>('./utils');
  return {
    ...actual,
    fetchData: vi.fn().mockResolvedValue('mocked data'),
  };
});

import { fetchData, formatData } from './utils';

test('mocks fetchData but keeps formatData', async () => {
  expect(await fetchData()).toBe('mocked data');
  expect(formatData('test')).toBe('TEST');
});
```

## Spying on Methods

Track calls to existing object methods:

```ts
import { expect, test, vi } from 'vitest';

const calculator = {
  add: (a: number, b: number) => a + b,
};

test('spies on method', () => {
  const spy = vi.spyOn(calculator, 'add');

  const result = calculator.add(2, 3);

  expect(result).toBe(5);
  expect(spy).toHaveBeenCalledWith(2, 3);

  spy.mockRestore();
});
```

## Spy Without Calling Original

Replace implementation while spying:

```ts
const spy = vi.spyOn(console, 'log').mockImplementation(() => {});

console.log('This will not print');

expect(spy).toHaveBeenCalledWith('This will not print');

spy.mockRestore();
```

## Auto-Mocking

Automatically mock all module exports:

```ts
vi.mock('./api');

import * as api from './api';

test('auto-mocks all exports', () => {
  expect(vi.isMockFunction(api.fetchUser)).toBe(true);
  expect(vi.isMockFunction(api.updateUser)).toBe(true);
});
```

Auto-mocked functions return `undefined` by default. Configure them in your tests:

```ts
vi.mocked(api.fetchUser).mockResolvedValue({ id: '1', name: 'Alice' });
```

## Spy-Only Module Mocking (v3.2+)

Spy on all exports without replacing them. Useful in browser mode where module objects are sealed:

```ts
import { vi } from 'vitest';
import * as math from './math';

vi.mock('./math', { spy: true });

test('spies on real implementation', () => {
  expect(math.add(1, 2)).toBe(3);
  expect(vi.mocked(math.add)).toHaveBeenCalledWith(1, 2);

  vi.mocked(math.add).mockReturnValue(0);
  expect(math.add(1, 2)).toBe(0);
});
```

## Mocking Classes

Mock class constructors and methods:

```ts
vi.mock('./Database', () => {
  const Database = vi.fn();
  Database.prototype.query = vi.fn().mockResolvedValue([]);
  Database.prototype.insert = vi.fn().mockResolvedValue({ id: '1' });
  return { Database };
});

import { Database } from './Database';

test('mocks class', async () => {
  const db = new Database();
  const result = await db.query('SELECT * FROM users');

  expect(result).toEqual([]);
  expect(db.query).toHaveBeenCalledWith('SELECT * FROM users');
});
```

## vi.mocked Helper

Type-safe access to mock methods:

```ts
import { vi } from 'vitest';

vi.mock('./api');

import { fetchUser } from './api';

vi.mocked(fetchUser).mockResolvedValue({ id: '1', name: 'Alice' });

test('typed mock', async () => {
  const user = await fetchUser('1');
  expect(user.name).toBe('Alice');
});
```

`vi.mocked` provides proper TypeScript types for mock methods.

## Clearing and Resetting Mocks

Manage mock state between tests:

```ts
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest';

describe('mock management', () => {
  const mockFn = vi.fn();

  beforeEach(() => {
    mockFn.mockReturnValue('default');
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  test('uses mock', () => {
    mockFn();
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  test('has clean mock', () => {
    expect(mockFn).not.toHaveBeenCalled();
  });
});
```

Mock management methods:

- `vi.clearAllMocks()` — clears call history but keeps implementations
- `vi.resetAllMocks()` — clears history and resets implementations
- `vi.restoreAllMocks()` — restores original implementations for spies
- `mockFn.mockClear()` — clears history for specific mock
- `mockFn.mockReset()` — clears history and resets implementation
- `mockFn.mockRestore()` — restores original for specific spy

## Fake Timers

Control time-based functions:

```ts
import { afterEach, beforeEach, expect, test, vi } from 'vitest';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

test('advances timers', () => {
  const callback = vi.fn();

  setTimeout(callback, 1000);

  expect(callback).not.toHaveBeenCalled();

  vi.advanceTimersByTime(1000);

  expect(callback).toHaveBeenCalled();
});

test('runs all timers', () => {
  const callback = vi.fn();

  setTimeout(callback, 1000);
  setTimeout(callback, 2000);

  vi.runAllTimers();

  expect(callback).toHaveBeenCalledTimes(2);
});
```

Timer control methods:

- `vi.advanceTimersByTime(ms)` — advance by specific duration
- `vi.advanceTimersToNextTimer()` — advance to next scheduled timer
- `vi.runAllTimers()` — run all pending timers
- `vi.runOnlyPendingTimers()` — run timers scheduled before the call
- `vi.clearAllTimers()` — clear all pending timers
- `vi.setSystemTime(date)` — set current date for Date.now() and new Date()

## Mocking Date

Control Date.now() and new Date():

```ts
beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2024-01-01'));
});

afterEach(() => {
  vi.useRealTimers();
});

test('uses mocked date', () => {
  expect(Date.now()).toBe(new Date('2024-01-01').getTime());
  expect(new Date().toISOString()).toBe('2024-01-01T00:00:00.000Z');

  vi.setSystemTime(new Date('2024-01-02'));
  expect(new Date().toISOString()).toBe('2024-01-02T00:00:00.000Z');
});
```

## Mock Assertions

Verify mock behavior:

```ts
const mockFn = vi.fn();

mockFn('a', 'b');
mockFn('c', 'd');

expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveBeenCalledWith('a', 'b');
expect(mockFn).toHaveBeenLastCalledWith('c', 'd');
expect(mockFn).toHaveBeenNthCalledWith(1, 'a', 'b');
expect(mockFn).toHaveBeenNthCalledWith(2, 'c', 'd');

expect(mockFn.mock.calls).toEqual([
  ['a', 'b'],
  ['c', 'd'],
]);
expect(mockFn.mock.results).toEqual([
  { type: 'return', value: undefined },
  { type: 'return', value: undefined },
]);
```

## Mocking Environment Variables

Override process.env:

```ts
import { afterEach, beforeEach, expect, test, vi } from 'vitest';

beforeEach(() => {
  vi.stubEnv('NODE_ENV', 'test');
  vi.stubEnv('API_KEY', 'test-key');
});

afterEach(() => {
  vi.unstubAllEnvs();
});

test('uses stubbed env vars', () => {
  expect(process.env.NODE_ENV).toBe('test');
  expect(process.env.API_KEY).toBe('test-key');
});
```

## Mocking Globals

Replace global objects:

```ts
const originalFetch = global.fetch;

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ data: 'mocked' }),
  });
});

afterEach(() => {
  global.fetch = originalFetch;
});

test('uses mocked fetch', async () => {
  const response = await fetch('/api/data');
  const data = await response.json();

  expect(data).toEqual({ data: 'mocked' });
  expect(global.fetch).toHaveBeenCalledWith('/api/data');
});
```

## Unmocking Modules

Restore original module implementation:

```ts
vi.mock('./api');

import { fetchUser } from './api';

test('uses mock', () => {
  expect(vi.isMockFunction(fetchUser)).toBe(true);
});

vi.unmock('./api');

test('uses real implementation', async () => {
  expect(vi.isMockFunction(fetchUser)).toBe(false);
});
```

`vi.unmock` is hoisted like `vi.mock`, so it affects the entire file scope.
