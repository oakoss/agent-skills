---
title: Configuration
description: playwright.config.ts setup, projects, web server configuration, Docker deployment, dependencies, and browser launch options
tags:
  [
    config,
    playwright.config.ts,
    defineConfig,
    projects,
    webServer,
    Docker,
    Dockerfile,
    dependencies,
    workers,
    retries,
    reporter,
    teardown,
    serial,
    parallel,
    maxFailures,
    codegen,
    globalTimeout,
  ]
---

# Configuration

## playwright.config.ts

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 15'] },
    },
  ],
});
```

**Key settings:**

- `trace: 'on-first-retry'` -- captures full trace for debugging failed tests
- `screenshot: 'only-on-failure'` -- saves disk space
- `fullyParallel: true` -- runs tests in parallel across files and within files

## Multi-Project Setup with Auth

```typescript
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      dependencies: ['setup'],
      use: {
        ...devices['Desktop Chrome'],
        storageState: '.auth/user.json',
      },
    },
  ],
});
```

## Per-Project Workers (v1.52+)

```typescript
export default defineConfig({
  workers: 4,
  projects: [
    {
      name: 'fast-tests',
      workers: 4,
    },
    {
      name: 'slow-tests',
      workers: 1,
    },
  ],
});
```

The global `workers` limit still applies as a ceiling.

## Flaky Test Detection

```typescript
export default defineConfig({
  retries: 2,
  failOnFlakyTests: true,
});
```

CLI equivalent: `npx playwright test --fail-on-flaky-tests`

## Web Server Configuration

### Basic

```typescript
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### Dynamic Port Detection (v1.57+)

Wait for web server output using regex:

```typescript
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    wait: {
      stdout: '/Server running on port (?<SERVER_PORT>\\d+)/',
    },
  },
  use: {
    baseURL: `http://localhost:${process.env.SERVER_PORT ?? 3000}`,
  },
});
```

Named capture groups become environment variables. Handles dynamic ports from Vite, Next.js, and other dev servers.

### Graceful Shutdown (v1.50+)

```typescript
export default defineConfig({
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    gracefulShutdown: { signal: 'SIGTERM', timeout: 5000 },
  },
});
```

## Reporter Configuration

```typescript
export default defineConfig({
  reporter: [
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'results.xml' }],
    ['list'],
  ],
});
```

View HTML report: `npx playwright show-report`

## Docker Deployment

```dockerfile
FROM mcr.microsoft.com/playwright:v1.58.2-noble

RUN groupadd -r pwuser && useradd -r -g pwuser pwuser
USER pwuser

WORKDIR /app
COPY --chown=pwuser:pwuser . .
RUN npm ci

CMD ["npx", "playwright", "test"]
```

**Run with recommended flags:**

```bash
docker run -it --init --ipc=host my-playwright-tests
```

| Flag                  | Purpose                                   |
| --------------------- | ----------------------------------------- |
| `--init`              | Prevents zombie processes (handles PID=1) |
| `--ipc=host`          | Prevents Chromium memory exhaustion       |
| `--cap-add=SYS_ADMIN` | Only for local dev (enables sandbox)      |

**Available tags:**

- `:v1.58.2-noble` -- Ubuntu 24.04 LTS (recommended)
- `:v1.58.2-jammy` -- Ubuntu 22.04 LTS

**Python image:** `mcr.microsoft.com/playwright/python:v1.58.2-noble`

**Security:**

- Always create a non-root user inside the container
- Root user disables Chromium sandbox (security risk)
- Pin to specific version tags (avoid `:latest`)

## Browser Launch Options

| Option           | Value              | Purpose                  |
| ---------------- | ------------------ | ------------------------ |
| `headless`       | `true`/`false`     | Show browser UI          |
| `slowMo`         | `100` (ms)         | Slow down for debugging  |
| `args`           | `['--no-sandbox']` | Disable sandbox (Docker) |
| `executablePath` | `/path/to/chrome`  | Use custom browser       |
| `downloadsPath`  | `./downloads`      | Download location        |

## Common CI Environment Variables

| Variable               | Purpose                                       |
| ---------------------- | --------------------------------------------- |
| `CI=true`              | Detected by Playwright for CI-specific config |
| `PLAYWRIGHT_FORCE_TTY` | Control TTY behavior for reporters            |

## Dependencies

**Required:**

- `@playwright/test` -- Test runner and assertions
- Node.js 20+ (Node.js 18 deprecated) or Python 3.9+

**Optional (stealth):**

- `playwright-extra` -- Plugin system
- `puppeteer-extra-plugin-stealth` -- Anti-detection

```json
{
  "devDependencies": {
    "@playwright/test": "^1.58.0"
  }
}
```

## Breaking Changes Reference

| Version | Change                                                             |
| ------- | ------------------------------------------------------------------ |
| v1.58   | Removed `_react` and `_vue` selectors; removed `:light` suffix     |
| v1.57   | Chrome for Testing replaces Chromium; `page.accessibility` removed |
| v1.55   | Glob patterns in `page.route()` no longer support `?` and `[]`     |
| v1.55   | `route.continue()` cannot override `Cookie` header                 |
| v1.54   | Node.js 16 removed, Node.js 18 deprecated                          |

## Browser Versions (v1.58)

Chromium 145.0.7632.6 | Firefox 146.0.1 | WebKit 26.0

## webServer.url vs use.baseURL

- `webServer.url` -- readiness probe; Playwright polls until 2xx or 403, then starts tests
- `use.baseURL` -- what tests use for relative `page.goto('/')` calls
- Usually the same value but independent settings

## Multiple Web Servers

```typescript
export default defineConfig({
  webServer: [
    {
      name: 'app',
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
    {
      name: 'mock-smtp',
      command: 'npm run mock:smtp',
      url: 'http://localhost:1080',
      reuseExistingServer: !process.env.CI,
    },
  ],
});
```

The `name` field labels log lines when `stdout: 'pipe'` is set.

## Parallel Execution Modes

Per-describe overrides with `test.describe.configure()`:

```typescript
test.describe.configure({ mode: 'parallel' });
test.describe.configure({ mode: 'serial' });
test.describe.configure({ mode: 'default' });
```

- `parallel` -- individual tests in parallel
- `serial` -- sequential, skip rest if one fails; retries the entire block together
- `default` -- opt out of `fullyParallel`

## maxFailures

```typescript
export default defineConfig({ maxFailures: 5 });
```

CLI: `--max-failures=5` or `-x` (stop after first failure).

## Teardown Projects

```typescript
projects: [
  { name: 'setup db', testMatch: '**/db.setup.ts', teardown: 'cleanup db' },
  { name: 'cleanup db', testMatch: '**/db.teardown.ts' },
  { name: 'tests', dependencies: ['setup db'] },
],
```

Teardown runs after all dependents complete, regardless of pass/fail.

## globalTimeout

```typescript
export default defineConfig({ globalTimeout: 30 * 60 * 1000 });
```

Hard cap on entire test run. Prevents runaway CI jobs.

## Codegen Options

```bash
npx playwright codegen http://localhost:3000
npx playwright codegen --load-storage=playwright/.auth/user.json http://localhost:3000
npx playwright codegen --device="iPhone 15 Pro Max" http://localhost:3000
npx playwright codegen --color-scheme=dark http://localhost:3000
```
