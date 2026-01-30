---
name: zustand
description: |
  Zustand v5 state management for React. Covers TypeScript stores with double-parentheses syntax, persist middleware with hydration handling, devtools, slices pattern for large apps, SSR/Next.js provider pattern, immer middleware, and vanilla stores.

  Use when setting up global state, configuring persist middleware, implementing slices pattern, migrating from Redux or Context, or troubleshooting hydration and TypeScript issues.
---

# Zustand State Management

## Overview

Zustand v5 is a lightweight global state manager for React built on `useSyncExternalStore`. It provides type-safe stores, atomic selectors for minimal re-renders, composable middleware (persist, devtools, immer), and a slices pattern for large applications. Use Zustand for client-only global state; use TanStack Query for server-fetched data.

**When to use:** Client-side global state, persistent user preferences, complex multi-domain stores, cross-component state sharing.

**When NOT to use:** Server state with caching needs (use TanStack Query), single-component state (use useState), simple prop drilling scenarios.

## Quick Reference

| Pattern          | API                                     | Key Points                                         |
| ---------------- | --------------------------------------- | -------------------------------------------------- |
| Basic store      | `create<T>()((set) => ({...}))`         | Double parentheses required for TS                 |
| Atomic selector  | `useStore(state => state.bears)`        | Only re-renders when selected value changes        |
| Multiple values  | `useShallow(state => ({a, b}))`         | Prevents infinite re-renders from object selectors |
| Persist          | `persist(fn, { name })`                 | localStorage with SSR hydration handling           |
| Devtools         | `devtools(fn, { name })`                | Redux DevTools integration                         |
| Middleware order | `devtools(persist(fn))`                 | Outer to inner wrapping                            |
| Slices pattern   | `StateCreator<Combined, [], [], Slice>` | Split store by domain                              |
| SSR provider     | `createStore` + React Context           | Per-request stores prevent data leaks              |
| Immer            | `immer(fn)`                             | Safe nested state mutations                        |
| Vanilla store    | `createStore` from `zustand/vanilla`    | Use outside React                                  |
| Reset store      | `set(initialState)`                     | Restore to initial values                          |
| Derived values   | `useStore(s => s.items.length)`         | Compute in selector                                |

## Do / Don't

| Don't                                        | Do                                                    |
| -------------------------------------------- | ----------------------------------------------------- |
| `create<T>(...)` single parentheses          | `create<T>()()` double parentheses for TS middleware  |
| `useStore(state => state)` full object       | Atomic selectors: `state.bears`                       |
| `export const useStore = create(...)` in SSR | `StoreContext` provider pattern for SSR               |
| Monolithic store file                        | Slices pattern for complex domains                    |
| Direct mutation                              | `immer` middleware or functional updates              |
| `useEffect` for hydration sync               | `persist` with `skipHydration` / `onRehydrateStorage` |
| Store read in RSC                            | Pass data via props to client components              |
| New objects in selectors                     | `useShallow` or separate primitive selectors          |
| Same storage name for multiple stores        | Unique `name` per persisted store                     |
| Zustand for server state                     | TanStack Query instead                                |

## Common Mistakes

| Mistake                                                                   | Correct Pattern                                                                                   |
| ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Using `create<T>(...)` with single parentheses                            | Use `create<T>()(...)` double parentheses for correct TypeScript middleware inference             |
| Selecting full state object with `useStore(state => state)`               | Use atomic selectors like `state.bears` or `useShallow` to avoid unnecessary re-renders           |
| Creating new object references in selectors causing infinite loops        | Use separate primitive selectors or wrap with `useShallow` from `zustand/shallow`                 |
| Using a global singleton store with SSR or Next.js                        | Use the `StoreContext` provider pattern with `createStore` to prevent data leaks between requests |
| Using Zustand for server-fetched data that needs caching and revalidation | Use TanStack Query for server state; reserve Zustand for client-only global state                 |

## Delegation

- **Store architecture and slices design**: Use `Plan` agent to define domain boundaries, slice interfaces, and middleware composition order
- **Hydration and SSR debugging**: Use `Task` agent to diagnose persist middleware issues, hydration mismatches, and Next.js provider setup
- **Migration from v4 to v5**: Use `Explore` agent to find deprecated import paths, single-parentheses patterns, and legacy middleware usage

## References

- [Store patterns, TypeScript, and core API](references/store-patterns.md)
- [Middleware: persist, devtools, immer, and custom](references/middleware.md)
- [Slices pattern and large store architecture](references/slices-pattern.md)
- [SSR, Next.js, and hydration handling](references/ssr-hydration.md)
- [Migration guide: Redux, Context, and v4 to v5](references/migration.md)
