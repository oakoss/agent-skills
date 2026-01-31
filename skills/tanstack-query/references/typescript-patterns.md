---
title: TypeScript Patterns
description: Type inference with queryFn, type narrowing without destructuring, skipToken, Zod validation, useMutationState generics, and ESLint plugin
tags:
  [
    typescript,
    inference,
    type-narrowing,
    generics,
    queryOptions,
    strict-mode,
    skipToken,
    zod,
  ]
---

# TypeScript Patterns

## Let Inference Work

Type your `queryFn` return, not the `useQuery` generics:

```tsx
async function fetchTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos');
  if (!response.ok) throw new Error('Failed to fetch');
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
const query = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
});

if (query.isSuccess) {
  query.data; // Narrowed to Todo[]
}
```

Destructuring breaks narrowing because TypeScript treats each destructured variable independently:

```tsx
const { data, isSuccess } = useQuery({...});
if (isSuccess) {
  data; // Still Todo[] | undefined -- narrowing lost
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

No need for `enabled` option. TypeScript understands the query won't run when `userId` is undefined, and the `queryFn` closure properly narrows `userId` to `string`.

Works with `useSuspenseQuery` too, where `enabled` is not available:

```tsx
function UserDetail({ userId }: { userId: string | undefined }) {
  const { data } = useSuspenseQuery({
    queryKey: ['user', userId],
    queryFn: userId ? () => fetchUser(userId) : skipToken,
  });
}
```

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
  if (!response.ok) throw new Error('Failed to fetch');
  const data = await response.json();
  return todosSchema.parse(data);
}
```

Parse errors become query failures, triggering React Query's error handling and retry logic.

## Typing select Functions

```tsx
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (todos) => todos.length,
}); // data is number | undefined
```

Reusable query options with custom selectors:

```tsx
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

Type both input variables and return type on the function:

```tsx
type CreateTodoInput = { name: string; completed?: boolean };

const createTodo = async (input: CreateTodoInput): Promise<Todo> => {
  const response = await fetch('/api/todos', {
    method: 'POST',
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error('Failed to create');
  return response.json();
};

const mutation = useMutation({
  mutationFn: createTodo,
}); // Variables typed as CreateTodoInput, data as Todo
```

## Typing useMutationState

`useMutationState` uses fuzzy key matching, so type inference is lost. Use the generic parameter:

```tsx
const pendingTodos = useMutationState<CreateTodoInput>({
  filters: { mutationKey: ['addTodo'], status: 'pending' },
  select: (mutation) => mutation.state.variables,
});
// pendingTodos is CreateTodoInput[]
```

Without the generic, `mutation.state.variables` is typed as `unknown`. This is a known limitation of fuzzy matching.

## Error Type Handling

v5 defaults error type to `Error`. Handle errors defensively since JavaScript allows throwing any value:

```tsx
if (query.error instanceof Error) {
  return <div>Error: {query.error.message}</div>;
}
```

For custom error types, use Zod for runtime validation:

```tsx
const apiErrorSchema = z.object({
  message: z.string(),
  code: z.string(),
});

function isApiError(error: unknown): error is z.infer<typeof apiErrorSchema> {
  return apiErrorSchema.safeParse(error).success;
}
```

If throwing non-Error types from `queryFn`, register a global error type:

```tsx
declare module '@tanstack/react-query' {
  interface Register {
    defaultError: AxiosError;
  }
}
```

## ESLint Plugin

`@tanstack/eslint-plugin-query` catches common mistakes at lint time:

```bash
pnpm add -D @tanstack/eslint-plugin-query
```

```ts
import pluginQuery from '@tanstack/eslint-plugin-query';

export default [...pluginQuery.configs['flat/recommended']];
```

Key rules:

| Rule                            | What It Catches                                              |
| ------------------------------- | ------------------------------------------------------------ |
| `exhaustive-deps`               | Missing variables in `queryKey` that `queryFn` depends on    |
| `stable-query-client`           | Creating `QueryClient` inside component body (no `useState`) |
| `no-rest-destructuring`         | Destructuring query result breaks type narrowing             |
| `infinite-query-property-order` | Wrong property order in infinite query options               |
| `no-unstable-deps`              | Unstable references in `queryKey` (inline objects/arrays)    |

## End-to-End Type Safety

For full-stack TypeScript, consider:

- **tRPC**: Auto-infers frontend types from backend definitions
- **Zodios**: REST API client with Zod schema validation
- **OpenAPI/Swagger**: Generate types from API specs
