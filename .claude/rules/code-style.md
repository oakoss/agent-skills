---
paths:
  - 'skills/**/references/**'
  - 'scripts/**/*.ts'
---

# Code Style

## Formatting (Prettier v3)

Configured:

- Single quotes (`'`) for strings
- `package.json` keys auto-sorted (via `prettier-plugin-packagejson`)

Defaults (Prettier v3):

- Semicolons: Yes
- Tab width: 2 spaces
- Trailing commas: `all` (ES5+)
- Print width: 80 characters
- Bracket spacing: Yes (`{ foo }` not `{foo}`)
- JSX quotes: Double quotes in JSX

Max 0 ESLint warnings enforced.

## Global Ignores (Not Linted)

- `node_modules`, `dist`, `build`, `out`
- `.nitro`, `.output`, `.tanstack`, `.vinxi`, `.wrangler`
- `.turbo`, `.beads`
- `coverage`, `playwright-report`, `test-results`, `storybook-static`
- `**/*.gen.ts` - Generated files
- `**/drizzle.config.ts` - Drizzle config

## ESLint JS Recommended (Base Rules)

The project extends `@eslint/js` recommended:

- No syntax errors (`no-dupe-keys`, `no-duplicate-case`, `no-invalid-regexp`)
- No unreachable code (`no-unreachable`, `no-fallthrough`)
- No unsafe operations (`no-unsafe-negation`, `no-unsafe-finally`)
- No common bugs (`no-cond-assign`, `no-constant-condition`, `no-debugger`)
- Valid types (`valid-typeof`, `use-isnan`)
- No redeclarations (`no-redeclare`, `no-const-assign`, `no-class-assign`)

## General Rules

- Strict equality required (`===`/`!==`, never `==`/`!=`)
- Avoid `console.log` (warning) - allowed in tests, seeds, logger, env

```ts
// Bad - debug console.log in production code
console.log('user:', user);

// Good - use structured logging
logger.info('User logged in', { userId: user.id });

// Good - console.error for actual errors
console.error('Failed to fetch:', error);
```

## Sorted Object Keys

Object keys sorted alphabetically (when 3+ keys):

```ts
const config = { alpha: 1, beta: 2, gamma: 3 }; // sorted
```

## Ignored Files for console.log

- `**/*.gen.ts` - Generated files
- Tests, specs, stories, seeds, logger, env config, e2e
