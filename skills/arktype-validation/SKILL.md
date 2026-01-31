---
name: arktype-validation
description: 'ArkType runtime validation with TypeScript-native syntax. Type-safe schemas using string expressions, morphs, scopes, and generics. Use when defining schemas, validating data, transforming input, or building type-safe APIs with ArkType.'
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# ArkType Validation

## Overview

ArkType is a TypeScript-native runtime validation library that defines schemas using string expressions mirroring TypeScript syntax, providing editor autocomplete, syntax highlighting, and optimized validators. Use when building type-safe APIs, validating JSON payloads, or replacing Zod with a more TypeScript-idiomatic approach. Not suitable for projects that need Zod ecosystem compatibility or JSON Schema output.

**Package:** `arktype`

## Quick Reference

| Pattern                           | Usage                                           |
| --------------------------------- | ----------------------------------------------- |
| `type({ key: "string" })`         | Define object schema                            |
| `type("string")`                  | Primitive type                                  |
| `"string.email"`, `"string.url"`  | Built-in string validators                      |
| `"string.trim"`, `"string.lower"` | Built-in string morphs (transforms)             |
| `"string.json.parse"`             | Parse JSON string to validated object           |
| `"number > 0"`, `"string >= 1"`   | Inline constraints                              |
| `"string \| number"`              | Union types                                     |
| `"'a' \| 'b' \| 'c'"`             | String literal unions                           |
| `"string[]"`                      | Array types                                     |
| `"key?": "string"`                | Optional properties                             |
| `"key = 'default'"`               | Default values                                  |
| `.pipe()`, `.to()`                | Transform output (morphs)                       |
| `.narrow()`                       | Custom validation (like Zod refine)             |
| `.pick()`, `.omit()`              | Object property selection                       |
| `.merge()`                        | Combine object types                            |
| `scope({...}).export()`           | Named type scopes with cross-references         |
| `type("<t>", { box: "t" })`       | Generic type definitions                        |
| `type.errors`                     | Error handling (check `instanceof type.errors`) |

## Common Mistakes

| Mistake                               | Fix                                             |
| ------------------------------------- | ----------------------------------------------- |
| `type("string.email()")` with parens  | `type("string.email")` (no parens)              |
| Checking errors with `=== null`       | Use `instanceof type.errors`                    |
| `{ key: "string?" }` for optional     | `{ "key?": "string" }` (question mark on key)   |
| Importing from `arktype/types`        | Import `type` and `scope` from `"arktype"`      |
| Nested `type()` in string expressions | Use `scope()` for cross-referencing types       |
| Raw `.pipe()` without error handling  | Use `.pipe.try()` for operations that can throw |
| `"string.lowercase"` for case morph   | `"string.lower"` (also `"string.upper"`)        |

## Delegation

Use this skill for ArkType schema definitions, runtime validation, morphs/transforms, scopes, and type inference. For Zod-based validation, delegate to the zod-validation skill.

## References

- [Schema Types](references/schema-types.md) — primitives, string keywords, number constraints, objects, arrays, tuples, unions, optional, defaults
- [Morphs and Scopes](references/morphs-and-scopes.md) — pipe, morph transforms, narrow validation, scopes, recursive types, generics
- [Common Patterns](references/common-patterns.md) — JSON parsing, form validation, API responses, error handling, comparison with Zod
