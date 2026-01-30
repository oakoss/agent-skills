---
title: Network Mocking
description: Network mocking with page.route, REST API mocking, image blocking, HAR replay for high-fidelity mocks, and WebSocket mocking
tags:
  [
    mocking,
    page-route,
    har-replay,
    network-interception,
    websocket,
    api-mocking,
  ]
---

# Network Mocking

## Why Mock

1. **Speed**: Skipping real network calls makes tests 5-10x faster
2. **Stability**: Third-party APIs (Stripe, GitHub) can be down or have rate limits
3. **Edge Case Testing**: Easily simulate 500 errors, timeouts, or malformed JSON

## Mocking a REST API

```ts
test('shows error when API fails', async ({ page }) => {
  await page.route('**/api/user/*', (route) => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal Server Error' }),
    });
  });

  await page.goto('/profile');
  await expect(page.getByText('API Error')).toBeVisible();
});
```

## Blocking Images for Performance

In E2E tests, you often do not need real images. Block them to save bandwidth and speed up page load:

```ts
await page.route('**/*.{png,jpg,jpeg}', (route) => route.abort());
```

## HAR Replay

Record real network traffic into a `.har` file and replay it during tests for high-fidelity mocks:

```ts
await page.routeFromHAR('tests/fixtures/api-snapshot.har', {
  url: '**/api/**',
  update: false,
});
```

Set `update: true` during recording to capture fresh traffic, then switch to `false` for stable test execution.

## WebSocket Mocking

Playwright supports deep introspection and mocking of WebSocket messages, essential for testing real-time applications like chat, notifications, and live dashboards.
