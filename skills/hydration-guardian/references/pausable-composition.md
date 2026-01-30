---
title: Pausable Composition
description: React Pausable primitive for controlled hydration including frozen state, priority hydration, nesting patterns, and migration from legacy approaches
tags: [pausable, react, hydration, selective-hydration, priority, suspense]
---

# Pausable Composition

`Pausable` is a React primitive that allows developers to explicitly pause the hydration of a component tree until a specific condition is met, without blocking the rest of the application.

## Why Pausable Replaces Legacy Patterns

The legacy `if (!mounted) return null` pattern caused:

- **Layout shift** -- the component was invisible, then suddenly appeared
- **SEO impact** -- search engines saw an empty hole where content should be

`Pausable` solves this by keeping server-rendered HTML static and "frozen" while the rest of the app becomes interactive.

## Basic Usage

```tsx
import { Pausable } from 'react';

function DynamicUserWidget({ userId }: { userId: string }) {
  return (
    <Pausable fallback={<Skeleton />}>
      <UserDetail id={userId} />
    </Pausable>
  );
}
```

The `fallback` renders only if the server-rendered content cannot be preserved. If the server HTML is valid, it stays visible while the client-side version hydrates in the background.

## The Frozen State Pattern

For components with a valid server-state whose client-state takes time to calculate (complex charts, localized prices):

```tsx
<Pausable fallback={<StaticServerVersion />}>
  <InteractiveClientVersion />
</Pausable>
```

The server-rendered static version remains visible and non-interactive until the client version is ready.

## Priority Hydration

Control hydration order to prioritize above-the-fold content.

```tsx
function ProductPage({ product }: { product: Product }) {
  return (
    <main>
      <Pausable priority="urgent">
        <HeroSection product={product} />
      </Pausable>

      <Pausable priority="high">
        <ProductDetails product={product} />
      </Pausable>

      <Pausable priority="low">
        <RecommendedProducts categoryId={product.categoryId} />
      </Pausable>

      <Pausable priority="background">
        <Footer />
      </Pausable>
    </main>
  );
}
```

**Priority levels:**

| Priority     | Use Case                            | Hydration Timing         |
| ------------ | ----------------------------------- | ------------------------ |
| `urgent`     | Elements inside the viewport (LCP)  | Immediate                |
| `high`       | Above-the-fold interactive elements | After urgent completes   |
| `low`        | Below-the-fold content              | When main thread is idle |
| `background` | Footers, analytics, non-visible UI  | Last, after all others   |

## Nesting Pausables

Granularly control hydration order with nested boundaries.

```tsx
<Pausable priority="high">
  <HeroSection />
  <Pausable priority="low">
    <RecommendedProducts />
  </Pausable>
</Pausable>
```

The outer boundary hydrates first. Inner boundaries hydrate according to their own priority once the parent is active.

## Combining with Suspense

Use `Suspense` for data loading and `Pausable` for hydration control to create a dual-layer loading experience.

```tsx
import { Suspense, Pausable, use } from 'react';

function Dashboard({ dataPromise }: { dataPromise: Promise<DashboardData> }) {
  return (
    <Suspense fallback={<DashboardSkeleton />}>
      <Pausable fallback={<div>Initializing locale...</div>}>
        <DashboardContent dataPromise={dataPromise} />
      </Pausable>
    </Suspense>
  );
}

function DashboardContent({
  dataPromise,
}: {
  dataPromise: Promise<DashboardData>;
}) {
  const data = use(dataPromise);
  return (
    <div>
      <span>Welcome back, {data.userName}</span>
      <span>{formatLocalizedTime(data.timestamp)}</span>
    </div>
  );
}
```

## How Pausable Works

1. **Server phase:** React renders the component as static HTML
2. **Client hydration phase:** React skips the `Pausable` boundary during the initial hydration pass
3. **Activation phase:** Once the main thread is idle (or the priority condition is met), React hydrates the boundary in a background transition

## Common Pitfalls

| Pitfall                               | Consequence                             | Solution                                           |
| ------------------------------------- | --------------------------------------- | -------------------------------------------------- |
| Over-pausing everything               | App feels "dead" for several seconds    | Pause only non-deterministic branches              |
| Mismatched fallback visuals           | "Jump" when the pause ends              | Ensure fallback matches the final component layout |
| No fallback provided                  | Empty space until hydration completes   | Always provide a visually appropriate fallback     |
| Pausing critical interactive elements | Users cannot interact with key features | Use `priority="urgent"` for viewport elements      |

## Migration from Legacy Patterns

```tsx
// LEGACY: useEffect mounted pattern (causes layout shift)
function LegacyComponent() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  return <ClientOnlyContent />;
}

// MODERN: Pausable boundary (no layout shift, SSR preserved)
function ModernComponent() {
  return (
    <Pausable fallback={<ServerPlaceholder />}>
      <ClientOnlyContent />
    </Pausable>
  );
}
```
