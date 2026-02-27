---
title: Common Patterns
description: Practical Zod patterns for form validation, API responses, environment variables, schema composition, recursive types, branded types, and error formatting
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
    branded,
    recursive,
    lazy,
    getter,
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

### Paginated Response

```ts
const PaginatedResponse = <T extends z.ZodType>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number().int().nonnegative(),
    page: z.number().int().positive(),
    pageSize: z.number().int().positive(),
    hasNext: z.boolean(),
  });
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

## Recursive Types (v4 Getter Syntax)

v4 supports getter-based recursion that retains full object methods (`.pick()`, `.partial()`, `.extend()`):

```ts
// Single recursion
const Category = z.object({
  name: z.string(),
  get subcategories() {
    return z.array(Category);
  },
});

type Category = z.infer<typeof Category>;
// { name: string; subcategories: Category[] }
```

### Mutually Recursive Types

```ts
const User = z.object({
  email: z.email(),
  get posts() {
    return z.array(Post);
  },
});

const Post = z.object({
  title: z.string(),
  get author() {
    return User;
  },
});

// Full object methods still work
Post.pick({ title: true });
Post.partial();
Post.extend({ publishDate: z.date() });
```

### Legacy Recursive Types (z.lazy)

Still supported but the getter syntax is preferred in v4:

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

## Branded Types

```ts
const UserId = z.uuid().brand<'UserId'>();
const PostId = z.uuid().brand<'PostId'>();

type UserId = z.infer<typeof UserId>;
type PostId = z.infer<typeof PostId>;

function getUser(id: UserId) {
  // Only accepts branded UserId, not plain string or PostId
}

const userId = UserId.parse('550e8400-e29b-41d4-a716-446655440000');
getUser(userId); // OK
```

## Intersection

```ts
const HasId = z.object({ id: z.string() });
const HasTimestamps = z.object({
  createdAt: z.date(),
  updatedAt: z.date(),
});

// Combine schemas with intersection
const Entity = z.intersection(HasId, HasTimestamps);
// Shorthand
const Entity2 = HasId.and(HasTimestamps);
```

## Preprocess

Transform input before schema validation:

```ts
const CommaSeparated = z.preprocess(
  (val) => (typeof val === 'string' ? val.split(',') : val),
  z.array(z.string()),
);

CommaSeparated.parse('a,b,c'); // ["a", "b", "c"]
```
