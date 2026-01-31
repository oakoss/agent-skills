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

## Scopes

Define named types that can reference each other:

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
