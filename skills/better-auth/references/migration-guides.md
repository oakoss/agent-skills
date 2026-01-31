---
title: Migration Guides
description: Migrate from NextAuth/Auth.js, Clerk, or Supabase Auth to Better Auth with database schema mappings, session strategies, and client-side changes
tags: [migration, nextauth, authjs, clerk, supabase, database, schema, session]
---

## Migrating from Auth.js (NextAuth)

### Schema Differences

Better Auth and Auth.js share a similar schema structure but differ in field names and types:

**User table:**

| Auth.js Field      | Better Auth Field  | Notes                                 |
| ------------------ | ------------------ | ------------------------------------- |
| `name` (optional)  | `name` (required)  | Must backfill nulls before migration  |
| `email` (optional) | `email` (required) | Must backfill nulls before migration  |
| `emailVerified`    | `emailVerified`    | Changes from `timestamp` to `boolean` |
| `image`            | `image`            | Same                                  |
| N/A                | `createdAt`        | New required field                    |
| N/A                | `updatedAt`        | New required field                    |

**Session table:**

| Auth.js Field  | Better Auth Field | Notes              |
| -------------- | ----------------- | ------------------ |
| `sessionToken` | `token`           | Renamed            |
| `expires`      | `expiresAt`       | Renamed            |
| `userId`       | `userId`          | Same               |
| N/A            | `ipAddress`       | New optional field |
| N/A            | `userAgent`       | New optional field |
| N/A            | `createdAt`       | New required field |
| N/A            | `updatedAt`       | New required field |

**Account table:**

| Auth.js Field         | Better Auth Field      | Notes                             |
| --------------------- | ---------------------- | --------------------------------- |
| `provider`            | `providerId`           | Renamed                           |
| `providerAccountId`   | `accountId`            | Renamed                           |
| `refresh_token`       | `refreshToken`         | camelCase                         |
| `access_token`        | `accessToken`          | camelCase                         |
| `expires_at` (number) | `accessTokenExpiresAt` | Renamed, changes to `Date`        |
| N/A                   | `password`             | New field for credential accounts |

### Database Migration Script

```ts
import { sql } from 'drizzle-orm';

async function migrateFromAuthJs(db: ReturnType<typeof drizzle>) {
  await db.transaction(async (tx) => {
    await tx.run(sql`
      ALTER TABLE user ADD COLUMN "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    `);
    await tx.run(sql`
      ALTER TABLE user ADD COLUMN "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    `);
    await tx.run(sql`
      UPDATE user SET name = email WHERE name IS NULL;
    `);
    await tx.run(sql`
      UPDATE user SET "emailVerified" = CASE
        WHEN "emailVerified" IS NOT NULL THEN 1
        ELSE 0
      END;
    `);

    await tx.run(sql`
      ALTER TABLE session RENAME COLUMN "sessionToken" TO "token";
    `);
    await tx.run(sql`
      ALTER TABLE session RENAME COLUMN "expires" TO "expiresAt";
    `);

    await tx.run(sql`
      ALTER TABLE account RENAME COLUMN "provider" TO "providerId";
    `);
    await tx.run(sql`
      ALTER TABLE account RENAME COLUMN "providerAccountId" TO "accountId";
    `);
  });
}
```

### Server Configuration Change

```ts
// Before (Auth.js)
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GoogleProvider({ clientId: '...', clientSecret: '...' })],
});

// After (Better Auth)
import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  socialProviders: {
    google: { clientId: '...', clientSecret: '...' },
  },
});
```

### Route Handler Change

```ts
// Before: app/api/auth/[...nextauth]/route.ts
import { handlers } from '@/lib/auth';
export const { GET, POST } = handlers;

// After: app/api/auth/[...all]/route.ts
import { auth } from '@/lib/auth';
import { toNextJsHandler } from 'better-auth/next-js';
export const { GET, POST } = toNextJsHandler(auth);
```

### Client-Side Hooks

```ts
// Before (Auth.js)
import { useSession, signIn, signOut } from 'next-auth/react';

const { data: session, status } = useSession();
await signIn('github');
await signOut();

// After (Better Auth)
import { authClient } from '@/lib/auth-client';

const { data: session, isPending } = authClient.useSession();
await authClient.signIn.social({ provider: 'github' });
await authClient.signOut();
```

### Server-Side Session

```ts
// Before (Auth.js)
import { auth } from '@/lib/auth';
const session = await auth();

// After (Better Auth)
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';
const session = await auth.api.getSession({ headers: await headers() });
```

## Migrating from Clerk

### Key Differences

| Aspect        | Clerk                   | Better Auth              |
| ------------- | ----------------------- | ------------------------ |
| Hosting       | Third-party managed     | Self-hosted              |
| Cost          | Monthly subscription    | Free (open source)       |
| User data     | Stored on Clerk servers | Stored in your database  |
| Customization | Limited by Clerk API    | Full control via plugins |

### Migration Steps

1. **Export user data** from Clerk Dashboard (CSV) or via Clerk API
2. **Run Better Auth CLI** to create database tables:

```bash
npx @better-auth/cli@latest migrate
```

3. **Import users** with plugin-aware field mapping:

```ts
import { auth } from '@/lib/auth';

async function migrateFromClerk(clerkUsers: ClerkExportRow[]) {
  const ctx = await auth.$context;

  for (const user of clerkUsers) {
    await ctx.adapter.create({
      model: 'user',
      data: {
        id: user.id,
        email: user.primary_email_address,
        emailVerified: user.verified_email_addresses.length > 0,
        name: `${user.first_name} ${user.last_name}`.trim(),
        image: user.image_url,
        createdAt: new Date(user.created_at),
        updatedAt: new Date(user.updated_at),
      },
      forceAllowId: true,
    });

    if (user.password_digest) {
      await ctx.adapter.create({
        model: 'account',
        data: {
          userId: user.id,
          providerId: 'credential',
          accountId: user.id,
          password: user.password_digest,
        },
      });
    }
  }
}
```

4. **Replace Clerk client SDK**:

```ts
// Before (Clerk)
import { useUser, useAuth } from '@clerk/nextjs';
const { user } = useUser();
const { signOut } = useAuth();

