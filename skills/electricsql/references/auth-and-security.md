---
title: Authentication and Security
description: Auth proxy patterns, shape gatekeeper middleware, per-table security, where clause injection, token refresh in ShapeStream, and production security checklist
tags:
  [
    auth,
    proxy,
    gatekeeper,
    JWT,
    where-clause-injection,
    token-refresh,
    ELECTRIC_SECRET,
    HTTPS,
    middleware,
    security,
  ]
---

## Why Proxy

Never expose Electric directly to the internet. Electric has no built-in concept of users, roles, or permissions. Your API server must sit between clients and Electric to:

- Validate authentication tokens
- Inject where clauses that restrict data to the authenticated user
- Enforce per-table access rules
- Add audit logging

```text
Client  -->  Your API (auth + where injection)  -->  Electric  -->  Postgres
```

## Shape Proxy Pattern

Your API validates the request, adds security constraints, and proxies to Electric.

### Express Proxy

```ts
import express from 'express';

const app = express();
const ELECTRIC_URL = process.env.ELECTRIC_URL ?? 'http://localhost:3000';

app.get('/api/shapes/items', authenticateUser, async (req, res) => {
  const userId = req.user.id;

  const url = new URL(`${ELECTRIC_URL}/v1/shape`);
  url.searchParams.set('table', 'items');
  url.searchParams.set('where', 'user_id = $1');
  url.searchParams.set('params[1]', userId);
  url.searchParams.set('columns', 'id,title,status,created_at');

  if (req.query.offset) {
    url.searchParams.set('offset', req.query.offset as string);
  }
  if (req.query.handle) {
    url.searchParams.set('handle', req.query.handle as string);
  }
  if (req.query.live) {
    url.searchParams.set('live', 'true');
  }

  const response = await fetch(url.toString());

  res.status(response.status);
  for (const [key, value] of response.headers.entries()) {
    res.setHeader(key, value);
  }

  const body = await response.text();
  res.send(body);
});
```

### Hono Proxy

```ts
import { Hono } from 'hono';
import { jwt } from 'hono/jwt';

const app = new Hono();
const ELECTRIC_URL = process.env.ELECTRIC_URL ?? 'http://localhost:3000';

app.get(
  '/api/shapes/items',
  jwt({ secret: process.env.JWT_SECRET! }),
  async (c) => {
    const userId = c.get('jwtPayload').sub;

    const url = new URL(`${ELECTRIC_URL}/v1/shape`);
    url.searchParams.set('table', 'items');
    url.searchParams.set('where', 'user_id = $1');
    url.searchParams.set('params[1]', userId);

    const params = ['offset', 'handle', 'live'] as const;
    for (const param of params) {
      const value = c.req.query(param);
      if (value) url.searchParams.set(param, value);
    }

    const response = await fetch(url.toString());
    return new Response(response.body, {
      status: response.status,
      headers: response.headers,
    });
  },
);
```

### TanStack Start Server Function Proxy

```ts
import { createServerFn } from '@tanstack/react-start';

const getItemsShape = createServerFn({ method: 'GET' })
  .validator(
    (input: { offset?: string; handle?: string; live?: string }) => input,
  )
  .handler(async ({ data, context }) => {
    const userId = context.user.id;
    const ELECTRIC_URL = process.env.ELECTRIC_URL ?? 'http://localhost:3000';

    const url = new URL(`${ELECTRIC_URL}/v1/shape`);
    url.searchParams.set('table', 'items');
    url.searchParams.set('where', 'user_id = $1');
    url.searchParams.set('params[1]', userId);

    if (data.offset) url.searchParams.set('offset', data.offset);
    if (data.handle) url.searchParams.set('handle', data.handle);
    if (data.live) url.searchParams.set('live', 'true');

    const response = await fetch(url.toString());
    return response;
  });
```

## Gatekeeper Pattern

A middleware layer that checks permissions before allowing shape subscriptions. Useful when multiple shapes need different access rules.

```ts
import { type Request, type Response, type NextFunction } from 'express';

type ShapeConfig = {
  table: string;
  allowedRoles: string[];
  userFilter?: (userId: string) => Record<string, string>;
};

const SHAPE_CONFIGS: Record<string, ShapeConfig> = {
  items: {
    table: 'items',
    allowedRoles: ['user', 'admin'],
    userFilter: (userId) => ({
      where: 'user_id = $1',
      'params[1]': userId,
    }),
  },
  analytics: {
    table: 'analytics_events',
    allowedRoles: ['admin'],
  },
  public_posts: {
    table: 'posts',
    allowedRoles: ['user', 'admin'],
    userFilter: () => ({
      where: "visibility = 'public'",
    }),
  },
};

function shapeGatekeeper(shapeName: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    const config = SHAPE_CONFIGS[shapeName];
    if (!config) {
      res.status(404).json({ error: 'Shape not found' });
      return;
    }

    if (!config.allowedRoles.includes(req.user.role)) {
      res.status(403).json({ error: 'Insufficient permissions' });
      return;
    }

    req.shapeConfig = config;
    next();
  };
}
```

