---
title: Data Protection
description: Password hashing with argon2id and bcrypt, AES-256-GCM encryption at rest, and secrets management best practices
tags:
  [encryption, argon2id, bcrypt, aes-256, secrets-management, password-hashing]
---

# Data Protection

## Password Hashing

**Algorithm priority (per OWASP):** argon2id > scrypt > bcrypt > PBKDF2 (FIPS only).

### Argon2id (Preferred)

Memory-hard algorithm resistant to GPU/ASIC attacks. Use argon2id variant for combined protection against side-channel and time-memory tradeoff attacks.

```ts
import argon2 from 'argon2';

// Hash on signup — OWASP minimum: memoryCost 19456 (19 MiB), timeCost 2
const hashedPassword = await argon2.hash(password, {
  type: argon2.argon2id,
  memoryCost: 47104,
  timeCost: 1,
  parallelism: 1,
});
await db.user.create({ email, password: hashedPassword });

// Verify on login
const isValid = await argon2.verify(user.password, password);
if (!isValid) throw new Error('Invalid credentials');
```

### bcrypt (Legacy / Fallback)

Acceptable when argon2id is unavailable. Use cost factor 12 or higher, targeting 250-500ms hash time.

```ts
import bcrypt from 'bcrypt';

const hashedPassword = await bcrypt.hash(password, 12);
await db.user.create({ email, password: hashedPassword });

const isValid = await bcrypt.compare(password, user.password);
if (!isValid) throw new Error('Invalid credentials');
```

Always use async hash/compare to avoid blocking the event loop. Benchmark on production hardware and adjust cost parameters so hashing takes 250ms-1s.

## Encryption at Rest (AES-256-GCM)

```ts
import crypto from 'crypto';

const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY!, 'hex');

function encrypt(text: string) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  const encrypted = Buffer.concat([
    cipher.update(text, 'utf8'),
    cipher.final(),
  ]);
  const authTag = cipher.getAuthTag();
  return {
    iv: iv.toString('hex'),
    encryptedData: encrypted.toString('hex'),
    authTag: authTag.toString('hex'),
  };
}

function decrypt(encrypted: {
  iv: string;
  encryptedData: string;
  authTag: string;
}) {
  const decipher = crypto.createDecipheriv(
    algorithm,
    key,
    Buffer.from(encrypted.iv, 'hex'),
  );
  decipher.setAuthTag(Buffer.from(encrypted.authTag, 'hex'));
  return (
    decipher.update(encrypted.encryptedData, 'hex', 'utf8') +
    decipher.final('utf8')
  );
}
```

## Secrets Management

- Use AWS Secrets Manager, HashiCorp Vault, or Doppler in production
- Environment variables for config (never in code)
- Rotate secrets regularly (90 days)
- Use IAM roles over long-lived credentials
