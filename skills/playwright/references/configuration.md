---
title: Configuration
description: playwright.config.ts setup, dynamic web server configuration, Docker deployment, dependencies, and package versions
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
    v1.57,
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
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'stealth',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: {
          args: [
            '--disable-blink-features=AutomationControlled',
            '--no-sandbox',
          ],
        },
      },
    },
  ],
});
```

**Key settings:**

- `trace: 'on-first-retry'` — captures full trace for debugging failed tests
- `screenshot: 'only-on-failure'` — saves disk space
- `viewport: { width: 1920, height: 1080 }` — common desktop resolution

## Dynamic Web Server Configuration (v1.57+)

Wait for web server output before starting tests using regex:

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

- Named capture groups become environment variables
- Handles dynamic ports from Vite, Next.js dev mode
- No need for HTTP readiness checks

## Docker Deployment

```dockerfile
FROM mcr.microsoft.com/playwright:v1.57.0-noble

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

- `:v1.57.0-noble` — Ubuntu 24.04 LTS (recommended)
- `:v1.57.0-jammy` — Ubuntu 22.04 LTS

**Python image:** `mcr.microsoft.com/playwright/python:v1.57.0-noble`

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

## Common Launch Args for Stealth

```typescript
args: [
  '--disable-blink-features=AutomationControlled',
  '--no-sandbox',
  '--disable-setuid-sandbox',
  '--disable-dev-shm-usage',
  '--disable-accelerated-2d-canvas',
  '--no-first-run',
  '--no-zygote',
  '--single-process',
  '--disable-gpu',
];
```

## Dependencies

**Required:**

- `playwright@1.57.0` — Core browser automation library
- Node.js 20+ (Node.js 18 deprecated) or Python 3.9+

**Optional (Node.js stealth):**

- `playwright-extra@4.3.6` — Plugin system
- `puppeteer-extra-plugin-stealth@2.11.2` — Anti-detection

**Optional (Python stealth):**

- `playwright-stealth@0.0.1`

```json
{
  "devDependencies": {
    "playwright": "^1.57.0",
    "@playwright/test": "^1.57.0",
    "playwright-extra": "^4.3.6",
    "puppeteer-extra-plugin-stealth": "^2.11.2"
  }
}
```

## v1.57 Breaking Change

Playwright now uses [Chrome for Testing](https://developer.chrome.com/blog/chrome-for-testing/) builds instead of Chromium. This provides more authentic browser behavior but changes the browser icon and title bar.

Browser versions: Chromium 143.0.7499.4 | Firefox 144.0.2 | WebKit 26.0
