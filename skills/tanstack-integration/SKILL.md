---
name: tanstack-integration
description: |
  Strategic adoption of TanStack libraries (Query, Router, Start, Table, Form, Virtual). Patterns for Router+Query integration, SSR hydration, caching coordination, loader data flow.

  Use when integrating multiple TanStack libraries, setting up Router+Query SSR, fixing dual caching issues, or choosing which TanStack library to adopt.
---

# TanStack Integration

## Overview

Strategic patterns for combining TanStack libraries in production applications. Covers Router+Query integration with single-source caching, SSR hydration via `setupRouterSsrQueryIntegration`, loader-to-component data flow, and Form+Query coordination. Start vanilla, then strategically adopt TanStack where it provides clear benefits.

**When to use:** Integrating multiple TanStack libraries, setting up SSR with Router+Query, resolving dual caching, or planning TanStack adoption.

**When NOT to use:** Simple client-only apps with one TanStack library, or projects not using TanStack Router.

## Quick Reference

| Library     | Use When                                                    | Skip When                            |
| ----------- | ----------------------------------------------------------- | ------------------------------------ |
| **Query**   | Caching, background refetch, optimistic updates, pagination | Simple one-time fetches, static data |
| **Router**  | Type-safe routing, search params, code splitting            | Few routes, simple navigation        |
| **Start**   | Full-stack SSR with Router+Query                            | Client-only apps                     |
| **Table**   | Sorting, filtering, pagination, column management           | Static tables, < 20 rows             |
| **Form**    | Multi-step forms, dynamic fields, async validation          | Simple 3-4 field forms               |
| **Virtual** | 1000+ item lists, infinite scroll, large grids              | < 100 items, performance is fine     |

## Setup Checklist

| Step                                    | Pattern                                                    | Priority |
| --------------------------------------- | ---------------------------------------------------------- | -------- |
| Pass QueryClient through router context | `createRootRouteWithContext<{ queryClient: QueryClient }>` | CRITICAL |
| Use `setupRouterSsrQueryIntegration`    | Automatic SSR dehydrate/hydrate                            | CRITICAL |
| Set `defaultPreloadStaleTime: 0`        | Let Query manage all caching                               | CRITICAL |
| Define queries with `queryOptions`      | Reusable, type-safe query definitions                      | HIGH     |
| Use `ensureQueryData` in loaders        | Prefetch during navigation                                 | HIGH     |
| Use `useSuspenseQuery` in components    | Data guaranteed by loader                                  | HIGH     |

## Troubleshooting

| Symptom                            | Cause                                   | Fix                                                 |
| ---------------------------------- | --------------------------------------- | --------------------------------------------------- |
| Data refetches on every navigation | Router cache competing with Query       | Set `defaultPreloadStaleTime: 0`                    |
| SSR data not hydrating             | Missing SSR integration                 | Add `setupRouterSsrQueryIntegration`                |
| Stale data after mutation          | Cache not invalidated                   | Call `invalidateQueries` in `onSuccess`             |
| Loading flash on cached routes     | Using `useQuery` not `useSuspenseQuery` | Use `useSuspenseQuery` with loader prefetch         |
| Type errors in loader context      | Missing router context type             | Use `createRootRouteWithContext<RouterContext>()`   |
| SSR memory leak                    | Shared QueryClient across requests      | Create QueryClient inside `getRouter()` per request |

## Common Mistakes

| Mistake                                                     | Correct Pattern                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Installing all TanStack libraries at project start          | Build vanilla first, adopt selectively where clear benefit exists                  |
| Using a global QueryClient singleton                        | Create QueryClient per request inside `getRouter()` for SSR safety and testability |
| Leaving Router cache enabled alongside Query cache          | Set `defaultPreloadStaleTime: 0` so Query is the single caching source             |
| Fetching data in components with `useQuery` without loaders | Use `ensureQueryData` in route loaders to prevent loading waterfalls               |
| Manual `dehydrate`/`hydrate` calls for SSR                  | Use `setupRouterSsrQueryIntegration` for automatic SSR cache transfer              |

## Delegation

- **TanStack library selection and adoption strategy**: Use `Explore` agent
- **Router+Query integration setup across routes**: Use `Task` agent
- **SSR architecture and caching strategy planning**: Use `Plan` agent

## References

- [Router+Query setup and SSR integration](references/router-query-setup.md)
- [Loader data flow and parallel loading patterns](references/loader-patterns.md)
- [Form+Query integration, Zod validation, field arrays, and mutation patterns](references/form-query-integration.md)
- [Caching coordination and anti-patterns](references/caching-coordination.md)
- [Recommended libraries for React + TanStack projects](references/recommended-libraries.md)
- [Debugging guide: DevTools, profiling, memory leaks, error boundaries](references/debugging-guide.md)
