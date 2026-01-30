---
title: Navigation
description: Link component, active styling, relative navigation, hash links, route masks for modals, useBlocker for dirty forms, history state, and scroll restoration
tags:
  [
    navigation,
    Link,
    useNavigate,
    active-styling,
    route-mask,
    useBlocker,
    scroll-restoration,
  ]
---

# Navigation

## Link Component

Prefer `<Link>` over `useNavigate()` for proper `<a>` tags, right-click, accessibility, SEO, and preloading:

```tsx
<Link
  to="/posts/$postId"
  params={{ postId: '123' }}
  activeProps={{ className: 'nav-link-active', 'aria-current': 'page' }}
  activeOptions={{ exact: true }}
  preload="intent"
>
  View Post
</Link>
```

Reserve `useNavigate()` for side effects: form submissions, auth redirects, programmatic navigation.

## Active Link Styling

```tsx
// 1. activeProps / inactiveProps
<Link
  to="/dashboard"
  activeProps={{ className: 'text-primary font-semibold' }}
  inactiveProps={{ className: 'text-muted-foreground' }}
>
  Dashboard
</Link>

// 2. data-status attribute (CSS-driven)
<Link to="/posts" className="data-[status=active]:text-primary">
  Posts
</Link>

// 3. useMatchRoute for complex logic
const matchRoute = useMatchRoute();
const isOnPosts = matchRoute({ to: '/posts', fuzzy: true });
```

## Relative Navigation

Use `useNavigate({ from })` for type-safe relative paths:

```ts
const navigate = useNavigate({ from: '/posts/$postId' });
navigate({ to: '..', search: { page: 1 } }); // Go to /posts
navigate({ to: '.', search: (prev) => ({ ...prev }) }); // Stay, update search
```

## Hash Navigation

```tsx
<Link to="." hash="comments">Jump to Comments</Link>
<Link to="/about" hash="team">Meet the Team</Link>
navigate({ hash: 'section-2' });
```

## Route Masks (Modal URLs)

```tsx
<Link
  to="/posts/$postId"
  params={{ postId: post.id }}
  mask={{ to: '/posts', search: { preview: post.id } }}
>
  {post.title}
</Link>
// URL shows: /posts?preview=123 — Router navigates to: /posts/123
```

## Block Navigation (Dirty Forms)

```ts
import { useBlocker } from '@tanstack/react-router';

function EditForm() {
  const [isDirty, setIsDirty] = useState(false);

  useBlocker({
    shouldBlockFn: () => {
      if (!isDirty) return false;
      return !window.confirm('You have unsaved changes. Leave anyway?');
    },
  });
}
```

## History State

Store ephemeral state that survives navigation but not page refresh:

```ts
navigate({
  to: '/posts/$postId',
  params: { postId: '123' },
  state: { fromFeed: true, scrollPosition: 500 },
});

function PostPage() {
  const state = useRouterState({ select: (s) => s.location.state });
  const fromFeed = state?.fromFeed;
}
```

## Scroll Restoration

```ts
// Custom element scroll restoration
export const Route = createFileRoute('/posts')({
  scrollRestoration: {
    getElement: () => document.getElementById('posts-container'),
  },
});

// Preserve scroll when updating filters
navigate({
  search: (prev) => ({ ...prev, filter }),
  resetScroll: false,
});

// Reset scroll explicitly
<Link to="/posts" resetScroll>Posts</Link>
```
