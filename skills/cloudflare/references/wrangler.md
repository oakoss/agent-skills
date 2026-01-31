---
title: Wrangler
description: Wrangler CLI commands, wrangler.toml configuration, dev server, deploy, secrets, tail, and environments
tags: [wrangler, cli, config, toml, deploy, dev, secrets, tail, environments]
---

# Wrangler

## Installation

```bash
npm install -D wrangler

npx wrangler --version

npx wrangler login
```

## Core Commands

| Command                                       | Description                          |
| --------------------------------------------- | ------------------------------------ |
| `wrangler init`                               | Create a new Worker project          |
| `wrangler dev`                                | Start local dev server with bindings |
| `wrangler deploy`                             | Deploy Worker to Cloudflare          |
| `wrangler delete`                             | Delete a deployed Worker             |
| `wrangler tail`                               | Stream live logs from production     |
| `wrangler secret put NAME`                    | Set an encrypted secret              |
| `wrangler secret list`                        | List all secrets                     |
| `wrangler secret delete NAME`                 | Remove a secret                      |
| `wrangler pages deploy DIR`                   | Deploy a Pages project               |
| `wrangler d1 create DB_NAME`                  | Create a D1 database                 |
| `wrangler d1 execute DB_NAME --command "SQL"` | Run SQL on D1                        |
| `wrangler d1 migrations apply DB_NAME`        | Apply D1 migrations                  |
| `wrangler r2 bucket create BUCKET_NAME`       | Create an R2 bucket                  |
| `wrangler kv namespace create NS_NAME`        | Create a KV namespace                |

## Configuration File

The primary configuration file for Workers and Pages projects. Supports both JSON (`wrangler.json` / `wrangler.jsonc`) and TOML (`wrangler.toml`) formats. **`wrangler.jsonc` is recommended for new projects** -- it provides JSON Schema validation, IDE autocompletion, and inline comments. Some newer Wrangler features are only available in the JSON format.

### Minimal Worker Config

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-09-23"
```

### Full Worker Config

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-09-23"
compatibility_flags = ["nodejs_compat"]

[observability]
enabled = true

[vars]
ENVIRONMENT = "production"
API_URL = "https://api.example.com"

[[kv_namespaces]]
binding = "CACHE"
id = "abc123def456"
preview_id = "preview_abc123"

[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "abc123-def456-ghi789"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "my-assets"
preview_bucket_name = "my-assets-preview"

[durable_objects]
bindings = [
  { name = "COUNTER", class_name = "Counter" },
  { name = "ROOM", class_name = "ChatRoom" },
]

[[migrations]]
tag = "v1"
new_sqlite_classes = ["ChatRoom"]
new_classes = ["Counter"]

[[queues.producers]]
queue = "my-queue"
binding = "QUEUE"

[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10
max_batch_timeout = 5

[triggers]
crons = ["*/5 * * * *"]

[[rules]]
type = "Text"
globs = ["**/*.html"]
fallthrough = true
```

### Pages Config

```toml
name = "my-pages-project"
pages_build_output_dir = "dist"
compatibility_date = "2024-09-23"

[vars]
API_URL = "https://api.example.com"

[[kv_namespaces]]
binding = "MY_KV"
id = "abc123"
```

### JSON Config Format

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "main": "src/index.ts",
  "compatibility_date": "2024-09-23",
  "kv_namespaces": [
    {
      "binding": "CACHE",
      "id": "abc123def456",
    },
  ],
}
```

## Environments

Define per-environment overrides for staging, production, or custom environments:

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-09-23"

[vars]
ENVIRONMENT = "production"

[env.staging]
name = "my-worker-staging"
[env.staging.vars]
ENVIRONMENT = "staging"

[env.preview]
name = "my-worker-preview"
[env.preview.vars]
ENVIRONMENT = "preview"
```

Deploy to a specific environment:

```bash
wrangler deploy --env staging

wrangler dev --env staging
```

## Local Development

### Dev Server

```bash
wrangler dev

wrangler dev --port 8787

wrangler dev --local

wrangler dev --remote
```

The dev server provides:

- Local KV, D1, R2, and Durable Object simulation via Miniflare
- Hot reloading on file changes
- Access to `request.cf` properties in remote mode
- Local persistence in `.wrangler/state/`

### Persist Local State

```bash
wrangler dev --persist-to .wrangler/state
```

Local D1, KV, and R2 data persists between dev sessions at this path.

## Secrets Management

Secrets are encrypted environment variables that never appear in `wrangler.toml` or logs.

```bash
wrangler secret put API_KEY

echo "my-secret-value" | wrangler secret put API_KEY

wrangler secret list

wrangler secret delete API_KEY

wrangler secret put API_KEY --env staging
```

Access secrets the same way as environment variables in Worker code:

```ts
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const apiKey = env.API_KEY;
    return new Response('OK');
  },
};
```

## Tail (Live Logs)

Stream real-time logs from a deployed Worker:

```bash
wrangler tail

wrangler tail --format json

wrangler tail --status error

wrangler tail --method POST

wrangler tail --search "user-123"

wrangler tail --env staging
```

## D1 CLI Operations

```bash
wrangler d1 create my-database

wrangler d1 list

wrangler d1 execute my-database --command "SELECT * FROM users"

wrangler d1 execute my-database --file schema.sql

wrangler d1 execute my-database --command "SELECT 1" --remote

wrangler d1 migrations create my-database migration-name

wrangler d1 migrations apply my-database

wrangler d1 migrations apply my-database --remote
```

## KV CLI Operations

```bash
wrangler kv namespace create MY_KV

wrangler kv namespace list

wrangler kv key put --binding=MY_KV "key" "value"

wrangler kv key get --binding=MY_KV "key"

wrangler kv key list --binding=MY_KV

wrangler kv key list --binding=MY_KV --prefix="user:"

wrangler kv key delete --binding=MY_KV "key"

wrangler kv bulk put --binding=MY_KV data.json
```

## R2 CLI Operations

```bash
wrangler r2 bucket create my-bucket

wrangler r2 bucket list

wrangler r2 object put my-bucket/path/file.txt --file ./local-file.txt

wrangler r2 object get my-bucket/path/file.txt

wrangler r2 object delete my-bucket/path/file.txt
```

## Compatibility Dates and Flags

The `compatibility_date` controls which Workers runtime behavior your code uses. Set it to the current date when creating a project, and update it periodically to opt into new behavior.

```toml
compatibility_date = "2024-09-23"

compatibility_flags = ["nodejs_compat"]
```

Common compatibility flags:

| Flag                                          | Purpose                                                 |
| --------------------------------------------- | ------------------------------------------------------- |
| `nodejs_compat`                               | Enable Node.js built-in module support                  |
| `streams_enable_constructors`                 | Enable `ReadableStream` / `WritableStream` constructors |
| `transformstream_enable_standard_constructor` | Standard `TransformStream` constructor                  |

## Custom Domains and Routes

```toml
routes = [
  { pattern = "example.com/api/*", zone_name = "example.com" },
  { pattern = "api.example.com/*", zone_name = "example.com" },
]

[env.production]
routes = [
  { pattern = "example.com/api/*", zone_name = "example.com" },
]
```

Or use custom domains (automatically provisions SSL):

```toml
[env.production]
workers_dev = false
routes = [
  { pattern = "api.example.com", custom_domain = true },
]
```
