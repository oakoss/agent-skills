---
title: Schema Types
description: Zod v4 primitives, top-level string formats, number formats, template literals, string and number constraints, objects, arrays, tuples, enums, unions, discriminated unions, records, maps, optional, nullable, and defaults
tags:
  [
    primitives,
    string,
    number,
    object,
    array,
    tuple,
    enum,
    union,
    discriminatedUnion,
    record,
    map,
    optional,
    nullable,
    default,
    catch,
    literal,
    templateLiteral,
    int,
    float32,
    cidr,
    file,
  ]
---

# Schema Types

## Primitives

```ts
z.string();
z.number();
z.boolean();
z.bigint();
z.date();
z.symbol();
z.undefined();
z.null();
z.void();
z.any();
z.unknown();
z.never();
```

## String Formats (v4 Top-Level API)

Zod v4 uses top-level functions instead of method chaining:

```ts
z.email();
z.url();
z.uuid();
z.cuid();
z.cuid2();
z.ulid();
z.nanoid();
z.ipv4();
z.ipv6();
z.cidrv4(); // IP range (CIDR notation)
z.cidrv6();
z.base64();
z.base64url();
z.emoji();
```

### ISO Date/Time Formats

```ts
z.iso.date(); // "2024-01-15"
z.iso.time(); // "14:30:00"
z.iso.datetime(); // "2024-01-15T14:30:00Z"
z.iso.duration(); // "P3Y6M4DT12H30M5S"
```

## String Constraints

```ts
z.string().min(1); // Non-empty
z.string().max(100); // Max length
z.string().length(5); // Exact length
z.string().regex(/^[a-z]+$/); // Pattern
z.string().trim(); // Trim whitespace
z.string().toLowerCase(); // Lowercase
z.string().toUpperCase(); // Uppercase
z.string().startsWith('https');
z.string().endsWith('.com');
z.string().includes('@');
```

## Number Formats (v4)

Fixed-width numeric types with pre-configured min/max constraints:

```ts
z.int(); // Safe integer (Number.MIN_SAFE_INTEGER to MAX_SAFE_INTEGER)
z.int32(); // -2147483648 to 2147483647
z.uint32(); // 0 to 4294967295
z.float32(); // IEEE 754 32-bit float range
z.float64(); // IEEE 754 64-bit float range
z.int64(); // Returns ZodBigInt (exceeds safe number range)
z.uint64(); // Returns ZodBigInt (exceeds safe number range)
```

## Number Constraints

```ts
z.number().min(0);
z.number().max(100);
z.number().int(); // Safe integers only (v4: enforces safe range)
z.number().positive();
z.number().negative();
z.number().nonnegative();
z.number().nonpositive();
z.number().multipleOf(5);
z.number().finite();
z.number().safe(); // Same as .int() in v4
```

In v4, `z.number()` no longer accepts `Infinity`. Both `.safe()` and `.int()` enforce the safe integer range.

## Objects

```ts
const User = z.object({
  id: z.string(),
  email: z.email(),
  age: z.number().optional(),
});

type User = z.infer<typeof User>;

// Modifiers
User.partial(); // All optional
User.required(); // All required
User.pick({ id: true, email: true });
User.omit({ age: true });
User.extend({ role: z.string() });
User.merge(OtherSchema);
User.passthrough(); // Allow extra keys
User.strict(); // Reject extra keys
User.strip(); // Remove extra keys
```

## Arrays and Tuples

```ts
z.array(z.string());
z.array(z.number()).min(1); // Non-empty
z.array(z.number()).max(10);
z.array(z.number()).length(5);
z.array(z.number()).nonempty(); // Non-empty (typed)

// Tuple
z.tuple([z.string(), z.number()]);
z.tuple([z.string(), z.number()]).rest(z.boolean());
```

## Enums and Unions

```ts
// Native enum
z.enum(['admin', 'user', 'guest']);

// Union
z.union([z.string(), z.number()]);
z.string().or(z.number()); // Shorthand

// Discriminated union (better errors)
z.discriminatedUnion('type', [
  z.object({ type: z.literal('email'), email: z.email() }),
  z.object({ type: z.literal('phone'), phone: z.string() }),
]);

// Literal
z.literal('active');
z.literal(42);
z.literal(true);
```

## Records and Maps

```ts
// Record (v4 requires both key and value schemas)
z.record(z.string(), z.number()); // { [key: string]: number }

// Enum keys (v4: all keys required)
z.record(z.enum(['a', 'b']), z.number()); // { a: number, b: number }
z.partialRecord(z.enum(['a', 'b']), z.number()); // { a?: number, b?: number }

// Map
z.map(z.string(), z.number());
```

## Template Literal Types (v4)

Represent TypeScript template literal types with validation:

```ts
const greeting = z.templateLiteral(['hello, ', z.string()]);
// `hello, ${string}`

const cssUnits = z.enum(['px', 'em', 'rem', '%']);
const cssValue = z.templateLiteral([z.number(), cssUnits]);
// `${number}px` | `${number}em` | `${number}rem` | `${number}%`

const emailPattern = z.templateLiteral([
  z.string().min(1),
  '@',
  z.string().max(64),
]);
// `${string}@${string}` (min/max constraints are enforced)
```

Supports strings, string formats, numbers, booleans, bigints, enums, literals, and nested template literals. Constraints like `.min()` and `.max()` are enforced in the generated regex.

## File Validation (v4)

Validate JavaScript `File` instances:

```ts
const fileSchema = z.file();

fileSchema.min(10_000); // minimum .size (bytes)
fileSchema.max(1_000_000); // maximum .size (bytes)
fileSchema.mime(['image/png', 'image/jpeg']); // MIME type

// Practical upload schema
const UploadSchema = z.object({
  avatar: z.file().max(5_000_000).mime(['image/png', 'image/jpeg']),
  document: z.file().max(10_000_000).mime(['application/pdf']),
});
```

## Optional, Nullable, and Defaults

```ts
z.string().optional(); // string | undefined
z.string().nullable(); // string | null
z.string().nullish(); // string | null | undefined

// Defaults
z.string().default('hello');
z.number().default(0);

// Catch (use default on parse error)
z.string().catch('fallback');
```
