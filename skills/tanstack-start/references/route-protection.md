---
title: Route Protection
description: Authentication and authorization patterns using beforeLoad, pathless layout routes, session security, login/logout server functions, and HTTP-only cookies
tags:
  [
    auth,
    beforeLoad,
    redirect,
    layout,
    pathless,
    session,
    cookies,
    useSession,
    protected-routes,
    login,
    logout,
  ]
---

# Route Protection

## beforeLoad for Auth Checks

```ts
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ location }) => {
    const session = await getSessionData();
    if (!session) {
      throw redirect({
        to: '/login',
        search: { redirect: location.href },
      });
    }
    return { user: session };
  },
  component: AuthenticatedLayout,
});
```

Child routes automatically inherit protection and `context.user`:

```ts
export const Route = createFileRoute('/_authenticated/dashboard')({
  loader: async ({ context }) => {
    return await fetchDashboardData(context.user.id);
  },
});
```

## Session Management

```ts
import { useSession } from '@tanstack/react-start/server';

export function getSession() {
  return useSession({
    password: process.env.SESSION_SECRET!,
    cookie: {
      name: '__session',
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7,
    },
  });
}
```

## Login and Logout Server Functions

```ts
import { createServerFn } from '@tanstack/react-start';
import { redirect } from '@tanstack/react-router';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(100),
});

export const loginFn = createServerFn({ method: 'POST' })
  .inputValidator(loginSchema)
  .handler(async ({ data }) => {
    const user = await db.users.findUnique({ where: { email: data.email } });

    if (!user || !(await verifyPassword(data.password, user.passwordHash))) {
      return { error: 'Invalid credentials', code: 'AUTH_FAILED' };
    }

    const session = await getSession();
    await session.update({ userId: user.id });

    throw redirect({ to: '/dashboard' });
  });

export const logoutFn = createServerFn({ method: 'POST' }).handler(async () => {
  const session = await getSession();
  await session.update({ userId: undefined });

  throw redirect({ to: '/login' });
});
```

## Reading Session in Loaders

```ts
export const getSessionData = createServerFn().handler(async () => {
  const session = await getSession();

  if (!session.data.userId) {
    return null;
  }

  const user = await db.users.findUnique({
    where: { id: session.data.userId },
    select: { id: true, email: true, name: true, role: true },
  });

  return user;
});
```

Use in the root route to make session data available app-wide:

```ts
export const Route = createRootRouteWithContext()({
  beforeLoad: async () => {
    const user = await getSessionData();
    return { user };
  },
});
```

## Security Anti-Patterns

- **Storing auth tokens in localStorage** — Use HTTP-only cookies
- **Checking auth in component useEffect** — Use `beforeLoad` on routes to prevent data loading for unauthenticated users
- **Exposing secrets via `process.env` in shared files** — Use `createServerOnlyFn` for secrets. Use `VITE_` prefix only for public config
- **Allowing client to set `role` / `isAdmin`** — Strip privileged fields in validation schema
- **Returning the full user object from session** — Select only needed fields to avoid leaking sensitive data
