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
const ApiResponse = type('<t>', {
  data: 't',
  error: 'string | null',
  status: "'success' | 'error'",
});

const UserResponse = ApiResponse({
  id: 'string.uuid',
  name: 'string',
  email: 'string.email',
});

type UserResponse = typeof UserResponse.infer;
```

## Environment Variables with ArkEnv

[ArkEnv](https://arkenv.js.org) wraps ArkType for environment variable validation with automatic coercion, defaults, and framework plugins.

Install alongside ArkType:

```bash
pnpm add arkenv arktype
```

### Basic Usage

```ts
import arkenv from 'arkenv';

const env = arkenv({
  HOST: "string.ip | 'localhost'",
  PORT: '0 <= number.integer <= 65535',
  NODE_ENV: "'development' | 'production' | 'test' = 'development'",
  DEBUGGING: 'boolean = false',
  SESSION_SECRET: 'string >= 32',
  'API_KEY?': 'string',
});

env.PORT; // number (auto-coerced from string)
env.DEBUGGING; // boolean
env.NODE_ENV; // 'development' | 'production' | 'test'
```

ArkEnv auto-coerces environment strings to the target type. If validation fails, the app exits with a clear error:

```text
ArkEnvError: Errors found while validating environment variables
  HOST must be a string or "localhost" (was missing)
  PORT must be a number (was a string)
```

### Arrays

Comma-separated values are parsed automatically:

```ts
import arkenv from 'arkenv';
import { type } from 'arkenv/arktype';

const env = arkenv({
  ALLOWED_ORIGINS: type('string[]').default(() => ['localhost']),
  FEATURE_FLAGS: type('string[]').default(() => []),
});
```

```text
ALLOWED_ORIGINS=http://localhost:3000,https://example.com
```

### Lazy Validation with Proxy

Defer validation until the first property access. This allows `.env` files or test setup to load before validation runs:

```ts
import arkenv from 'arkenv';
import { type } from 'arkenv/arktype';

export const Env = type({
  DATABASE_URL: 'string > 0',
  BETTER_AUTH_SECRET: 'string >= 32',
  BETTER_AUTH_URL: 'string.url',
  PASSWORD_MIN_LENGTH: '6 <= number.integer <= 128 = 8',
  TRUSTED_ORIGINS: 'string > 0',
  'OTEL_EXPORTER_OTLP_ENDPOINT?': 'string.url',
  VITE_APP_TITLE: "string > 0 = 'My App'",
});

type ValidatedEnv = typeof Env.infer;

let _env: ValidatedEnv | undefined;

function getEnv(): ValidatedEnv {
  if (!_env) {
    if (process.env.SKIP_ENV_VALIDATION === 'true') {
      return process.env as unknown as ValidatedEnv;
    }
    _env = arkenv(Env, {
      env: process.env,
      coerce: true,
      onUndeclaredKey: 'delete',
    });
  }
  return _env;
}

export const env = new Proxy({} as ValidatedEnv, {
  get(_, prop: string) {
    return getEnv()[prop as keyof ValidatedEnv];
  },
});
```

`SKIP_ENV_VALIDATION` bypasses validation for CI builds or test environments that don't set all variables.

### Vite Plugin

The `@arkenv/vite-plugin` validates env vars at build time and auto-filters `VITE_*` prefixed variables for the client bundle:

```bash
pnpm add @arkenv/vite-plugin
```

Define the schema in a shared config file so both vite.config and type augmentation can import it:

```ts
// src/configs/env.ts
import { type } from 'arkenv/arktype';

export const Env = type({
  PORT: 'number.port',
  VITE_API_URL: 'string',
  VITE_FEATURE_FLAGS: 'boolean = false',
});
```

Use `@dotenvx/dotenvx` to load `.env` files before the plugin validates. The `flow` convention loads files in dotenv-flow order (`.env.local`, `.env`):

```ts
// vite.config.ts
import arkenvVitePlugin from '@arkenv/vite-plugin';
import { config } from '@dotenvx/dotenvx';
import tailwindcss from '@tailwindcss/vite';
import { tanstackStart } from '@tanstack/react-start/plugin/vite';
import viteReact from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import viteTsConfigPaths from 'vite-tsconfig-paths';

import { Env } from './src/configs/env';

config({ convention: 'flow', quiet: true });

export default defineConfig({
  plugins: [
    viteTsConfigPaths({ projects: ['./tsconfig.json'] }),
    arkenvVitePlugin(Env),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
  server: { port: 3000 },
});
```

The plugin auto-filters to only expose `VITE_*` prefixed variables to the client bundle — server-only variables like `DATABASE_URL` are excluded.

Type-safe `import.meta.env` in client code via `vite-env.d.ts`:

```ts
/// <reference types="vite/client" />

import type { ImportMetaEnvAugmented as ArkenvImportMetaEnvAugmented } from '@arkenv/vite-plugin';

import type { Env } from '@/configs/env';

type ImportMetaEnvAugmented = ArkenvImportMetaEnvAugmented<typeof Env>;

interface ViteTypeOptions {
  strictImportMetaEnv: unknown;
}

interface ImportMetaEnv extends ImportMetaEnvAugmented {}
```

```tsx
const apiUrl = import.meta.env.VITE_API_URL; // string — validated at build
// import.meta.env.PORT — TypeScript error, server-only
```

### Standard Schema Validators

ArkEnv also works with Zod, Valibot, or any Standard Schema validator:

```ts
import arkenv from 'arkenv';
import { z } from 'zod';

const env = arkenv({
  PORT: z.coerce.number().int().min(0).max(65535),
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development'),
});
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