// After (Better Auth)
import { authClient } from '@/lib/auth-client';
const { data: session } = authClient.useSession();
const user = session?.user;
await authClient.signOut();
```

5. **Replace middleware** for route protection:

```ts
// Before (Clerk)
import { clerkMiddleware } from '@clerk/nextjs/server';
export default clerkMiddleware();

// After (Better Auth) - Use per-route checks instead of middleware
import { auth } from '@/lib/auth';
import { headers } from 'next/headers';

const session = await auth.api.getSession({ headers: await headers() });
if (!session) redirect('/login');
```

6. **Reconfigure OAuth providers** with the same OAuth app credentials

## Migrating from Supabase Auth

### Migration Script Pattern

Better Auth provides an official migration script pattern for Supabase:

```ts
import { generateId } from 'better-auth';
import { Pool } from 'pg';
import { auth } from '@/lib/auth';

const CONFIG = {
  batchSize: 5000,
  resumeFromId: null as string | null,
  tempEmailDomain: 'temp.better-auth.com',
};

async function migrateFromSupabase() {
  const pool = new Pool({ connectionString: process.env.SUPABASE_DB_URL });
  const ctx = await auth.$context;

  let lastId = CONFIG.resumeFromId;
  let hasMore = true;

  while (hasMore) {
    const query = lastId
      ? `SELECT * FROM auth.users WHERE id > $1 ORDER BY id LIMIT $2`
      : `SELECT * FROM auth.users ORDER BY id LIMIT $1`;
    const params = lastId ? [lastId, CONFIG.batchSize] : [CONFIG.batchSize];

    const { rows: users } = await pool.query(query, params);
    if (users.length === 0) {
      hasMore = false;
      break;
    }

    for (const supaUser of users) {
      const email =
        supaUser.email ?? `${supaUser.phone}@${CONFIG.tempEmailDomain}`;

      await ctx.adapter.create({
        model: 'user',
        data: {
          id: supaUser.id,
          email,
          emailVerified: !!supaUser.email_confirmed_at,
          name: supaUser.raw_user_meta_data?.full_name ?? email,
          image: supaUser.raw_user_meta_data?.avatar_url,
          createdAt: new Date(supaUser.created_at),
          updatedAt: new Date(supaUser.updated_at ?? supaUser.created_at),
        },
        forceAllowId: true,
      });

      if (supaUser.encrypted_password) {
        await ctx.adapter.create({
          model: 'account',
          data: {
            id: generateId(),
            userId: supaUser.id,
            providerId: 'credential',
            accountId: supaUser.id,
            password: supaUser.encrypted_password,
          },
        });
      }
    }

    lastId = users[users.length - 1].id;
  }

  await pool.end();
}
```

### Key Differences from Supabase Auth

| Aspect             | Supabase Auth        | Better Auth               |
| ------------------ | -------------------- | ------------------------- |
| Session storage    | JWT in Supabase      | Database or stateless     |
| User metadata      | `raw_user_meta_data` | `additionalFields` config |
| Phone-only users   | Supported natively   | Need `phoneNumber` plugin |
| Email confirmation | Timestamp-based      | Boolean-based             |

## Database Migration Patterns

### Using Better Auth CLI

The recommended approach for initial schema setup:

```bash
npx @better-auth/cli@latest generate
npx @better-auth/cli@latest migrate
```

### Using Drizzle Kit (Recommended for D1/SQLite)

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
```

### Custom Table Name Mapping

If your existing tables use different names, map them in config:

```ts
export const auth = betterAuth({
  user: {
    modelName: 'users',
    fields: {
      name: 'full_name',
      email: 'email_address',
    },
  },
  session: {
    modelName: 'user_sessions',
    fields: {
      userId: 'user_id',
    },
  },
});
```

## Session Migration Strategies

### Database Sessions (Auth.js/Clerk to Better Auth)

Existing sessions will be invalidated after migration. Users must re-authenticate. Plan for:

1. Schedule migration during low-traffic window
2. Migrate user and account data
3. Drop old session table (or rename)
4. Run `@better-auth/cli migrate` to create new session table
5. Users re-authenticate on next visit

### JWT Sessions (Auth.js to Better Auth)

If migrating from Auth.js JWT strategy:

- Old JWTs become invalid immediately (different signing secret)
- No session table to migrate
- Users re-authenticate on next visit
- Consider a grace period with both auth systems running in parallel

## Common Migration Pitfalls

| Pitfall                                   | Solution                                                          |
| ----------------------------------------- | ----------------------------------------------------------------- |
| Null `name`/`email` from Auth.js          | Backfill required fields before migration                         |
| `emailVerified` type mismatch             | Convert timestamp to boolean (`IS NOT NULL` check)                |
| Password hashes incompatible              | Better Auth accepts bcrypt hashes from most providers             |
| Phone-only Supabase users have no email   | Assign temporary emails or enable `phoneNumber` plugin            |
| Clerk user IDs are prefixed (`user_xxx`)  | Use `forceAllowId: true` to preserve original IDs                 |
| D1 lacks `ALTER TABLE DROP COLUMN`        | Use fresh migration pattern (drop and recreate tables)            |
| Missing OAuth account records             | Migrate both `user` and `account` tables; OAuth needs `accountId` |
| Old sessions still active after migration | Invalidate all sessions; users must re-authenticate               |
