---
title: Search Params
description: Search params validation with Zod, stripSearchParams and retainSearchParams middleware, fine-grained subscriptions with select, debounced URL sync, and custom serializers
tags:
  [
    search-params,
    validateSearch,
    zod-validator,
    middleware,
    stripSearchParams,
    retainSearchParams,
    serializer,
  ]
---

# Search Params

## Validation with Zod

Always validate search params — they are user-controlled input:

```ts
import { zodValidator, fallback } from '@tanstack/zod-adapter';
import { z } from 'zod';

const searchSchema = z.object({
  query: z.string().min(1).max(100),
  page: fallback(z.number().int().positive(), 1),
  sortBy: z.enum(['name', 'date', 'relevance']).optional(),
});

export const Route = createFileRoute('/search')({
  validateSearch: zodValidator(searchSchema),
});
```

Use `.catch()` to silently fix malformed params. Use `.default()` + `errorComponent` to show validation errors.

## Validation with Valibot

Valibot is a lighter alternative to Zod with the same adapter pattern:

```ts
import { valibotValidator, fallback } from '@tanstack/valibot-adapter';
import * as v from 'valibot';

const searchSchema = v.object({
  page: fallback(v.pipe(v.number(), v.integer(), v.minValue(1)), 1),
  sort: v.optional(v.picklist(['name', 'date'])),
});

export const Route = createFileRoute('/search')({
  validateSearch: valibotValidator(searchSchema),
});
```

Install: `npm install @tanstack/valibot-adapter valibot`

## Updating Search Params

```ts
const navigate = useNavigate();
navigate({
  to: '.',
  search: (prev) => ({ ...prev, sort: 'price', page: 1 }),
});
```

## stripSearchParams Middleware

Remove default values from URLs for cleaner links:

```ts
import { stripSearchParams } from '@tanstack/react-router';

const defaults = { page: 1, sort: 'newest' as const };

export const Route = createFileRoute('/posts')({
  validateSearch: zodValidator(searchSchema),
  search: { middlewares: [stripSearchParams(defaults)] },
});
```

| Input                                 | Behavior                                      |
| ------------------------------------- | --------------------------------------------- |
| `stripSearchParams(defaultsObj)`      | Strip params matching defaults                |
| `stripSearchParams(['key1', 'key2'])` | Strip specific keys                           |
| `stripSearchParams(true)`             | Strip all params (only if no required params) |

## retainSearchParams Middleware

Preserve specific search params across navigations:

```ts
import { retainSearchParams } from '@tanstack/react-router';

export const Route = createRootRoute({
  validateSearch: zodValidator(globalSchema),
  search: { middlewares: [retainSearchParams(['debug', 'theme'])] },
});
```

## Custom Search Middleware

Transform search params before URL serialization:

```ts
export const Route = createFileRoute('/posts')({
  validateSearch: searchSchema,
  search: {
    middlewares: [
      ({ search, next }) => {
        const cleaned = Object.fromEntries(
          Object.entries(search).filter(([_, v]) => v !== undefined),
        );
        return next(cleaned);
      },
    ],
  },
});
```

## Fine-Grained Subscriptions

Use `select` to subscribe to specific search values and prevent unnecessary re-renders:

```ts
function PostsPage() {
  const page = Route.useSearch({ select: (s) => s.page });
  const isFiltered = Route.useSearch({ select: (s) => Boolean(s.filter) });
}
```

Search params use structural sharing — when only `filter` changes, components subscribed only to `page` won't re-render.

## Debounced URL Sync

```ts
function FiltersComponent() {
  const search = Route.useSearch();
  const navigate = useNavigate();
  const [localFilter, setLocalFilter] = useState(search.filter ?? '');

  useEffect(() => {
    const timeout = setTimeout(() => {
      navigate({
        search: (prev) => ({ ...prev, filter: localFilter || undefined }),
        replace: true,
      });
    }, 300);
    return () => clearTimeout(timeout);
  }, [localFilter]);

  return (
    <input
      value={localFilter}
      onChange={(e) => setLocalFilter(e.target.value)}
    />
  );
}
```

## Custom Serializers

Configure once on router for cleaner URLs:

```ts
import JSURL from 'jsurl2';

const router = createRouter({
  routeTree,
  search: {
    serialize: (search) => JSURL.stringify(search),
    parse: (searchString) => JSURL.parse(searchString) || {},
  },
});
```
