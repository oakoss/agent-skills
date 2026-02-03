---
title: Input Validation
description: SQL injection prevention with parameterized queries, XSS prevention, Zod schema validation for user input, and file upload security
tags: [input-validation, sql-injection, xss, zod, file-upload, sanitization]
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

Use React's default escaping. When rendering raw HTML is unavoidable, sanitize with DOMPurify before rendering.

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
