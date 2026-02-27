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
    useCanGoBack,
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
  preloadDelay={100}
  disabled={!post.published}
  replace={false}
>
  View Post
</Link>
```

Reserve `useNavigate()` for side effects: form submissions, auth redirects, programmatic navigation.

### Link Component Props

| Prop            | Type                                          | Description                           |
| --------------- | --------------------------------------------- | ------------------------------------- |
| `to`            | `string`                                      | Target route path                     |
| `params`        | `object`                                      | Route params (type-safe)              |
| `search`        | `object \| (prev) => object`                  | Search params (type-safe)             |
| `hash`          | `string`                                      | URL hash fragment                     |
| `state`         | `object`                                      | History state (survives navigation)   |
| `replace`       | `boolean`                                     | Replace history entry instead of push |
| `resetScroll`   | `boolean`                                     | Reset scroll position on navigation   |
| `disabled`      | `boolean`                                     | Disable link (prevents navigation)    |
| `preload`       | `false \| 'intent' \| 'render' \| 'viewport'` | When to preload route data            |
| `preloadDelay`  | `number`                                      | Delay (ms) before intent preloading   |
| `activeProps`   | `object`                                      | Props applied when link is active     |
| `inactiveProps` | `object`                                      | Props applied when link is inactive   |
| `activeOptions` | `ActiveLinkOptions`                           | Control active matching behavior      |
| `mask`          | `MaskOptions`                                 | Display different URL (route masking) |

## Disabled Links

Disable navigation conditionally:

```tsx
<Link
  to="/edit-post"
  params={{ postId: post.id }}
  disabled={!hasPermission}
  className="data-[status=disabled]:opacity-50 data-[status=disabled]:cursor-not-allowed"
>
  Edit Post
</Link>
```

Disabled links render with `aria-disabled="true"` and prevent navigation, but still render as `<a>` tags for consistency.

## Replace vs Push

Control history behavior with `replace`:

```tsx
// Default: Push new entry to history
<Link to="/dashboard">Dashboard</Link>

// Replace current entry (no new history entry)
<Link to="/login" replace>
  Login
</Link>

// Useful after form submission
function CreatePost() {
  const { mutate } = useMutation({
    mutationFn: createPost,
    onSuccess: (post) => {
      navigate({
        to: '/posts/$postId',
        params: { postId: post.id },
        replace: true, // Replace /create with /posts/123
      });
    },
  });
}
```

Use `replace` for redirects, auth flows, and post-submission navigations where users shouldn't go back to the form.

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

## Preloading Strategies

Control when route data loads with the `preload` prop:

```tsx
// Preload on hover or focus (recommended default)
<Link to="/posts/$postId" params={{ postId: post.id }} preload="intent">
  {post.title}
</Link>

// Preload immediately when Link mounts
<Link to="/dashboard" preload="render">
  Dashboard
</Link>

// Preload when Link enters viewport
<Link to="/settings" preload="viewport">
  Settings
</Link>

// Disable preloading (for heavy routes)
<Link to="/admin/reports" preload={false}>
  Reports
</Link>
```

Add delay to avoid excessive preloading on fast mouse movements:

```tsx
<Link
  to="/posts/$postId"
  params={{ postId: post.id }}
  preload="intent"
  preloadDelay={100} // Wait 100ms after hover
>
  {post.title}
</Link>
```

Preload strategies inherit from route config and router defaults if not explicitly set.

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

  const { proceed, reset, status, next } = useBlocker({
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
          <p>Leave for {next?.pathname}? You have unsaved changes.</p>
          <button onClick={reset}>Stay</button>
          <button onClick={proceed}>Leave</button>
        </dialog>
      ) : null}
    </div>
  );
}
```

## Check Back Navigation

`useCanGoBack` returns whether the router can go back without exiting the application (experimental):

```tsx
import { useRouter, useCanGoBack } from '@tanstack/react-router';

function BackButton() {
  const router = useRouter();
  const canGoBack = useCanGoBack();

  return canGoBack ? (
    <button onClick={() => router.history.back()}>Go back</button>
  ) : null;
}
```

Returns `false` when history is at index `0` or after a `reloadDocument` navigation resets the history index.

## Catch-All Splat Route

`routes/$.tsx` catches all unmatched paths. The `_splat` param contains the matched path:

```tsx
// routes/$.tsx
export const Route = createFileRoute('/$')({
  component: CatchAllComponent,
});

function CatchAllComponent() {
  const { _splat } = Route.useParams();
  return <div>Page not found: /{_splat}</div>;
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
