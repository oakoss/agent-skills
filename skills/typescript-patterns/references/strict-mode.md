---
title: Strict Mode Patterns
description: Strict TypeScript configuration including noUncheckedIndexedAccess, exactOptionalPropertyTypes, const assertions, and satisfies
tags:
  [
    strict-mode,
    noUncheckedIndexedAccess,
    exactOptionalPropertyTypes,
    const-assertions,
    satisfies,
    strict,
  ]
---

# Strict Mode Patterns

Strict mode TypeScript catches more bugs at compile time with additional type checking.

## Strict Flag

Enable all strict checks with `strict: true`:

```json
{
  "compilerOptions": {
    "strict": true
  }
}
```

This enables:

- `noImplicitAny` - No implicit `any` types
- `strictNullChecks` - `null` and `undefined` must be handled explicitly
- `strictFunctionTypes` - Stricter function parameter checking
- `strictBindCallApply` - Type-check `bind`, `call`, `apply`
- `strictPropertyInitialization` - Class properties must be initialized
- `noImplicitThis` - `this` must be typed explicitly
- `alwaysStrict` - Emit `"use strict"` in generated code
- `useUnknownInCatchVariables` - Catch variables typed as `unknown`

## noUncheckedIndexedAccess

Array and object access returns `T | undefined`:

```ts
const arr: number[] = [1, 2, 3];
const first = arr[0];

const value = arr[10];

if (value !== undefined) {
  console.log(value * 2);
}

const obj: Record<string, string> = { a: 'hello' };
const a = obj['a'];

const b = obj['b'];

if (b) {
  console.log(b.toUpperCase());
}
```

Without this flag, `arr[10]` would be typed as `number` even though it's `undefined`.

Enable with:

```json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true
  }
}
```

## exactOptionalPropertyTypes

Distinguish between `undefined` value and missing property:

```ts
type User = {
  name: string;
  email?: string;
};

const user1: User = { name: 'Alice' };

const user2: User = { name: 'Bob', email: undefined };

const user3: User = { name: 'Charlie', email: 'charlie@example.com' };

function hasEmail(user: User): boolean {
  return 'email' in user;
}
```

Without this flag, `email: undefined` is allowed. With it, optional properties cannot be explicitly set to `undefined`.

Enable with:

```json
{
  "compilerOptions": {
    "exactOptionalPropertyTypes": true
  }
}
```

## Const Assertions

Use `as const` for narrowest possible types:

```ts
const config = {
  host: 'localhost',
  port: 3000,
} as const;

type Config = typeof config;

const routes = ['/', '/about', '/contact'] as const;
type Route = (typeof routes)[number];

const status = 'success' as const;

const tuple = [1, 'hello', true] as const;

const nested = {
  server: {
    host: 'localhost',
  },
  cache: {
    ttl: 3600,
  },
} as const;
```

`as const` makes all properties `readonly` and infers literal types instead of widened types.

## Const Assertions vs Readonly

Const assertions are deeper than `Readonly`:

```ts
const obj1: Readonly<{ a: string }> = { a: 'hello' };

const obj2 = { a: 'hello' } as const;

const nested1: Readonly<{ a: { b: string } }> = { a: { b: 'hello' } };
nested1.a.b = 'world';

const nested2 = { a: { b: 'hello' } } as const;
```

`as const` makes all nested properties readonly recursively.

## Satisfies Operator

Type-check without widening:

```ts
type Color = 'red' | 'green' | 'blue' | { r: number; g: number; b: number };

const palette = {
  primary: 'red',
  secondary: { r: 0, g: 255, b: 0 },
} satisfies Record<string, Color>;

const primary = palette.primary;

type Route = { path: string; method: 'GET' | 'POST' };

const routes = {
  home: { path: '/', method: 'GET' },
  createUser: { path: '/users', method: 'POST' },
} satisfies Record<string, Route>;

const homeMethod = routes.home.method;
```

`satisfies` ensures the value matches the type without changing the inferred type.

## Satisfies vs Type Annotation

Type annotation widens, `satisfies` preserves narrow types:

```ts
type Route = { path: string; handler: () => void };

const routes1: Record<string, Route> = {
  home: { path: '/', handler: () => console.log('home') },
};
const homePath = routes1.home.path;

const routes2 = {
  home: { path: '/', handler: () => console.log('home') },
} satisfies Record<string, Route>;
const homeHandler = routes2.home.handler;
```

