---
title: Convex Security
description: Identity validation in Convex functions, manual RLS implementation, granular function design, and encryption compliance
tags: [convex, auth, identity, rls, granular-functions, encryption]
---

# Convex Security

Convex functions are public by default. Every function must be explicitly secured using the `ctx.auth` object.

## Identity Validation

Create a helper to validate the user and return their metadata:

```ts
import { type QueryCtx, type MutationCtx } from './_generated/server';

async function getAuthenticatedUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) throw new Error('Unauthorized');
  return identity;
}
```

Every query and mutation handler must call this before accessing data:

```ts
import { query } from './_generated/server';
import { v } from 'convex/values';

export const getSecureData = query({
  args: { id: v.id('items') },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error('Unauthenticated');

    const item = await ctx.db.get(args.id);
    if (!item || item.ownerId !== identity.subject) {
      throw new Error('Unauthorized access attempt logged.');
    }
    return item;
  },
});
```

## Manual RLS in Functions

Since Convex does not have native SQL RLS, implement access control in function handlers:

```ts
import { mutation } from './_generated/server';
import { v } from 'convex/values';

export const updatePost = mutation({
  args: { id: v.id('posts'), content: v.string() },
  handler: async (ctx, args) => {
    const user = await getAuthenticatedUser(ctx);
    const post = await ctx.db.get(args.id);

    if (!post) throw new Error('Post not found');
    if (post.authorId !== user.subject) {
      throw new Error('You are not the author of this post.');
    }

    await ctx.db.patch(args.id, { content: args.content });
  },
});
```

## Granular Functions

Split broad update functions into specific, purpose-built functions:

| Anti-Pattern             | Correct Pattern                                                      |
| ------------------------ | -------------------------------------------------------------------- |
| `updateUser(data: any)`  | `updateUserDisplayName`, `updateUserAvatar`, `updateUserPermissions` |
| `manageResource(action)` | `createResource`, `updateResource`, `deleteResource`                 |

By splitting functions, different authorization rules apply to each specific action. For example, any user can update their display name, but only admins can update permissions.

## Role-Based Access

Custom claims from JWTs are accessed directly on the `UserIdentity` object. The field name depends on your auth provider's JWT template. Nested fields use dot notation in bracket syntax.

```ts
export const adminAction = mutation({
  args: { targetUserId: v.string() },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error('Unauthenticated');

    // Access custom claims directly (field name depends on auth provider)
    // Clerk example: configure "role" in JWT template Claims
    const role = identity.role as string | undefined;
    // Custom JWT example: nested fields use dot notation
    // const role = identity["properties.role"] as string | undefined;
    if (role !== 'admin') {
      throw new Error('Admin access required');
    }

    // Proceed with admin action
  },
});
```

## Encryption and Compliance

Convex encrypts all data at rest and in transit. For high-compliance environments:

| Requirement              | Standard   | Convex Support                |
| ------------------------ | ---------- | ----------------------------- |
| Encryption at rest       | All        | Built-in                      |
| Encryption in transit    | All        | Built-in (TLS)                |
| Audit logs               | HIPAA/SOC2 | Enterprise tier               |
| Infrastructure isolation | HIPAA      | Enterprise tier (dedicated)   |
| Data residency           | GDPR       | Region selection (Enterprise) |

## Security Checklist

- [ ] Every function calls `ctx.auth.getUserIdentity()`
- [ ] Ownership checked before data access or modification
- [ ] Functions are granular (not generic update-all)
- [ ] Role-based access for admin operations
- [ ] No function exposes data without authorization
- [ ] Error messages do not leak internal details
