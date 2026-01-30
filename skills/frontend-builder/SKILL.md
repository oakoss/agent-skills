---
name: frontend-builder
description: Build modern React/Next.js frontends. Use when creating web applications, choosing frontend stack, structuring components, or implementing UI/UX designs. Covers React, Next.js, Tailwind CSS, and component patterns.
version: 1.0.0
---

# Frontend Builder

Build maintainable, performant React and Next.js frontends.

## Core Principles

| Principle              | Description                                        |
| ---------------------- | -------------------------------------------------- |
| Component Composition  | Small, reusable, single-purpose components         |
| State Proximity        | Keep state as close to where it's used as possible |
| Performance by Default | Optimize rendering, code splitting, asset loading  |
| Developer Experience   | Clear naming, consistent patterns, helpful errors  |

## Framework Selection

| Criterion          | React + Vite         | Next.js       |
| ------------------ | -------------------- | ------------- |
| SEO needed         | No                   | Yes           |
| Server rendering   | No                   | Yes           |
| API routes         | No                   | Yes           |
| Static hosting     | Yes                  | Yes           |
| Image optimization | Manual               | Built-in      |
| Recommended for    | SPAs, internal tools | Most projects |

## Component Types

| Type    | Purpose                     | Example Path                       |
| ------- | --------------------------- | ---------------------------------- |
| Page    | Route entry point           | `app/users/page.tsx`               |
| Feature | Business logic + data       | `components/features/UserList.tsx` |
| UI      | Reusable, no business logic | `components/ui/button.tsx`         |
| Layout  | Page structure              | `components/layouts/Header.tsx`    |

## State Management Decision

| Scope                  | Solution                    |
| ---------------------- | --------------------------- |
| Single component       | `useState`                  |
| Parent + children      | Props or `useState` + props |
| Siblings               | Lift state to common parent |
| App-wide (theme, auth) | Context API                 |
| Complex app state      | Zustand                     |

## Data Fetching

| Pattern              | When to Use                                                |
| -------------------- | ---------------------------------------------------------- |
| TanStack Query       | Client-side fetching with caching, mutations, invalidation |
| Server Components    | Next.js App Router — data fetched on server                |
| `use client` + Query | Interactive lists with client-side state                   |

## Folder Structure (Next.js App Router)

| Directory              | Contents                                     |
| ---------------------- | -------------------------------------------- |
| `app/`                 | Route groups, pages, layouts, API routes     |
| `components/ui/`       | shadcn/ui components (button, input, dialog) |
| `components/features/` | Feature components (UserList, UserProfile)   |
| `components/layouts/`  | Header, Footer, Sidebar                      |
| `lib/`                 | Utility functions, API client, Zod schemas   |
| `hooks/`               | Custom React hooks                           |
| `stores/`              | Zustand stores                               |

## Styling Preference

| Approach                 | When to Use                            |
| ------------------------ | -------------------------------------- |
| Tailwind CSS + shadcn/ui | Recommended default                    |
| CSS Modules              | Legacy projects, CSS-in-JS alternative |
| Styled Components        | Existing projects using it             |

## Common Mistakes

| Mistake                                            | Correct Pattern                                                        |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| Giant multi-responsibility component               | Break into focused sub-components with single purposes                 |
| Placing all state at the top of the component tree | Keep state as close to where it is consumed as possible                |
| Using `useEffect` to compute derived data          | Use `useMemo` for derived values; reserve `useEffect` for side effects |
| Missing error boundaries around feature sections   | Wrap feature areas with `ErrorBoundary` to prevent full-page crashes   |
| No code splitting on heavy routes                  | Use `React.lazy()` or Next.js `dynamic()` for route-level splitting    |

## Delegation

When building frontends, delegate to:

- `react` — React hooks and performance patterns
- `tanstack-query` — Data fetching and caching
- `tanstack-form` — Form handling and validation
- `tailwind` — Tailwind CSS patterns
- `design-system` — Token hierarchy and component architecture
- `performance-optimizer` — Performance profiling and optimization

## References

- [Component Architecture](references/component-architecture.md) — Page, feature, and UI component patterns with TypeScript
- [State Management](references/state-management.md) — useState, Context API, and Zustand patterns
- [Data Fetching](references/data-fetching.md) — TanStack Query and Next.js Server Components
- [Forms and Validation](references/forms.md) — React Hook Form with Zod validation
- [Styling](references/styling.md) — Tailwind CSS and CSS Modules patterns
- [Performance and Errors](references/performance-and-errors.md) — React memoization, Next.js optimization, error boundaries
