---
title: Known Issues
description: 20 documented TanStack Router issues with fixes covering build/setup, routing, search params, loaders, SSR, and anti-patterns
tags:
  [
    issues,
    troubleshooting,
    devtools,
    vite-plugin,
    type-registration,
    search-params,
    SSR,
  ]
---

# Known Issues

## Build and Setup

**#1: Devtools dependency resolution** — Build fails with `@tanstack/router-devtools-core` not found. Fix: `npm install @tanstack/router-devtools`.

**#2: Vite plugin order** (CRITICAL) — Routes not auto-generated, `routeTree.gen.ts` missing. Fix: TanStackRouterVite MUST come before `react()` in plugins array.

**#3: Type registration missing** — `<Link to="...">` not typed. Fix: Add `declare module '@tanstack/react-router'` with `Register` interface in main.tsx.

**#4: Loader not running** — Loader function not called. Fix: Ensure route exports `Route` constant from `createFileRoute`.

**#5: Memory leak with TanStack Form** — Fixed in latest versions. Update `@tanstack/form` and `@tanstack/react-start`.

## Routing and Navigation

**#6: Virtual routes index/layout conflict** — `route.tsx` and `index.tsx` conflict when using `physical()`. Fix: Use pathless route `_layout.tsx` + `_layout.index.tsx`.

**#11: Pathless route notFoundComponent not rendering** — `notFoundComponent` on pathless layout routes ignored. Fix: Define on child routes instead.

**#18: Virtual routes don't support manual lazy loading** — `createLazyFileRoute` silently replaced. Use `autoCodeSplitting: true`.

**#20: Missing leading slash** — Routes fail to match. Always use `'/about'` not `'about'`.

## Search Params and Validation

**#7: Search params type inference** — `zodSearchValidator` broken since v1.81.5. Fix: Use `zodValidator` from `@tanstack/zod-adapter`.

**#8: TanStack Start validators on reload** — `validateSearch` fails on direct page load. Works on client-side navigation only.

**#9: Server function validation errors lose structure** — Zod errors stringified. Workaround: `JSON.parse(error.message)` when message starts with `[`.

**#10: useParams({ strict: false }) returns unparsed values** — After navigation, params are strings instead of parsed types. Fix: Use strict mode (default) or manually parse.

**#19: NavigateOptions type inconsistency** — `NavigateOptions` type doesn't enforce required params like `useNavigate()` does. Use `useNavigate()` return type for safety.

## Loaders and Data Loading

**#12: Aborted loader renders errorComponent with undefined error** — Rapid navigation causes undefined error. Fix: Guard with `if (!error) return null` in errorComponent.

**#17: Route head() executes before loader finishes** — Meta tags use incomplete data. Workaround: `await loaderData` in head function.

## SSR and Deployment

**#13: Vitest useState null error** — `tanstackStart()` conflicts with Vitest. Workaround: Disable plugin for tests.

**#14: Streaming SSR loader crash** — Unawaited promise rejections crash dev server. Fix: Always await or try/catch in loaders.

**#15: Prerender hangs on empty filter** — Build hangs when `prerender.filter` returns zero routes. Ensure at least one route or disable prerender.

**#16: Docker prerender failure** — Preview server not accessible. Fix: Add `preview: { host: true }` to vite config.

## Anti-Patterns

- **Fetching in useEffect** instead of route loaders — creates waterfalls, no preloading
- **Using `prefetchQuery` in loaders** instead of `ensureQueryData` — swallows errors, no return value
- **Missing router type registration** — no autocomplete, no type checking on routes
- **Using `useParams()` without `from`** — returns union of all route params instead of exact types
- **Using `useNavigate()` for links** — loses right-click, accessibility, SEO, preloading
- **Sequential fetches in loaders** — use `Promise.all` for parallel requests
- **Importing globals instead of using route context** — harder to test, couples to implementation
- **Creating empty main route files** — use virtual routes when only a `.lazy.tsx` is needed
- **Using `createLazyFileRoute` in virtual file routes** — silently replaced, use `autoCodeSplitting` instead
