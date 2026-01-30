---
title: Authentication and Authorization
description: JWT token creation and verification, session-based auth, OAuth 2.0/OIDC, RBAC middleware, ABAC patterns, and IDOR protection
tags: [authentication, authorization, jwt, rbac, abac, idor, oauth, sessions]
---

# Authentication and Authorization

## JWT (JSON Web Tokens)

When: Stateless APIs, mobile apps, microservices. Use RS256 (not HS256), short expiry (15min access, 7d refresh). Store in httpOnly cookies.

```ts
import { SignJWT, jwtVerify } from 'jose';

const secret = new TextEncoder().encode(process.env.JWT_SECRET!);

export async function createToken(userId: string) {
  return await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('15m')
    .sign(secret);
}

export async function verifyToken(token: string) {
  const { payload } = await jwtVerify(token, secret);
  return payload;
}
```

## Session-Based Auth

Server stores session ID in encrypted cookie (HttpOnly, Secure, SameSite=Strict).

## OAuth 2.0 / OIDC

Use established libraries (NextAuth.js, Auth0). Validate state parameter, use PKCE for mobile.

## RBAC (Role-Based Access Control)

```ts
enum Role {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

function requireRole(allowedRoles: Role[]) {
  return (req, res, next) => {
    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

app.delete('/api/users/:id', requireRole([Role.ADMIN]), deleteUser);
```

## ABAC (Attribute-Based)

More granular, e.g., user can edit resource only if they created it.

## IDOR Protection

```ts
const doc = await db.document.findFirst({
  where: {
    id: req.params.id,
    userId: req.user.id,
  },
});
if (!doc) return res.status(404).json({ error: 'Not found' });
```
