---
title: Runtime APIs
description: Bun.serve() HTTP server, Bun.file() I/O, Bun.write(), SQLite database, Bun.password hashing, and utility functions
tags:
  [
    Bun.serve,
    Bun.file,
    Bun.write,
    SQLite,
    Bun.password,
    Bun.sleep,
    Bun.hash,
    HTTP,
    server,
    file-io,
  ]
---

# Runtime APIs

## HTTP Server with Bun.serve()

### Basic Server with Routes

```ts
const server = Bun.serve({
  port: 3000,

  routes: {
    '/api/health': new Response('OK'),

    '/api/users/:id': (req) => {
      return Response.json({ id: req.params.id });
    },

    '/api/users': {
      GET: () => Response.json([]),
      POST: async (req) => {
        const body = await req.json();
        return Response.json(body, { status: 201 });
      },
    },

    '/favicon.ico': Bun.file('./public/favicon.ico'),

    '/api/*': Response.json({ error: 'Not found' }, { status: 404 }),
  },

  fetch(req) {
    return new Response('Not Found', { status: 404 });
  },

  error(error) {
    console.error(error);
    return new Response('Internal Server Error', { status: 500 });
  },
});

console.log(`Server running at ${server.url}`);
```

### Route Features

- **Static responses**: Map path to `new Response()` or `Response.json()`
- **Dynamic routes**: Use `:param` syntax, access via `req.params.id`
- **Per-method handlers**: Object with `GET`, `POST`, `PUT`, `DELETE` keys
- **Wildcard routes**: Use `*` for catch-all matching
- **File serving**: Map path to `Bun.file()` for static assets
- **Redirects**: `Response.redirect("/new-path")`

### Hot Reload and Shutdown

```ts
server.reload({
  routes: {
    '/api/version': () => Response.json({ version: '2.0.0' }),
  },
});

await server.stop();
```

### WebSocket Support

```ts
Bun.serve({
  fetch(req, server) {
    if (server.upgrade(req)) return;
    return new Response('Not a WebSocket request', { status: 400 });
  },

  websocket: {
    open(ws) {
      ws.subscribe('chat');
    },
    message(ws, message) {
      ws.publish('chat', message);
    },
    close(ws) {
      ws.unsubscribe('chat');
    },
  },
});
```

## File I/O

### Reading Files with Bun.file()

```ts
const file = Bun.file('./config.json');

console.log(`Size: ${file.size} bytes`);
console.log(`Type: ${file.type}`);

const exists = await file.exists();

const text = await file.text();
const json = await file.json();
const buffer = await file.arrayBuffer();
const bytes = await file.bytes();
const stream = file.stream();
```

### Writing Files with Bun.write()

```ts
await Bun.write('output.txt', 'Hello, World!');
await Bun.write('data.json', JSON.stringify({ key: 'value' }));
await Bun.write('copy.txt', Bun.file('original.txt'));

const response = await fetch('https://example.com');
await Bun.write('page.html', response);
```

### Incremental Writing with FileSink

```ts
const writer = Bun.file('log.txt').writer({ highWaterMark: 1024 * 1024 });
writer.write('Line 1\n');
writer.write('Line 2\n');
writer.flush();
writer.end();
```

### Delete a File

```ts
await Bun.file('temp.txt').delete();
```

### Write to stdout

```ts
await Bun.write(Bun.stdout, 'Output to terminal\n');
```

## SQLite with bun:sqlite

### Basic Usage

```ts
import { Database } from 'bun:sqlite';

const db = new Database('app.db');
db.exec('PRAGMA journal_mode = WAL');

db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
  )
`);
```

### Queries and Prepared Statements

```ts
const insert = db.prepare('INSERT INTO users (name, email) VALUES (?, ?)');
insert.run('Alice', 'alice@example.com');

const user = db.query('SELECT * FROM users WHERE id = ?').get(1);

const allUsers = db.query('SELECT * FROM users').all();

const names = db.query('SELECT name FROM users').values();
```

### Transactions

```ts
const insertMany = db.transaction(
  (users: { name: string; email: string }[]) => {
    const insert = db.prepare(
      'INSERT INTO users (name, email) VALUES ($name, $email)',
    );
    for (const user of users) {
      insert.run(user);
    }
  },
);

