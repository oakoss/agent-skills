---
name: tanstack-start
description: 'Full-stack React framework built on TanStack Router. Type-safe routing, server functions, SSR/streaming, middleware, and multi-platform deployment. Use when building full-stack React apps with SSR, server functions, middleware, or authentication.'
---

# TanStack Start

Full-stack React framework built on TanStack Router. Type-safe server functions, SSR/streaming, middleware composition, and deployment to Cloudflare Workers, Vercel, Netlify, AWS Lambda, and more.

**Package:** `@tanstack/react-start`

## Server Functions

| Pattern                              | Usage                                               |
| ------------------------------------ | --------------------------------------------------- |
| `createServerFn()`                   | GET (default) — idempotent, cacheable data fetching |
| `createServerFn({ method: 'POST' })` | Mutations that change data                          |
| `.inputValidator(zodSchema)`         | Input validation before handler                     |
| `.handler(async ({ data }) => {})`   | Server-side logic                                   |
| `createIsomorphicFn()`               | Different implementations per environment           |
| `createServerOnlyFn()`               | Server-only utility — crashes if called from client |
| `createClientOnlyFn()`               | Client-only utility — crashes if called from server |

## Middleware

| Pattern                                    | Usage                                         |
| ------------------------------------------ | --------------------------------------------- |
| `createMiddleware().server(fn)`            | Request middleware for cross-cutting concerns |
| `.middleware([dep])`                       | Compose middleware with dependencies          |
| `next({ context: {} })`                    | Pass data downstream                          |
| `requestMiddleware: []` in `createStart()` | Global middleware                             |

## Route Protection

| Pattern                                                                 | Usage                                        |
| ----------------------------------------------------------------------- | -------------------------------------------- |
| `beforeLoad`                                                            | Auth check before route loads                |
| `_authenticated.tsx`                                                    | Pathless layout route for grouped protection |
| `context.user`                                                          | User data from parent `beforeLoad`           |
| `throw redirect({ to: '/login', search: { redirect: location.href } })` | Redirect with return URL                     |

## SSR Strategies

| Pattern                          | Usage                                   |
| -------------------------------- | --------------------------------------- |
| `await ensureQueryData()`        | Block SSR on critical data              |
| `prefetchQuery()`                | Start fetch, don't block SSR            |
| `<Suspense>` boundaries          | Define streaming chunks                 |
| `head: ({ loaderData }) => ({})` | Meta tags, Open Graph, favicons         |
| `headers: () => ({...})`         | ISR / cache-control on route definition |
| `prerender: false`               | Disable prerendering for dynamic routes |

## Execution Boundaries

| Function               | Purpose                            | Client Can Call? |
| ---------------------- | ---------------------------------- | ---------------- |
| `createServerFn()`     | Data fetching, mutations           | Yes (RPC stub)   |
| `createServerOnlyFn()` | Secrets, DB connections, utilities | No (throws)      |
| `createClientOnlyFn()` | localStorage, DOM APIs             | N/A              |
| `createIsomorphicFn()` | Per-environment implementations    | N/A              |

## Deployment (Vite Plugins)

| Platform       | Plugin                                 | Runtime |
| -------------- | -------------------------------------- | ------- |
| Cloudflare     | `@cloudflare/vite-plugin`              | Workers |
| Netlify        | `@netlify/vite-plugin-tanstack-start`  | Node    |
| Vercel         | `nitro/vite` (`preset: 'vercel'`)      | Node    |
| Node.js/Docker | `nitro/vite` (`preset: 'node-server'`) | Node    |
| AWS Lambda     | `nitro/vite` (`preset: 'aws-lambda'`)  | Node    |
| Bun            | `nitro/vite` (`preset: 'bun'`)         | Bun     |
| Static         | `nitro/vite` (`preset: 'static'`)      | None    |

## Common Mistakes

| Mistake                                      | Fix                                             |
| -------------------------------------------- | ----------------------------------------------- |
| No `.inputValidator()` on server functions   | Always validate with Zod schemas                |
| Raw fetch instead of `createServerFn`        | Loses type safety and serialization             |
| Mixing server/client code without boundaries | Use `createServerOnlyFn` / `createClientOnlyFn` |
| Checking auth in every handler               | Use middleware composition                      |
| Awaiting all data in loader                  | Only await critical data, prefetch the rest     |
| `Date.now()` in render                       | Pass timestamp from loader (hydration mismatch) |
| Missing `nodejs_compat` flag                 | Required in `wrangler.toml` for Cloudflare      |
| GET for mutations                            | Use POST for create/update/delete               |

## Delegation

Use this skill for TanStack Start server functions, middleware, SSR/streaming, route protection, API routes, and deployment configuration.

## References

- [Server Functions](references/server-functions.md) — createServerFn, validation, auth, request context, response headers, file uploads, streaming
- [Middleware](references/middleware.md) — composition, function-level middleware, global middleware
- [SSR and Streaming](references/ssr-and-streaming.md) — Suspense, prerendering, ISR, cache-control, hydration safety
- [Route Protection](references/route-protection.md) — beforeLoad, pathless layouts, session security
- [API Routes](references/api-routes.md) — createFileRoute server handlers, REST patterns, route-level middleware, webhooks, health check
- [Deployment](references/deployment.md) — Vite plugins for Cloudflare, Netlify, Nitro presets, Docker, Cloudflare bindings
- [SEO and Head Management](references/seo.md) — head property, meta tags, Open Graph, Twitter Cards, favicons, SEO helper
- [Error Handling](references/error-handling.md) — structured errors, ApiResult type, status codes, anti-patterns
- [File Organization](references/file-organization.md) — entry points, plugin config, execution boundaries, feature-based structure, environment config
- [Known Issues](references/known-issues.md) — 10 documented issues with workarounds
