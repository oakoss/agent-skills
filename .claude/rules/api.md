---
paths:
  - 'skills/hono/references/**'
  - 'skills/openapi/references/**'
  - 'skills/better-auth/references/**'
  - 'skills/*api*/references/**'
  - 'skills/**/references/*server*'
  - 'skills/**/references/*api*'
  - 'skills/**/references/*middleware*'
  - 'skills/**/references/*endpoint*'
  - 'skills/**/references/*rpc*'
---

# Server-Side API Patterns

Conventions for code examples in API and server-related skill references.

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

## Auth Guard Pattern

Always check authentication for protected operations:

```ts
async function deletePost(id: string, session: Session | null) {
  if (!session) {
    throw new Error('AUTH_REQUIRED');
  }

  const post = await db.query.posts.findFirst({
    where: eq(posts.id, id),
  });

  if (!post) {
    throw new Error('NOT_FOUND');
  }

  if (post.authorId !== session.user.id) {
    throw new Error('FORBIDDEN');
  }

  await db.delete(posts).where(eq(posts.id, id));
  return { success: true };
}
```

## Input Validation Rules

1. **Always validate** user input with Zod
2. **Server-side validation** is required (client validation is optional UX)
3. **Sanitize** strings before database operations
4. **Validate** URL parameters and search params

```ts
const schema = z.object({ id: z.uuid() });
const result = schema.safeParse(input);
if (!result.success) {
  return Response.json(
    { error: 'Validation failed', code: 'VALIDATION_ERROR' },
    { status: 400 },
  );
}
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
