---
title: Hook Testing
description: Testing custom React hooks with renderHook, testing async hooks, TanStack Query/Form patterns, and hook lifecycle testing
tags:
  [
    renderHook,
    hooks,
    useHook,
    async-hooks,
    tanstack-query,
    tanstack-form,
    custom-hooks,
    rerender,
  ]
---

# Hook Testing

## Basic Hook Testing

Test custom hooks with `renderHook`:

```tsx
import { renderHook } from '@testing-library/react';
import { expect, test } from 'vitest';
import { useCounter } from './useCounter';

test('increments counter', () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  result.current.increment();

  expect(result.current.count).toBe(1);
});
```

`result.current` contains the return value of the hook.

## Testing Hook Updates

Use `act` when state updates are needed:

```tsx
import { renderHook, waitFor } from '@testing-library/react';

test('updates count', async () => {
  const { result } = renderHook(() => useCounter());

  result.current.increment();

  await waitFor(() => {
    expect(result.current.count).toBe(1);
  });
});
```

## Re-rendering Hooks with New Props

Update hook props between renders:

```tsx
test('updates when props change', () => {
  const { result, rerender } = renderHook(({ step }) => useCounter(step), {
    initialProps: { step: 1 },
  });

  expect(result.current.count).toBe(0);

  result.current.increment();
  expect(result.current.count).toBe(1);

  rerender({ step: 5 });

  result.current.increment();
  expect(result.current.count).toBe(6);
});
```

## Testing Async Hooks

Wait for async operations to complete:

```tsx
import { renderHook, waitFor } from '@testing-library/react';

test('fetches data', async () => {
  const { result } = renderHook(() => useFetchUser('1'));

  expect(result.current.loading).toBe(true);
  expect(result.current.data).toBeNull();

  await waitFor(() => {
    expect(result.current.loading).toBe(false);
  });

  expect(result.current.data).toEqual({ id: '1', name: 'Alice' });
});
```

## Testing Hooks with Context

Provide context to hooks:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook } from '@testing-library/react';

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

test('uses query client', async () => {
  const { result } = renderHook(() => useUserQuery('1'), {
    wrapper: createWrapper(),
  });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });

  expect(result.current.data?.name).toBe('Alice');
});
```

## Testing TanStack Query Hooks

Test hooks that use `useQuery`:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll, expect, test } from 'vitest';

const server = setupServer(
  http.get('/api/user/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches user with useQuery', async () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const { result } = renderHook(() => useUserQuery('1'), { wrapper });

  expect(result.current.isPending).toBe(true);

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });

  expect(result.current.data).toEqual({ id: '1', name: 'Alice' });
});
```

## Testing Query Refetch

Verify refetch behavior:

```tsx
test('refetches on demand', async () => {
  const { result } = renderHook(() => useUserQuery('1'), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));

  expect(result.current.data?.name).toBe('Alice');

  server.use(
    http.get('/api/user/:id', () => {
      return HttpResponse.json({ id: '1', name: 'Bob' });
    }),
  );

  await result.current.refetch();

  expect(result.current.data?.name).toBe('Bob');
});
```

## Testing Mutations

Test `useMutation` hooks:

```tsx
test('creates user with mutation', async () => {
  server.use(
    http.post('/api/users', async ({ request }) => {
      const body = await request.json();
      return HttpResponse.json({ id: '2', ...body }, { status: 201 });
    }),
  );

  const { result } = renderHook(() => useCreateUserMutation(), {
    wrapper: createWrapper(),
  });

  result.current.mutate({ name: 'Bob' });

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });

  expect(result.current.data).toEqual({ id: '2', name: 'Bob' });
});
```

## Testing Optimistic Updates

Verify optimistic UI behavior:

```tsx
test('updates optimistically', async () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  queryClient.setQueryData(['users'], [{ id: '1', name: 'Alice' }]);

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const { result } = renderHook(() => useUpdateUserMutation(), { wrapper });

  result.current.mutate({ id: '1', name: 'Bob' });

  const cachedData = queryClient.getQueryData<
    Array<{ id: string; name: string }>
  >(['users']);
  expect(cachedData?.[0]?.name).toBe('Bob');

  await waitFor(() => {
    expect(result.current.isSuccess).toBe(true);
  });
});
```

