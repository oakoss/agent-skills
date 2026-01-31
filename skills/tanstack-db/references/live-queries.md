---
title: Live Queries
description: Reactive queries with filtering, joins, aggregations, and cross-collection data access
tags:
  [
    live-queries,
    useLiveQuery,
    where,
    join,
    select,
    orderBy,
    groupBy,
    aggregate,
    filter,
  ]
---

# Live Queries

Live queries run reactively against collections. They automatically update when underlying data changes, powered by differential dataflow for sub-millisecond performance.

## Basic Live Query (React)

```tsx
import { useLiveQuery } from '@tanstack/react-db';
import { eq } from '@tanstack/db';

function Todos() {
  const { data: todos } = useLiveQuery((q) =>
    q
      .from({ todo: todoCollection })
      .where(({ todo }) => eq(todo.completed, false))
      .orderBy(({ todo }) => todo.createdAt, 'desc'),
  );

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>{todo.text}</li>
      ))}
    </ul>
  );
}
```

## Expression Functions

All expression functions are imported from `@tanstack/db`:

```ts
import {
  eq,
  gt,
  gte,
  lt,
  lte,
  like,
  ilike,
  inArray,
  and,
  or,
  not,
} from '@tanstack/db';

eq(user.id, 1);
gt(user.age, 18);
gte(user.age, 18);
lt(user.age, 65);
lte(user.age, 65);
like(user.name, 'John%');
ilike(user.name, 'john%');
inArray(user.id, [1, 2, 3]);
and(condition1, condition2);
or(condition1, condition2);
not(condition);
```

## Selecting Fields

Project specific fields to reduce data passed to components:

```ts
const { data: todos } = useLiveQuery((q) =>
  q
    .from({ todo: todoCollection })
    .where(({ todo }) => eq(todo.completed, false))
    .orderBy(({ todo }) => todo.created_at, 'asc')
    .select(({ todo }) => ({
      id: todo.id,
      text: todo.text,
    })),
);
```

## Combining Filters

```ts
const { data: results } = useLiveQuery((q) =>
  q
    .from({ user: userCollection })
    .where(({ user }) =>
      and(
        gte(user.age, 18),
        lt(user.age, 65),
        or(eq(user.role, 'admin'), eq(user.role, 'editor')),
      ),
    ),
);
```

## Cross-Collection Joins

Join multiple collections with type-safe conditions:

```tsx
import { useLiveQuery } from '@tanstack/react-db';
import { eq } from '@tanstack/db';

function TodosWithLists() {
  const { data: todos } = useLiveQuery((q) =>
    q
      .from({ todos: todoCollection })
      .join(
        { lists: listCollection },
        ({ todos, lists }) => eq(lists.id, todos.listId),
        'inner',
      )
      .where(({ lists }) => eq(lists.active, true))
      .select(({ todos, lists }) => ({
        id: todos.id,
        title: todos.title,
        listName: lists.name,
      })),
  );

  return (
    <ul>
      {todos.map((todo) => (
        <li key={todo.id}>
          {todo.title} ({todo.listName})
        </li>
      ))}
    </ul>
  );
}
```

## GroupBy and Aggregations

Group data and compute aggregates using `count`, `sum`, `avg`, `min`, `max`:

```ts
import { count, sum, avg, min, max } from '@tanstack/db';
import { createCollection } from '@tanstack/react-db';
import { liveQueryCollectionOptions } from '@tanstack/db';

const orderStats = createCollection(
  liveQueryCollectionOptions({
    query: (q) =>
      q
        .from({ order: ordersCollection })
        .groupBy(({ order }) => order.customerId)
        .select(({ order }) => ({
          customerId: order.customerId,
          totalOrders: count(order.id),
          totalAmount: sum(order.amount),
          avgOrderValue: avg(order.amount),
          minOrder: min(order.amount),
          maxOrder: max(order.amount),
        })),
  }),
);
```

## Filtering Aggregated Results

Use `fn.having()` to filter after aggregation:

```ts
const highValueCustomers = createLiveQueryCollection((q) =>
  q
    .from({ order: ordersCollection })
    .groupBy(({ order }) => order.customerId)
    .select(({ order }) => ({
      customerId: order.customerId,
      totalSpent: sum(order.amount),
      orderCount: count(order.id),
    }))
    .fn.having(({ $selected }) => {
      return $selected.totalSpent > 1000 && $selected.orderCount >= 3;
    }),
);
```

## Query Method Chain

The query builder follows a SQL-like fluent API:

| Method         | Purpose                     | Required |
| -------------- | --------------------------- | -------- |
| `.from()`      | Source collection(s)        | Yes      |
| `.join()`      | Join additional collections | No       |
| `.where()`     | Filter rows                 | No       |
| `.select()`    | Project specific fields     | No       |
| `.orderBy()`   | Sort results                | No       |
| `.groupBy()`   | Group for aggregation       | No       |
| `.fn.having()` | Filter aggregated results   | No       |
