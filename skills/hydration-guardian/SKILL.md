---
name: hydration-guardian
description: 'Ensures zero-mismatch integrity between server-rendered HTML and client-side React trees. Use when debugging hydration errors, fixing text content mismatches, handling browser extension DOM pollution, or implementing Pausable Composition and deterministic bridges in React and Next.js.'
---

# Hydration Guardian

## Overview

Ensures zero-mismatch integrity between server-rendered HTML and client-side React trees. Covers hydration error diagnosis, Pausable Composition for non-deterministic UI, deterministic data bridges with the `use` hook, `@use cache` for eliminating data drift, and automated sensory validation of rendered DOM state.

**When to use:** Debugging hydration mismatch errors, fixing text content mismatches, handling browser extension DOM pollution, implementing deterministic data bridges, optimizing SSR/client hydration performance.

**When NOT to use:** Client-only React applications without SSR, static sites without hydration, API-only backends.

## Quick Reference

| Pattern              | Approach                                          | Key Points                                             |
| -------------------- | ------------------------------------------------- | ------------------------------------------------------ |
| Pausable Composition | `<Pausable fallback={...}>` boundary              | Delays hydration of branches without blocking the page |
| Deterministic bridge | `use(serverPromise)` instead of useEffect         | Seamless server-to-client data transition              |
| Cache directive      | `'use cache'` in data fetchers                    | Share exact server result with client during hydration |
| Sensory validation   | Automated DOM audit via browser tools             | Detect silent hydration warnings that do not crash     |
| Priority hydration   | `<Pausable priority="high">` for viewport content | Hydrate above-the-fold content first                   |
| Date/time safety     | UTC normalization or server-synced context        | Prevent locale-dependent hydration mismatches          |
| Extension resilience | Test with common browser extensions active        | Detect DOM pollution from translators, dark-mode tools |
| Mutation monitoring  | MutationObserver within first 100ms               | Flag excessive DOM changes during hydration            |

## Hydration Error Diagnosis

| Error Message                  | Likely Cause                             | Corrective Action                                       |
| ------------------------------ | ---------------------------------------- | ------------------------------------------------------- |
| `Text content did not match`   | Conditional rendering in inline elements | Wrap in `<Pausable>` or use `use(data)` pattern         |
| `Extra attributes from server` | Server-side metadata pollution           | Use `'use cache'` to isolate server-side data           |
| `Hydration failed (Extension)` | Third-party extension modifying DOM      | Verify extension resilience in hydration-guardian logic |
| `Pausable boundary timed out`  | Deadlocked promise in `use()`            | Implement timeout strategy for paused boundaries        |

## Common Mistakes

| Mistake                                                             | Correct Pattern                                                             |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Using `suppressHydrationWarning` on container elements              | Fix the root cause; use `Pausable` boundaries for non-deterministic content |
| Accessing `window` or `document` directly in the render body        | Wrap client-only code in `useEffect` or a `Pausable` boundary               |
| Using `Math.random()` or `new Date()` without stable seeds          | Use UTC normalization or server-cached deterministic values                 |
| Ignoring silent hydration warnings that do not crash the app        | Run the sensory validation protocol to detect hidden mismatches             |
| Using `dangerouslySetInnerHTML` with server/client content mismatch | Use a dedicated `key` change or move dynamic content to `Pausable`          |
| Over-pausing everything causing a "dead" app feel                   | Pause only non-deterministic branches; keep critical UI interactive         |

## Delegation

- **Scan rendered pages for hidden hydration warnings**: Use `Explore` agent with Chrome DevTools to run the hydration audit script
- **Fix hydration mismatches across multiple routes**: Use `Task` agent to isolate, correct, and verify each affected component
- **Design hydration-safe architecture for new features**: Use `Plan` agent to select between Pausable, deterministic bridge, and cache patterns

## References

- [Sensory Validation](references/sensory-validation.md) -- automated DOM verification, flash detection, mutation monitoring, environment simulation
- [Pausable Composition](references/pausable-composition.md) -- React Pausable primitive, frozen state, priority hydration, nesting patterns
- [Use Cache Patterns](references/use-cache-patterns.md) -- data drift prevention, `@use cache` directive, `use()` hook consumption, performance impact
