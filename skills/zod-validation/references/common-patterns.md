---
title: Common Patterns
description: Practical Zod patterns for form validation, API responses, environment variables, schema composition, error formatting, and branded types
tags:
  [
    form,
    login,
    API,
    response,
    environment,
    env,
    composition,
    extend,
    merge,
    partial,
    error,
    formatting,
    branded,
    ZodError,
  ]
---

# Common Patterns

## Form Validation

```ts
const LoginSchema = z.object({
  email: z.email(),
  password: z.string().min(8),
  rememberMe: z.boolean().default(false),
});

const RegisterSchema = z
  .object({
    name: z.string().min(1).max(100),
    email: z.email(),
    password: z.string().min(8).max(100),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords must match',
    path: ['confirmPassword'],
  });
```

## API Response

```ts
const ApiResponse = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    data: dataSchema,
    error: z.string().nullable(),
    status: z.enum(['success', 'error']),
  });

const UserResponse = ApiResponse(
  z.object({
    id: z.string(),
    email: z.email(),
    name: z.string(),
  }),
);
```

## Environment Variables

```ts
const EnvSchema = z.object({
  DATABASE_URL: z.url(),
  PORT: z.coerce.number().default(3000),
  DEBUG: z.stringbool().default(false),
  NODE_ENV: z.enum(['development', 'production', 'test']),
  SESSION_SECRET: z.string().min(32),
  API_KEY: z.string().optional(),
});

const env = EnvSchema.parse(process.env);
```

## Schema Composition

```ts
// Base schema shared across operations
const baseUserSchema = z.object({
  name: z.string().min(1),
  email: z.email(),
});

// Extend for creation (adds required fields)
const createUserSchema = baseUserSchema.extend({
  password: z.string().min(8),
});

// Partial for updates (all fields optional)
const updateUserSchema = baseUserSchema.partial();

// Pick specific fields
const userEmailSchema = baseUserSchema.pick({ email: true });

// Merge two schemas
const fullProfileSchema = baseUserSchema.merge(
  z.object({
    bio: z.string().max(500).optional(),
    avatar: z.url().optional(),
  }),
);
```

## Error Formatting

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

## Branded Types

```ts
const UserId = z.string().uuid().brand<'UserId'>();
const PostId = z.string().uuid().brand<'PostId'>();

type UserId = z.infer<typeof UserId>;
type PostId = z.infer<typeof PostId>;

function getUser(id: UserId) {
  // Only accepts branded UserId, not plain string or PostId
}

const userId = UserId.parse('550e8400-e29b-41d4-a716-446655440000');
getUser(userId); // OK
```

## Recursive Schemas

```ts
type Category = {
  name: string;
  children: Category[];
};

const CategorySchema: z.ZodType<Category> = z.object({
  name: z.string(),
  children: z.lazy(() => z.array(CategorySchema)),
});
```
