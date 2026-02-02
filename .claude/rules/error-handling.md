---
paths:
  - 'skills/*error*/references/**'
  - 'skills/destructive-command-guard/references/**'
  - 'skills/**/references/*error*'
  - 'skills/**/references/*troubleshooting*'
  - 'skills/**/references/*boundary*'
  - 'skills/**/references/*fallback*'
---

# Error Handling Patterns

## Quick Reference

| Error Code            | HTTP Status | Use Case                       |
| --------------------- | ----------- | ------------------------------ |
| `AUTH_REQUIRED`       | 401         | User not logged in             |
| `INVALID_CREDENTIALS` | 401         | Wrong email/password           |
| `SESSION_EXPIRED`     | 401         | Session timed out              |
| `FORBIDDEN`           | 403         | Logged in but not authorized   |
| `NOT_FOUND`           | 404         | Resource doesn't exist         |
| `CONFLICT`            | 409         | Duplicate or conflicting state |
| `VALIDATION_ERROR`    | 400         | Invalid input data             |
| `INTERNAL_ERROR`      | 500         | Server-side failure            |

## Standard Error Response Format

All API errors use this structure:

```ts
type ApiError = {
  error: string; // Human-readable message for display
  code: string; // Machine-readable code for programmatic handling
};
```

## Error Codes Enum

Define error codes consistently:

```ts
// lib/errors.ts
export const ErrorCodes = {
  // Authentication
  AUTH_REQUIRED: 'AUTH_REQUIRED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  SESSION_EXPIRED: 'SESSION_EXPIRED',

  // Authorization
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_PERMISSIONS: 'INSUFFICIENT_PERMISSIONS',

  // Resources
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  ALREADY_EXISTS: 'ALREADY_EXISTS',

  // Validation
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',

  // Server
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
} as const;

export type ErrorCode = (typeof ErrorCodes)[keyof typeof ErrorCodes];
```

## Server Function Error Handling (TanStack Start)

```ts
const updateUser = createServerFn({ method: 'POST' })
  .validator(schema)
  .handler(async ({ data, request }) => {
    try {
      const session = await auth.api.getSession({ headers: request.headers });
      if (!session) {
        return { error: 'Authentication required', code: 'AUTH_REQUIRED' };
      }

      const result = await db.update(users).set(data).returning();
      return { data: result };
    } catch (error) {
      console.error('updateUser failed:', error);

      // Return generic error to client (never expose internals)
      return { error: 'Failed to update user', code: 'INTERNAL_ERROR' };
    }
  });
```

## Client Error Handling

### Handling Server Function Responses

```tsx
async function handleSubmit(formData: FormData) {
  const result = await updateUser({ data: formData });

  if ('error' in result) {
    switch (result.code) {
      case 'AUTH_REQUIRED':
        navigate({ to: '/login' });
        break;
      case 'VALIDATION_ERROR':
        setErrors(result.details);
        break;
      default:
        toast.error(result.error);
    }
    return;
  }

  toast.success('Updated successfully');
}
```

### TanStack Query Error Handling

```tsx
const mutation = useMutation({
  mutationFn: createPost,
  onError: (error) => {
    toast.error(error.message);
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['posts'] });
    toast.success('Post created');
  },
});
```

## Error Boundaries

### Route-Level Error Boundary (TanStack Router)

```tsx
export const Route = createFileRoute('/posts/$id')({
  errorComponent: ({ error, reset }) => (
    <div className="p-4">
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <Button onPress={reset}>Try again</Button>
    </div>
  ),
});
```

### Global Error Boundary

```tsx
export const getRouter = () =>
  createRouter({
    routeTree,
    defaultErrorComponent: GlobalError,
    defaultNotFoundComponent: NotFoundError,
  });
```

## Logging Conventions

### What to Log

- Server errors with stack traces (server-side only)
- Authentication failures (without sensitive data)
- Database query failures
- External API failures

### What NOT to Log

- User passwords or tokens
- Full request bodies with sensitive data
- Personal information (PII)
- Stack traces in production client code

### Logging Pattern

```ts
// Server-side logging
try {
  await riskyOperation();
} catch (error) {
  console.error('[updateUser] Operation failed:', {
    userId: session.user.id,
    operation: 'update',
    error: error instanceof Error ? error.message : 'Unknown error',
    // In development, include stack trace
    ...(process.env.NODE_ENV === 'development' && {
      stack: error instanceof Error ? error.stack : undefined,
    }),
  });

  return { error: 'Update failed', code: 'INTERNAL_ERROR' };
}
```

## Production Safety Rules

1. **Never expose stack traces** to clients in production
2. **Never log sensitive data** (passwords, tokens, PII)
3. **Use generic messages** for internal errors
4. **Log detailed errors** server-side for debugging
5. **Validate all inputs** before processing

## Toast/Notification Patterns

```tsx
// Success messages - brief and positive
toast.success('Saved');
toast.success('Post created');

// Error messages - actionable when possible
toast.error('Failed to save. Please try again.');
toast.error('Session expired. Please log in again.');

// Loading states
const toastId = toast.loading('Saving...');
toast.success('Saved', { id: toastId });
// or
toast.error('Failed', { id: toastId });
```

## Form Validation Errors

Display field-level errors from Zod:

```tsx
function FormField({ field, errors }) {
  const fieldErrors = errors?.fieldErrors?.[field.name];

  return (
    <div data-invalid={!!fieldErrors}>
      <Label>{label}</Label>
      <Input {...field} aria-invalid={!!fieldErrors} />
      {fieldErrors && (
        <span className="text-sm text-red-600">{fieldErrors[0]}</span>
      )}
    </div>
  );
}
```
