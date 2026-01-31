---
title: Type Guards and Narrowing
description: Runtime type checking with typeof, instanceof, in, custom type guards, and assertion functions
tags:
  [
    type-guards,
    narrowing,
    typeof,
    instanceof,
    in,
    type-predicates,
    assertion-functions,
  ]
---

# Type Guards and Narrowing

Type guards narrow union types to specific types based on runtime checks.

## typeof Guards

Check primitive types with `typeof`:

```ts
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}

function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function formatValue(value: string | number | boolean) {
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'number') {
    return value.toString();
  }
  return value ? 'yes' : 'no';
}
```

`typeof` returns: `'string'`, `'number'`, `'boolean'`, `'symbol'`, `'undefined'`, `'object'`, `'function'`, `'bigint'`.

Note: `typeof null` returns `'object'` due to a JavaScript quirk.

## instanceof Guards

Check class instances with `instanceof`:

```ts
class NetworkError extends Error {
  constructor(
    message: string,
    public statusCode: number,
  ) {
    super(message);
  }
}

function handleError(error: Error) {
  if (error instanceof NetworkError) {
    console.error(`HTTP ${error.statusCode}: ${error.message}`);
    return;
  }
  console.error(error.message);
}

function isDate(value: unknown): value is Date {
  return value instanceof Date;
}
```

`instanceof` works with class constructors, not plain object types or interfaces.

## in Operator

Check for property existence:

```ts
type Dog = { bark: () => void };
type Cat = { meow: () => void };

function makeSound(animal: Dog | Cat) {
  if ('bark' in animal) {
    animal.bark();
  } else {
    animal.meow();
  }
}

type Response = { data: unknown } | { error: string };

function handleResponse(response: Response) {
  if ('error' in response) {
    console.error(response.error);
    return;
  }
  console.log(response.data);
}
```

`in` narrows based on property presence. Works with optional properties too.

## Truthiness Narrowing

TypeScript narrows based on truthiness checks:

```ts
function processUser(user: User | null | undefined) {
  if (!user) {
    return;
  }
  console.log(user.name);
}

function firstElement<T>(arr: T[]): T | undefined {
  if (arr.length) {
    return arr[0];
  }
  return undefined;
}

function processValue(value: string | null) {
  if (value) {
    return value.toUpperCase();
  }
}
```

Avoid truthiness checks for values that can be falsy but valid (e.g., `0`, `''`, `false`).

## Equality Narrowing

Check for specific values:

```ts
type Status = 'idle' | 'loading' | 'success' | 'error';

function renderStatus(status: Status) {
  if (status === 'loading') {
    return 'Loading...';
  }
  if (status === 'success') {
    return 'Done!';
  }
  return 'Error or idle';
}

function processValue(value: string | number | null) {
  if (value === null) {
    return;
  }
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}
```

Equality checks narrow unions to specific literal types.

## Custom Type Guards

Define type predicates for reusable narrowing:

```ts
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value &&
    typeof (value as User).id === 'string' &&
    typeof (value as User).name === 'string'
  );
}

function processValue(value: unknown) {
  if (isUser(value)) {
    console.log(value.name);
  }
}

function isNotNull<T>(value: T | null): value is T {
  return value !== null;
}

const users: (User | null)[] = [user1, null, user2];
const validUsers = users.filter(isNotNull);

function isError(value: unknown): value is Error {
  return value instanceof Error;
}
```

Type predicates use the `value is Type` syntax in the return type.

## Assertion Functions

Throw if a condition is not met, narrowing the type:

```ts
function assert(condition: unknown, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

function processUser(user: User | null) {
  assert(user !== null, 'User must be defined');
  console.log(user.name);
}

function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new TypeError('Value must be a string');
  }
}

function processValue(value: unknown) {
  assertIsString(value);
  return value.toUpperCase();
}

function assertNonNull<T>(value: T | null | undefined): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error('Value must not be null or undefined');
  }
}
```

Assertion functions use `asserts condition` or `asserts value is Type` in the return type.

## Array.isArray Narrowing

Narrow arrays with `Array.isArray`:

```ts
function processValue(value: string | string[]) {
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  return value;
}

function flatten(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }
  return [value];
}

function isStringArray(value: unknown): value is string[] {
  return (
    Array.isArray(value) && value.every((item) => typeof item === 'string')
  );
}
```

`Array.isArray` narrows to array types.

## Nullish Checks

Check for null or undefined:

```ts
function getLength(value: string | null | undefined): number {
  if (value == null) {
    return 0;
  }
  return value.length;
}

function processUser(user: User | null | undefined) {
  if (user !== null && user !== undefined) {
    console.log(user.name);
  }
}

const value: string | null = getValue();
if (value !== null) {
  console.log(value.toUpperCase());
}
```

Use `== null` to check for both `null` and `undefined`, or check explicitly.

## Control Flow Analysis

TypeScript tracks narrowing through control flow:

```ts
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  return value.toFixed(2);
}

function formatValue(value: string | null) {
  if (!value) {
    return 'N/A';
  }
  const upper = value.toUpperCase();
  const trimmed = value.trim();
  return `${upper} (${trimmed.length})`;
}

function handleError(error: unknown) {
  if (!(error instanceof Error)) {
    return;
  }
  console.error(error.message);
  if (error instanceof NetworkError) {
    console.error(`Status: ${error.statusCode}`);
  }
}
```

Type narrowing persists within the same code path.

## Type Predicates vs Assertion Functions

Choose based on how you want to handle invalid values:

```ts
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

if (isUser(value)) {
  console.log(value.name);
}

function assertIsUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new TypeError('Invalid user object');
  }
}

assertIsUser(value);
console.log(value.name);
```

Use type predicates for conditional handling. Use assertion functions when invalid input is a programming error.

## Inferred Type Predicates

TypeScript automatically infers type predicates for simple guard functions:

```ts
const isNumber = (x: unknown) => typeof x === 'number';
// Inferred: (x: unknown) => x is number

const isNonNullish = <T>(x: T) => x != null;
// Inferred: <T>(x: T) => x is NonNullable<T>

// Array.filter benefits from inferred predicates
const nums = [1, 2, null, 3].filter((x) => x !== null);
// nums: number[] (not (number | null)[])

const birds = countries
  .map((country) => nationalBirds.get(country))
  .filter((bird) => bird !== undefined);
// birds: Bird[] (not (Bird | undefined)[])
```

The function must return a boolean, take a single parameter, and not use explicit return type annotation. Add an explicit `x is Type` annotation if the inference is not what you want.

## Narrowing with Destructuring

Narrowing can be lost with destructuring:

```ts
type Response = { ok: true; data: string } | { ok: false; error: string };

function handleResponse(response: Response) {
  const { ok } = response;
  if (ok) {
    console.log(response.data);
  }
}

function handleResponseCorrect(response: Response) {
  if (response.ok) {
    console.log(response.data);
  }
}
```

Keep the object intact for discriminated union narrowing to work.
