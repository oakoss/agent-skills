---
title: Common Patterns
description: Practical ArkType patterns for JSON parsing, form validation, API responses, error handling, environment variables, and comparison with Zod syntax
tags:
  [
    json,
    parse,
    form,
    validation,
    API,
    response,
    error,
    handling,
    type.errors,
    environment,
    env,
    zod,
    comparison,
    pattern,
  ]
---

# Common Patterns

## JSON Parsing and Validation

```ts
import { type } from 'arktype';

const parseConfig = type('string.json.parse').to({
  host: 'string',
  port: 'number.integer > 0 & number < 65536',
  'ssl = false': 'boolean',
});

const result = parseConfig('{"host": "localhost", "port": 3000}');

if (result instanceof type.errors) {
  console.error(result.summary);
} else {
  console.log(result.host); // "localhost"
}
```

## Error Handling

ArkType returns errors as `type.errors` instances instead of throwing:

```ts
const User = type({
  name: 'string >= 1',
  email: 'string.email',
  age: 'number.integer >= 0',
});

const result = User({ name: '', email: 'bad', age: -1 });

if (result instanceof type.errors) {
  // Full error summary
  console.error(result.summary);
  // "name must be at least length 1 (was 0)
  //  email must be an email address (was "bad")
  //  age must be at least 0 (was -1)"

  // Iterate individual errors
  for (const error of result) {
    console.log(error.path, error.message);
  }
}
```

## Form Validation

```ts
const LoginSchema = type({
  email: 'string.email',
  password: 'string >= 8',
  'rememberMe = false': 'boolean',
});

const RegisterSchema = type({
  name: 'string >= 1 & string <= 100',
  email: 'string.email',
  password: 'string >= 8 & string <= 100',
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

## API Response Pattern

```ts
const ApiResponse = type.generic('T')((T) =>
  type({
    data: T,
    error: 'string | null',
    status: "'success' | 'error'",
  }),
);

const UserResponse = ApiResponse({
  id: 'string.uuid',
  name: 'string',
  email: 'string.email',
});

type UserResponse = typeof UserResponse.infer;
```

## Environment Variables

```ts
const EnvSchema = type({
  DATABASE_URL: 'string.url',
  PORT: 'string.numeric.parse',
  NODE_ENV: "'development' | 'production' | 'test'",
  'SESSION_SECRET >= 32': 'string',
  'API_KEY?': 'string',
}).pipe((env) => ({
  ...env,
  PORT: typeof env.PORT === 'number' ? env.PORT : 3000,
}));
```

## Discriminated Unions

```ts
const Event = type(
  {
    type: "'click'",
    x: 'number',
    y: 'number',
  },
  '|',
  {
    type: "'keypress'",
    key: 'string',
    'modifiers?': 'string[]',
  },
  '|',
  {
    type: "'scroll'",
    deltaY: 'number',
  },
);
```

## Zod vs ArkType Comparison

| Concept         | Zod                                 | ArkType                                     |
| --------------- | ----------------------------------- | ------------------------------------------- |
| Define object   | `z.object({ name: z.string() })`    | `type({ name: "string" })`                  |
| Optional        | `z.string().optional()`             | `"key?": "string"`                          |
| Default         | `z.string().default("x")`           | `"key = 'x'": "string"`                     |
| Union           | `z.union([z.string(), z.number()])` | `type("string \| number")`                  |
| Array           | `z.array(z.string())`               | `type("string[]")`                          |
| Email           | `z.email()`                         | `type("string.email")`                      |
| Min length      | `z.string().min(1)`                 | `type("string >= 1")`                       |
| Integer         | `z.number().int()`                  | `type("number.integer")`                    |
| Transform       | `.transform(fn)`                    | `.pipe(fn)` or `["string", "=>", fn]`       |
| Custom validate | `.refine(fn)`                       | `.narrow(fn)`                               |
| Parse           | `schema.parse(data)`                | `schema(data)`                              |
| Safe parse      | `schema.safeParse(data)`            | `schema(data)` (returns errors, not throws) |
| Infer type      | `z.infer<typeof Schema>`            | `typeof Schema.infer`                       |
| Recursive       | `z.lazy(() => schema)`              | `scope({...}).export()`                     |
| Scoped types    | N/A                                 | `scope({...}).export()`                     |
