---
title: Data Protection
description: Password hashing with bcrypt, AES-256-GCM encryption at rest, and secrets management best practices
tags: [encryption, bcrypt, aes-256, secrets-management, password-hashing]
---

# Data Protection

## Password Hashing

```ts
import bcrypt from 'bcrypt';

// Hash on signup
const hashedPassword = await bcrypt.hash(password, 12);
await db.user.create({ email, password: hashedPassword });

// Verify on login
const isValid = await bcrypt.compare(password, user.password);
if (!isValid) throw new Error('Invalid credentials');
```

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
