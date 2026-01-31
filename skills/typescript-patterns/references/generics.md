---
title: Generics
description: Generic type parameters, constraints, inference, default values, and variance
tags: [generics, constraints, inference, type-parameters, variance, extends]
---

# Generics

Generics enable code reuse across different types while maintaining type safety.

## Basic Generics

Generic functions and types with type parameters:

```ts
function identity<T>(value: T): T {
  return value;
}

const num = identity(42);
const str = identity('hello');

function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

type Box<T> = {
  value: T;
};

const numberBox: Box<number> = { value: 42 };
const stringBox: Box<string> = { value: 'hello' };
```

TypeScript infers the type parameter from usage. Explicit type arguments are rarely needed.

## Generic Constraints

Restrict type parameters with `extends`:

```ts
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { id: '1', name: 'Alice' };
const id = getProperty(user, 'id');

function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

longest('hello', 'world');
longest([1, 2], [3, 4, 5]);

function merge<T extends object, U extends object>(obj1: T, obj2: U): T & U {
  return { ...obj1, ...obj2 };
}
```

Always constrain generics when you need to access specific properties or methods.

## Multiple Type Parameters

Use multiple generics for complex relationships:

```ts
function map<T, U>(arr: T[], fn: (item: T) => U): U[] {
  const result: U[] = [];
  for (const item of arr) {
    result.push(fn(item));
  }
  return result;
}

const numbers = [1, 2, 3];
const strings = map(numbers, (n) => n.toString());

type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

function tryParse(json: string): Result<unknown, SyntaxError> {
  try {
    return { ok: true, value: JSON.parse(json) };
  } catch (error) {
    return { ok: false, error: error as SyntaxError };
  }
}
```

The second generic `E = Error` has a default type, making it optional.

## Default Type Parameters

Provide default values for type parameters:

```ts
type ApiResponse<T = unknown, E = Error> = {
  data?: T;
  error?: E;
  status: number;
};

const response1: ApiResponse = { status: 200 };
const response2: ApiResponse<User> = { data: user, status: 200 };

interface State<T = string> {
  value: T;
  update: (newValue: T) => void;
}

const stringState: State = { value: '', update: () => {} };
const numberState: State<number> = { value: 0, update: () => {} };
```

Defaults make generics optional, improving usability for common cases.

## Generic Inference

Let TypeScript infer types from function arguments:

```ts
function createPair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

const pair = createPair('hello', 42);

function filterNotNull<T>(arr: (T | null)[]): T[] {
  const result: T[] = [];
  for (const item of arr) {
    if (item !== null) {
      result.push(item);
    }
  }
  return result;
}

const numbers = filterNotNull([1, null, 2, null, 3]);

function promisify<T extends unknown[], R>(
  fn: (...args: T) => R,
): (...args: T) => Promise<R> {
  return async (...args) => fn(...args);
}
```

Inference works best when the generic appears in function parameters, not just the return type.

## Conditional Generic Constraints

Use conditional types with generics:

```ts
type Flatten<T> = T extends unknown[] ? T[0] : T;

function flatten<T>(value: T): Flatten<T> {
  return (Array.isArray(value) ? value[0] : value) as Flatten<T>;
}

const num = flatten(42);
const str = flatten(['hello']);

type Unpromisify<T> = T extends Promise<infer U> ? U : T;

function resolve<T>(value: T): Unpromisify<T> {
  return (
    value instanceof Promise ? value : Promise.resolve(value)
  ) as Unpromisify<T>;
}
```

Conditional types within generics enable complex type transformations.

## Generic Classes

Classes with type parameters:

```ts
class Queue<T> {
  private items: T[] = [];

  enqueue(item: T): void {
    this.items.push(item);
  }

  dequeue(): T | undefined {
    return this.items.shift();
  }

  peek(): T | undefined {
    return this.items[0];
  }
}

const numberQueue = new Queue<number>();
numberQueue.enqueue(1);
numberQueue.enqueue(2);

class Result<T, E extends Error = Error> {
  private constructor(
    public readonly ok: boolean,
    public readonly value?: T,
    public readonly error?: E,
  ) {}

  static success<T>(value: T): Result<T> {
    return new Result(true, value);
  }

  static failure<E extends Error>(error: E): Result<never, E> {
    return new Result(false, undefined, error);
  }
}
```

Generic classes are useful for data structures and container types.

## Variance

TypeScript automatically infers variance for generics:

```ts
type Producer<out T> = () => T;
type Consumer<in T> = (value: T) => void;
type Mutable<in out T> = {
  get: () => T;
  set: (value: T) => void;
};

interface ReadonlyBox<out T> {
  readonly value: T;
}

interface WriteableBox<in T> {
  set(value: T): void;
}

interface Box<T> {
  value: T;
}
```

- `out T` (covariance): Type can be returned but not accepted as parameter
- `in T` (contravariance): Type can be accepted but not returned
- `in out T` (invariance): Type can be both accepted and returned

Most generic types are covariant by default.

## Generic Utility Functions

Reusable type-safe utilities:

```ts
function groupBy<T, K extends string | number>(
  arr: T[],
  getKey: (item: T) => K,
): Record<K, T[]> {
  const result = {} as Record<K, T[]>;
  for (const item of arr) {
    const key = getKey(item);
    if (!result[key]) {
      result[key] = [];
    }
    result[key].push(item);
  }
  return result;
}

const users = [
  { id: '1', role: 'admin' },
  { id: '2', role: 'user' },
];
const byRole = groupBy(users, (u) => u.role);

function memoize<Args extends unknown[], Return>(
  fn: (...args: Args) => Return,
): (...args: Args) => Return {
  const cache = new Map<string, Return>();
  return (...args) => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}
```

Generics enable type-safe higher-order functions.

## Avoiding Manual Type Arguments

Prefer inference over explicit type parameters:

```ts
const arr1 = Array<number>();
const arr2 = [] as number[];
const arr3: number[] = [];

function fetch<T>(url: string): Promise<T> {
  return fetch(url).then((r) => r.json());
}
const user1 = await fetch<User>('/api/user');

async function fetchTyped(url: string): Promise<User> {
  const response = await fetch(url);
  return response.json();
}
const user2 = await fetchTyped('/api/user');
```

Type the function return instead of making the caller specify type arguments.
