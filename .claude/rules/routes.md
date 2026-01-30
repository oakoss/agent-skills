---
paths:
  - 'skills/**/references/*navigation*.md'
  - 'skills/**/references/*route*.md'
  - 'skills/**/references/*auth-and-context*.md'
  - 'skills/**/references/*data-loading*.md'
---

# Route Conventions

## Route Groups

| Directory  | Purpose                              | Auth Required |
| ---------- | ------------------------------------ | ------------- |
| `_public/` | Public pages (landing, marketing)    | No            |
| `_auth/`   | Auth pages (login, register, logout) | No            |
| `_app/`    | Protected application pages          | Yes           |
| `api/`     | REST API endpoints                   | Varies        |

## Directory-Based Routing

**Use directories, not dot notation.** Only use a single file when:

1. There are no child routes, AND
2. No layout is needed

```sh
routes/
├── __root.tsx        # Root layout (shell, meta, CSS)
├── index.tsx         # Homepage (/) - single file OK, no children
├── _public/
│   ├── route.tsx     # Public layout
│   └── index.tsx     # /public landing
├── _auth/
│   ├── route.tsx     # Auth layout
│   ├── login.tsx     # /login - single file OK within group
│   └── register.tsx  # /register
├── _app/
│   ├── route.tsx     # Auth guard + app layout
│   ├── index.tsx     # /app (dashboard)
│   └── settings/     # Directory for settings routes
│       ├── route.tsx # Settings layout (if needed)
│       ├── index.tsx # /app/settings
│       └── profile.tsx
└── api/
    ├── posts.ts      # /api/posts
    └── auth/$.ts     # /api/auth/* (Better Auth)
```

## Decision Tree

```text
Does this route have child routes?
  → Yes: Use a directory with route.tsx
  → No: Does it need a layout?
    → Yes: Use a directory with route.tsx
    → No: Single file is OK
```

## Avoid Dot Notation

**Bad - Flat, hard to navigate:**

```sh
routes/
├── _app.settings.tsx
├── _app.settings.profile.tsx
└── _app.settings.billing.tsx
```

**Good - Scannable, supports layouts:**

```sh
routes/_app/settings/
├── route.tsx      # Optional layout
├── index.tsx      # /app/settings
├── profile.tsx    # /app/settings/profile
└── billing.tsx    # /app/settings/billing
```

## route.tsx Pattern

The `route.tsx` file inside a route group folder serves dual purpose:

1. **Auth guards** via `beforeLoad`
2. **Layout** via `component`

```tsx
// _app/route.tsx
export const Route = createFileRoute('/_app')({
  beforeLoad: async () => {
    const session = await getSession();
    if (!session) {
      throw redirect({ to: '/login' });
    }
  },
  component: AppLayout,
});

function AppLayout() {
  return (
    <div>
      <Sidebar />
      <main>
        <Outlet />
      </main>
    </div>
  );
}
```
