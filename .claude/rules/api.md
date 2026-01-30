---
paths:
  - 'skills/**/references/*server*.md'
  - 'skills/**/references/*api*.md'
  - 'skills/**/references/*middleware*.md'
---

# Server-Side API Patterns

## Server Functions

Use `createServerFn()` for type-safe server-side logic:

```ts
import { createServerFn } from '@tanstack/react-start';
import { z } from 'zod';

// GET - No input validation needed
const getUsers = createServerFn({ method: 'GET' }).handler(async () => {
  return await db.query.users.findMany();
});

// POST - Always validate with Zod
const createUser = createServerFn({ method: 'POST' })
  .validator(z.object({ name: z.string().min(1), email: z.email() }))
  .handler(async ({ data }) => {
    return await db.insert(users).values(data).returning();
  });
```

## API Route Handlers

Use `createAPIFileRoute()` for REST endpoints:

```ts
// apps/web/src/routes/api/posts.ts
import { createAPIFileRoute } from '@tanstack/react-start/api';

export const Route = createAPIFileRoute('/api/posts')({
  GET: async () => {
    const posts = await db.query.posts.findMany();
    return Response.json(posts);
  },

  POST: async ({ request }) => {
    const body = await request.json();
    const result = schema.safeParse(body);
    if (!result.success) {
      return Response.json(
        { error: 'Validation failed', code: 'VALIDATION_ERROR' },
        { status: 400 },
      );
    }
    const [post] = await db.insert(posts).values(result.data).returning();
    return Response.json(post, { status: 201 });
  },
});
```

## Standard Error Response

Always return errors in this format:

```ts
type ApiError = {
  error: string; // Human-readable message
  code: string; // Machine-readable code
};

// Response.json({ error: 'Not found', code: 'NOT_FOUND' }, { status: 404 })
```

## Error Codes

| Code               | Status | Description                         |
| ------------------ | ------ | ----------------------------------- |
| `AUTH_REQUIRED`    | 401    | User must be authenticated          |
| `FORBIDDEN`        | 403    | User lacks permission               |
| `NOT_FOUND`        | 404    | Resource doesn't exist              |
| `VALIDATION_ERROR` | 400    | Invalid input data                  |
| `CONFLICT`         | 409    | Resource already exists             |
| `INTERNAL_ERROR`   | 500    | Server error (don't expose details) |

## Auth in Server Functions

Always check authentication for protected operations:

```ts
import { auth } from '@oakoss/auth/server';

const deletePost = createServerFn({ method: 'POST' })
  .validator(z.object({ id: z.string() }))
  .handler(async ({ data, request }) => {
    // Get session from request headers
    const session = await auth.api.getSession({ headers: request.headers });

    if (!session) {
      throw new Error('AUTH_REQUIRED');
    }

    // Check ownership
    const post = await db.query.posts.findFirst({
      where: eq(posts.id, data.id),
    });

    if (!post) {
      throw new Error('NOT_FOUND');
    }

    if (post.authorId !== session.user.id) {
      throw new Error('FORBIDDEN');
    }

    await db.delete(posts).where(eq(posts.id, data.id));
    return { success: true };
  });
```

## Input Validation Rules

1. **Always validate** user input with Zod
2. **Server-side validation** is required (client validation is optional UX)
3. **Sanitize** strings before database operations
4. **Validate** URL parameters and search params

```ts
// Route params validation
const getPost = createServerFn({ method: 'GET' })
  .validator(z.object({ id: z.uuid() })) // Validate UUID format
  .handler(async ({ data }) => {
    return await db.query.posts.findFirst({
      where: eq(posts.id, data.id),
    });
  });
```

## Response Patterns

```ts
// Success with data
return Response.json(data);
return Response.json(data, { status: 201 }); // Created

// Success with no content
return new Response(null, { status: 204 });

// Error responses
return Response.json(
  { error: 'Not found', code: 'NOT_FOUND' },
  { status: 404 },
);
return Response.json(
  { error: 'Unauthorized', code: 'AUTH_REQUIRED' },
  { status: 401 },
);

// Validation error with details
return Response.json(
  {
    error: 'Validation failed',
    code: 'VALIDATION_ERROR',
    details: result.error.flatten(),
  },
  { status: 400 },
);
```

## File Structure (Planned)

```sh
apps/web/src/routes/
├── api/
│   ├── posts.ts           # /api/posts (GET, POST)
│   ├── posts/$id.ts       # /api/posts/:id (GET, PUT, DELETE)
│   └── auth/$.ts          # /api/auth/* (Better Auth handler)
```

Note: The `api/` directory will be created when implementing API routes.
