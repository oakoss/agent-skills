---
title: Selective Hydration
description: Suspense-based selective hydration, streaming SSR with renderToPipeableStream, two-pass rendering for client-only content, and Next.js dynamic imports
tags:
  [
    suspense,
    selective-hydration,
    streaming-ssr,
    two-pass-rendering,
    dynamic-import,
    hydrateRoot,
  ]
---

# Selective Hydration

React 18+ supports selective hydration via Suspense boundaries. Each Suspense boundary can hydrate independently, and React prioritizes hydrating components the user interacts with.

## How Selective Hydration Works

With `hydrateRoot` and Suspense, React solves three SSR bottlenecks:

1. **No waiting for all data** -- Streaming HTML sends content as it becomes ready
2. **No waiting for all JS** -- Code-split components hydrate when their code loads
3. **No waiting for all hydration** -- User interactions trigger priority hydration

```tsx
import { hydrateRoot } from 'react-dom/client';

hydrateRoot(document.getElementById('root')!, <App />);
```

## Suspense Boundaries for Hydration Control

Wrap independent sections in Suspense to create hydration boundaries. Each boundary hydrates independently without blocking siblings.

```tsx
import { Suspense } from 'react';

function ProductPage({ product }: { product: Product }) {
  return (
    <main>
      <ProductHeader product={product} />

      <Suspense fallback={<DetailsSkeleton />}>
        <ProductDetails product={product} />
      </Suspense>

      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews productId={product.id} />
      </Suspense>

      <Suspense fallback={<RecommendationsSkeleton />}>
        <RecommendedProducts categoryId={product.categoryId} />
      </Suspense>
    </main>
  );
}
```

**Hydration behavior:**

- `ProductHeader` hydrates first (not wrapped in Suspense)
- Each Suspense section hydrates independently when its code loads
- If a user clicks on `ProductReviews` before it hydrates, React prioritizes hydrating that section immediately

## Streaming SSR with renderToPipeableStream

Server-side streaming sends HTML progressively as components resolve their data.

```tsx
import { renderToPipeableStream } from 'react-dom/server';

function handleRequest(req: Request, res: Response) {
  const { pipe } = renderToPipeableStream(<App />, {
    bootstrapScripts: ['/client.js'],
    onShellReady() {
      res.statusCode = 200;
      res.setHeader('Content-Type', 'text/html');
      pipe(res);
    },
    onShellError(error) {
      res.statusCode = 500;
      res.send('Server error');
    },
  });
}
```

The shell (content outside Suspense boundaries) sends immediately. Suspended content streams in as it resolves, with inline `<script>` tags that swap fallbacks for real content.

## Two-Pass Rendering

For content that must differ between server and client (browser-only APIs, user preferences), use the two-pass rendering pattern.

```tsx
import { useState, useEffect } from 'react';

function ThemeToggle() {
  const [theme, setTheme] = useState<string | null>(null);

  useEffect(() => {
    setTheme(localStorage.getItem('theme') ?? 'light');
  }, []);

  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      {theme ?? 'light'}
    </button>
  );
}
```

**How it works:**

1. **First render (server + client initial):** `theme` is `null`, both render the same fallback
2. **Second render (client only):** `useEffect` fires, `theme` updates, component re-renders with real value

**Trade-offs:**

- Components render twice on the client (slower hydration)
- Users see a brief flash as content changes
- Use sparingly for genuinely client-dependent content

## Client-Only Components with next/dynamic

For components that cannot run on the server at all (depend on `window`, `document`, or browser-only libraries), use Next.js dynamic imports.

```tsx
import dynamic from 'next/dynamic';

const MapView = dynamic(() => import('./MapView'), {
  ssr: false,
  loading: () => <MapSkeleton />,
});

function LocationPage() {
  return (
    <div>
      <h1>Our Location</h1>
      <MapView />
    </div>
  );
}
```

**When to use `ssr: false`:**

| Scenario                                 | Use `ssr: false` | Alternative                            |
| ---------------------------------------- | ---------------- | -------------------------------------- |
| Browser-only library (Leaflet, Chart.js) | Yes              | None; library crashes on server        |
| Content using `window.matchMedia`        | Maybe            | Two-pass rendering with `useEffect`    |
| Content using `localStorage`             | Maybe            | Two-pass rendering with `useEffect`    |
| Content that just differs by time        | No               | `suppressHydrationWarning` or two-pass |

**Important:** `'use client'` does NOT mean "client-only." Client components still render on the server during SSR. Only `next/dynamic` with `ssr: false` truly skips server rendering.

## Reusable Client-Only Wrapper

```tsx
import { useState, useEffect, type ReactNode } from 'react';

function ClientOnly({
  children,
  fallback = null,
}: {
  children: ReactNode;
  fallback?: ReactNode;
}) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return mounted ? children : fallback;
}

// Usage
function App() {
  return (
    <ClientOnly fallback={<TimeSkeleton />}>
      <LocalizedClock />
    </ClientOnly>
  );
}
```

## Hydration with Error Recovery

Configure `hydrateRoot` to monitor and report hydration recovery events in production.

```tsx
import { hydrateRoot } from 'react-dom/client';

hydrateRoot(document.getElementById('root')!, <App />, {
  onRecoverableError(error, errorInfo) {
    console.error('Hydration recovery:', error);
    reportToMonitoring({
      type: 'hydration-recovery',
      error: error.message,
      componentStack: errorInfo.componentStack,
    });
  },
});
```

When React encounters a hydration mismatch, it attempts to recover by re-rendering the affected subtree. `onRecoverableError` fires for each recovery event, enabling production monitoring of silent hydration issues.

## Next.js Automatic Suspense

Next.js App Router automatically wraps route segments in Suspense boundaries via `loading.tsx` files. Each route segment becomes an independent hydration boundary.

```text
app/
  layout.tsx
  loading.tsx       <-- Suspense boundary for root
  page.tsx
  products/
    loading.tsx     <-- Suspense boundary for products
    page.tsx
    [id]/
      loading.tsx   <-- Suspense boundary for product detail
      page.tsx
```

This provides selective hydration at the route level without manual Suspense placement.
