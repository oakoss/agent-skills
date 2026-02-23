---
title: React Integration
description: PGliteProvider, usePGlite, useLiveQuery, useLiveIncrementalQuery, and makePGliteProvider for typed hooks
tags:
  [
    react,
    hooks,
    PGliteProvider,
    usePGlite,
    useLiveQuery,
    useLiveIncrementalQuery,
    makePGliteProvider,
  ]
---

# React Integration

## Installation

```bash
npm install @electric-sql/pglite @electric-sql/pglite-react
```

## PGliteProvider

Wrap the application with `PGliteProvider` to make the PGlite instance available to all hooks.

```tsx
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';
import { PGliteProvider } from '@electric-sql/pglite-react';

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: { live },
});

function App() {
  return (
    <PGliteProvider db={db}>
      <TodoList />
    </PGliteProvider>
  );
}
```

The live extension is required for `useLiveQuery` and `useLiveIncrementalQuery` hooks.

## usePGlite

Access the PGlite instance directly for imperative operations.

```tsx
import { usePGlite } from '@electric-sql/pglite-react';

function AddTodo() {
  const db = usePGlite();

  async function handleSubmit(task: string) {
    await db.query('INSERT INTO todos (task) VALUES ($1)', [task]);
  }

  return <button onClick={() => handleSubmit('New task')}>Add</button>;
}
```

## useLiveQuery

Reactive hook that re-renders the component when query results change. Wraps `live.query()` internally.

```tsx
import { useLiveQuery } from '@electric-sql/pglite-react';

interface Todo {
  id: number;
  task: string;
  done: boolean;
}

function TodoList() {
  const result = useLiveQuery<Todo>(
    'SELECT * FROM todos WHERE done = $1 ORDER BY id',
    [false],
  );

  if (!result) return null;

  return (
    <ul>
      {result.rows.map((todo) => (
        <li key={todo.id}>{todo.task}</li>
      ))}
    </ul>
  );
}
```

The hook returns `undefined` on the initial render before the query resolves. Always handle the loading state.

### With Parameters

Parameters are reactive. When they change, the live query re-subscribes automatically.

```tsx
import { useLiveQuery } from '@electric-sql/pglite-react';

interface SearchResult {
  id: number;
  name: string;
}

function SearchResults({ query }: { query: string }) {
  const result = useLiveQuery<SearchResult>(
    'SELECT * FROM products WHERE name ILIKE $1 LIMIT 20',
    [`%${query}%`],
  );

  if (!result) return <p>Loading...</p>;

  return (
    <ul>
      {result.rows.map((item) => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

## useLiveIncrementalQuery

Optimized for large result sets. Computes diffs using a key column instead of re-running the full query.

```tsx
import { useLiveIncrementalQuery } from '@electric-sql/pglite-react';

interface Article {
  id: number;
  title: string;
  body: string;
}

function ArticleList() {
  const result = useLiveIncrementalQuery<Article>(
    'SELECT * FROM articles ORDER BY id',
    [],
    'id',
  );

  if (!result) return null;

  return (
    <ul>
      {result.rows.map((article) => (
        <li key={article.id}>{article.title}</li>
      ))}
    </ul>
  );
}
```

The third argument is the key column used for diffing. Must be a unique column, typically the primary key.

## makePGliteProvider: Typed Hooks

Create a typed provider and hooks for full type safety across the application.

```tsx
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';
import { makePGliteProvider } from '@electric-sql/pglite-react';

const { PGliteProvider, usePGlite, useLiveQuery, useLiveIncrementalQuery } =
  makePGliteProvider<PGlite & { live: typeof live }>();

const db = await PGlite.create({
  dataDir: 'idb://my-app',
  extensions: { live },
});

function App() {
  return (
    <PGliteProvider db={db}>
      <Content />
    </PGliteProvider>
  );
}
```

The returned hooks are typed to the specific PGlite instance type, providing autocomplete for extensions.

## Initialization Pattern

Handle async PGlite creation with a loading state.

```tsx
import { useState, useEffect } from 'react';
import { PGlite } from '@electric-sql/pglite';
import { live } from '@electric-sql/pglite/live';
import { PGliteProvider } from '@electric-sql/pglite-react';

function AppLoader() {
  const [db, setDb] = useState<PGlite | null>(null);

  useEffect(() => {
    let mounted = true;

    PGlite.create({
      dataDir: 'idb://my-app',
      extensions: { live },
    }).then((instance) => {
      if (mounted) setDb(instance);
    });

    return () => {
      mounted = false;
    };
  }, []);

  if (!db) return <p>Loading database...</p>;

  return (
    <PGliteProvider db={db}>
      <App />
    </PGliteProvider>
  );
}
```

## Mutation Pattern with Live Queries

Mutations trigger live query updates automatically. No manual invalidation is needed.

```tsx
import { usePGlite, useLiveQuery } from '@electric-sql/pglite-react';

interface Todo {
  id: number;
  task: string;
  done: boolean;
}

function TodoApp() {
  const db = usePGlite();
  const result = useLiveQuery<Todo>('SELECT * FROM todos ORDER BY id');

  async function addTodo(task: string) {
    await db.query('INSERT INTO todos (task, done) VALUES ($1, false)', [task]);
  }

  async function toggleTodo(id: number, done: boolean) {
    await db.query('UPDATE todos SET done = $1 WHERE id = $2', [!done, id]);
  }

  if (!result) return null;

  return (
    <div>
      <button onClick={() => addTodo('New task')}>Add</button>
      <ul>
        {result.rows.map((todo) => (
          <li key={todo.id} onClick={() => toggleTodo(todo.id, todo.done)}>
            {todo.done ? '(done) ' : ''}
            {todo.task}
          </li>
        ))}
      </ul>
    </div>
  );
}
```
