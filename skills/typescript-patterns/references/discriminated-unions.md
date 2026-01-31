---
title: Discriminated Unions
description: Tagged unions, exhaustive checking, never type, and pattern matching
tags:
  [
    discriminated-unions,
    tagged-unions,
    exhaustive-checking,
    never,
    pattern-matching,
  ]
---

# Discriminated Unions

Discriminated unions (tagged unions) use a common property with literal types to enable exhaustive type checking.

## Basic Discriminated Unions

Add a `type` or `kind` property to distinguish union members:

```ts
type Success = { ok: true; data: string };
type Failure = { ok: false; error: string };
type Result = Success | Failure;

function handleResult(result: Result) {
  if (result.ok) {
    console.log(result.data);
  } else {
    console.error(result.error);
  }
}

type Circle = { kind: 'circle'; radius: number };
type Rectangle = { kind: 'rectangle'; width: number; height: number };
type Triangle = { kind: 'triangle'; base: number; height: number };
type Shape = Circle | Rectangle | Triangle;

function area(shape: Shape): number {
  if (shape.kind === 'circle') {
    return Math.PI * shape.radius ** 2;
  }
  if (shape.kind === 'rectangle') {
    return shape.width * shape.height;
  }
  return (shape.base * shape.height) / 2;
}
```

The discriminant property must be a literal type (`string`, `number`, `boolean`, `null`, `undefined`).

## Switch Statement Exhaustiveness

Use `switch` for cleaner exhaustive checks:

```ts
type Action =
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'reset'; value: number };

function reducer(state: number, action: Action): number {
  switch (action.type) {
    case 'increment':
      return state + 1;
    case 'decrement':
      return state - 1;
    case 'reset':
      return action.value;
  }
}

type Status = 'idle' | 'loading' | 'success' | 'error';

function statusColor(status: Status): string {
  switch (status) {
    case 'idle':
      return 'gray';
    case 'loading':
      return 'blue';
    case 'success':
      return 'green';
    case 'error':
      return 'red';
  }
}
```

TypeScript ensures all cases are handled when there's no default case.

## Never Type for Exhaustiveness

Use `never` to catch unhandled cases:

```ts
function assertNever(value: never): never {
  throw new Error(`Unhandled value: ${JSON.stringify(value)}`);
}

type Event = { type: 'click' } | { type: 'scroll' } | { type: 'resize' };

function handleEvent(event: Event) {
  switch (event.type) {
    case 'click':
      return 'Clicked';
    case 'scroll':
      return 'Scrolled';
    case 'resize':
      return 'Resized';
    default:
      return assertNever(event);
  }
}

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return (shape.base * shape.height) / 2;
    default:
      return assertNever(shape);
  }
}
```

Adding a new union member without handling it in the switch will cause a type error.

## Nested Discriminated Unions

Discriminated unions can be nested:

```ts
type Loading = { status: 'loading' };
type Success = { status: 'success'; data: { user: User } | { users: User[] } };
type Error = { status: 'error'; error: string };
type State = Loading | Success | Error;

function render(state: State) {
  if (state.status === 'loading') {
    return 'Loading...';
  }
  if (state.status === 'error') {
    return state.error;
  }
  if ('user' in state.data) {
    return state.data.user.name;
  }
  return `${state.data.users.length} users`;
}
```

Use multiple discriminants for deeply nested structures.

## Discriminating with Boolean

Boolean discriminants work for two-member unions:

```ts
type Unauthenticated = { authenticated: false };
type Authenticated = { authenticated: true; user: User };
type Auth = Unauthenticated | Authenticated;

function render(auth: Auth) {
  if (auth.authenticated) {
    return `Welcome, ${auth.user.name}`;
  }
  return 'Please log in';
}

type Empty = { hasValue: false };
type Filled = { hasValue: true; value: string };
type Optional = Empty | Filled;

function getValue(opt: Optional): string {
  if (opt.hasValue) {
    return opt.value;
  }
  return 'N/A';
}
```

For unions with more than two members, use string literals instead.

## Discriminated Unions in Reducers

