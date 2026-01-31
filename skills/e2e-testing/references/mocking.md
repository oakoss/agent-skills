---
title: Network Mocking
description: Network mocking with page.route, REST API mocking, response modification, image blocking, HAR replay, and WebSocket mocking
tags:
  [
    mocking,
    page-route,
    har-replay,
    network-interception,
    websocket,
    api-mocking,
    response-modification,
  ]
---

# Network Mocking

## Why Mock

1. **Speed**: Skipping real network calls makes tests 5-10x faster
2. **Stability**: Third-party APIs (Stripe, GitHub) can be down or have rate limits
3. **Edge case testing**: Easily simulate 500 errors, timeouts, or malformed JSON
4. **Determinism**: Tests produce the same results regardless of backend state

## Mocking a REST API

Intercept requests and return custom responses:

```ts
test('shows error when API fails', async ({ page }) => {
  await page.route('**/api/user/*', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    }),
  );

  await page.goto('/profile');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
```

## Mocking Successful Responses

```ts
test('displays user profile', async ({ page }) => {
  await page.route('**/api/user/1', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 1,
        name: 'Jane Doe',
        email: 'jane@example.com',
      }),
    }),
  );

  await page.goto('/profile/1');
  await expect(page.getByRole('heading', { name: 'Jane Doe' })).toBeVisible();
});
```

## Modifying Real Responses

Intercept the real response and modify it before it reaches the page:

```ts
test('adds feature flag to API response', async ({ page }) => {
  await page.route('**/api/config', async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.featureFlags.newDashboard = true;

    await route.fulfill({ response, json });
  });

  await page.goto('/dashboard');
  await expect(page.getByText('New Dashboard')).toBeVisible();
});
```

## Waiting for API Responses

Use `page.waitForResponse` to wait for a specific request to complete:

```ts
test('submits form and waits for API', async ({ page }) => {
  await page.goto('/contact');
  await page.getByLabel('Message').fill('Hello');
  await page.getByRole('button', { name: 'Send' }).click();

  const response = await page.waitForResponse('**/api/messages');
  expect(response.status()).toBe(201);
});
```

## Blocking Images for Performance

Skip image downloads to speed up tests:

```ts
await page.route('**/*.{png,jpg,jpeg,gif,svg,webp}', (route) => route.abort());
```

## Conditional Mocking

Mock only specific conditions while letting other requests through:

```ts
await page.route('**/api/**', (route) => {
  if (route.request().method() === 'POST') {
    return route.fulfill({
      status: 201,
      body: JSON.stringify({ id: 'new-item' }),
    });
  }
  return route.continue();
});
```

## HAR Replay

Record real network traffic into a `.har` file and replay it during tests:

```ts
await page.routeFromHAR('tests/fixtures/api-snapshot.har', {
  url: '**/api/**',
  update: false,
});
```

### Recording HAR Files

Set `update: true` to capture fresh traffic:

```ts
await page.routeFromHAR('tests/fixtures/api-snapshot.har', {
  url: '**/api/**',
  update: true,
});
```

Or record from the command line:

```bash
npx playwright open --save-har=tests/fixtures/api-snapshot.har https://your-app.com
```

Switch `update` back to `false` for stable test execution.

## WebSocket Mocking

Mock WebSocket connections for real-time features:

```ts
test('receives live notification', async ({ page }) => {
  const ws = await page.routeWebSocket('**/ws/notifications', (ws) => {
    ws.onMessage((message) => {
      if (message === 'ping') {
        ws.send('pong');
      }
    });
  });

  await page.goto('/dashboard');

  ws.send(JSON.stringify({ type: 'notification', text: 'New message' }));

  await expect(page.getByText('New message')).toBeVisible();
});
```

## Route Patterns

| Pattern                     | Matches                                |
| --------------------------- | -------------------------------------- |
| `**/api/**`                 | Any URL containing `/api/`             |
| `**/api/user/*`             | Single path segment after `/api/user/` |
| `https://api.stripe.com/**` | All Stripe API calls                   |
| `**/*.{png,jpg}`            | All PNG and JPG files                  |

## Context-Level Mocking

Apply mocks to all pages within a context:

```ts
test('mock at context level', async ({ context, page }) => {
  await context.route('**/api/**', (route) =>
    route.fulfill({
      status: 200,
      body: JSON.stringify({ data: 'mocked' }),
    }),
  );

  await page.goto('/page-one');
  const popup = await page.waitForEvent('popup');
  await expect(popup.getByText('mocked')).toBeVisible();
});
```
