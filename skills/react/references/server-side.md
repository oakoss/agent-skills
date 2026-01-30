---
title: Server-Side Rendering
description: Partial Pre-rendering, React.cache(), RSC serialization, parallel composition, and post-response operations
tags: [ssr, ppr, server-components, cache, streaming, hydration]
---

# Server-Side Rendering

## Partial Pre-rendering (PPR)

**Impact: CRITICAL** -- Sub-100ms LCP for dynamic pages.

PPR allows a single route to have both static and dynamic parts. The static shell is served immediately from the edge, while dynamic holes (wrapped in Suspense) are streamed in.

```tsx
// next.config.ts
export default {
  experimental: {
    ppr: 'incremental',
  },
};

// app/dashboard/page.tsx
import { Suspense } from 'react';
import { StaticShell, DynamicStats } from './components';

export const experimental_ppr = true;

export default function Page() {
  return (
    <main>
      <StaticShell />
      <Suspense fallback={<StatsSkeleton />}>
        <DynamicStats />
      </Suspense>
    </main>
  );
}
```

**Rule of Thumb**: Anything NOT wrapped in `<Suspense>` at the page level becomes part of the static pre-rendered shell.

## Per-Request Deduplication with React.cache()

Use `React.cache()` for server-side request deduplication. Authentication and database queries benefit most.

```typescript
import { cache } from 'react';

export const getCurrentUser = cache(async () => {
  const session = await auth();
  if (!session?.user?.id) return null;
  return await db.user.findUnique({
    where: { id: session.user.id },
  });
});
```

## Cross-Request LRU Caching

`React.cache()` only works within one request. For data shared across sequential requests, use an LRU cache.

```typescript
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, any>({
  max: 1000,
  ttl: 5 * 60 * 1000, // 5 minutes
});

export async function getUser(id: string) {
  const cached = cache.get(id);
  if (cached) return cached;
  const user = await db.user.findUnique({ where: { id } });
  cache.set(id, user);
  return user;
}
```

With Vercel's Fluid Compute, LRU caching is especially effective because multiple concurrent requests share the same function instance.

## Minimize Serialization at RSC Boundaries

The React Server/Client boundary serializes all object properties. Only pass fields that the client actually uses.

```tsx
// Bad: serializes all 50 fields
async function Page() {
  const user = await fetchUser();
  return <Profile user={user} />;
}

// Good: serializes only 1 field
async function Page() {
  const user = await fetchUser();
  return <Profile name={user.name} />;
}
```

## Parallel Data Fetching with Component Composition

React Server Components execute sequentially within a tree. Restructure with composition to parallelize:

```tsx
// Bad: Sidebar waits for Page's fetch to complete
export default async function Page() {
  const header = await fetchHeader();
  return (
    <div>
      <div>{header}</div>
      <Sidebar />
    </div>
  );
}

// Good: both fetch simultaneously
export default function Page() {
  return (
    <div>
      <Header />
      <Sidebar />
    </div>
  );
}
```

## Non-Blocking Post-Response Operations

Schedule work that should execute after a response is sent:

```tsx
import onFinished from 'on-finished';

app.post('/api/action', async (req, res) => {
  await updateDatabase(req.body);

  onFinished(res, (err) => {
    if (err) return;
    logUserAction({
      userAgent: req.headers['user-agent'],
      status: res.statusCode,
    });
  });

  res.json({ status: 'success' });
});
```

## Server Action Security

Authenticate server actions like API routes. Always validate input and check permissions.

## Hydration Mismatch Prevention

Use inline `<script>` to set client-only values before React hydrates. Use `suppressHydrationWarning` for intentional mismatches.

## `<Activity>` Component (React 19.2+)

Hide a component tree while keeping it mounted and preserving state:

```tsx
import { Activity } from 'react';

function Dashboard({ activeTab }) {
  return (
    <>
      <Activity mode={activeTab === 'home' ? 'visible' : 'hidden'}>
        <HomeTab />
      </Activity>
      <Activity mode={activeTab === 'settings' ? 'visible' : 'hidden'}>
        <SettingsTab />
      </Activity>
    </>
  );
}
```

When `mode="hidden"`, React skips the rendering and commit phase but keeps the DOM nodes and state in memory.
