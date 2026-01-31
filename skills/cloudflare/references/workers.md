---
title: Workers
description: Worker syntax, fetch handler, scheduled events, middleware, bindings, environment variables, and WorkerEntrypoint
tags:
  [
    workers,
    fetch,
    scheduled,
    bindings,
    env,
    middleware,
    entrypoint,
    module,
    handler,
  ]
---

# Workers

## Module Format

Workers use ES module syntax with a default export containing event handlers. The `env` parameter provides access to all bindings (KV, D1, R2, Durable Objects, secrets, variables).

```ts
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    return new Response('Hello from the edge');
  },
};
```

## Environment Type

Define an `Env` interface for type-safe binding access:

```ts
interface Env {
  MY_KV: KVNamespace;
  DB: D1Database;
  BUCKET: R2Bucket;
  MY_DO: DurableObjectNamespace;
  API_KEY: string;
  ENVIRONMENT: string;
}
```

## Fetch Handler

The primary handler for HTTP requests. Receives the incoming `Request`, environment bindings, and an execution context.

```ts
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/api/data') {
      const data = await env.MY_KV.get('key', { type: 'json' });
      return Response.json(data);
    }

    if (request.method === 'POST' && url.pathname === '/api/submit') {
      const body = await request.json();
      await env.DB.prepare('INSERT INTO submissions (data) VALUES (?)')
        .bind(JSON.stringify(body))
        .run();
      return new Response('Created', { status: 201 });
    }

    return new Response('Not Found', { status: 404 });
  },
};
```

## Execution Context

The `ctx` parameter provides lifecycle methods:

```ts
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    ctx.waitUntil(logAnalytics(request, env));
    ctx.passThroughOnException();

    return new Response('OK');
  },
};
```

- `ctx.waitUntil(promise)` keeps the Worker alive after returning a response to perform background work (logging, cache updates)
- `ctx.passThroughOnException()` falls through to the origin server if the Worker throws

## Scheduled Handler

Triggered by cron expressions configured in `wrangler.toml`. Useful for periodic tasks like cleanup, aggregation, or external API polling.

```ts
export default {
  async scheduled(
    controller: ScheduledController,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<void> {
    ctx.waitUntil(performCleanup(env));
  },
};
```

```toml
[triggers]
crons = ["0 * * * *", "0 0 * * *"]
```

The `controller` provides:

- `controller.scheduledTime` — the time the cron was scheduled (milliseconds since epoch)
- `controller.cron` — the cron pattern that triggered the event

## Queue Handler

Processes messages from Cloudflare Queues:

```ts
export default {
  async queue(
    batch: MessageBatch<unknown>,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<void> {
    for (const message of batch.messages) {
      await processMessage(message.body, env);
      message.ack();
    }
  },
};
```

## Email Handler

Processes incoming emails via Email Routing:

```ts
export default {
  async email(
    message: EmailMessage,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<void> {
    const { from, to } = message;
    const content = await new Response(message.raw).text();
    await env.DB.prepare(
      'INSERT INTO emails (sender, recipient, body) VALUES (?, ?, ?)',
    )
      .bind(from, to, content)
      .run();
  },
};
```

## WorkerEntrypoint (RPC)

Extend `WorkerEntrypoint` to expose methods for Service Bindings with RPC:

```ts
import { WorkerEntrypoint } from 'cloudflare:workers';

export default class extends WorkerEntrypoint<Env> {
  async fetch(request: Request): Promise<Response> {
    return new Response('Hello');
  }

  async greet(name: string): Promise<string> {
    return `${this.env.GREETING} ${name}`;
  }
}
```

The calling Worker invokes RPC methods directly on the binding:

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const greeting = await env.MY_SERVICE.greet('World');
    return new Response(greeting);
  },
};
```

## DurableObject Entrypoint

Extend `DurableObject` for stateful, single-instance coordination:

```ts
import { DurableObject } from 'cloudflare:workers';

export class Counter extends DurableObject<Env> {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/increment') {
      const value = (await this.ctx.storage.get<number>('count')) ?? 0;
      await this.ctx.storage.put('count', value + 1);
      return Response.json({ count: value + 1 });
    }

    const count = (await this.ctx.storage.get<number>('count')) ?? 0;
    return Response.json({ count });
  }
}
```

Accessing a Durable Object from a Worker:

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.COUNTER.idFromName('global');
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  },
};
```

## Request and Response Patterns

Workers use the standard Web API `Request` and `Response` objects:

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const headers = Object.fromEntries(request.headers);
    const method = request.method;
    const body = method === 'POST' ? await request.json() : null;
    const cfProperties = request.cf;

    return Response.json(
      { url: url.pathname, method, country: cfProperties?.country },
      {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 's-maxage=60',
        },
      },
    );
  },
};
```

## CORS Handling

```ts
function corsHeaders(origin: string): HeadersInit {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  };
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get('Origin') ?? '*';

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders(origin) });
    }

    const response = await handleRequest(request, env);
    const newHeaders = new Headers(response.headers);
    Object.entries(corsHeaders(origin)).forEach(([key, value]) => {
      newHeaders.set(key, value);
    });

    return new Response(response.body, {
      status: response.status,
      headers: newHeaders,
    });
  },
};
```

## Error Handling

```ts
export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext,
  ): Promise<Response> {
    try {
      return await handleRequest(request, env);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Internal Server Error';
      return Response.json({ error: message }, { status: 500 });
    }
  },
};
```

## Environment Variables Configuration

Variables are set in `wrangler.toml` and accessed via `env`:

```toml
[vars]
API_HOST = "https://api.example.com"
ENVIRONMENT = "production"
```

For environment-specific overrides:

```toml
[env.staging.vars]
API_HOST = "https://staging-api.example.com"
ENVIRONMENT = "staging"
```
