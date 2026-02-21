---
title: Morphs and Scopes
description: ArkType morphs (pipe transforms), narrow validation, scopes with cross-references, recursive types, and generics for reusable type definitions
tags:
  [
    morph,
    pipe,
    narrow,
    transform,
    scope,
    recursive,
    cyclic,
    generic,
    pick,
    omit,
    merge,
    this,
    alias,
  ]
---

# Morphs and Scopes

## Morphs (Transforms)

Transform validated input using `.pipe()` or the `=>` tuple syntax:

```ts
import { type } from 'arktype';

// Pipe syntax — chain transformations
const trimmed = type('string').pipe((s) => s.trim());

// Tuple syntax
const trimmed2 = type(['string', '=>', (s) => s.trim()]);

// Chain multiple steps
const trimToNonEmpty = type.pipe(
  type.string,
  (s) => s.trimStart(),
  type.string.atLeastLength(1),
);
```

## Pipe with Validation (.to)

`.to()` is shorthand for `.pipe()` with a single output validator:

```ts
const parseJson = type('string.json.parse').to({
  name: 'string',
  version: 'string.semver',
});

const out = parseJson('{ "name": "arktype", "version": "2.0.0" }');

if (!(out instanceof type.errors)) {
  console.log(`${out.name}:${out.version}`);
}
```

## Safe Pipe (.pipe.try)

Use `.pipe.try()` for operations that can throw:

```ts
const parseJson = type('string').pipe.try(
  (s): object => JSON.parse(s),
  type({
    name: 'string',
    version: 'string.semver',
  }),
);
```

## Narrow (Custom Validation)

Add custom validation logic without transforming the output:

```ts
const even = type('number.integer').narrow((n, ctx) => {
  if (n % 2 !== 0) {
    return ctx.reject({ expected: 'an even number' });
  }
  return true;
});

const passwordMatch = type({
  password: 'string >= 8',
  confirm: 'string',
}).narrow((data, ctx) => {
  if (data.password !== data.confirm) {
    return ctx.reject({
      expected: 'passwords to match',
      path: ['confirm'],
    });
  }
  return true;
});
```

## Assert (Throwing Validation)

`.assert()` throws on invalid input instead of returning `type.errors`:

```ts
import { type } from 'arktype';

const User = type({
  name: 'string >= 1',
  email: 'string.email',
});

const user = User.assert({ name: 'Alice', email: 'alice@example.com' });
// Returns validated data or throws AggregateError
```

Use `assert` when invalid data is a programmer error rather than expected user input.

## Branding

Add type-only symbols so only directly validated values satisfy the type:

```ts
import { type } from 'arktype';

const Even = type('(number % 2)#even');
type Even = typeof Even.infer;

const good: Even = Even.assert(2);
// const bad: Even = 5; // TypeScript error — not branded
```

Fluent API:

```ts
const PositiveInt = type.number.moreThan(0).brand('positiveInt');
type PositiveInt = typeof PositiveInt.infer;
```

## Scopes

Define named types that can reference each other. Use `scope()` for complex type systems, `type.module()` for quick groups:

```ts
import { scope } from 'arktype';

const types = scope({
  User: {
    name: 'string',
    email: 'string.email',
    'posts?': 'Post[]',
  },
  Post: {
    title: 'string',
    content: 'string',
    author: 'User',
  },
}).export();

// Access types
const user = types.User({ name: 'Alice', email: 'alice@example.com' });
type User = typeof types.User.infer;
```

## Quick Modules

`type.module()` is a lighter alternative when you don't need `scope`'s full power:

```ts
import { type } from 'arktype';

const auth = type.module({
  Credentials: {
    username: 'string >= 3',
    password: 'string >= 8',
  },
  Token: {
    value: 'string',
    expiresAt: 'Date',
  },
});

const creds = auth.Credentials({ username: 'alice', password: 'secret123' });
```

## Recursive Types

Scopes enable recursive/cyclic type definitions:

```ts
const types = scope({
  Category: {
    name: 'string',
    'children?': 'Category[]',
  },
}).export();

const tree = types.Category({
  name: 'root',
  children: [
    { name: 'child1' },
    { name: 'child2', children: [{ name: 'grandchild' }] },
  ],
});
```

Self-referencing within a scope:

```ts
const types = scope({
  Package: {
    name: 'string',
    'dependencies?': 'Package[]',
    'contributors?': 'Contributor[]',
  },
  Contributor: {
    email: 'string.email',
    'packages?': 'Package[]',
  },
}).export();
```

## Generics

Define reusable generic type constructors using string-based angle bracket syntax:

```ts
const boxOf = type('<t>', { box: 't' });

const stringBox = boxOf('string');
// { box: string }

// Constrained generics
const nonEmpty = type('<arr extends unknown[]>', 'arr > 0');

// Multi-parameter generics
const either = type('<a, b>', 'a | b');
const stringOrNumber = either('string', 'number');
```

### Scoped Generics

```ts
const types = scope({
  'box<t, u>': {
    box: 't | u',
  },
  bitBox: 'box<0, 1>',
}).export();

const out = types.bitBox({ box: 0 });
```

## Global Configuration

Import from `arktype/config` **before** importing from `arktype`:

```ts
import { configure } from 'arktype/config';

configure({ onUndeclaredKey: 'delete' });

// Now import arktype
import { type } from 'arktype';
```

Configuration applied after `arktype` is imported will not affect built-in keywords that were already parsed.

## Pattern Matching (2.1)

The `match` function provides type-safe pattern matching:

```ts
import { type, match } from 'arktype';

const describe = match({
  string: (s) => `a string: ${s}`,
  number: (n) => `a number: ${n}`,
  default: 'something else',
});

describe('hello'); // "a string: hello"
describe(42); // "a number: 42"
```

## Standard Schema

ArkType co-authors the [Standard Schema](https://github.com/standard-schema/standard-schema) spec with Zod and Valibot. Any ArkType schema works as a Standard Schema validator — libraries like TanStack Form, ArkEnv, and tRPC can consume it without coupling to a specific validation library.

## arkregex

The `arkregex` package infers string literal types from regular expressions at compile time with zero runtime overhead:

```ts
import { regex } from 'arkregex';

const semver = regex('^(\\d*)\\.(\\d*)\\.(\\d*)$');
// Regex<`${bigint}.${bigint}.${bigint}`, { captures: [...] }>

const email = regex('^(?<name>\\w+)@(?<domain>\\w+\\.\\w+)$');
// Named capture groups are typed
```

For most validation, ArkType's built-in `string.email`, `string.semver`, or inline `/regex/` syntax is sufficient. Use `arkregex` when you need typed capture groups or compile-time string type inference.
