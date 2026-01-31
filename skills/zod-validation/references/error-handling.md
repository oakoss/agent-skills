---
title: Error Handling
description: Zod v4 unified error function, prettifyError, treeifyError, ZodError structure, error formatting utilities, and internationalization with locales
tags:
  [
    error,
    ZodError,
    prettifyError,
    treeifyError,
    formatting,
    errorMap,
    i18n,
    locale,
    internationalization,
    custom-errors,
  ]
---

# Error Handling

## Unified Error Function (v4)

Zod v4 replaces `errorMap`, `required_error`, and `invalid_type_error` with a single `error` function:

```ts
// v3 (deprecated)
// z.string({
//   required_error: "This field is required",
//   invalid_type_error: "Not a string",
// });

// v4 — unified error function
z.string({
  error: 'Must be a string',
});

// Dynamic error messages based on issue details
z.string({
  error: (issue) => {
    if (issue.input === undefined) {
      return 'This field is required';
    }
    return 'Not a string';
  },
});

// Conditional on issue code
z.string().min(5, {
  error: (issue) => {
    if (issue.code === 'too_small') {
      return `Must be at least ${issue.minimum} characters`;
    }
  },
});
```

## ZodError Structure

```ts
const result = schema.safeParse(invalidData);
if (!result.success) {
  const error = result.error; // ZodError instance

  // Access individual issues
  for (const issue of error.issues) {
    console.log(issue.code); // Error code (e.g., "invalid_type", "too_small")
    console.log(issue.path); // Path to the field (e.g., ["user", "email"])
    console.log(issue.message); // Error message
  }
}
```

### Common Issue Codes

| Code                | When triggered                           |
| ------------------- | ---------------------------------------- |
| `invalid_type`      | Wrong type (expected string, got number) |
| `too_small`         | Below minimum length/value               |
| `too_big`           | Above maximum length/value               |
| `invalid_string`    | Failed string format check               |
| `unrecognized_keys` | Extra keys on strict objects             |
| `custom`            | From `.refine()` / `.superRefine()`      |

## Pretty Printing Errors (v4)

```ts
const result = UserSchema.safeParse(invalidData);
if (!result.success) {
  // Human-readable multi-line format
  console.log(z.prettifyError(result.error));
  // Output:
  // ✖ Invalid input: expected string, received number
  //   → at username
  // ✖ Too small: expected number to be >=0
  //   → at favoriteNumbers[1]
}
```

## Tree Error Formatting (v4)

`z.treeifyError()` replaces the deprecated `.format()` and `.flatten()` methods on ZodError:

```ts
const result = UserSchema.safeParse(invalidData);
if (!result.success) {
  const tree = z.treeifyError(result.error);
  // Structured error tree with nested field paths
}
```

`.format()` and `.flatten()` still work but are deprecated in v4. Prefer `z.treeifyError()` for new code.

## Field-Level Error Formatting

```ts
function formatZodErrors(error: z.ZodError): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const issue of error.issues) {
    const path = issue.path.join('.');
    if (!errors[path]) {
      errors[path] = issue.message;
    }
  }
  return errors;
}

const result = RegisterSchema.safeParse(formData);
if (!result.success) {
  const fieldErrors = formatZodErrors(result.error);
  // { email: "Invalid email", confirmPassword: "Passwords must match" }
}
```

## Error Handling Patterns

### Safe Parse with Early Return

```ts
function processUser(input: unknown) {
  const result = UserSchema.safeParse(input);
  if (!result.success) {
    return { ok: false, errors: formatZodErrors(result.error) } as const;
  }
  return { ok: true, data: result.data } as const;
}
```

### Try-Catch with Parse

```ts
try {
  const user = UserSchema.parse(input);
  // user is fully typed
} catch (err) {
  if (err instanceof z.ZodError) {
    console.log(z.prettifyError(err));
  }
  throw err;
}
```

## Internationalization (v4)

Configure global locale for error messages:

```ts
import * as z from 'zod';

// Set English locale (default)
z.config(z.locales.en());

// Per-schema error messages remain possible via the error function
const AgeSchema = z.number().min(18, {
  error: 'Must be 18 or older',
});
```

## Custom Error Map (v4)

Replace the global error generation with a custom function:

```ts
z.config({
  customError: (issue) => {
    if (issue.code === 'invalid_type') {
      return `Expected ${issue.expected}, got ${typeof issue.input}`;
    }
  },
});
```