## Testing TanStack Form Hooks

Test form validation and submission:

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { useForm } from '@tanstack/react-form';

test('validates form', async () => {
  const { result } = renderHook(() =>
    useForm({
      defaultValues: { email: '', password: '' },
      onSubmit: vi.fn(),
    }),
  );

  const emailField = result.current.Field({
    name: 'email',
    validators: {
      onChange: ({ value }) =>
        value.includes('@') ? undefined : 'Invalid email',
    },
  });

  emailField.handleChange('invalid');

  await waitFor(() => {
    expect(emailField.state.meta.errors).toContain('Invalid email');
  });

  emailField.handleChange('valid@example.com');

  await waitFor(() => {
    expect(emailField.state.meta.errors).toHaveLength(0);
  });
});
```

## Testing Hook Cleanup

Verify cleanup functions run:

```tsx
test('cleans up on unmount', () => {
  const cleanup = vi.fn();

  const useTestHook = () => {
    useEffect(() => {
      return cleanup;
    }, []);
  };

  const { unmount } = renderHook(() => useTestHook());

  expect(cleanup).not.toHaveBeenCalled();

  unmount();

  expect(cleanup).toHaveBeenCalledTimes(1);
});
```

## Testing Hook Dependencies

Verify effects run on dependency changes:

```tsx
test('effect runs on dependency change', () => {
  const effect = vi.fn();

  const useTestHook = (dep: number) => {
    useEffect(() => {
      effect(dep);
    }, [dep]);
  };

  const { rerender } = renderHook(({ dep }) => useTestHook(dep), {
    initialProps: { dep: 1 },
  });

  expect(effect).toHaveBeenCalledWith(1);

  rerender({ dep: 2 });

  expect(effect).toHaveBeenCalledWith(2);
  expect(effect).toHaveBeenCalledTimes(2);
});
```

## Testing Debounced Hooks

Wait for debounced updates:

```tsx
import { renderHook, waitFor } from '@testing-library/react';
import { expect, test, vi } from 'vitest';

test('debounces value updates', async () => {
  const { result, rerender } = renderHook(
    ({ value }) => useDebouncedValue(value, 300),
    { initialProps: { value: 'initial' } },
  );

  expect(result.current).toBe('initial');

  rerender({ value: 'updated' });

  expect(result.current).toBe('initial');

  await waitFor(() => expect(result.current).toBe('updated'), {
    timeout: 500,
  });
});
```

## Testing Error Handling in Hooks

Verify error states:

```tsx
test('handles errors', async () => {
  server.use(
    http.get('/api/user/:id', () => {
      return HttpResponse.json({ message: 'Not found' }, { status: 404 });
    }),
  );

  const { result } = renderHook(() => useUserQuery('999'), {
    wrapper: createWrapper(),
  });

  await waitFor(() => {
    expect(result.current.isError).toBe(true);
  });

  expect(result.current.error?.message).toContain('404');
});
```

## Testing Suspense Hooks

Test hooks that suspend:

```tsx
import { Suspense } from 'react';
import { renderHook, waitFor } from '@testing-library/react';

test('suspends while loading', async () => {
  const { result } = renderHook(
    () => useSuspenseQuery({ queryKey: ['user', '1'], queryFn }),
    {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>
          <Suspense fallback={<div>Loading...</div>}>{children}</Suspense>
        </QueryClientProvider>
      ),
    },
  );

  await waitFor(() => {
    expect(result.current.data).toBeDefined();
  });
});
```

## Testing Multiple Hook Instances

Verify hook instances are independent:

```tsx
test('maintains separate state per instance', () => {
  const { result: result1 } = renderHook(() => useCounter());
  const { result: result2 } = renderHook(() => useCounter());

  result1.current.increment();

  expect(result1.current.count).toBe(1);
  expect(result2.current.count).toBe(0);
});
```
