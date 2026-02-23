---
title: Error Handling
description: TRPCError codes, error formatting, Zod error integration, custom error shapes, and onError callbacks
tags:
  [TRPCError, error-formatter, onError, error-codes, zod-errors, HTTP-status]
---

# Error Handling

## TRPCError

All tRPC errors extend `TRPCError` with a required `code`:

```ts
import { TRPCError } from '@trpc/server';

throw new TRPCError({
  code: 'NOT_FOUND',
  message: 'User not found',
  cause: originalError,
});
```

## Error Codes

| Code                    | HTTP Status | Usage                             |
| ----------------------- | ----------- | --------------------------------- |
| `BAD_REQUEST`           | 400         | Invalid input or parameters       |
| `UNAUTHORIZED`          | 401         | Missing or invalid authentication |
| `FORBIDDEN`             | 403         | Authenticated but not authorized  |
| `NOT_FOUND`             | 404         | Resource does not exist           |
| `METHOD_NOT_SUPPORTED`  | 405         | Wrong procedure type              |
| `TIMEOUT`               | 408         | Operation timed out               |
| `CONFLICT`              | 409         | Resource conflict                 |
| `PRECONDITION_FAILED`   | 412         | Precondition not met              |
| `PAYLOAD_TOO_LARGE`     | 413         | Request body too large            |
| `UNPROCESSABLE_CONTENT` | 422         | Semantic validation failure       |
| `TOO_MANY_REQUESTS`     | 429         | Rate limit exceeded               |
| `CLIENT_CLOSED_REQUEST` | 499         | Client disconnected               |
| `INTERNAL_SERVER_ERROR` | 500         | Unexpected server error           |

## Error Formatter

Customize the error shape returned to clients:

```ts
import { initTRPC } from '@trpc/server';
import { ZodError } from 'zod';

const t = initTRPC.context<Context>().create({
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.code === 'BAD_REQUEST' && error.cause instanceof ZodError
            ? error.cause.flatten()
            : null,
      },
    };
  },
});
```

Client receives structured Zod errors for validation failures:

```ts
const mutation = trpc.userCreate.useMutation();

if (mutation.error?.data?.zodError) {
  const fieldErrors = mutation.error.data.zodError.fieldErrors;
}
```

## onError Callback

Handle errors at the adapter level for logging and monitoring:

```ts
import { createHTTPServer } from '@trpc/server/adapters/standalone';

createHTTPServer({
  router: appRouter,
  onError({ error, path, type, ctx, input }) {
    console.error(`tRPC error on ${type} ${path}:`, error.message);

    if (error.code === 'INTERNAL_SERVER_ERROR') {
      sentry.captureException(error);
    }
  },
});
```

## Error Handling in Procedures

Let errors propagate naturally; avoid try/catch unless transforming errors:

```ts
const getUser = publicProcedure.input(z.string()).query(async ({ input }) => {
  const user = await db.user.findById(input);
  if (!user) {
    throw new TRPCError({
      code: 'NOT_FOUND',
      message: `User ${input} not found`,
    });
  }
  return user;
});
```

## Wrapping External Errors

Convert third-party errors into TRPCError:

```ts
const chargeUser = protectedProcedure
  .input(z.object({ amount: z.number().positive() }))
  .mutation(async ({ input, ctx }) => {
    try {
      return await stripe.charges.create({
        amount: input.amount,
        customer: ctx.user.stripeId,
      });
    } catch (err) {
      throw new TRPCError({
        code: 'INTERNAL_SERVER_ERROR',
        message: 'Payment failed',
        cause: err,
      });
    }
  });
```

## HTTP Status Code Extraction

Convert TRPCError codes to HTTP status codes for non-tRPC consumers:

```ts
import { TRPCError } from '@trpc/server';
import { getHTTPStatusCodeFromError } from '@trpc/server/http';

try {
  const result = await caller.user.byId('nonexistent');
} catch (cause) {
  if (cause instanceof TRPCError) {
    const httpCode = getHTTPStatusCodeFromError(cause);
    res.status(httpCode).json({ error: cause.message });
  }
}
```
