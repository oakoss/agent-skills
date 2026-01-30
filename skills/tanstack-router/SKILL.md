---
name: tanstack-router
description: 'Type-safe, file-based React routing with route loaders, search params validation, code splitting, preloading, navigation, route context, and TanStack Query integration. Use when setting up file-based routing, adding search params validation, implementing route loaders, code splitting routes, or fixing type registration errors.'
---

# TanStack Router

Type-safe, file-based routing for React with route-level data loading, search params validation, code splitting, and TanStack Query integration.

**Package:** `@tanstack/react-router@1.146.2` | **Plugin:** `@tanstack/router-plugin`

## Quick Reference

| Pattern                           | Usage                           |
| --------------------------------- | ------------------------------- |
| `createFileRoute('/path')`        | Define file-based route         |
| `createRootRouteWithContext<T>()` | Root route with typed context   |
| `createLazyFileRoute('/path')`    | Code-split route component      |
| `zodValidator(schema)`            | Search params validation        |
| `Route.useLoaderData()`           | Access loader data in component |
| `Route.useParams()`               | Type-safe route params          |
| `Route.useSearch()`               | Type-safe search params         |
| `useNavigate()`                   | Programmatic navigation         |
| `useBlocker()`                    | Block navigation (dirty forms)  |
| `notFound()`                      | Throw 404 from loader           |

## Data Loading

| Method            | Returns | Throws | Use Case                    |
| ----------------- | ------- | ------ | --------------------------- |
| `ensureQueryData` | Data    | Yes    | Route loaders (recommended) |
| `prefetchQuery`   | void    | No     | Background prefetching      |
| `fetchQuery`      | Data    | Yes    | Immediate data need         |
| `defer()`         | Promise | No     | Stream non-critical data    |

## Preloading

| Strategy     | Behavior                  | Use Case                    |
| ------------ | ------------------------- | --------------------------- |
| `'intent'`   | Preload on hover/focus    | Default for most links      |
| `'render'`   | Preload when Link mounts  | Critical next pages         |
| `'viewport'` | Preload when Link in view | Below-fold content          |
| `false`      | No preloading             | Heavy, rarely-visited pages |

## File Organization

| File                 | Purpose                      |
| -------------------- | ---------------------------- |
| `__root.tsx`         | Root route with `<Outlet />` |
| `index.tsx`          | Index route for `/`          |
| `posts.$postId.tsx`  | Dynamic param route          |
| `_authenticated.tsx` | Pathless layout (auth guard) |
| `dashboard.lazy.tsx` | Code-split component         |

## Common Mistakes

| Mistake                           | Fix                                                 |
| --------------------------------- | --------------------------------------------------- |
| Missing router type registration  | Add `declare module` with `Register` interface      |
| `useParams()` without `from`      | Always pass `from: '/route/path'` for exact types   |
| `useNavigate()` for regular links | Use `<Link>` for `<a>` tags, a11y, preloading       |
| `prefetchQuery` in loaders        | Use `ensureQueryData` (returns data, throws errors) |
| Fetching in `useEffect`           | Use route loaders (prevents waterfalls)             |
| Sequential fetches in loader      | Use `Promise.all` for parallel requests             |
| Missing leading slash             | Always `'/about'` not `'about'`                     |
| TanStackRouterVite after react()  | Plugin MUST come before `react()` in Vite config    |

## Delegation

Use this skill for TanStack Router file-based routing, route loaders, search params, code splitting, navigation, auth guards, and route context.

## References

- [Setup](references/setup.md) — installation, Vite config, file structure, app setup, router default options
- [Type Safety](references/type-safety.md) — register router, `from` param, `strict: false`, type utilities
- [Data Loading](references/data-loading.md) — route loaders, Query integration, parallel loading, streaming, deferred data, abort signal
- [Search Params](references/search-params.md) — validation, strip/retain middleware, fine-grained subscriptions, debounce, custom serializers
- [Navigation](references/navigation.md) — Link, active styling, relative navigation, hash, route masks, blocker, scroll restoration
- [Auth and Context](references/auth-and-context.md) — beforeLoad, context inheritance, pathless layouts, dependency injection
- [Code Splitting](references/code-splitting.md) — lazy routes, virtual routes, auto splitting, preloading
- [Known Issues](references/known-issues.md) — 20 documented issues with fixes, anti-patterns
