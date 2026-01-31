---
name: tanstack-integration
description: |
  Strategic adoption of TanStack libraries (Query, Router, Start, Table, Form, Virtual). Patterns for Router+Query integration, SSR hydration, caching coordination, loader data flow, server functions, and error handling.

  Use when integrating multiple TanStack libraries, setting up Router+Query SSR, fixing dual caching issues, coordinating form submissions with cache invalidation, or choosing which TanStack library to adopt.
license: MIT
metadata:
  author: oakoss
  version: '1.1'
  source: 'https://tanstack.com'
---

# TanStack Integration

## Overview

Strategic patterns for combining TanStack libraries in production applications. Covers Router+Query integration with single-source caching, SSR hydration via `setupRouterSsrQueryIntegration`, loader-to-component data flow, Form+Query+Server Function coordination, structured error handling, and paginated table patterns with URL state. Start vanilla, then strategically adopt TanStack where it provides clear benefits.

**When to use:** Integrating multiple TanStack libraries, setting up SSR with Router+Query, resolving dual caching, coordinating forms with mutations and cache, or planning TanStack adoption.

**When NOT to use:** Simple client-only apps with one TanStack library, or projects not using TanStack Router.

## Adoption Methodology

Build the feature with vanilla React first. Only reach for a TanStack library when you hit a specific pain point it solves (caching, type-safe routes, complex forms). Avoid the "man with a hammer" anti-pattern where every problem looks like it needs a TanStack solution.

## Quick Reference

| Library     | Use When                                                     | Skip When                            |
| ----------- | ------------------------------------------------------------ | ------------------------------------ |
| **Query**   | Caching, background refetch, optimistic updates, pagination  | Simple one-time fetches, static data |
| **Router**  | Type-safe routing, search params, code splitting             | Few routes, simple navigation        |
| **Start**   | Full-stack SSR with Router+Query, server functions           | Client-only apps                     |
| **Table**   | Sorting, filtering, pagination, column management            | Static tables, < 20 rows             |
| **Form**    | Multi-step forms, dynamic fields, async validation           | Simple 3-4 field forms               |
| **Virtual** | 1000+ item lists, infinite scroll, large grids               | < 100 items, performance is fine     |
| **DB**      | Reactive local-first data, cross-collection joins, sync      | Simple fetch-and-display             |
| **Store**   | Shared reactive state, derived computations, cross-framework | Component-local state (useState)     |
| **Pacer**   | Debounce, throttle, rate limit, async queuing                | Simple setTimeout/setInterval        |

## Configuration Scope

| Scope                     | Where                           | Example                                        |
| ------------------------- | ------------------------------- | ---------------------------------------------- |
| All packages in monorepo  | Shared package `queryClient.ts` | Default `staleTime`, `gcTime`, error handlers  |
| One package/module        | Module-level `queryOptions()`   | Feature-specific stale times, retry logic      |
| Single route or component | Inline options on hook          | One-off `refetchInterval`, `select` transforms |

Place configuration at the narrowest scope that covers all consumers.

## Setup Checklist

| Step                                    | Pattern                                                    | Priority |
| --------------------------------------- | ---------------------------------------------------------- | -------- |
| Pass QueryClient through router context | `createRootRouteWithContext<{ queryClient: QueryClient }>` | CRITICAL |
| Use `setupRouterSsrQueryIntegration`    | Automatic SSR dehydrate/hydrate                            | CRITICAL |
| Set `defaultPreloadStaleTime: 0`        | Let Query manage all caching                               | CRITICAL |
| Set `defaultErrorComponent`             | Catch errors at route level                                | HIGH     |
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
| Table state lost on navigation     | State in component, not URL             | Sync pagination/sort/filter to search params        |

## Common Mistakes

| Mistake                                                     | Correct Pattern                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Installing all TanStack libraries at project start          | Build vanilla first, adopt selectively where clear benefit exists                  |
| Using a global QueryClient singleton                        | Create QueryClient per request inside `getRouter()` for SSR safety and testability |
| Leaving Router cache enabled alongside Query cache          | Set `defaultPreloadStaleTime: 0` so Query is the single caching source             |
| Fetching data in components with `useQuery` without loaders | Use `ensureQueryData` in route loaders to prevent loading waterfalls               |
| Manual `dehydrate`/`hydrate` calls for SSR                  | Use `setupRouterSsrQueryIntegration` for automatic SSR cache transfer              |
| Handling server function errors in `onError`                | Server functions return errors in result object, check in `onSuccess`              |
| Not resetting page on filter change in tables               | Set `page: 1` when search or filter params change                                  |

## Delegation

> For library-specific patterns, delegate to the corresponding skill: `tanstack-query`, `tanstack-router`, `tanstack-start`, `tanstack-table`, `tanstack-form`, `tanstack-virtual`, `tanstack-db`, `tanstack-store`, `tanstack-pacer`, or `tanstack-devtools`.

- **TanStack library selection and adoption strategy**: Use `Explore` agent
- **Router+Query integration setup across routes**: Use `Task` agent
- **SSR architecture and caching strategy planning**: Use `Plan` agent

## References

- [Router+Query setup and SSR integration](references/router-query-setup.md)
- [Loader data flow, parallel loading, and search-param-dependent loaders](references/loader-patterns.md)
- [Form+Query integration, Zod validation, field arrays, server functions, and mutation patterns](references/form-query-integration.md)
- [End-to-end flows: form submission, infinite scroll, paginated table, auth-protected routes, error handling](references/end-to-end-flows.md)
- [Caching coordination and anti-patterns](references/caching-coordination.md)
- [Recommended libraries for React + TanStack projects](references/recommended-libraries.md)
- [Debugging guide: DevTools, profiling, memory leaks, error boundaries](references/debugging-guide.md)
