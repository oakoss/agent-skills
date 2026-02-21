---
title: Schema Types
description: ArkType primitives, string keywords, number constraints, objects with optional and default properties, arrays, tuples, unions, literals, regex patterns, and inline constraints
tags:
  [
    type,
    string,
    number,
    boolean,
    object,
    array,
    tuple,
    union,
    literal,
    optional,
    default,
    constraints,
    regex,
    email,
    url,
    uuid,
    semver,
    integer,
  ]
---

# Schema Types

## Primitives

ArkType supports both string syntax and fluent API:

```ts
import { type } from 'arktype';

// String syntax
const str = type('string');
const num = type('number');
const bool = type('boolean');
const bigint = type('bigint');
const sym = type('symbol');
const date = type('Date');

// Fluent API
const str2 = type.string;
const num2 = type.number;
const bool2 = type.boolean;
```

## String Keywords

Built-in string format validators:

```ts
// Validators (return string)
type('string.email');
type('string.url');
type('string.uuid');
type('string.uuid.v4');
type('string.semver');
type('string.ip');
type('string.ip.v4');
type('string.ip.v6');
type('string.date');
type('string.date.iso');
type('string.numeric');
type('string.integer');
type('string.alpha');
type('string.alphanumeric');
type('string.digits');
type('string.hex');
type('string.creditCard');
type('string.base64');
type('string.base64.url');
type('string.json');
type('string.host'); // Hostname (IP or domain)

// Morphs (transform the value)
type('string.trim'); // Trims whitespace
type('string.lower'); // Transforms to lowercase
type('string.upper'); // Transforms to uppercase
type('string.capitalize'); // Capitalizes first letter
type('string.normalize.NFC'); // Unicode normalization
type('string.json.parse'); // Parses JSON string at runtime
type('string.numeric.parse'); // Parses numeric string to number
type('string.integer.parse'); // Parses integer string to number
type('string.date.parse'); // Parses date string to Date
type('string.date.iso.parse'); // Parses ISO date string to Date
type('string.url.parse'); // Parses URL string to URL instance
```

## String Constraints

```ts
type('string >= 1'); // Min length 1
type('string <= 100'); // Max length 100
type('string >= 1 & string <= 100'); // Range (intersection)
type('5 <= string <= 20'); // Range (compact syntax)
type('string == 5'); // Exact length

// Regex patterns
type('/^[a-z]+$/');
type({ key: /^[a-z]+$/ }); // RegExp object
```

## Number Constraints

```ts
type('number > 0'); // Positive
type('number >= 0'); // Non-negative
type('number < 100'); // Less than 100
type('number % 2'); // Divisible by 2 (even)
type('number.integer'); // Integer only
type('number.safe'); // Safe integer range
type('number.epoch'); // Unix timestamp (safe integer >= 0)
type('number.port'); // Valid port (integer 0-65535)
type('number > 0 & number < 100'); // Range (intersection)
type('0 <= number <= 100'); // Range (compact syntax)
type('1 <= number.integer <= 5'); // Constrained range
type('0 <= number.integer % 5 <= 100'); // Range + divisibility

// Fluent API constraints
type.number.atLeast(0);
type.number.atMost(100);
type.number.moreThan(0);
type.number.lessThan(100);
type.number.divisibleBy(5);
```

## Objects

```ts
const User = type({
  name: 'string',
  email: 'string.email',
  age: 'number >= 0',
});

// Infer TypeScript type
type User = typeof User.infer;
// { name: string; email: string; age: number }
```

### Optional Properties

```ts
const User = type({
  name: 'string',
  'bio?': 'string', // Optional (question mark on key)
  'age?': 'number',
});
```

### Default Values

```ts
const Config = type({
  'theme = "light"': 'string',
  'retries = 3': 'number',
  'debug = false': 'boolean',
});
```

### Undeclared Key Handling

```ts
// Inline syntax with "+"
const Strict = type({
  '+': 'reject',
  name: 'string',
});

// Fluent API
const StrictFluent = type({
  name: 'string',
}).onUndeclaredKey('reject'); // Reject extra keys

const Strip = type({
  name: 'string',
}).onUndeclaredKey('delete'); // Strip extra keys

// Deep undeclared key handling (nested objects)
const DeepStrip = type({
  name: 'string',
  nested: {
    preserved: 'string',
  },
}).onDeepUndeclaredKey('delete');
```

### Object Modifiers

```ts
const User = type({
  name: 'string',
  email: 'string.email',
  'age?': 'number',
});

User.pick('name', 'email'); // Only name and email
User.omit('age'); // Remove age
User.merge({
  role: "'admin' | 'user'",
});
```

## Arrays and Tuples

```ts
// Arrays
type('string[]');
type('number[]');
type('string.email[]');

// In objects
const Team = type({
  members: 'string[]',
  scores: 'number[]',
});

// Tuples
type(['string', 'number']); // [string, number]
type(['string', 'number', '...', 'boolean[]']); // [string, number, ...boolean[]]
```

## Unions and Literals

```ts
// Unions
type('string | number');
type("'success' | 'error' | 'pending'");

// Literal values
type('true');
type('false');
type('0');
type("'active'");

// In objects
const Event = type({
  type: "'click' | 'hover' | 'focus'",
  target: 'string',
  'data?': 'unknown',
});
```

## Intersections

```ts
// Combine constraints
type('number > 0 & number < 100 & number.integer');
type('string >= 1 & string <= 50');

// Object intersections
const Named = type({ name: 'string' });
const Aged = type({ age: 'number' });
const Person = Named.and(Aged);
```

## Date Constraints

```ts
// String syntax with date literals
const Bounded = type({
  dateInThePast: `Date < ${Date.now()}`,
  dateAfter2000: "Date > d'2000-01-01'",
  dateAtOrAfter1970: 'Date >= 0',
});

// Fluent API
const FluentBounded = type({
  dateInThePast: type.Date.earlierThan(Date.now()),
  dateAfter2000: type.Date.laterThan('2000-01-01'),
  dateAtOrAfter1970: type.Date.atOrAfter(0),
});
```

## Index Signatures and keyof

```ts
// Index signatures
type('Record<string, unknown>');
const Dict = type({ '[string]': 'number' });

// Extract object keys as union type
const User = type({
  name: 'string',
  email: 'string.email',
});

const UserKey = User.keyof();
type UserKey = typeof UserKey.infer; // "name" | "email"
```

## Special Types

```ts
type('unknown'); // Any value
type('never'); // No value
type('void'); // undefined
type('null');
type('undefined');
type('object'); // Non-null object
type('Record<string, unknown>'); // String-keyed object
```
