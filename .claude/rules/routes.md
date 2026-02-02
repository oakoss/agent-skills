---
paths:
  - 'skills/tanstack-router/references/**'
  - 'skills/**/references/*route*'
  - 'skills/**/references/*navigation*'
  - 'skills/**/references/*loader*'
  - 'skills/**/references/*data-loading*'
---

# Route Conventions

Conventions for code examples in routing and navigation skill references.

## Route Groups

Organize routes by auth requirement using pathless layout groups:

| Group      | Purpose                              | Auth Required |
| ---------- | ------------------------------------ | ------------- |
| `_public/` | Public pages (landing, marketing)    | No            |
| `_auth/`   | Auth pages (login, register, logout) | No            |
| `_app/`    | Protected application pages          | Yes           |
| `api/`     | REST API endpoints                   | Varies        |

## Directory-Based Routing

**Use directories, not dot notation.** Only use a single file when:

1. There are no child routes, AND
2. No layout is needed

```text
Does this route have child routes?
  → Yes: Use a directory with route.tsx
  → No: Does it need a layout?
    → Yes: Use a directory with route.tsx
    → No: Single file is OK
```

**Bad — flat, hard to navigate:**

```sh
routes/
├── _app.settings.tsx
├── _app.settings.profile.tsx
└── _app.settings.billing.tsx
```

**Good — scannable, supports layouts:**

```sh
routes/_app/settings/
├── route.tsx      # Optional layout
├── index.tsx      # /app/settings
├── profile.tsx    # /app/settings/profile
└── billing.tsx    # /app/settings/billing
```

## Auth Guard Pattern

Route layout files serve dual purpose — auth guards via `beforeLoad` and layout via `component`:

```tsx
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
