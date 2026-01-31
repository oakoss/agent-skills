---
title: Route Protection
description: Authentication and authorization patterns using beforeLoad, pathless layout routes, session security, login/logout server functions, role-based access, and HTTP-only cookies
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
    createIsomorphicFn,
    getRequestHeaders,
    better-auth,
    header-forwarding,
    role-based,
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

## Role-Based Access

```ts
export const Route = createFileRoute('/_authenticated/_admin')({
  beforeLoad: async ({ context }) => {
    if (context.user.role !== 'admin') {
      throw redirect({ to: '/unauthorized' });
    }
  },
  component: AdminLayout,
});
```

File structure for nested protection:

```sh
routes/
  _authenticated.tsx           # Requires login
  _authenticated/
    dashboard.tsx              # /dashboard - any authenticated user
    settings.tsx               # /settings - any authenticated user
    _admin.tsx                 # Admin layout
    _admin/
      users.tsx                # /users - admin only
      analytics.tsx            # /analytics - admin only
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

## Session Security Checklist

| Setting    | Value                 | Purpose                            |
| ---------- | --------------------- | ---------------------------------- |
| `httpOnly` | `true`                | Prevents XSS from accessing cookie |
| `secure`   | `true` in prod        | Requires HTTPS                     |
| `sameSite` | `'lax'` or `'strict'` | CSRF protection                    |
| `maxAge`   | Application-specific  | Session duration                   |
| `password` | 32+ random chars      | Encryption key                     |

Generate a secure session secret: `openssl rand -base64 32`

## Session Validation and Expiry

```ts
interface SessionData {
  userId: string;
  email: string;
  role: 'user' | 'admin';
  createdAt: number;
}

export async function getValidatedSession(): Promise<SessionData | null> {
  const session = await getSession();
  const data = session.data as SessionData | undefined;

  if (!data?.userId) {
    return null;
  }

  const maxAge = 7 * 24 * 60 * 60 * 1000;
  if (Date.now() - data.createdAt > maxAge) {
    await session.clear();
    return null;
  }

  return data;
}
```

## Session Refresh

```ts
export const refreshSession = createServerFn({ method: 'POST' }).handler(
  async () => {
    const session = await getSession();
    const currentData = session.data as SessionData;

    if (!currentData?.userId) {
      throw redirect({ to: '/login' });
    }

    const user = await db.users.findUnique({
      where: { id: currentData.userId },
      select: { id: true, email: true, role: true },
    });

    if (!user) {
      await session.clear();
      throw redirect({ to: '/login' });
    }

    await session.update({
      ...currentData,
      createdAt: Date.now(),
    });

    return { success: true };
  },
);
```

## Session Cleanup

```ts
export const logout = createServerFn({ method: 'POST' }).handler(async () => {
  const session = await getSession();
  await session.clear();
  throw redirect({ to: '/login' });
});

export const logoutAllDevices = createServerFn({ method: 'POST' }).handler(
  async () => {
    const session = await getSession();
    const data = session.data as SessionData;

    if (data?.userId) {
      await db.sessions.deleteMany({
        where: { userId: data.userId },
      });
    }

    await session.clear();
    throw redirect({ to: '/login' });
  },
);
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

## Preserving Redirect URL

```tsx
import { z } from 'zod';

export const Route = createFileRoute('/login')({
  validateSearch: z.object({
    redirect: z.string().optional(),
  }),
  component: LoginPage,
});

function LoginPage() {
  const { redirect: redirectTo } = Route.useSearch();
  const loginMutation = useMutation({
    mutationFn: loginFn,
    onSuccess: () => {
      navigate({ to: redirectTo ?? '/dashboard' });
    },
  });

  return <LoginForm onSubmit={loginMutation.mutate} />;
}
```

## Forward Headers to External APIs

Server functions originate from the Start server, not the browser. Cookies and auth headers must be forwarded manually:

```ts
import { createServerFn } from '@tanstack/react-start';
import { getRequestHeaders } from '@tanstack/react-start/server';

export const getExternalUser = createServerFn().handler(async () => {
  const headers = getRequestHeaders();

  const response = await fetch('https://api.example.com/me', {
    headers: {
      Cookie: headers.get('cookie') || '',
      Authorization: headers.get('authorization') || '',
    },
  });

  return response.json();
});
```

## createIsomorphicFn for Cookie Maintenance

Use `createIsomorphicFn` to avoid header forwarding for read operations. On the client, the browser attaches cookies automatically:

```ts
import { createIsomorphicFn } from '@tanstack/react-start';
import { getRequestHeaders } from '@tanstack/react-start/server';

const fetchUser = createIsomorphicFn()
  .client(async () => {
    const res = await fetch('/api/user', { credentials: 'include' });
    return res.json();
  })
  .server(async () => {
    const headers = getRequestHeaders();
    const res = await fetch('https://api.example.com/user', {
      headers: { Cookie: headers.get('cookie') || '' },
    });
    return res.json();
  });
```

## Better Auth Integration

Use the `reactStartCookies()` plugin to handle cookie synchronization:

```ts
import { betterAuth } from 'better-auth';
import { reactStartCookies } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [reactStartCookies()],
});
```

Without this plugin, session cookies may not be set or refreshed properly in TanStack Start server functions.

## Security Anti-Patterns

- **Storing auth tokens in localStorage** -- Use HTTP-only cookies
- **Checking auth in component useEffect** -- Use `beforeLoad` on routes to prevent data loading for unauthenticated users
- **Exposing secrets via `process.env` in shared files** -- Use `createServerOnlyFn` for secrets, `VITE_` prefix only for public config
- **Allowing client to set `role` / `isAdmin`** -- Strip privileged fields in validation schema
- **Returning the full user object from session** -- Select only needed fields to avoid leaking sensitive data