Common pattern in state management:

```ts
type State = { count: number; message: string };

type Action =
  | { type: 'increment'; by?: number }
  | { type: 'decrement'; by?: number }
  | { type: 'reset'; to: number }
  | { type: 'setMessage'; message: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + (action.by ?? 1) };
    case 'decrement':
      return { ...state, count: state.count - (action.by ?? 1) };
    case 'reset':
      return { ...state, count: action.to };
    case 'setMessage':
      return { ...state, message: action.message };
  }
}

const newState = reducer(
  { count: 0, message: '' },
  { type: 'increment', by: 5 },
);
```

Each action has a `type` discriminant and type-specific payload.

## Generic Discriminated Unions

Make discriminated unions generic:

```ts
type Ok<T> = { ok: true; value: T };
type Err<E> = { ok: false; error: E };
type Result<T, E = Error> = Ok<T> | Err<E>;

function parseJSON(json: string): Result<unknown, SyntaxError> {
  try {
    return { ok: true, value: JSON.parse(json) };
  } catch (error) {
    return { ok: false, error: error as SyntaxError };
  }
}

function map<T, U, E>(result: Result<T, E>, fn: (value: T) => U): Result<U, E> {
  if (result.ok) {
    return { ok: true, value: fn(result.value) };
  }
  return result;
}

const result = parseJSON('{"name":"Alice"}');
const mapped = map(result, (data) => (data as { name: string }).name);
```

Generic discriminated unions enable type-safe error handling patterns.

## Multiple Discriminants

Use multiple properties for complex discrimination:

```ts
type Event =
  | { category: 'user'; action: 'login'; userId: string }
  | { category: 'user'; action: 'logout'; userId: string }
  | { category: 'system'; action: 'error'; message: string }
  | { category: 'system'; action: 'info'; message: string };

function logEvent(event: Event) {
  if (event.category === 'user') {
    if (event.action === 'login') {
      console.log(`User ${event.userId} logged in`);
    } else {
      console.log(`User ${event.userId} logged out`);
    }
  } else {
    if (event.action === 'error') {
      console.error(event.message);
    } else {
      console.info(event.message);
    }
  }
}
```

Multiple discriminants allow hierarchical narrowing.

## Const Assertions in Unions

Use `as const` for literal type inference:

```ts
const success = { ok: true, data: 'hello' } as const;
const failure = { ok: false, error: 'oops' } as const;

type Result = typeof success | typeof failure;

function handleResult(result: Result) {
  if (result.ok) {
    console.log(result.data);
  } else {
    console.error(result.error);
  }
}

const actions = {
  increment: { type: 'increment' } as const,
  decrement: { type: 'decrement' } as const,
  reset: (to: number) => ({ type: 'reset', to }) as const,
};

type Action = ReturnType<(typeof actions)[keyof typeof actions]>;
```

Const assertions ensure discriminants are literal types.

## Avoiding Common Pitfalls

Keep the discriminant property consistent:

```ts
type Event = { type: 'click'; x: number } | { kind: 'scroll'; y: number };

function handle(event: Event) {
  if ('type' in event) {
    console.log(event.x);
  }
}

type EventFixed = { type: 'click'; x: number } | { type: 'scroll'; y: number };

function handleFixed(event: EventFixed) {
  if (event.type === 'click') {
    console.log(event.x);
  } else {
    console.log(event.y);
  }
}
```

Use the same discriminant property name across all union members.

## Pattern Matching Libraries

TypeScript doesn't have built-in pattern matching, but libraries provide it:

```ts
import { match } from 'ts-pattern';

type Response =
  | { status: 'loading' }
  | { status: 'success'; data: string }
  | { status: 'error'; error: Error };

const result = match(response)
  .with({ status: 'loading' }, () => 'Loading...')
  .with({ status: 'success' }, ({ data }) => `Data: ${data}`)
  .with({ status: 'error' }, ({ error }) => `Error: ${error.message}`)
  .exhaustive();
```

Pattern matching libraries provide exhaustiveness checking and cleaner syntax.
