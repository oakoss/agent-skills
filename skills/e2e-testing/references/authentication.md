---
title: Authentication
description: Authentication with storageState, setup projects, multi-role testing, worker-scoped auth fixtures, and session management
tags:
  [authentication, storageState, setup-projects, multi-role, session, fixtures]
---

# Authentication

## Why Reuse Auth State

Logging in via UI for every test is slow and fragile. Playwright's `storageState` captures cookies and localStorage from an authenticated session and replays them in subsequent tests, skipping the login UI entirely.

## Setup Projects (Recommended)

Configure a setup project in `playwright.config.ts` that runs authentication before all test projects:

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: {
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

## Auth Setup File

Create `tests/auth.setup.ts` to perform login once and save the auth state:

```ts
import { setup, expect } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/auth/login');
  await page.getByLabel('Email address').fill('user@example.com');
  await page.getByLabel('Password').fill('password123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.waitForURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();

  await page.context().storageState({ path: authFile });
});
```

All tests in projects that depend on `setup` automatically receive the authenticated state.

## API-Based Authentication

For faster setup, authenticate via API instead of UI:

```ts
import { setup } from '@playwright/test';

const authFile = 'playwright/.auth/user.json';

setup('authenticate via API', async ({ request }) => {
  await request.post('/api/auth/login', {
    data: {
      email: 'user@example.com',
      password: 'password123',
    },
  });

  await request.storageState({ path: authFile });
});
```

## Multi-Role Authentication

Test different user roles by creating separate auth states and projects:

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'admin tests',
      use: { storageState: 'playwright/.auth/admin.json' },
      dependencies: ['setup'],
    },
    {
      name: 'user tests',
      use: { storageState: 'playwright/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

Auth setup file for multiple roles:

```ts
import { setup } from '@playwright/test';

setup('authenticate as admin', async ({ page }) => {
  await page.goto('/auth/login');
  await page.getByLabel('Email address').fill('admin@example.com');
  await page.getByLabel('Password').fill('admin-pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/admin');

  await page.context().storageState({ path: 'playwright/.auth/admin.json' });
});

setup('authenticate as user', async ({ page }) => {
  await page.goto('/auth/login');
  await page.getByLabel('Email address').fill('user@example.com');
  await page.getByLabel('Password').fill('user-pass');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  await page.context().storageState({ path: 'playwright/.auth/user.json' });
});
```

## Unauthenticated Tests

For tests that need no auth (login page tests, public pages), override `storageState` to clear it:

```ts
import { test, expect } from '@playwright/test';

test.use({ storageState: { cookies: [], origins: [] } });

test('login page shows sign-in form', async ({ page }) => {
  await page.goto('/auth/login');
  await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
});
```

## Worker-Scoped Auth for Parallel Tests

When tests run in parallel and each worker needs its own authenticated session (to avoid sharing session state), use worker-scoped fixtures:

```ts
import { test as base, type BrowserContext } from '@playwright/test';
import path from 'node:path';

export const test = base.extend<{}, { workerStorageState: string }>({
  storageState: ({ workerStorageState }, use) => use(workerStorageState),

  workerStorageState: [
    async ({ browser }, use) => {
      const id = test.info().parallelIndex;
      const fileName = path.resolve(`playwright/.auth/worker-${id}.json`);

      const page = await browser.newPage({
        storageState: undefined,
      });

      const account = { email: `user-${id}@example.com`, password: 'pass' };
      await page.goto('/auth/login');
      await page.getByLabel('Email address').fill(account.email);
      await page.getByLabel('Password').fill(account.password);
      await page.getByRole('button', { name: 'Sign in' }).click();
      await page.waitForURL('/dashboard');

      await page.context().storageState({ path: fileName });
      await page.close();
      await use(fileName);
    },
    { scope: 'worker' },
  ],
});

export { expect } from '@playwright/test';
```

## Security

- Add `playwright/.auth/` to `.gitignore` to avoid committing session data
- Use environment variables for credentials, never hardcode in test files
- Use separate test accounts with minimal permissions
- Regenerate auth state on each CI run (do not cache `storageState` files)