## Per-Table Security

Different tables often need different auth rules. Map each shape endpoint to specific access policies.

```ts
const ELECTRIC_URL = process.env.ELECTRIC_URL ?? 'http://localhost:3000';

async function proxyShape(
  table: string,
  extraParams: Record<string, string>,
  query: Record<string, string>,
): Promise<Response> {
  const url = new URL(`${ELECTRIC_URL}/v1/shape`);
  url.searchParams.set('table', table);

  for (const [key, value] of Object.entries(extraParams)) {
    url.searchParams.set(key, value);
  }
  for (const param of ['offset', 'handle', 'live']) {
    if (query[param]) url.searchParams.set(param, query[param]);
  }

  return fetch(url.toString());
}

app.get('/api/shapes/my-items', authenticateUser, async (req, res) => {
  const response = await proxyShape(
    'items',
    { where: 'user_id = $1', 'params[1]': req.user.id },
    req.query as Record<string, string>,
  );
  res.status(response.status).send(await response.text());
});

app.get(
  '/api/shapes/team-items',
  authenticateUser,
  requireRole('manager'),
  async (req, res) => {
    const response = await proxyShape(
      'items',
      { where: 'team_id = $1', 'params[1]': req.user.teamId },
      req.query as Record<string, string>,
    );
    res.status(response.status).send(await response.text());
  },
);

app.get(
  '/api/shapes/all-items',
  authenticateUser,
  requireRole('admin'),
  async (req, res) => {
    const response = await proxyShape(
      'items',
      {},
      req.query as Record<string, string>,
    );
    res.status(response.status).send(await response.text());
  },
);
```

## Where Clause Injection

The server adds user-scoped filters so the client never controls what data it receives.

```ts
function buildUserShape(
  userId: string,
  table: string,
  additionalWhere?: string,
) {
  const params: Record<string, string> = {
    table,
    where: additionalWhere
      ? `user_id = $1 AND (${additionalWhere})`
      : 'user_id = $1',
    'params[1]': userId,
  };
  return params;
}
```

The client requests shapes through the proxy without specifying where clauses:

```ts
const stream = new ShapeStream({
  url: '/api/shapes/my-items',
  params: {},
});
```

The proxy injects `user_id = $1` before forwarding to Electric. The client has no ability to bypass this filter.

## Token Refresh in ShapeStream

ShapeStream connections are long-lived. Tokens expire during the connection lifetime. Use the `onError` callback to detect 401s and refresh:

```ts
import { FetchError, ShapeStream } from '@electric-sql/client';

function createAuthenticatedStream<T>(
  table: string,
  refreshToken: () => Promise<string>,
) {
  let currentToken = '';

  const stream = new ShapeStream<T>({
    url: '/api/shapes/' + table,
    params: { table },
    headers: {
      Authorization: async () => {
        if (!currentToken) {
          currentToken = await refreshToken();
        }
        return `Bearer ${currentToken}`;
      },
    },
    onError: async (error) => {
      if (error instanceof FetchError && error.status === 401) {
        currentToken = await refreshToken();
      }
    },
  });

  return stream;
}
```

```tsx
function ItemList() {
  const { getAccessToken } = useAuth();

  const { data, isLoading } = useShape<Item>({
    url: '/api/shapes/items',
    params: { table: 'items' },
    headers: {
      Authorization: async () => `Bearer ${await getAccessToken()}`,
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <ul>
      {data.map((item) => (
        <li key={item.id}>{item.title}</li>
      ))}
    </ul>
  );
}
```

## Production Checklist

| Requirement                         | How                                                        |
| ----------------------------------- | ---------------------------------------------------------- |
| `ELECTRIC_SECRET` is set            | Set a strong secret; never use `ELECTRIC_INSECURE` in prod |
| HTTPS termination in place          | Use a reverse proxy (nginx, Caddy, cloud LB) for TLS       |
| Auth proxy deployed                 | All shape requests routed through your API                 |
| No direct client access to Electric | Electric port not exposed publicly                         |
| Where clauses injected server-side  | Client cannot control `where` or `params` directly         |
| Token refresh handled               | `onError` callback refreshes expired tokens                |
| Rate limiting on proxy              | Prevent abuse of shape subscriptions                       |
| Postgres role is restricted         | Electric DB user has minimal necessary permissions         |
| Publication scoped to needed tables | Do not use `FOR ALL TABLES` unless required                |
| Health checks configured            | Monitor `/v1/health` for alerting                          |
