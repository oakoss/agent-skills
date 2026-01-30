---
paths:
  - 'skills/**/references/**'
  - 'scripts/**/*.ts'
---

# TypeScript Rules

## Unicorn Overrides

```ts
// null IS allowed (unicorn/no-null: off)
const value = null; // Good

// Abbreviations ARE allowed (unicorn/prevent-abbreviations: off)
const btn = document.querySelector('button'); // Good
const handleErr = (e) => {}; // Good
```

For full unicorn patterns (arrays, strings, errors), see the `typescript` skill.

## Naming Conventions

| Style                  | Use For                                |
| ---------------------- | -------------------------------------- |
| `PascalCase`           | Types, interfaces, classes, components |
| `camelCase`            | Functions, variables, methods          |
| `SCREAMING_SNAKE_CASE` | Constants                              |
| `kebab-case`           | File names (enforced by ESLint)        |

File naming exceptions:

- Route parameter files starting with `$` are allowed (e.g., `$id.tsx`, `$postId.tsx`) — TanStack Router convention

## Type Safety

- **No `any`** without explicit justification comment
- **No `@ts-ignore`** or `@ts-expect-error` without explanation
- Prefer `unknown` over `any` when type is truly unknown
- Use explicit return types on exported functions

```ts
// Bad
const data: any = response;

// Good - justified
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- Legacy API returns untyped response
const data: any = legacyApi.fetch();

// Better - use unknown and narrow
const data: unknown = response;
if (isUser(data)) {
  // data is now typed as User
}
```

## Async/Await

- Always handle promise rejections
- Use try/catch for async operations
- Avoid floating promises (unhandled)

```ts
// Bad - floating promise
fetchData();

// Good - handled
await fetchData();
fetchData().catch(console.error);
void fetchData(); // Explicitly ignored
```

## Compiler Options

Recommended strict TypeScript configuration:

- `strict: true` - All strict type checks enabled
- `target: ES2023` - Modern JavaScript features (toSorted, toReversed, findLast, etc.)
- `noImplicitOverride: true` - Require `override` keyword for inherited methods
- `noUncheckedIndexedAccess: true` - Include `undefined` in index signatures
- `isolatedModules: true` - Each file is a separate module
- `moduleResolution: bundler` - Modern bundler resolution

## Type Definitions

Use `type` keyword, not `interface`:

```ts
type User = { id: string; name: string }; // Good
interface User {
  id: string;
  name: string;
} // Bad
```

## Type Imports & Exports

Inline type imports AND exports:

```ts
import { type User, getUser } from './user'; // Good
export { type User, getUser }; // Good
import type { User } from './user'; // Bad
export type { User } from './user'; // Bad
```

## Unused Variables

Prefix unused variables with `_`:

```ts
const [_unused, setUsed] = useState(); // Good
```

## Class Fields

Use class fields over constructor assignments:

```ts
class Foo {
  bar = 'value';
} // Good
```

## Import Sorting

- Auto-sorted via `simple-import-sort` (imports AND exports)
- Group imports: external → internal (aliases) → relative
- Imports must be at top of file, with blank line after
- No duplicate imports (prefer inline: `import { A, B } from 'x'`)
- No circular dependencies

```ts
// External
import { useState } from 'react';
import { z } from 'zod';

// Internal (aliases or packages)
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// Relative (same module only)
import { helper } from './helper';
```

## TypeScript ESLint Rules (recommended-type-checked + stylistic-type-checked)

### Type-Checked Rules (Enabled)

```ts
// await-thenable - Only await Promises
await promise; // Good
await 'string'; // Bad

// no-for-in-array - Use for-of for arrays
for (const x in array) {
} // Bad
for (const x of array) {
} // Good

// no-base-to-string - Don't stringify objects without toString
`${object}`; // Bad if object has no toString

// no-unnecessary-type-assertion - Don't assert known types
const x = value as string; // Bad if already string

// restrict-plus-operands - Only add compatible types
'str' + 123; // Bad
'str' + String(123); // Good

// unbound-method - Don't pass unbound methods
array.map(obj.method); // Bad
array.map((x) => obj.method(x)); // Good
```

### Stylistic Rules (Enabled)

```ts
// array-type - Use T[] not Array<T>
// consistent-type-definitions - Use 'type' not 'interface'
// consistent-type-exports/imports - Inline style
// dot-notation - Use obj.prop not obj['prop']
// no-inferrable-types - Don't annotate obvious types
const x: number = 5; // Bad
const x = 5; // Good

// prefer-nullish-coalescing - Use ?? over ||
const x = a ?? b; // Good
const x = a || b; // Bad (when a could be 0 or '')

// prefer-optional-chain - Use ?. chaining
obj?.prop?.method?.(); // Good
obj && obj.prop && obj.prop.method && obj.prop.method(); // Bad

// prefer-return-this-type - Return this type in chainable methods
```

### Rules OFF in This Project

| Rule                            | Why Disabled                                   |
| ------------------------------- | ---------------------------------------------- |
| `no-explicit-any`               | Allowed with justification comment (see above) |
| `no-unsafe-*`                   | Unsafe operations allowed with any             |
| `no-unnecessary-condition`      | Optional checks allowed                        |
| `only-throw-error`              | Can throw non-Error objects                    |
| `restrict-template-expressions` | Any type in template literals OK               |
