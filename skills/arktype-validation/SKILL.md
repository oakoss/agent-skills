---
name: arktype-validation
description: 'ArkType runtime validation with TypeScript-native syntax. Type-safe schemas using string expressions, morphs, scopes, and generics. Use when defining schemas, validating data, transforming input, or building type-safe APIs with ArkType.'
---

# ArkType Validation

Runtime validation library that uses TypeScript-native syntax for schema definitions. Schemas are defined as string expressions that mirror TypeScript types, providing autocomplete, syntax highlighting, and optimized validators.

**Package:** `arktype`

## Quick Reference

| Pattern                          | Usage                                           |
| -------------------------------- | ----------------------------------------------- |
| `type({ key: "string" })`        | Define object schema                            |
| `type("string")`                 | Primitive type                                  |
| `"string.email"`, `"string.url"` | Built-in string formats                         |
| `"string.json.parse"`            | Parse JSON string to validated object           |
| `"number > 0"`, `"string >= 1"`  | Inline constraints                              |
| `"string \| number"`             | Union types                                     |
| `"'a' \| 'b' \| 'c'"`            | String literal unions                           |
| `"string[]"`                     | Array types                                     |
| `"key?": "string"`               | Optional properties                             |
| `"key = 'default'"`              | Default values                                  |
| `.pipe()`, `.to()`               | Transform output (morphs)                       |
| `.narrow()`                      | Custom validation (like Zod refine)             |
| `.pick()`, `.omit()`             | Object property selection                       |
| `.merge()`                       | Combine object types                            |
| `scope({...}).export()`          | Named type scopes with cross-references         |
| `type.errors`                    | Error handling (check `instanceof type.errors`) |

## Common Mistakes

| Mistake                               | Fix                                             |
| ------------------------------------- | ----------------------------------------------- |
| `type("string.email()")` with parens  | `type("string.email")` (no parens)              |
| Checking errors with `=== null`       | Use `instanceof type.errors`                    |
| `{ key: "string?" }` for optional     | `{ "key?": "string" }` (question mark on key)   |
| Importing from `arktype/types`        | Import `type` and `scope` from `"arktype"`      |
| Nested `type()` in string expressions | Use `scope()` for cross-referencing types       |
| Raw `.pipe()` without error handling  | Use `.pipe.try()` for operations that can throw |

## Delegation

Use this skill for ArkType schema definitions, runtime validation, morphs/transforms, scopes, and type inference. For Zod-based validation, delegate to the zod-validation skill.

## References

- [Schema Types](references/schema-types.md) — primitives, string keywords, number constraints, objects, arrays, tuples, unions, optional, defaults
- [Morphs and Scopes](references/morphs-and-scopes.md) — pipe, morph transforms, narrow validation, scopes, recursive types, generics
- [Common Patterns](references/common-patterns.md) — JSON parsing, form validation, API responses, error handling, comparison with Zod
