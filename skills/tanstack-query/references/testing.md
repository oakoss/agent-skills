---
title: Testing Patterns
description: Test setup with isolated QueryClient, renderHook patterns, mocking queries, testing mutations, and loading states
tags: [testing, renderHook, QueryClient, mock, vitest, waitFor, test-isolation]
---

# Testing Patterns

## Test Setup

Create a fresh QueryClient for each test to ensure complete isolation:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { renderHook, waitFor } from '@testing-library/react';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
}

function createWrapper() {
  const queryClient = createTestQueryClient();
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}
```

Retries cause test timeouts -- always set `retry: false`.

## Network Mocking with MSW

Use [Mock Service Worker](https://mswjs.io/) as the single source of truth for API mocking:

```tsx
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const handlers = [
  http.get('/api/todos', () => {
    return HttpResponse.json([
      { id: '1', name: 'Learn TanStack Query' },
      { id: '2', name: 'Write tests' },
    ]);
  }),

  http.post('/api/todos', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: '3', ...body }, { status: 201 });
  }),
];

const server = setupServer(...handlers);

// In test setup
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

Benefits: works in Node.js tests, browser, and Cypress. Single source of truth for mocks. Intercepts actual network requests (not fetch mocks).

## Testing Queries

```tsx
test('fetches todos successfully', async () => {
  const { result } = renderHook(() => useTodosQuery(), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));

  expect(result.current.data).toHaveLength(2);
  expect(result.current.data?.[0].name).toBe('Learn TanStack Query');
});
```

## Testing Components

```tsx
test('renders todos', async () => {
  const queryClient = createTestQueryClient();

  render(
    <QueryClientProvider client={queryClient}>
      <TodoList />
    </QueryClientProvider>,
  );

  await waitFor(() => {
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  expect(screen.getByText('Learn TanStack Query')).toBeInTheDocument();
});
```

## Testing Mutations

```tsx
test('creates todo successfully', async () => {
  const { result } = renderHook(() => useCreateTodoMutation(), {
    wrapper: createWrapper(),
  });

  act(() => {
    result.current.mutate({ name: 'New todo' });
  });

  await waitFor(() => expect(result.current.isSuccess).toBe(true));
  expect(result.current.data?.name).toBe('New todo');
});
```

## Testing Error States

Override handlers for specific tests:

```tsx
test('handles error state', async () => {
  server.use(
    http.get('/api/todos', () => {
      return HttpResponse.json({ message: 'Server error' }, { status: 500 });
    }),
  );

  const { result } = renderHook(() => useTodosQuery(), {
    wrapper: createWrapper(),
  });

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(result.current.error?.message).toContain('500');
});
```

## Testing with Suspense

```tsx
test('renders with suspense', async () => {
  const queryClient = createTestQueryClient();

  render(
    <QueryClientProvider client={queryClient}>
      <Suspense fallback={<div>Loading...</div>}>
        <SuspenseTodoList />
      </Suspense>
    </QueryClientProvider>,
  );

  expect(screen.getByText('Loading...')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('Learn TanStack Query')).toBeInTheDocument();
  });
});
```

## Pre-Populating Cache for Tests

Seed the cache to skip network requests:

```tsx
test('renders with pre-populated cache', async () => {
  const queryClient = createTestQueryClient();

  queryClient.setQueryData(
    ['todos'],
    [{ id: '1', name: 'Pre-populated todo' }],
  );

  render(
    <QueryClientProvider client={queryClient}>
      <TodoList />
    </QueryClientProvider>,
  );

  expect(screen.getByText('Pre-populated todo')).toBeInTheDocument();
});
```

## Common Testing Mistakes

| Mistake                          | Why It's Wrong                    | Correct Approach                   |
| -------------------------------- | --------------------------------- | ---------------------------------- |
| Shared QueryClient between tests | State leaks between tests         | Create fresh client per test       |
| Not disabling retries            | Tests timeout waiting for retries | Set `retry: false`                 |
| Immediate assertions             | Query hasn't completed            | Use `waitFor` for async            |
| Mocking fetch directly           | Brittle, misses network layer     | Use MSW                            |
| Testing without provider         | Hook throws error                 | Always wrap in QueryClientProvider |
