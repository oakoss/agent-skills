---
title: TypeScript Patterns
description: Type inference with queryFn, type narrowing without destructuring, generic constraints, and typing query options
tags:
  [typescript, inference, type-narrowing, generics, queryOptions, strict-mode]
---

# TypeScript Patterns

## Let Inference Work

Type your `queryFn` return, not the `useQuery` generics:

```tsx
// BAD: Manual generics
const { data } = useQuery<Todo[], Error>({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

// GOOD: Let inference work
async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos');
  return response.json();
}

const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
}); // data is inferred as Todo[] | undefined
```

TypeScript lacks partial type argument inference. Specifying one generic forces you to specify all four (`TQueryFnData`, `TError`, `TData`, `TQueryKey`).

## Type Narrowing Without Destructuring

```tsx
// BAD: Destructuring breaks narrowing
const { data, isSuccess } = useQuery({...});
if (isSuccess) {
  data; // Still Todo[] | undefined
}

// GOOD: Keep object intact
const query = useQuery({...});
if (query.isSuccess) {
  query.data; // Narrowed to Todo[]
}
```

## skipToken for Type-Safe Disabling

Use `skipToken` instead of `enabled: false` for better type safety:

```tsx
import { skipToken, useQuery } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string | undefined }) {
  const { data } = useQuery({
    queryKey: ['user', userId],
    queryFn: userId ? () => fetchUser(userId) : skipToken,
  });
}
```

No need for `enabled` option. TypeScript understands the query won't run when `userId` is undefined.

## Runtime Validation with Zod

TypeScript types don't exist at runtime. Validate API responses:

```tsx
import { z } from 'zod';

const todoSchema = z.object({
  id: z.string(),
  name: z.string(),
  completed: z.boolean(),
});

const todosSchema = z.array(todoSchema);
type Todo = z.infer<typeof todoSchema>;

async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos');
  const data = await response.json();
  return todosSchema.parse(data); // Throws on invalid data
}
```

Parse errors become query failures, triggering React Query's error handling.

## Typing select Functions

```tsx
// Inference works automatically
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos, // Returns Todo[]
  select: (todos) => todos.length, // data is number | undefined
});

// Reusable query options with custom selectors
function todoOptions<TData = Todo[]>(select?: (data: Todo[]) => TData) {
  return queryOptions({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    select,
  });
}

useQuery(todoOptions()); // data: Todo[] | undefined
useQuery(todoOptions((todos) => todos.length)); // data: number | undefined
```

## Typing Mutations

Type both input variables and return type:

```tsx
type CreateTodoInput = { name: string; completed?: boolean };

const createTodo = async (input: CreateTodoInput): Promise<Todo> => {
  const response = await fetch('/api/todos', {
    method: 'POST',
    body: JSON.stringify(input),
  });
  return response.json();
};

const mutation = useMutation({
  mutationFn: createTodo,
}); // Variables typed as CreateTodoInput, data as Todo
```

## Error Type Handling

Handle errors defensively since JavaScript allows throwing any value:

```tsx
if (query.error instanceof Error) {
  return <div>Error: {query.error.message}</div>;
}

// Or use custom error type with Zod
const apiErrorSchema = z.object({
  message: z.string(),
  code: z.string(),
});

function isApiError(error: unknown): error is z.infer<typeof apiErrorSchema> {
  return apiErrorSchema.safeParse(error).success;
}
```

## End-to-End Type Safety

For full-stack TypeScript, consider:

- **tRPC**: Auto-infers frontend types from backend definitions
- **Zodios**: REST API client with Zod schema validation
- **OpenAPI/Swagger**: Generate types from API specs
