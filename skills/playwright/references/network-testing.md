---
title: Network Testing
description: Network interception, request mocking, HAR replay, API testing patterns, and route handlers
tags:
  [
    network,
    mock,
    intercept,
    route,
    fulfill,
    abort,
    HAR,
    api-testing,
    request,
    response,
    service-worker,
  ]
---

# Network Testing

## Route Handler Methods

Three methods on route objects control how requests are handled:

### Fulfill — Return Mock Response

```typescript
import { test, expect } from '@playwright/test';

test('mock API response', async ({ page }) => {
  await page.route('**/api/users', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Test User' }]),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});
```

### Abort — Block Resources

```typescript
test('block images to speed up test', async ({ page }) => {
  await page.route('**/*.{png,jpg,jpeg,gif,webp}', (route) => route.abort());
  await page.goto('/heavy-page');
});
```

### Continue — Forward with Modifications

```typescript
test('add auth header to requests', async ({ page }) => {
  await page.route('**/api/**', async (route) => {
    await route.continue({
      headers: {
        ...route.request().headers(),
        'x-custom-token': 'test-value',
      },
    });
  });

  await page.goto('/dashboard');
});
```

## Modify Live Responses with route.fetch()

Intercept the real response, modify it, and return the modified version:

```typescript
test('modify live API response', async ({ page }) => {
  await page.route('**/api/accounts', async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json[0].balance = -999.99;
    await route.fulfill({ response, json });
  });

  await page.goto('/accounts');
  await expect(page.getByText('-999.99')).toBeVisible();
});
```

Patch a single field while preserving the rest of the real response:

```typescript
await page.route('**/api/feature-flags', async (route) => {
  const response = await route.fetch();
  const json = await response.json();
  json.darkMode = true;
  await route.fulfill({ response, json });
});
```

## Glob Pattern Rules for page.route()

| Pattern | Matches                                         |
| ------- | ----------------------------------------------- |
| `*`     | Any characters EXCEPT `/`                       |
| `**`    | Any characters INCLUDING `/`                    |
| `?`     | A LITERAL question mark (NOT "any single char") |
| `{}`    | Alternatives: `**/*.{png,jpg}`                  |

`?` matching a literal question mark is a Playwright-specific difference from shell globs (changed in v1.55).

Patterns must match the ENTIRE URL. Use RegExp for partial matching:

```typescript
await page.route('**/api/users', handler);

await page.route(/\/api\/users\/\d+/, handler);
```

## HAR Record and Replay

Record network traffic to a HAR file:

```bash
npx playwright test --save-har=hars/api.har --save-har-glob="**/api/**"
```

Replay from HAR in tests:

```typescript
test('replay from HAR', async ({ page }) => {
  await page.routeFromHAR('hars/api.har', { url: '**/api/**' });
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});
```

Update HAR when API changes:

```typescript
test('update HAR on miss', async ({ page }) => {
  await page.routeFromHAR('hars/api.har', {
    url: '**/api/**',
    update: true,
  });
  await page.goto('/dashboard');
});
```

## Waiting for Network Events

Set up the wait BEFORE triggering the action that causes the network request:

### Wait for Response

```typescript
test('wait for API response', async ({ page }) => {
  await page.goto('/app');

  const responsePromise = page.waitForResponse('**/api/submit');
  await page.getByRole('button', { name: 'Submit' }).click();
  const response = await responsePromise;

  expect(response.status()).toBe(200);
});
```

### Wait for Response with Predicate

```typescript
const responsePromise = page.waitForResponse(
  (response) =>
    response.url().includes('/api/search') && response.status() === 200,
);
await page.getByRole('button', { name: 'Search' }).click();
const response = await responsePromise;
const data = await response.json();
expect(data.results.length).toBeGreaterThan(0);
```

### Wait for Request

```typescript
const requestPromise = page.waitForRequest('**/api/analytics');
await page.getByRole('button', { name: 'Track' }).click();
const request = await requestPromise;
expect(request.method()).toBe('POST');
```

## Network Lifecycle Events

### Confirm Fire-and-Forget Requests

```typescript
test('beacon request completes', async ({ page }) => {
  const requestFinished = page.waitForEvent('requestfinished', (req) =>
    req.url().includes('/api/analytics'),
  );

  await page.goto('/page-with-beacon');
  await page.getByRole('link', { name: 'Leave' }).click();
  await requestFinished;
});
```

### Detect Failed Requests

```typescript
test('handle request failure', async ({ page }) => {
  const failures: string[] = [];
  page.on('requestfailed', (request) => {
    failures.push(`${request.url()} - ${request.failure()?.errorText}`);
  });

  await page.goto('/app');
  expect(failures).toHaveLength(0);
});
```

## Service Worker Caveat

If Mock Service Worker (MSW) or any Service Worker is active, it intercepts requests BEFORE `page.route()` sees them, making route handlers silently ineffective.

Fix in config:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    serviceWorkers: 'block',
  },
});
```

Or per-context:

```typescript
const context = await browser.newContext({
  serviceWorkers: 'block',
});
```

## Context-Level Routing

`page.route()` only covers the page it is called on. For popups opened via `window.open()`, use `context.route()`:

```typescript
test('intercept popup requests', async ({ context, page }) => {
  await context.route('**/api/**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ mocked: true }),
    });
  });

  await page.goto('/app');
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.getByRole('button', { name: 'Open window' }).click(),
  ]);
  await expect(popup.getByText('mocked')).toBeVisible();
});
```

## API Testing in E2E

### Shared Cookie Context via page.request

The `request` fixture on a page shares the browser context cookies:

```typescript
test('verify server state after UI action', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();

  const response = await page.request.get('/api/profile');
  expect(response.ok()).toBeTruthy();
  const profile = await response.json();
  expect(profile.email).toBe('user@test.com');
});
```

### Isolated API Context

```typescript
import { test, expect, request } from '@playwright/test';

test('standalone API test', async () => {
  const apiContext = await request.newContext({
    baseURL: 'https://api.example.com',
    extraHTTPHeaders: {
      Authorization: 'Bearer test-token',
    },
  });

  const response = await apiContext.get('/users');
  expect(response.ok()).toBeTruthy();

  await apiContext.dispose();
});
```

### Data Setup and Teardown

```typescript
test.describe('order workflow', () => {
  let orderId: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post('/api/orders', {
      data: { product: 'widget', quantity: 1 },
    });
    orderId = (await response.json()).id;
  });

  test.afterAll(async ({ request }) => {
    await request.delete(`/api/orders/${orderId}`);
  });

  test('displays order', async ({ page }) => {
    await page.goto(`/orders/${orderId}`);
    await expect(page.getByText('widget')).toBeVisible();
  });
});
```

## Global HTTP Headers

Set headers attached to every browser request via config:

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    extraHTTPHeaders: {
      'x-request-id': 'playwright-test',
      Accept: 'application/json',
    },
  },
});
```

Or per-context:

```typescript
const context = await browser.newContext({
  extraHTTPHeaders: {
    'x-api-key': 'test-key',
  },
});
```
