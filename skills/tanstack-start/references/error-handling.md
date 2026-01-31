---
title: Error Handling
description: Structured error handling patterns including discriminated unions, custom error classes, setResponseStatus, notFound, centralized error handlers, and status code conventions
tags:
  [
    error,
    ApiResult,
    AppError,
    status-code,
    discriminated-union,
    error-handling,
    server-error,
    validation,
    result-type,
    try-catch,
    notFound,
    setResponseStatus,
  ]
---

# Error Handling

## Discriminated Union Pattern

```ts
type ApiResult<T> = { data: T } | { error: string; code: string };

export const updateUser = createServerFn({ method: 'POST' })
  .inputValidator(updateUserSchema)
  .handler(async ({ data }): Promise<ApiResult<User>> => {
    try {
      const user = await db.users.update({ where: { id: data.id }, data });
      return { data: user };
    } catch (error) {
      console.error('updateUser failed:', error);
      return { error: 'Update failed', code: 'INTERNAL_ERROR' };
    }
  });
```

## Custom Error Class

```ts
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public status: number = 400,
  ) {
    super(message);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404);
  }
}

export class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 'UNAUTHORIZED', 401);
  }
}
```

## Server Function with Error Handling

```ts
import { createServerFn, notFound } from '@tanstack/react-start';
import { setResponseStatus } from '@tanstack/react-start/server';

export const getPost = createServerFn()
  .inputValidator(z.object({ id: z.string() }))
  .handler(async ({ data }) => {
    const post = await db.posts.findUnique({ where: { id: data.id } });
    if (!post) throw notFound();
    return post;
  });

export const createPost = createServerFn({ method: 'POST' })
  .inputValidator(createPostSchema)
  .handler(async ({ data }) => {
    try {
      return await db.posts.create({ data });
    } catch (error) {
      if (error instanceof Prisma.PrismaClientKnownRequestError) {
        if (error.code === 'P2002') {
          setResponseStatus(409);
          throw new AppError(
            'A post with this title already exists',
            'DUPLICATE',
            409,
          );
        }
      }
      console.error('Failed to create post:', error);
      setResponseStatus(500);
      throw new AppError('Failed to create post', 'INTERNAL_ERROR', 500);
    }
  });
```

## Centralized Error Handler

```ts
function handleServerError(error: unknown): { error: string; code: string } {
  if (error instanceof AppError) {
    return { error: error.message, code: error.code };
  }

  if (error instanceof PostgresError && error.code === '23505') {
    return { error: 'Resource already exists', code: 'CONFLICT' };
  }

  console.error('Unhandled error:', error);
  return { error: 'Internal server error', code: 'INTERNAL_ERROR' };
}
```

## Client-Side Error Handling

```tsx
function CreatePostForm() {
  const [error, setError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: createPost,
    onError: (error) => {
      if (error instanceof AppError) {
        setError(error.message);
      } else {
        setError('An unexpected error occurred');
      }
    },
    onSuccess: (post) => {
      navigate({ to: '/posts/$postId', params: { postId: post.id } });
    },
  });

  return (
    <form onSubmit={handleSubmit}>
      {error ? <Alert variant="error">{error}</Alert> : null}
      {/* form fields */}
    </form>
  );
}
```

## Auth Errors with Redirects

```ts
export const updateProfile = createServerFn({ method: 'POST' })
  .inputValidator(updateProfileSchema)
  .handler(async ({ data }) => {
    const session = await getSessionData();

    if (!session) {
      throw redirect({
        to: '/login',
        search: { redirect: '/settings' },
      });
    }

    return await db.users.update({
      where: { id: session.userId },
      data,
    });
  });
```

## Status Code Conventions

| Scenario             | Status | Code               | Response                     |
| -------------------- | ------ | ------------------ | ---------------------------- |
| Validation failed    | 400    | `VALIDATION_ERROR` | Field-specific errors        |
| Not authenticated    | 401    | `AUTH_REQUIRED`    | Redirect to login            |
| Not authorized       | 403    | `FORBIDDEN`        | Generic forbidden message    |
| Resource not found   | 404    | `NOT_FOUND`        | Use `notFound()`             |
| Conflict (duplicate) | 409    | `CONFLICT`         | Specific conflict message    |
| Server error         | 500    | `INTERNAL_ERROR`   | Generic message, log details |

## Try-Catch vs Result Types

Two approaches to error handling in server functions:

### Try-Catch: Exceptions as Control Flow

```ts
export const deletePost = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ id: z.string() }))
  .handler(async ({ data }) => {
    const post = await db.posts.findUnique({ where: { id: data.id } });
    if (!post) {
      setResponseStatus(404);
      throw new AppError('Post not found', 'NOT_FOUND', 404);
    }
    await db.posts.delete({ where: { id: data.id } });
    return { success: true };
  });
```

### Result Types: Errors as Values

```ts
type Result<T> =
  | { ok: true; data: T }
  | { ok: false; error: string; code: string };

export const deletePost = createServerFn({ method: 'POST' })
  .inputValidator(z.object({ id: z.string() }))
  .handler(async ({ data }): Promise<Result<{ success: true }>> => {
    const post = await db.posts.findUnique({ where: { id: data.id } });
    if (!post) {
      return { ok: false, error: 'Post not found', code: 'NOT_FOUND' };
    }
    await db.posts.delete({ where: { id: data.id } });
    return { ok: true, data: { success: true } };
  });
```

### Comparison

| Aspect            | Try-Catch               | Result Types               |
| ----------------- | ----------------------- | -------------------------- |
| Type safety       | Errors are untyped      | Compiler enforces checks   |
| Forgotten checks  | Silent runtime bugs     | Type error at compile time |
| Redirect/notFound | Works naturally (throw) | Must be handled separately |
| Verbosity         | Less boilerplate        | More explicit              |
| Composition       | try-catch nesting       | Flat conditional chains    |

Use result types for business logic errors (validation, not found, forbidden). Use exceptions for truly exceptional cases (redirect, notFound, infrastructure failures).

## Anti-Patterns

- **Throwing instead of returning errors** -- Return `{ error, code }` format for predictable client handling
- **Missing error codes** -- Always include both `error` and `code` in error responses
- **Exposing raw DB errors** -- Catch and return user-friendly messages, log the real error with `console.error()`
- **Returning sensitive data in errors** -- Only return what the client needs to display
