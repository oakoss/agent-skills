---
title: Configuration
description: vercel.json and vercel.ts configuration, build settings, output directory, framework presets, rewrites, redirects, and headers
tags:
  [
    vercel-json,
    vercel-ts,
    rewrites,
    redirects,
    headers,
    build,
    framework,
    clean-urls,
  ]
---

# Configuration

## vercel.json Basics

Place `vercel.json` in the project root. It controls build settings, routing, functions, and deployment behavior.

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "pnpm install",
  "framework": "nextjs"
}
```

The `$schema` field enables IDE autocompletion and validation.

## Programmatic Configuration with vercel.ts

As an alternative to `vercel.json`, use a typed config file. Install the package first:

```bash
npm install @vercel/config
```

```ts
import { type VercelConfig } from '@vercel/config';

export const config: VercelConfig = {
  buildCommand: 'npm run build',
  cleanUrls: true,
  trailingSlash: false,
};
```

Supported filenames: `vercel.ts`, `vercel.js`, `vercel.mjs`, `vercel.cjs`, `vercel.mts`.

## Build Settings

Configure builds via `vercel.json` or the dashboard under Project Settings > General.

```json
{
  "buildCommand": "pnpm run build",
  "outputDirectory": ".next",
  "installCommand": "pnpm install --frozen-lockfile",
  "devCommand": "pnpm dev",
  "framework": "nextjs"
}
```

Common `framework` values: `nextjs`, `vite`, `remix`, `sveltekit`, `nuxtjs`, `astro`, `gatsby`, `angular`, `hugo`, `eleventy`. Setting a framework auto-configures build/output defaults.

Override the Node.js version used during builds:

```json
{
  "engines": {
    "node": "20.x"
  }
}
```

## Rewrites

Rewrites route requests to a different destination without changing the browser URL. Useful for SPA routing, API proxying, and friendly URLs.

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.example.com/:path*"
    },
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

Path parameters use `:param` syntax. Wildcards use `:path*` to capture all segments.

Order matters: more specific rewrites should come first. API routes should precede catch-all SPA rewrites.

```json
{
  "rewrites": [
    { "source": "/docs/:slug", "destination": "/documentation/:slug" },
    { "source": "/blog/:year/:month/:slug", "destination": "/posts/:slug" },
    { "source": "/app/:path*", "destination": "/index.html" }
  ]
}
```

## Redirects

Redirects change the URL in the browser. Use `permanent: true` for 301 (SEO-friendly) or `permanent: false` for 307 (temporary).

```json
{
  "redirects": [
    { "source": "/old-page", "destination": "/new-page", "permanent": true },
    {
      "source": "/blog/:slug",
      "destination": "/posts/:slug",
      "permanent": true
    },
    {
      "source": "/twitter",
      "destination": "https://twitter.com/vercel",
      "permanent": false
    }
  ]
}
```

Limit: 1024 static redirects per project. For larger sets, use `bulkRedirects`:

```json
{
  "bulkRedirects": [{ "source": "/redirects.csv" }]
}
```

The CSV format: `source,destination,permanent` (one redirect per line).

## Headers

Set custom response headers for specific paths. Commonly used for CORS, security headers, and caching.

```json
{
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Access-Control-Allow-Origin", "value": "*" },
        { "key": "Access-Control-Allow-Methods", "value": "GET, POST, OPTIONS" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

Cache control for static assets:

```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

## URL Formatting

Control URL appearance with `cleanUrls` and `trailingSlash`:

```json
{
  "cleanUrls": true,
  "trailingSlash": false
}
```

| Setting                | Effect                          |
| ---------------------- | ------------------------------- |
| `cleanUrls: true`      | `/about.html` becomes `/about`  |
| `trailingSlash: false` | `/about/` redirects to `/about` |
| `trailingSlash: true`  | `/about` redirects to `/about/` |

Pick one trailing slash strategy and apply it consistently to avoid redirect loops and duplicate content.

## Functions Configuration

Configure serverless function behavior per-route or globally:

```json
{
  "functions": {
    "api/heavy-computation.ts": {
      "maxDuration": 60,
      "memory": 1024
    },
    "api/**/*.ts": {
      "maxDuration": 30
    }
  }
}
```

| Plan       | Default Duration | Max Duration | Fluid Compute |
| ---------- | ---------------- | ------------ | ------------- |
| Hobby      | 10s              | 60s          | 300s default  |
| Pro        | 15s              | 300s         | 300s default  |
| Enterprise | 15s              | 900s         | 900s max      |

Fluid Compute is enabled by default for new projects. It allows a single worker to handle multiple concurrent requests, improving resource utilization and reducing cold starts. Functions using Fluid Compute get a default execution time of 300s and are billed only for active CPU time.

## Regions

Deploy functions to specific regions:

```json
{
  "regions": ["iad1", "sfo1", "cdg1"]
}
```

Common regions: `iad1` (US East), `sfo1` (US West), `cdg1` (Paris), `hnd1` (Tokyo), `syd1` (Sydney). Functions default to `iad1` (US East).

## Ignoring Files

Exclude files from deployment:

```json
{
  "ignoreCommand": "git diff --quiet HEAD^ HEAD -- .",
  "git": {
    "deploymentEnabled": {
      "main": true,
      "staging": true
    }
  }
}
```

The `ignoreCommand` skips deployment if it exits with code 0 (no changes). Useful for monorepos to skip unchanged packages.

## Full Example

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "buildCommand": "pnpm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    {
      "source": "/(.*)",
      "headers": [{ "key": "X-Frame-Options", "value": "DENY" }]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.example.com/:path*"
    },
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "redirects": [
    {
      "source": "/old-docs/:path*",
      "destination": "/docs/:path*",
      "permanent": true
    }
  ],
  "regions": ["iad1"]
}
```
