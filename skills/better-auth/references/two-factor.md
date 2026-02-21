---
title: Two-Factor Authentication
description: TOTP authenticator apps, email/SMS OTP, backup codes, trusted devices, session flow during 2FA, and security considerations
tags: [two-factor, totp, otp, backup-codes, trusted-devices, 2fa, mfa]
---

# Two-Factor Authentication

## Setup

Server:

```ts
import { betterAuth } from 'better-auth';
import { twoFactor } from 'better-auth/plugins';

export const auth = betterAuth({
  appName: 'My App',
  plugins: [
    twoFactor({
      issuer: 'My App',
    }),
  ],
});
```

Run `npx @better-auth/cli@latest migrate` after adding the plugin.

Client:

```ts
import { createAuthClient } from 'better-auth/client';
import { twoFactorClient } from 'better-auth/client/plugins';

export const authClient = createAuthClient({
  plugins: [
    twoFactorClient({
      onTwoFactorRedirect() {
        window.location.href = '/2fa';
      },
    }),
  ],
});
```

## Enabling 2FA for Users

```ts
const { data, error } = await authClient.twoFactor.enable({ password });
// data.totpURI — generate QR code from this
// data.backupCodes — show to user for safekeeping
```

`twoFactorEnabled` stays `false` until the user verifies their first TOTP code. To skip initial verification (not recommended):

```ts
twoFactor({ skipVerificationOnEnable: true });
```

## TOTP (Authenticator App)

### QR Code Display

```tsx
import QRCode from 'react-qr-code';

function TotpSetup({ totpURI }: { totpURI: string }) {
  return <QRCode value={totpURI} />;
}
```

### Verifying Codes

Better Auth accepts codes from one period before and after current time (clock skew tolerance):

```ts
const { data, error } = await authClient.twoFactor.verifyTotp({
  code,
  trustDevice: true, // Remember this device for 30 days
});
```

### Configuration

```ts
twoFactor({
  totpOptions: {
    digits: 6, // 6 or 8 (default: 6)
    period: 30, // Code validity in seconds (default: 30)
  },
});
```

## OTP (Email/SMS)

### Configuring Delivery

```ts
twoFactor({
  otpOptions: {
    sendOTP: async ({ user, otp }, ctx) => {
      await sendEmail({
        to: user.email,
        subject: 'Your verification code',
        text: `Your code is: ${otp}`,
      });
    },
    period: 5, // Minutes (default: 3)
    digits: 6,
    allowedAttempts: 5, // Max attempts (default: 5)
  },
});
```

### Sending and Verifying

```ts
await authClient.twoFactor.sendOtp();

const { data, error } = await authClient.twoFactor.verifyOtp({
  code,
  trustDevice: true,
});
```

### OTP Storage Security

```ts
twoFactor({
  otpOptions: {
    storeOTP: 'encrypted', // "plain" | "encrypted" | "hashed"
  },
});
```

Custom encryption:

```ts
twoFactor({
  otpOptions: {
    storeOTP: {
      encrypt: async (token) => myEncrypt(token),
      decrypt: async (token) => myDecrypt(token),
    },
  },
});
```

## Backup Codes

Generated automatically when 2FA is enabled. Always show to users at enable time.

### Regenerating

```ts
const { data } = await authClient.twoFactor.generateBackupCodes({
  password,
});
// data.backupCodes — invalidates all previous codes
```

### Recovery

```ts
const { data } = await authClient.twoFactor.verifyBackupCode({
  code,
  trustDevice: true,
});
```

Each code is single-use — deleted after successful verification.

### Configuration

```ts
twoFactor({
  backupCodeOptions: {
    amount: 10, // Default: 10
    length: 10, // Default: 10
    storeBackupCodes: 'encrypted', // "plain" | "encrypted"
  },
});
```

## Sign-In Flow with 2FA

### Client-Side Detection

```ts
const { data, error } = await authClient.signIn.email(
  { email, password },
  {
    onSuccess(context) {
      if (context.data.twoFactorRedirect) {
        window.location.href = '/2fa';
      }
    },
  },
);
```

### Server-Side Detection

```ts
const response = await auth.api.signInEmail({
  body: { email: 'user@example.com', password: 'password' },
});

if ('twoFactorRedirect' in response) {
  // Handle 2FA verification
}
```

### Session Flow During 2FA

1. User signs in with credentials
2. Session cookie is removed (not yet authenticated)
3. Temporary two-factor cookie set (default: 10-minute expiration)
4. User verifies via TOTP, OTP, or backup code
5. Full session cookie created on success

```ts
twoFactor({ twoFactorCookieMaxAge: 600 }); // 10 minutes (default)
```

## Trusted Devices

```ts
await authClient.twoFactor.verifyTotp({
  code: '123456',
  trustDevice: true,
});

twoFactor({
  trustDeviceMaxAge: 30 * 24 * 60 * 60, // 30 days (default)
});
```

Trust period refreshes on each successful sign-in within the window.

## Disabling 2FA

```ts
const { data } = await authClient.twoFactor.disable({ password });
// Trusted device records are revoked on disable
```

## Security Considerations

- **Rate limiting**: Built-in 3 requests per 10 seconds on all 2FA endpoints. OTP has additional attempt limiting via `allowedAttempts`.
- **Encryption at rest**: TOTP secrets encrypted with auth secret (symmetric). Backup codes encrypted by default. OTP storage is configurable.
- **Constant-time comparison**: OTP verification uses constant-time comparison to prevent timing attacks.
- **Credential accounts only**: 2FA only applies to credential-based accounts. Social auth accounts are assumed to handle 2FA through the provider.

## Complete Configuration

```ts
import { betterAuth } from 'better-auth';
import { twoFactor } from 'better-auth/plugins';

export const auth = betterAuth({
  appName: 'My App',
  plugins: [
    twoFactor({
      issuer: 'My App',
      totpOptions: { digits: 6, period: 30 },
      otpOptions: {
        sendOTP: async ({ user, otp }) => {
          await sendEmail({
            to: user.email,
            subject: 'Your verification code',
            text: `Your code is: ${otp}`,
          });
        },
        period: 5,
        allowedAttempts: 5,
        storeOTP: 'encrypted',
      },
      backupCodeOptions: {
        amount: 10,
        length: 10,
        storeBackupCodes: 'encrypted',
      },
      twoFactorCookieMaxAge: 600,
      trustDeviceMaxAge: 30 * 24 * 60 * 60,
    }),
  ],
});
```
