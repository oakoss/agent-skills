---
name: zod-validation
description: 'Zod v4 schema validation for TypeScript. Covers primitives, string formats, objects, arrays, unions, coercion, transforms, refinements, parsing, and type inference. Use when writing schemas, validating input, parsing data, or inferring types with Zod.'
---

# Zod Validation (v4)

Type-safe schema validation for TypeScript. Zod v4 introduces top-level format functions, `z.stringbool()`, `z.iso.*` date formats, and `z.overwrite()` transforms.

**Package:** `zod`

## Quick Reference

| Pattern                                    | Usage                                   |
| ------------------------------------------ | --------------------------------------- |
| `z.object({ ... })`                        | Define object schemas                   |
| `z.string()`, `z.number()`                 | Primitive types                         |
| `z.email()`, `z.url()`, `z.uuid()`         | Top-level string formats (v4)           |
| `z.iso.date()`, `z.iso.datetime()`         | ISO date/time formats (v4)              |
| `z.int()`, `z.float32()`, `z.int32()`      | Fixed-width number formats (v4)         |
| `z.templateLiteral([...])`                 | Template literal type validation (v4)   |
| `z.enum([...])`, `z.literal()`             | Enums and literals                      |
| `z.union([...])`, `z.discriminatedUnion()` | Union types                             |
| `z.array()`, `z.tuple()`                   | Array and tuple types                   |
| `z.record()`, `z.map()`                    | Key-value collections                   |
| `.optional()`, `.nullable()`               | Optional and nullable modifiers         |
| `.default()`, `.catch()`                   | Default values and fallbacks            |
| `z.coerce.number()`                        | Type coercion before validation         |
| `z.stringbool()`                           | String-to-boolean parsing (v4)          |
| `.transform()`, `.overwrite()`             | Output transforms                       |
| `z.pipe()`                                 | Chain schemas (output feeds next input) |
| `.refine()`, `.superRefine()`              | Custom validation logic                 |
| `.parse()`, `.safeParse()`                 | Validate and extract data               |
| `z.infer<typeof Schema>`                   | Extract TypeScript type from schema     |
| `z.input<>`, `z.output<>`                  | Input vs output types with transforms   |

## Common Mistakes

| Mistake                         | Fix                                         |
| ------------------------------- | ------------------------------------------- |
| `z.string().email()`            | `z.email()` (v4 top-level format)           |
| `z.string().url()`              | `z.url()` (v4 top-level format)             |
| Using `parse` without try/catch | Use `safeParse` for error handling          |
| Forgetting `.optional()`        | Add when field may be undefined             |
| `z.any()` for unknown data      | Use `z.unknown()` for type-safe unknown     |
| `.transform()` for same-type    | Use `.overwrite()` (introspectable, v4)     |
| Missing `.min(1)` on strings    | Empty strings pass `z.string()` by default  |
| `z.number().parse(Infinity)`    | `z.number()` rejects `Infinity` in v4       |
| `z.number().safe()` for floats  | `.safe()` equals `.int()` in v4 (no floats) |

## Delegation

Use this skill for Zod schema definition, validation, parsing, type inference, and coercion patterns. For form integration, delegate to the tanstack-form skill.

## References

- [Schema Types](references/schema-types.md) — primitives, string formats, number formats, template literals, objects, arrays, enums, unions, records, optional, nullable
- [Transforms and Parsing](references/transforms-and-parsing.md) — coercion, stringbool, transforms, overwrite, pipe, refinements, parsing, type inference
- [Common Patterns](references/common-patterns.md) — form validation, API responses, environment variables, schema composition, error formatting
