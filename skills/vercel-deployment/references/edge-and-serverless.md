---
title: Edge and Serverless Functions
description: Edge functions, serverless functions, API routes, runtime selection, streaming responses, and function configuration
tags: [edge, serverless, api-routes, runtime, streaming, v8, node, functions]
---

# Edge and Serverless Functions

## Runtime Overview

Vercel supports two function runtimes:

| Feature           | Serverless (Node.js)          | Edge (V8)                |
| ----------------- | ----------------------------- | ------------------------ |
| Runtime           | Node.js                       | V8 isolates              |
| Cold start        | 100-1000ms                    | Sub-50ms                 |
| Max bundle size   | 50MB (compressed)             | 4MB                      |
| Max request body  | 4.5MB                         | 1MB                      |
| Node.js APIs      | Full                          | Limited subset           |
| Network           | TCP/UDP supported             | HTTP only                |
| Execution regions | Configurable                  | All edge locations       |
| Use case          | Complex logic, DB connections | Low-latency, lightweight |

## Serverless Functions

### File-Based Routing (api/ Directory)

Create files in the `api/` directory at the project root. Each file becomes an endpoint:

```text
api/
├── users.ts          → GET/POST /api/users
├── users/[id].ts     → GET/PUT/DELETE /api/users/:id
└── health.ts         → GET /api/health
```

```ts
import { type VercelRequest, type VercelResponse } from '@vercel/node';

export default function handler(req: VercelRequest, res: VercelResponse) {
  const { id } = req.query;
  res.status(200).json({ id, name: 'Example User' });
}
```

### Framework-Based Routes (Next.js)

Next.js App Router route handlers in `app/api/`:

```ts
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const data = await fetchData();
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  const result = await createItem(body);
  return NextResponse.json(result, { status: 201 });
}
```

### Function Configuration

Set per-function options via the config export:

```ts
export const config = {
  maxDuration: 60,
};

export default function handler(req: VercelRequest, res: VercelResponse) {
  // Long-running operation
}
```

Or configure globally in `vercel.json`:

```json
{
  "functions": {
    "api/heavy/*.ts": {
      "maxDuration": 60,
      "memory": 1024
    }
  }
}
```

Memory options: 128, 256, 512, 1024, 2048, 3008 (MB).

## Edge Functions

### Selecting Edge Runtime

Export a `runtime` config to opt into edge:

```ts
export const runtime = 'edge';

export default function handler(request: Request) {
  return new Response(JSON.stringify({ message: 'Hello from the edge' }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

Next.js App Router edge route handler:

```ts
export const runtime = 'edge';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name') ?? 'World';
  return Response.json({ greeting: `Hello, ${name}!` });
}
```

### Edge Runtime Limitations

The edge runtime uses V8 isolates (not Node.js). These Node.js APIs are unavailable:

- `fs` (file system)
- `path`
- `child_process`
- `net` / `dgram` (TCP/UDP)
- `process.env` access varies (use `process.env.VAR_NAME` directly)
- Native Node.js modules (e.g., `crypto` full API — use Web Crypto API instead)

Available Web APIs include: `fetch`, `Request`, `Response`, `URL`, `Headers`, `TextEncoder`, `TextDecoder`, `crypto.subtle`, `ReadableStream`, `WritableStream`.

### When to Use Edge vs Serverless

**Use Edge for:**

- Authentication checks and redirects
- A/B testing and feature flags
- Geolocation-based responses
- Simple API responses (JSON transforms)
- Content personalization

**Use Serverless for:**

- Database connections (TCP required)
- File processing
- Complex computation
- Third-party SDKs requiring Node.js
- Operations exceeding 4MB bundle size

## Streaming Responses

Stream data from both runtimes for long-running operations:

### Edge Streaming

```ts
export const runtime = 'edge';

export async function GET() {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      for (const chunk of ['Hello', ' ', 'World']) {
        controller.enqueue(encoder.encode(chunk));
        await new Promise((resolve) => setTimeout(resolve, 100));
      }
      controller.close();
    },
  });

  return new Response(stream, {
    headers: { 'Content-Type': 'text/plain' },
  });
}
```

### Serverless Streaming (Node.js)

```ts
export const config = { supportsResponseStreaming: true };

export default function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Content-Type', 'text/plain');
  res.setHeader('Transfer-Encoding', 'chunked');

  const chunks = ['Hello', ' ', 'World'];
  let i = 0;

  const interval = setInterval(() => {
    if (i < chunks.length) {
      res.write(chunks[i]);
      i++;
    } else {
      clearInterval(interval);
      res.end();
    }
  }, 100);
}
```

## Middleware

Middleware runs before every request. It executes on the Edge runtime:

```ts
import { NextResponse } from 'next/server';
import { type NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  if (!request.cookies.has('session')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
};
```

Middleware cannot:

- Access databases directly (no TCP)
- Use Node.js-specific APIs
- Return response bodies (only redirect, rewrite, or set headers)

Use the `matcher` config to limit which paths trigger middleware. Avoid running middleware on static assets.

## Cron Jobs

Schedule serverless functions to run on a schedule:

```json
{
  "crons": [
    {
      "path": "/api/cron/cleanup",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cron/sync",
      "schedule": "*/15 * * * *"
    }
  ]
}
```

The cron handler should verify the request is from Vercel:

```ts
export default function handler(req: VercelRequest, res: VercelResponse) {
  if (req.headers.authorization !== `Bearer ${process.env.CRON_SECRET}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  // Run scheduled task
}
```

Cron limits by plan: Hobby (2 crons, daily minimum), Pro (40 crons, per-minute minimum).