insertMany([
  { name: 'Bob', email: 'bob@example.com' },
  { name: 'Carol', email: 'carol@example.com' },
]);
```

### In-Memory Database

```ts
const memDb = new Database(':memory:');
```

## Password Hashing

### Argon2id (Default)

```ts
const hash = await Bun.password.hash('super-secure-password');
const isValid = await Bun.password.verify('super-secure-password', hash);
```

### Bcrypt

```ts
const bcryptHash = await Bun.password.hash('password', {
  algorithm: 'bcrypt',
  cost: 10,
});
const isValid = await Bun.password.verify('password', bcryptHash);
```

### Synchronous Variants

```ts
const hash = Bun.password.hashSync('password');
const isValid = Bun.password.verifySync('password', hash);
```

## S3 Client

Bun includes a built-in S3 client compatible with any S3-compatible storage (AWS, R2, MinIO).

### Basic S3 Operations

```ts
import { S3Client } from 'bun';

const s3 = new S3Client({
  accessKeyId: Bun.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: Bun.env.AWS_SECRET_ACCESS_KEY,
  region: 'us-east-1',
  bucket: 'my-bucket',
});

const file = s3.file('uploads/photo.jpg');
const exists = await file.exists();
const content = await file.text();

await s3.file('output.json').write(JSON.stringify({ key: 'value' }));
```

### List Objects

```ts
import { s3 } from 'bun';

const objects = await s3.list({ prefix: 'uploads/' });
for (const obj of objects) {
  console.log(obj.key, obj.size);
}
```

### Presigned URLs

```ts
const url = s3.presign('uploads/photo.jpg', {
  expiresIn: 3600,
  method: 'GET',
});
```

## HTML Imports (Fullstack)

Import HTML files directly as route handlers. Bun automatically bundles associated scripts and styles.

```ts
import homepage from './index.html';
import dashboard from './dashboard.html';

Bun.serve({
  routes: {
    '/': homepage,
    '/dashboard': dashboard,
  },
  fetch(req) {
    return new Response('Not Found', { status: 404 });
  },
});
```

### Production Build

```ts
await Bun.build({
  entrypoints: ['./index.html'],
  outdir: './dist',
  minify: true,
});
```

## Utility Functions

### Bun.sleep()

```ts
await Bun.sleep(1000);
await Bun.sleep('5s');
```

### Bun.hash()

```ts
const hash = Bun.hash('hello world');
const wyhash = Bun.hash.wyhash('data');
const adler32 = Bun.hash.adler32('data');
const crc32 = Bun.hash.crc32('data');
```

### Bun.peek()

```ts
const value = Bun.peek(promise);
```

### Bun.which()

```ts
const path = Bun.which('node');
```

### Environment Variables

```ts
const apiKey = Bun.env.API_KEY;
const port = Bun.env.PORT ?? '3000';
```

### Bun.version

```ts
console.log(Bun.version);
console.log(Bun.revision);
```

## Server + SQLite Integration

```ts
import { Database } from 'bun:sqlite';

const db = new Database('posts.db');
db.exec('PRAGMA journal_mode = WAL');
db.exec(`
  CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
  )
`);

Bun.serve({
  routes: {
    '/api/posts': {
      GET: () => {
        const posts = db.query('SELECT * FROM posts').all();
        return Response.json(posts);
      },
      POST: async (req) => {
        const { title, content } = await req.json();
        const id = crypto.randomUUID();
        db.query(
          'INSERT INTO posts (id, title, content, created_at) VALUES (?, ?, ?, ?)',
        ).run(id, title, content, new Date().toISOString());
        return Response.json({ id, title, content }, { status: 201 });
      },
    },
    '/api/posts/:id': (req) => {
      const post = db
        .query('SELECT * FROM posts WHERE id = ?')
        .get(req.params.id);
      if (!post) return new Response('Not Found', { status: 404 });
      return Response.json(post);
    },
  },
  fetch(req) {
    return new Response('Not Found', { status: 404 });
  },
});
```