Use `satisfies` when you want type safety without losing narrow types.

## Combining Satisfies and As Const

Order matters when combining operators:

```ts
const config = {
  host: 'localhost',
  port: 3000,
} as const satisfies Config;

const routes = [
  { path: '/', method: 'GET' },
  { path: '/users', method: 'POST' },
] satisfies Route[] as const;
```

Use `as const satisfies Type` when you want both narrowing and validation.

## Unknown vs Any

Prefer `unknown` over `any`:

```ts
function processValue(value: unknown) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  if (typeof value === 'number') {
    return value.toFixed(2);
  }
  throw new Error('Unsupported type');
}

function parseJSON(json: string): unknown {
  return JSON.parse(json);
}

const data = parseJSON('{"name":"Alice"}');

if (typeof data === 'object' && data !== null && 'name' in data) {
  console.log((data as { name: string }).name);
}
```

`unknown` requires type narrowing before use. `any` bypasses all type checking.

## Non-null Assertion Operator

Use `!` sparingly to assert non-null:

```ts
function getElement(id: string): HTMLElement | null {
  return document.getElementById(id);
}

const element = getElement('root')!;
element.textContent = 'Hello';

const arr: number[] = [1, 2, 3];
const first = arr[0]!;

const user: User | undefined = getUser();
console.log(user!.name);
```

Only use `!` when you're certain the value is non-null. Prefer explicit null checks.

## Definite Assignment Assertion

Tell TypeScript a property is initialized:

```ts
class Component {
  element!: HTMLElement;

  constructor(id: string) {
    this.initialize(id);
  }

  initialize(id: string) {
    this.element = document.getElementById(id) as HTMLElement;
  }
}

let x!: number;
initialize();
console.log(x * 2);

function initialize() {
  x = 42;
}
```

Use `!` after property name to skip initialization checks. Ensure the property is actually initialized.

## Template Literal Types with Strict Mode

Combine template literals with strict checks:

```ts
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type Route = `/${string}`;

type Endpoint = `${HttpMethod} ${Route}`;

const endpoint1: Endpoint = 'GET /users';

type CSSUnit = `${number}${'px' | 'em' | 'rem' | '%'}`;

const width: CSSUnit = '100px';

type EventName<T extends string> = `on${Capitalize<T>}`;

type Handler<T extends string> = Record<EventName<T>, () => void>;

const handlers: Handler<'click' | 'scroll'> = {
  onClick: () => {},
  onScroll: () => {},
};
```

Template literal types enable compile-time string validation.

## Real-World Example: Type-Safe Configuration

```ts
type Environment = 'development' | 'staging' | 'production';

type Config = {
  env: Environment;
  api: {
    baseUrl: string;
    timeout: number;
  };
  features: {
    analytics: boolean;
    darkMode: boolean;
  };
};

const config = {
  env: 'production',
  api: {
    baseUrl: 'https://api.example.com',
    timeout: 5000,
  },
  features: {
    analytics: true,
    darkMode: true,
  },
} as const satisfies Config;

type ConfigEnv = typeof config.env;

function getApiUrl(env: ConfigEnv): string {
  return config.api.baseUrl;
}
```

Combine strict mode features for fully type-safe configuration.

## NoImplicitAny

Avoid implicit `any` types:

```ts
function add(a, b) {
  return a + b;
}

function addTyped(a: number, b: number): number {
  return a + b;
}

const values = [1, 2, 3];
const doubled = values.map((x) => x * 2);

const user = { name: 'Alice', age: 30 };
const keys = Object.keys(user);
const name = user[keys[0]];
```

Always type function parameters explicitly. Array methods often infer correctly.

## StrictNullChecks

Handle `null` and `undefined` explicitly:

```ts
function getLength(str: string | null): number {
  if (str === null) {
    return 0;
  }
  return str.length;
}

function getUser(): User | undefined {
  return undefined;
}

const user = getUser();
if (user) {
  console.log(user.name);
}

const value: string | null = getValue();
const length = value?.length ?? 0;
```

`strictNullChecks` makes `null` and `undefined` distinct types that must be handled.
