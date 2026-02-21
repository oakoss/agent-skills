---
title: Input Validation
description: SQL injection, XSS, command injection, path traversal prevention, Zod schema validation, file upload security, and output encoding
tags:
  [
    input-validation,
    sql-injection,
    xss,
    command-injection,
    path-traversal,
    zod,
    file-upload,
    sanitization,
  ]
---

# Input Validation

## Prevent SQL Injection

```ts
// BAD: string interpolation
const query = `SELECT * FROM users WHERE email = '${userInput}'`;

// GOOD: parameterized queries
const query = 'SELECT * FROM users WHERE email = ?';
db.query(query, [userInput]);

// GOOD: ORM handles it
const user = await prisma.user.findUnique({ where: { email: userInput } });
```

## Prevent XSS

React escapes by default. When rendering raw HTML is unavoidable, sanitize with DOMPurify:

```ts
import DOMPurify from 'isomorphic-dompurify';

const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'p', 'a'],
  ALLOWED_ATTR: ['href'],
});
```

Set Content Security Policy headers to limit damage from any bypass. See the [Secure Configuration](secure-config.md) reference.

## Prevent Command Injection

Never pass user input to shell commands. Use argument arrays instead of string interpolation:

```ts
import { execFile } from 'child_process';

// BAD: shell injection via string
exec(`convert ${userFilename} output.png`);

// GOOD: argument array, no shell interpretation
execFile('convert', [userFilename, 'output.png']);
```

If shell execution is unavoidable, validate input against a strict allowlist:

```ts
const ALLOWED_FORMATS = ['png', 'jpg', 'webp'];
if (!ALLOWED_FORMATS.includes(format)) {
  throw new Error('Invalid format');
}
```

## Prevent Path Traversal

```ts
import path from 'path';

function safePath(baseDir: string, userPath: string): string {
  const resolved = path.resolve(baseDir, userPath);
  if (!resolved.startsWith(path.resolve(baseDir))) {
    throw new Error('Path traversal detected');
  }
  return resolved;
}

// Usage
const filePath = safePath('/uploads', req.params.filename);
```

Never use user input directly in `fs.readFile`, `fs.writeFile`, or similar calls without resolving and validating the resulting path.

## Schema Validation with Zod

```ts
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email().max(255),
  password: z
    .string()
    .min(8)
    .max(100)
    .regex(/[A-Z]/, 'Needs uppercase')
    .regex(/[a-z]/, 'Needs lowercase')
    .regex(/[0-9]/, 'Needs number'),
  age: z.number().int().min(13).max(120),
});

const result = UserSchema.safeParse(req.body);
if (!result.success) {
  return res.status(400).json({ errors: result.error.issues });
}
```

Validate all user input at system boundaries. Client-side validation is UX; server-side validation is security.

## File Upload Security

```ts
const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.mimetype)) {
      return cb(new Error('Invalid file type'));
    }
    cb(null, true);
  },
});

const filename = crypto.randomUUID() + path.extname(file.originalname);
```

Validate both MIME type and file extension. Generate random filenames to prevent directory traversal. Store uploads outside the web root or use a storage service (S3, R2).

## Output Encoding

Encode output based on context to prevent injection:

| Context    | Encoding                                     |
| ---------- | -------------------------------------------- |
| HTML body  | HTML entity encoding (React default)         |
| HTML attr  | Attribute encoding, quote wrapping           |
| JavaScript | JSON.stringify or template literal escaping  |
| URL param  | encodeURIComponent                           |
| SQL        | Parameterized queries (never string concat)  |
| Shell      | Argument arrays (never string interpolation) |
