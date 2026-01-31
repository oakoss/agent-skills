---
title: Transforms and Parsing
description: Zod v4 coercion, stringbool, transform, overwrite, refine, superRefine, parse, safeParse, async parsing, pipe, and type inference with z.infer, z.input, z.output
tags:
  [
    coerce,
    stringbool,
    transform,
    overwrite,
    pipe,
    refine,
    superRefine,
    parse,
    safeParse,
    parseAsync,
    infer,
    input,
    output,
    type-inference,
  ]
---

# Transforms and Parsing

## Coercion

Coerce input to the target type before validation:

```ts
z.coerce.string(); // Converts to string
z.coerce.number(); // Converts to number
z.coerce.boolean(); // Falsy -> false, truthy -> true
z.coerce.date(); // Converts to Date
z.coerce.bigint(); // Converts to BigInt
```

## String to Boolean (v4)

```ts
// Env-style boolean parsing
z.stringbool();

// Recognized values:
// true:  "true", "1", "yes", "on", "y", "enabled"
// false: "false", "0", "no", "off", "n", "disabled"

// Custom values
z.stringbool({
  truthy: ['yes', 'true'],
  falsy: ['no', 'false'],
});
```

## Transforms

```ts
// Transform output type (input -> different output)
z.string().transform((val) => val.length); // string -> number
z.string().transform((val) => parseInt(val, 10));

// Overwrite (same type, introspectable — v4)
z.number().overwrite((val) => val * 2);
z.string().overwrite((val) => val.trim());
```

Use `.overwrite()` when the output type matches the input -- it preserves schema introspection. Use `.transform()` when the output type differs.

## Pipe

Chain schemas so the output of one becomes the input of the next:

```ts
// Coerce string to number, then validate
const stringToPositiveInt = z.pipe(
  z.coerce.number(),
  z.number().int().positive(),
);

stringToPositiveInt.parse('42'); // 42
stringToPositiveInt.parse('-1'); // throws

// Shorthand with .pipe() method
const trimmedEmail = z.string().pipe(z.email());
```

Use `z.pipe()` when you need multi-step validation where each step expects a different input type.

## Refinements

```ts
// Simple refinement
z.string().refine((val) => val.includes('@'), {
  message: 'Must contain @',
});

// Multiple refinements
z.string()
  .refine((val) => val.length > 0, 'Required')
  .refine((val) => val.includes('@'), 'Must contain @');

// SuperRefine (custom error positioning)
z.string().superRefine((val, ctx) => {
  if (!val.includes('@')) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: 'Must contain @',
    });
  }
});
```

The `.refine()` overload that accepted a function as the second argument has been removed in v4. Use `.superRefine()` for dynamic error messages:

```ts
// v3 (removed in v4)
// z.string().refine(
//   (val) => val.length > 10,
//   (val) => ({ message: `${val} is not more than 10 characters` })
// );

// v4 replacement
z.string().superRefine((val, ctx) => {
  if (val.length <= 10) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: `${val} is not more than 10 characters`,
    });
  }
});
```

### Cross-Field Validation

```ts
const PasswordForm = z
  .object({
    password: z.string().min(8),
    confirm: z.string(),
  })
  .refine((data) => data.password === data.confirm, {
    message: 'Passwords must match',
    path: ['confirm'],
  });
```

## Parsing

```ts
const schema = z.string();

// Throws on error
schema.parse('hello'); // 'hello'
schema.parse(123); // throws ZodError

// Returns result object (preferred)
schema.safeParse('hello'); // { success: true, data: 'hello' }
schema.safeParse(123); // { success: false, error: ZodError }

// Async (for async refinements/transforms)
await schema.parseAsync('hello');
await schema.safeParseAsync('hello');
```

## Type Inference

```ts
const UserSchema = z.object({
  id: z.string(),
  email: z.email(),
});

type User = z.infer<typeof UserSchema>;
// { id: string; email: string }

// Input vs Output types (when using transforms)
type UserInput = z.input<typeof UserSchema>;
type UserOutput = z.output<typeof UserSchema>;
```

Use `z.input<>` and `z.output<>` when schemas include `.transform()` or `.default()` -- the input and output types will differ.

### Transform Type Inference Example

```ts
const StringToNumberSchema = z.object({
  count: z.string().transform((val) => parseInt(val, 10)),
  name: z.string().default('anonymous'),
});

type Input = z.input<typeof StringToNumberSchema>;
// { count: string; name?: string }

type Output = z.output<typeof StringToNumberSchema>;
// { count: number; name: string }
```
