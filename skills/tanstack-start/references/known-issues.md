---
title: Known Issues
description: 10 documented TanStack Start issues with workarounds including middleware error handling, file upload streaming, redirect undefined, Prisma edge, and Vinxi migration
tags:
  [
    issues,
    bugs,
    workarounds,
    middleware,
    file-upload,
    redirect,
    cookies,
    Prisma,
    better-auth,
    nodejs_compat,
    prerender,
    Vinxi,
    Vite,
    migration,
  ]
---

# Known Issues

## Issue 1: Middleware Does Not Catch Server Function Errors

**Error**: Errors thrown by server functions bypass middleware try-catch blocks.
**Status**: Fixed in v1.155+.
**Workaround** (v1.154 and earlier):

```ts
const middleware = createMiddleware().server(async (ctx) => {
  try {
    const r = await ctx.next();
    if ('error' in r && r.error) throw r.error;
    return r;
  } catch (error) {
    console.error('Middleware caught an error:', error);
    return new Response('An error occurred', { status: 500 });
  }
});
```

## Issue 2: File Upload Streaming Not Supported

**Error**: Large file uploads consume excessive memory.
**Cause**: Framework calls `await request.formData()` before handler runs.
**Status**: Open ([#5704](https://github.com/TanStack/router/issues/5704)).
**Workarounds**: Client-side file size validation; use Cloudflare R2 multipart upload API directly for large files.

## Issue 3: Server Function Redirects Return Undefined

**Error**: Type errors when using server function result after redirect.
**Status**: Open PR ([#6295](https://github.com/TanStack/router/pull/6295)).
**Prevention**: Always check return value before use.

```ts
const result = await login({ username, password });
if (result) {
  console.log(result.name);
}
```

## Issue 4: Stateful Auth Cookies Not Forwarded

**Error**: 401 Unauthorized when calling stateful backend APIs from server functions.
**Cause**: Server functions originate from Start server, not browser.
**Solutions**: Use `createIsomorphicFn` for read operations, or manually forward headers:

```ts
const headers = getRequestHeaders();
const response = await fetch('https://api.example.com/user', {
  headers: {
    Cookie: headers.get('cookie') || '',
    'X-XSRF-TOKEN': headers.get('x-xsrf-token') || '',
    Origin: headers.get('origin') || '',
  },
});
```

## Issue 5: Prisma Edge Module Not Found

**Error**: "No such module 'assets/.prisma/client/edge'".
**Fix**: Configure Prisma with `runtime = "cloudflare"` in schema.prisma.

```prisma
generator client {
  provider   = "prisma-client"
  output     = "../src/generated/prisma"
  engineType = "library"
  runtime    = "cloudflare"
}
```

## Issue 6: Better Auth Cookie Caching Issues

**Error**: Session cookies not set/refreshed properly.
**Fix**: Use `reactStartCookies()` plugin.

```ts
import { betterAuth } from 'better-auth';
import { reactStartCookies } from 'better-auth/plugins';

export const auth = betterAuth({
  plugins: [reactStartCookies()],
});
```

## Issue 7: Missing nodejs_compat Flag

**Error**: Runtime errors when using Node.js APIs on Cloudflare Workers.
**Fix**: Add `compatibility_flags = ["nodejs_compat"]` to `wrangler.toml`.

## Issue 8: Prerendering Fails with Cloudflare Bindings

**Error**: Build fails when routes with loaders use D1/KV/R2.
**Fix**: Set `prerender: false` on routes with bindings, or add conditional logic:

```ts
loader: async ({ context }) => {
  if (typeof context.cloudflare === 'undefined') {
    return { users: [] };
  }
  return {
    users: await context.cloudflare.env.DB.prepare('SELECT * FROM users').all(),
  };
};
```

## Issue 9: Migration History

TanStack Start has undergone two major architectural migrations:

### Vinxi → Vite (v1.121.0)

**Error**: "invariant failed: could not find the nearest match".

| Old (Vinxi)          | New (Vite)              |
| -------------------- | ----------------------- |
| `@tanstack/start`    | `@tanstack/react-start` |
| `app.config.ts`      | `vite.config.ts`        |
| `app/` source folder | `src/`                  |
| `vinxi dev`          | `vite dev`              |

### Server Routes Overhaul

| Old                                        | Current                                                |
| ------------------------------------------ | ------------------------------------------------------ |
| `createAPIFileRoute()` (Vinxi)             | `createFileRoute()` with `server.handlers`             |
| `createServerFileRoute().methods()` (Vite) | `createFileRoute()` with `server.handlers`             |
| `server: { preset: '...' }` (deployment)   | Vite plugins (`nitro/vite`, `@cloudflare/vite-plugin`) |
| `setHeaders()` import (ISR)                | `headers` property on route definition                 |

**Fix**: Update all imports, config files, and API route patterns. Delete `node_modules/` and reinstall if dependency conflicts persist.

## Issue 10: Dev Server Slow with Many Routes

**Cause**: `routeTree.gen.ts` statically imports every route. 100+ routes generate 700+ HTTP requests in Vite dev mode.
**Status**: Expected behavior until Router v2.
**Workarounds**: Use production builds for testing; use Cloudflare Tunnel instead of ngrok (avoids rate limits).
