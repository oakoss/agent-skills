---
title: Email and Password
description: Email verification, password reset flows with timing attack prevention, password hashing (scrypt, argon2), token security, and callback URLs
tags:
  [
    email,
    password,
    verification,
    reset,
    hashing,
    scrypt,
    argon2,
    token-security,
  ]
---

# Email and Password

## Email Verification

### Configuration

```ts
import { betterAuth } from 'better-auth';

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url, token }, request) => {
      await sendEmail({
        to: user.email,
        subject: 'Verify your email address',
        text: `Click the link to verify your email: ${url}`,
      });
    },
    sendOnSignUp: true,
    autoSignInAfterVerification: true,
    expiresIn: 3600,
  },
});
```

`requireEmailVerification` only applies to email/password sign-ins. Unverified users receive a new verification email on each sign-in attempt.

The `url` parameter contains the full verification link. The `token` is available for building custom verification URLs.

### Callback URLs

Always use absolute URLs (including the origin) for callback URLs:

```ts
const { data, error } = await authClient.signUp.email({
  email,
  password,
  name,
  callbackURL: 'https://example.com/callback',
});
```

## Password Reset

### Configuration

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    sendResetPassword: async ({ user, url, token }, request) => {
      await sendEmail({
        to: user.email,
        subject: 'Reset your password',
        text: `Click the link to reset your password: ${url}`,
      });
    },
    resetPasswordTokenExpiresIn: 60 * 60, // 1 hour (default)
    revokeSessionsOnPasswordReset: true,
    onPasswordReset: async ({ user }, request) => {
      console.log(`Password for ${user.email} has been reset`);
    },
  },
});
```

### Sending Reset Requests

Server-side:

```ts
const data = await auth.api.requestPasswordReset({
  body: {
    email: 'user@example.com',
    redirectTo: 'https://example.com/reset-password',
  },
});
```

Client-side:

```ts
const { data, error } = await authClient.requestPasswordReset({
  email: 'user@example.com',
  redirectTo: 'https://example.com/reset-password',
});
```

### Token Security

- Cryptographically random tokens via `generateId(24)` (24-character alphanumeric)
- Expire after 1 hour by default (configure with `resetPasswordTokenExpiresIn` in seconds)
- Single-use: tokens deleted immediately after successful reset
- `redirectTo` validated against `trustedOrigins` — malicious URLs rejected with 403

### Timing Attack Prevention

Better Auth prevents user enumeration on password reset:

1. Background email sending via `runInBackgroundOrAwait` prevents response-time enumeration
2. Dummy token generation + database lookup when user not found
3. Constant response: "If this email exists in our system, check your email for the reset link"

On serverless platforms, configure background tasks explicitly:

```ts
export const auth = betterAuth({
  advanced: {
    backgroundTasks: {
      handler: (promise) => {
        waitUntil(promise);
      },
    },
  },
});
```

## Password Requirements

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 12, // Default: 8
    maxPasswordLength: 256, // Default: 128
  },
});
```

## Password Hashing

Better Auth uses **scrypt** by default:

- Slow and memory-intensive (resistance to brute-force)
- Natively supported in Node.js (no external dependencies)
- OWASP-recommended when Argon2id is not available

### Custom Hashing (Argon2id)

```ts
import { betterAuth } from 'better-auth';
import { hash, verify, type Options } from '@node-rs/argon2';

const argon2Options: Options = {
  memoryCost: 65536, // 64 MiB
  timeCost: 3,
  parallelism: 4,
  outputLen: 32,
  algorithm: 2, // Argon2id
};

export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    password: {
      hash: (password) => hash(password, argon2Options),
      verify: ({ password, hash: storedHash }) =>
        verify(storedHash, password, argon2Options),
    },
  },
});
```

If you switch algorithms on an existing system, users with old-algorithm passwords cannot sign in. Plan a migration strategy (e.g., re-hash on next successful login).

## Session Revocation on Reset

```ts
export const auth = betterAuth({
  emailAndPassword: {
    enabled: true,
    revokeSessionsOnPasswordReset: true,
  },
});
```

When enabled, all active sessions are invalidated after a successful password reset, forcing re-authentication on all devices.
