---
title: SvelteKit Routing
description: File-based routing, server and universal load functions, layouts, route groups, and parameter matchers
tags: [routing, load, layout, params, groups, matchers, page, server, universal]
---

# SvelteKit Routing

## File-Based Routing

Routes are defined by the directory structure under `src/routes/`.

```text
src/routes/
├── +page.svelte              → /
├── +layout.svelte            → layout for all pages
├── about/
│   └── +page.svelte          → /about
├── blog/
│   ├── +page.svelte          → /blog
│   ├── +page.server.ts       → server load for /blog
│   └── [slug]/
│       ├── +page.svelte      → /blog/:slug
│       └── +page.server.ts   → server load for /blog/:slug
├── api/
│   └── users/
│       └── +server.ts        → /api/users (API endpoint)
└── (auth)/
    ├── +layout.svelte        → layout group (no URL segment)
    ├── login/
    │   └── +page.svelte      → /login
    └── register/
        └── +page.svelte      → /register
```

## Route Parameters

```text
src/routes/blog/[slug]/+page.svelte        → /blog/hello-world
src/routes/[category]/[id]/+page.svelte    → /electronics/42
src/routes/files/[...path]/+page.svelte    → /files/a/b/c (rest param)
src/routes/[[lang]]/about/+page.svelte     → /about or /en/about (optional)
```

### Parameter Matchers

Create type-safe route params by adding matchers in `src/params/`.

```ts
// src/params/integer.ts
import type { ParamMatcher } from '@sveltejs/kit';

export const match: ParamMatcher = (param) => {
  return /^\d+$/.test(param);
};
```

```text
src/routes/items/[id=integer]/+page.svelte  → only matches /items/42
```

## Server Load Functions

Run exclusively on the server. Have access to databases, secrets, and file system. Defined in `+page.server.ts` or `+layout.server.ts`.

```ts
// src/routes/blog/[slug]/+page.server.ts
import type { PageServerLoad } from './$types';
import { error } from '@sveltejs/kit';

export const load: PageServerLoad = async ({ params, locals }) => {
  const post = await locals.db.post.findUnique({
    where: { slug: params.slug },
  });

  if (!post) {
    error(404, { message: 'Post not found' });
  }

  return { post };
};
```

```svelte
<!-- src/routes/blog/[slug]/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
</script>

<h1>{data.post.title}</h1>
<div>{@html data.post.content}</div>
```

## Universal Load Functions

Run on both server and client. Use SvelteKit's `fetch` for automatic cookie forwarding and relative URL resolution. Defined in `+page.ts` or `+layout.ts`.

```ts
// src/routes/blog/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const response = await fetch('/api/posts');
  const posts: Post[] = await response.json();
  return { posts };
};
```

## Layouts

Shared UI and data loading for nested routes. Every route inherits from its nearest `+layout.svelte`.

```svelte
<!-- src/routes/+layout.svelte -->
<script lang="ts">
  import type { LayoutData } from './$types';
  import { type Snippet } from 'svelte';

  let { data, children }: { data: LayoutData; children: Snippet } = $props();
</script>

<nav>
  <a href="/">Home</a>
  <a href="/about">About</a>
  {#if data.user}
    <span>{data.user.name}</span>
  {/if}
</nav>

<main>
  {@render children()}
</main>
```

```ts
// src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  return { user: locals.user };
};
```

## Layout Groups

Group routes to share layouts without adding a URL segment. Wrap the group name in parentheses.

```text
src/routes/
├── (marketing)/
│   ├── +layout.svelte     → marketing layout (wide, no sidebar)
│   ├── +page.svelte       → /
│   └── pricing/
│       └── +page.svelte   → /pricing
└── (app)/
    ├── +layout.svelte     → app layout (sidebar, auth required)
    ├── dashboard/
    │   └── +page.svelte   → /dashboard
    └── settings/
        └── +page.svelte   → /settings
```

## Page Options

Control rendering strategy per route.

```ts
// +page.ts or +page.server.ts
export const prerender = true;
export const ssr = true;
export const csr = true;
export const trailingSlash = 'never';
```

| Option          | Effect                                  |
| --------------- | --------------------------------------- |
| `prerender`     | Generate static HTML at build time      |
| `ssr = false`   | Client-side only rendering              |
| `csr = false`   | No client-side JavaScript (static HTML) |
| `trailingSlash` | `'never'`, `'always'`, or `'ignore'`    |

## API Routes (+server.ts)

Standalone request handlers, not tied to a page.

```ts
// src/routes/api/users/+server.ts
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url, locals }) => {
  const limit = Number(url.searchParams.get('limit') ?? 10);
  const users = await locals.db.user.findMany({ take: limit });
  return json(users);
};

export const POST: RequestHandler = async ({ request, locals }) => {
  const body = await request.json();
  const user = await locals.db.user.create({ data: body });
  return json(user, { status: 201 });
};
```

## Using $page Store

Access current route info, URL, params, and data.

```svelte
<script>
  import { page } from '$app/stores';
</script>

<p>Current path: {$page.url.pathname}</p>
<p>Route param: {$page.params.slug}</p>
```

## Navigation

```svelte
<script>
  import { goto, invalidateAll } from '$app/navigation';

  async function navigateAway() {
    await goto('/dashboard');
  }

  async function refreshData() {
    await invalidateAll();
  }
</script>

<a href="/about">About (link)</a>
<button onclick={navigateAway}>Go to dashboard</button>
```

## Dependent Load Functions

Child load functions can access parent data via `await parent()`.

```ts
// src/routes/dashboard/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ parent }) => {
  const { user } = await parent();
  const stats = await fetchStats(user.id);
  return { stats };
};
```
