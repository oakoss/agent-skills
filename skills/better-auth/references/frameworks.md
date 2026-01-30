---
title: Framework Integration
description: TanStack Start setup with reactStartCookies, Expo/React Native with SecureStore, client imports, type safety, and server-side API usage
tags: [tanstack-start, expo, react-native, client, type-safety, server-api]
---

# Framework Integration

## TanStack Start

**CRITICAL**: TanStack Start requires the `reactStartCookies` plugin for cookie handling.

```ts
import { betterAuth } from 'better-auth';
import { reactStartCookies } from 'better-auth/react-start';

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: 'sqlite' }),
  plugins: [
    twoFactor(),
    organization(),
    reactStartCookies(), // MUST be LAST plugin
  ],
});
```

**API Route Setup** (`/src/routes/api/auth/$.ts`):

```ts
import { auth } from '@/lib/auth';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/api/auth/$')({
  server: {
    handlers: {
      GET: ({ request }) => auth.handler(request),
      POST: ({ request }) => auth.handler(request),
    },
  },
});
```

**Session Nullability**: `useSession()` always returns an object. Check `session?.user`, not just `session`:

```ts
const { data: session } = authClient.useSession();
if (session?.user) {
  /* logged in */
}
```

## Expo/React Native

```ts
import { expoClient } from '@better-auth/expo';
import * as SecureStore from 'expo-secure-store';

const authClient = createAuthClient({
  baseURL: 'https://api.example.com',
  plugins: [expoClient({ storage: SecureStore })],
});

// OAuth with deep linking
await authClient.signIn.social({
  provider: 'google',
  callbackURL: 'myapp://auth/callback',
});

// Server trustedOrigins (development)
trustedOrigins: ['exp://**', 'myapp://'];
```

## Client Imports

```ts
// Framework-specific
import { createAuthClient } from 'better-auth/react'; // or /vue, /svelte, /solid
import { createAuthClient } from 'better-auth/client'; // vanilla

// Key methods
authClient.signUp.email({ email, password, name });
authClient.signIn.email({ email, password });
authClient.signIn.social({ provider: 'google', callbackURL: '/dashboard' });
authClient.signOut();
authClient.useSession(); // React hook
authClient.getSession(); // Imperative
```

## Type Safety

```ts
// Infer types from auth instance
type Session = typeof auth.$Infer.Session;
type User = typeof auth.$Infer.Session.user;

// Separate client/server projects
const client = createAuthClient<typeof auth>();
```

## Server-Side API (`auth.api.*`)

Every HTTP endpoint has a corresponding server-side method. Use for middleware, background jobs, admin operations.

```ts
// Session
const session = await auth.api.getSession({ headers: request.headers });

// User management
await auth.api.signUpEmail({
  body: { email, password, name },
  headers: request.headers,
});

// Organization
const org = await auth.api.createOrganization({
  body: { name: 'Acme', slug: 'acme' },
  headers: request.headers,
});

// Admin (requires user.role === 'admin' in DB)
const users = await auth.api.listUsers({
  query: { search: 'john', limit: 10, offset: 0 },
  headers: request.headers,
});
```

80+ auto-generated endpoints at `/api/auth/*`. Use the OpenAPI plugin for interactive docs.
