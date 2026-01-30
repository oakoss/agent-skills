---
title: Error Handling
description: Structured error handling patterns including discriminated unions, custom error classes, centralized error handlers, and status code conventions
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

## Status Code Conventions

| Scenario             | Status | Code               | Response                     |
| -------------------- | ------ | ------------------ | ---------------------------- |
| Validation failed    | 400    | `VALIDATION_ERROR` | Field-specific errors        |
| Not authenticated    | 401    | `AUTH_REQUIRED`    | Redirect to login            |
| Not authorized       | 403    | `FORBIDDEN`        | Generic forbidden message    |
| Resource not found   | 404    | `NOT_FOUND`        | Use `notFound()`             |
| Conflict (duplicate) | 409    | `CONFLICT`         | Specific conflict message    |
| Server error         | 500    | `INTERNAL_ERROR`   | Generic message, log details |

## Anti-Patterns

- **Throwing instead of returning errors** — Return `{ error, code }` format for predictable client handling
- **Missing error codes** — Always include both `error` and `code` in error responses
- **Exposing raw DB errors** — Catch and return user-friendly messages. Log the real error with `console.error()`
- **Returning sensitive data in errors** — Only return what the client needs to display
