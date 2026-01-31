---
title: Metadata and JSON Schema
description: Zod v4 schema metadata with .meta() and .describe(), global registry, JSON Schema conversion with z.toJSONSchema(), file validation, and Zod Mini for bundle optimization
tags:
  [
    meta,
    describe,
    globalRegistry,
    toJSONSchema,
    jsonSchema,
    file,
    zodMini,
    bundle,
    metadata,
    registry,
  ]
---

# Metadata and JSON Schema

## Schema Metadata (.meta)

Attach arbitrary metadata to any schema:

```ts
const UserSchema = z.object({
  firstName: z.string().describe('Your first name'),
  lastName: z.string().meta({ title: 'last_name' }),
  age: z.number().meta({ examples: [12, 99] }),
});
```

`.describe()` sets a human-readable description. `.meta()` accepts an arbitrary key-value object for richer annotations.

## Typed Registries (v4)

Create strongly-typed registries for associating schemas with metadata:

```ts
const myRegistry = z.registry<{ title: string; description: string }>();

const UserSchema = z.object({ name: z.string() });
myRegistry.add(UserSchema, {
  title: 'User',
  description: 'A user object',
});
```

Typed registries provide type-safe metadata association. Use them for framework integrations that need to look up schema metadata at runtime.

## Global Registry

Track schemas globally and associate metadata:

```ts
const EmailSchema = z.email();

z.globalRegistry.add(EmailSchema, {
  id: 'email_address',
  title: 'Email address',
  description: 'Provide your email',
  examples: ['naomie@example.com'],
});
```

The global registry allows tools and frameworks to look up metadata associated with schemas at runtime.

## JSON Schema Conversion (v4)

Convert Zod schemas to JSON Schema:

```ts
const UserSchema = z.object({
  firstName: z.string().describe('Your first name'),
  lastName: z.string().meta({ title: 'last_name' }),
  age: z.number().meta({ examples: [12, 99] }),
});

const jsonSchema = z.toJSONSchema(UserSchema);
```

Metadata from `.describe()` and `.meta()` is automatically included in the generated JSON Schema output.

### Practical Use: OpenAPI / API Documentation

```ts
const CreateUserBody = z.object({
  name: z.string().min(1).describe('Full name of the user'),
  email: z.email().describe('Valid email address'),
  role: z.enum(['admin', 'user']).default('user').describe('User role'),
});

// Convert for use in OpenAPI spec
const bodySchema = z.toJSONSchema(CreateUserBody);
```

## File Validation (v4)

Validate JavaScript `File` instances with size and MIME type constraints:

```ts
const ImageSchema = z
  .file()
  .max(5_000_000) // 5MB max
  .mime(['image/png', 'image/jpeg', 'image/webp']);

const DocumentSchema = z
  .file()
  .min(1) // Non-empty
  .max(10_000_000) // 10MB max
  .mime(['application/pdf']);

// File upload form schema
const UploadFormSchema = z.object({
  title: z.string().min(1),
  attachment: z.file().max(25_000_000),
  thumbnail: z
    .file()
    .max(2_000_000)
    .mime(['image/png', 'image/jpeg'])
    .optional(),
});
```

## Zod Mini

A lighter variant for smaller bundle sizes:

```ts
import * as z from 'zod/mini';

const schema = z.boolean();
schema.parse(false);
```

Zod Mini provides the same core validation API with a reduced footprint. Use it in client-side code where bundle size is critical. The full `zod` package includes additional utilities like `.toJSONSchema()`, `.prettifyError()`, and advanced features not available in the mini variant.

### When to Use Zod Mini

| Use Case                    | Package    |
| --------------------------- | ---------- |
| Client-side form validation | `zod/mini` |
| Server-side API validation  | `zod`      |
| JSON Schema generation      | `zod`      |
| Bundle-sensitive libraries  | `zod/mini` |
| Full metadata / registry    | `zod`      |
