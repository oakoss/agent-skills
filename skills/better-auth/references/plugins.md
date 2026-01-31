---
title: Plugins and Social Auth
description: Plugin import patterns, OAuth 2.1 provider setup, admin plugin with RBAC, JWT key rotation, and social provider scope reference
tags: [plugins, oauth, admin, rbac, jwt, social-auth, two-factor]
---

# Plugins and Social Auth

**Import from dedicated paths for tree-shaking:**

```ts
import { twoFactor } from 'better-auth/plugins/two-factor';
// NOT from "better-auth/plugins"
```

Client plugins go in `createAuthClient({ plugins: [...] })`.

## OAuth 2.1 Provider Plugin (v1.4.9+)

Build your own OAuth provider for MCP servers, third-party apps, or API access. Requires separate package `@better-auth/oauth-provider`:

```ts
import { oauthProvider } from '@better-auth/oauth-provider';
import { jwt } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    jwt(),
    oauthProvider({
      accessTokenExpiresIn: 3600,
      refreshTokenExpiresIn: 2592000,
      authorizationCodeExpiresIn: 600,
    }),
  ],
});
```

OAuth 2.1 compliant: PKCE mandatory, S256 only, no implicit flow. Supports `authorization_code`, `refresh_token`, `client_credentials` grant types.

## Admin Plugin with RBAC

```ts
import { admin } from 'better-auth/plugins';
import { createAccessControl } from 'better-auth/plugins/access';

const ac = createAccessControl({
  user: ['create', 'read', 'update', 'delete', 'ban', 'impersonate'],
  project: ['create', 'read', 'update', 'delete', 'share'],
} as const);

admin({
  ac,
  roles: {
    support: ac.newRole({ user: ['read', 'ban'], project: ['read'] }),
    manager: ac.newRole({
      user: ['read', 'update'],
      project: ['create', 'read', 'update', 'delete'],
    }),
  },
  allowImpersonatingAdmins: false, // Default since v1.4.6
});
```

## JWT Key Rotation (v1.4.0+)

```ts
import { jwt } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [
    jwt({
      keyRotation: {
        enabled: true,
        rotationInterval: 60 * 60 * 24 * 30,
        keepPreviousKeys: 3,
      },
      algorithm: 'RS256',
      exposeJWKS: true, // /api/auth/jwks
    }),
  ],
});
```

## Social Provider Scopes

| Provider  | Scope        | Returns                        |
| --------- | ------------ | ------------------------------ |
| Google    | `openid`     | User ID only                   |
| Google    | `email`      | Email, email_verified          |
| Google    | `profile`    | Name, avatar, locale           |
| GitHub    | `user:email` | Email (may be private)         |
| GitHub    | `read:user`  | Name, avatar, profile URL, bio |
| Microsoft | `User.Read`  | Full profile from Graph API    |
| Discord   | `identify`   | Username, avatar               |
| Discord   | `email`      | Email address                  |
| Apple     | `name`       | First/last (first auth only)   |
| Apple     | `email`      | Email or relay address         |

```ts
socialProviders: {
  google: {
    clientId: env.GOOGLE_CLIENT_ID,
    clientSecret: env.GOOGLE_CLIENT_SECRET,
    scope: ['openid', 'email', 'profile'],
  },
  github: {
    clientId: env.GITHUB_CLIENT_ID,
    clientSecret: env.GITHUB_CLIENT_SECRET,
    scope: ['user:email', 'read:user'],
  },
}
```
