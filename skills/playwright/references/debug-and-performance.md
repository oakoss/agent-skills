---
title: Debug Methods and Performance
description: v1.56+ debug methods (console messages, page errors, network requests), v1.57+ mouse control with steps, and Speedboard performance analysis
tags:
  [
    debug,
    console,
    consoleMessages,
    pageErrors,
    requests,
    network,
    mouse,
    steps,
    click,
    drag,
    Speedboard,
    performance,
    profiling,
  ]
---

# Debug Methods and Performance

## Console Messages (v1.56+)

Capture console output without event listeners:

```typescript
import { test, expect } from '@playwright/test';

test('capture console output', async ({ page }) => {
  await page.goto('https://example.com');

  const messages = page.consoleMessages();
  const errors = messages.filter((m) => m.type() === 'error');
  const logs = messages.filter((m) => m.type() === 'log');

  console.log(
    'Console errors:',
    errors.map((m) => m.text()),
  );
});
```

## Page Errors (v1.56+)

Get uncaught JavaScript exceptions:

```typescript
test('check for JavaScript errors', async ({ page }) => {
  await page.goto('https://example.com');

  const errors = page.pageErrors();
  expect(errors).toHaveLength(0);
});
```

## Network Requests (v1.56+)

Inspect all network activity:

```typescript
test('inspect API calls', async ({ page }) => {
  await page.goto('https://example.com');

  const requests = page.requests();
  const apiCalls = requests.filter((r) => r.url().includes('/api/'));
  console.log('API calls made:', apiCalls.length);

  const failed = requests.filter((r) => r.failure());
  expect(failed).toHaveLength(0);
});
```

Use for: debugging test failures, verifying no console errors, auditing network activity.

## Advanced Mouse Control (v1.57+)

The `steps` option provides fine-grained control over mouse movement:

### Click with Steps

```typescript
// Smooth, human-like movement (10 intermediate steps)
await page.locator('button.submit').click({ steps: 10 });

// Fast click (fewer steps)
await page.locator('button.cancel').click({ steps: 2 });
```

### Drag with Steps

```typescript
const source = page.locator('#draggable');
const target = page.locator('#dropzone');

// Smooth drag animation
await source.dragTo(target, { steps: 20 });

// Quick drag
await source.dragTo(target, { steps: 5 });
```

Anti-detection benefit: many bot detection systems look for instantaneous mouse movements. Using `steps: 10` or higher simulates realistic human behavior.

## Speedboard Performance Analysis (v1.57+)

The HTML reporter includes Speedboard — a dedicated tab for identifying slow tests.

**Enable:**

```typescript
export default defineConfig({
  reporter: 'html',
});
```

**View:**

```bash
npx playwright test --reporter=html
npx playwright show-report
```

**What Speedboard shows:**

- All tests sorted by execution time (slowest first)
- Breakdown of wait times
- Network request durations
- Inefficient selectors and unnecessary waits

**Use cases:**

- Optimize test suite runtime
- Find tests with excessive `waitForTimeout()` calls
- Identify slow API responses affecting tests
- Prioritize refactoring for slowest tests
