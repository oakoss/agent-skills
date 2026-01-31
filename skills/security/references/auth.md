---
title: Authentication and Authorization
description: JWT token creation and verification, session-based auth, OAuth 2.0/OIDC, RBAC middleware, ABAC patterns, and IDOR protection
tags: [authentication, authorization, jwt, rbac, abac, idor, oauth, sessions]
---

# Authentication and Authorization

## JWT (JSON Web Tokens)

When: Stateless APIs, mobile apps, microservices. Use asymmetric algorithms (EdDSA preferred, ES256 widely supported, RS256 for legacy compatibility). Never use HS256 in distributed systems. Short expiry (15min access, 7d refresh). Store in httpOnly cookies.

**Algorithm priority:** EdDSA (best security + performance) > ES256 (modern + widely supported) > RS256 (maximum compatibility). Always whitelist allowed algorithms in verification to prevent algorithm confusion attacks.

```ts
import { SignJWT, jwtVerify, importPKCS8, importSPKI } from 'jose';

const privateKey = await importPKCS8(process.env.JWT_PRIVATE_KEY!, 'ES256');
const publicKey = await importSPKI(process.env.JWT_PUBLIC_KEY!, 'ES256');

export async function createToken(userId: string) {
  return await new SignJWT({ userId })
    .setProtectedHeader({ alg: 'ES256' })
    .setIssuedAt()
    .setExpirationTime('15m')
    .sign(privateKey);
}

export async function verifyToken(token: string) {
  const { payload } = await jwtVerify(token, publicKey, {
    algorithms: ['ES256'],
  });
  return payload;
}
```

## Token Refresh Pattern

```ts
async function refreshAccessToken(refreshToken: string) {
  const { payload } = await jwtVerify(refreshToken, publicKey, {
    algorithms: ['ES256'],
  });

  const newAccessToken = await createToken(payload.userId as string);

  return { accessToken: newAccessToken };
}
```

Rotate refresh tokens on each use (one-time use). Store refresh token family to detect reuse attacks and revoke the entire family if a used token is presented again.

## Session-Based Auth

Server stores session ID in encrypted cookie (HttpOnly, Secure, SameSite=Strict). Regenerate session ID after login to prevent session fixation.

## OAuth 2.0 / OIDC

Use established libraries (NextAuth.js / Auth.js, Auth0). Validate state parameter. Use PKCE (Proof Key for Code Exchange) for all clients, not just mobile -- PKCE is now recommended for all OAuth 2.0 flows per RFC 9126.

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
