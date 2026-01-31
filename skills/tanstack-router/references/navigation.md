---
title: Navigation
description: Link component, active styling with activeProps and data-status, relative navigation, hash links, route masks for modals, useBlocker for dirty forms with withResolver, history state, and scroll restoration
tags:
  [
    navigation,
    Link,
    useNavigate,
    active-styling,
    route-mask,
    useBlocker,
    scroll-restoration,
    useMatchRoute,
  ]
---

# Navigation

## Link Component

Prefer `<Link>` over `useNavigate()` for proper `<a>` tags, right-click, accessibility, SEO, and preloading:

```tsx
<Link
  to="/posts/$postId"
  params={{ postId: '123' }}
  search={{ tab: 'comments' }}
  activeProps={{ className: 'nav-link-active', 'aria-current': 'page' }}
  activeOptions={{ exact: true }}
  preload="intent"
>
  View Post
</Link>
```

Reserve `useNavigate()` for side effects: form submissions, auth redirects, programmatic navigation.

## Active Link Styling

Three approaches, from simplest to most flexible:

```tsx
// 1. activeProps / inactiveProps
<Link
  to="/dashboard"
  activeProps={{ className: 'text-primary font-semibold' }}
  inactiveProps={{ className: 'text-muted-foreground' }}
>
  Dashboard
</Link>

// 2. data-status attribute (CSS-driven, no re-render on state change)
<Link to="/posts" className="data-[status=active]:text-primary">
  Posts
</Link>

// 3. useMatchRoute for complex logic
const matchRoute = useMatchRoute();
const isOnPosts = matchRoute({ to: '/posts', fuzzy: true });
```

`activeOptions` controls matching behavior:

| Option              | Default | Effect                                    |
| ------------------- | ------- | ----------------------------------------- |
| `exact`             | `false` | Match only exact path (not children)      |
| `includeSearch`     | `false` | Include search params in active check     |
| `includeHash`       | `false` | Include hash in active check              |
| `explicitUndefined` | `false` | Treat undefined search params as explicit |

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

Route masks display one URL while internally routing to another. Use for modals, side panels, and quick views:

```tsx
function PostList() {
  return (
    <div>
      {posts.map((post) => (
        <Link
          key={post.id}
          to="/posts/$postId"
          params={{ postId: post.id }}
          mask={{
            to: '/posts',
            search: { preview: post.id },
          }}
        >
          {post.title}
        </Link>
      ))}
      <Outlet />
    </div>
  );
}
```

Programmatic navigation with mask:

```ts
navigate({
  to: '/posts/$postId',
  params: { postId: post.id },
  mask: { to: '/posts' },
});
```

| Scenario          | URL Shown  | Actual Route |
| ----------------- | ---------- | ------------ |
| Click masked link | Masked URL | Real route   |
| Share/copy URL    | Real URL   | Real route   |
| Direct navigation | Real URL   | Real route   |
| Browser refresh   | URL in bar | Matches URL  |

## Block Navigation (Dirty Forms)

Basic blocking with confirmation dialog:

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

Advanced blocking with custom UI using `withResolver`:

```tsx
function EditForm() {
  const [isDirty, setIsDirty] = useState(false);

  const { proceed, reset, status } = useBlocker({
    shouldBlockFn: ({ current, next }) => {
      if (!isDirty) return false;
      return true;
    },
    enableBeforeUnload: true,
    withResolver: true,
  });

  return (
    <div>
      <form>{/* form fields */}</form>
      {status === 'blocked' ? (
        <dialog open>
          <p>You have unsaved changes.</p>
          <button onClick={reset}>Stay</button>
          <button onClick={proceed}>Leave</button>
        </dialog>
      ) : null}
    </div>
  );
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

Enable globally in router config:

```ts
const router = createRouter({
  routeTree,
  scrollRestoration: true,
});
```

Custom element scroll restoration:

```ts
export const Route = createFileRoute('/posts')({
  scrollRestoration: {
    getElement: () => document.getElementById('posts-container'),
  },
});
```

Preserve scroll when updating filters:

```ts
navigate({
  search: (prev) => ({ ...prev, filter }),
  resetScroll: false,
});

// Reset scroll explicitly
<Link to="/posts" resetScroll>Posts</Link>
```
