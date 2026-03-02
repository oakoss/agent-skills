---
title: Advanced Assertions
description: Advanced assertion patterns including soft assertions, polling, retry blocks, custom matchers, and test annotations
tags:
  [
    expect,
    soft,
    poll,
    toPass,
    configure,
    extend,
    mergeExpects,
    annotation,
    tag,
    custom-matcher,
    retry,
    polling,
  ]
---

# Advanced Assertions

## Auto-Retrying vs Non-Retrying

| Category              | Behavior                          | Examples                                                               |
| --------------------- | --------------------------------- | ---------------------------------------------------------------------- |
| Auto-retrying (async) | Retry until timeout, must `await` | `toBeVisible`, `toHaveText`, `toHaveURL`, `toHaveValue`, `toBeEnabled` |
| Non-retrying (sync)   | Immediate check, no retry         | `toBe`, `toEqual`, `toHaveLength`, `toContain`, `toBeTruthy`           |

```typescript
import { test, expect } from '@playwright/test';

test('auto-retrying vs non-retrying', async ({ page }) => {
  await page.goto('/dashboard');

  // Auto-retrying — waits up to default timeout
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
  await expect(page).toHaveURL(/\/dashboard/);

  // Non-retrying — runs once against a resolved value
  const count = await page.getByRole('listitem').count();
  expect(count).toBeGreaterThan(0);
});
```

## Soft Assertions

`expect.soft()` continues the test on failure. All failures are reported at the end.

```typescript
test('verify dashboard widgets', async ({ page }) => {
  await page.goto('/dashboard');

  await expect.soft(page.getByTestId('revenue')).toHaveText('$1,200');
  await expect.soft(page.getByTestId('users')).toHaveText('340');
  await expect.soft(page.getByTestId('orders')).toHaveText('79');
});
```

### Bulk Soft Mode with expect.configure()

```typescript
test('bulk soft assertions', async ({ page }) => {
  await page.goto('/settings');

  const softExpect = expect.configure({ soft: true });

  await softExpect(page.getByLabel('Name')).toHaveValue('Jane');
  await softExpect(page.getByLabel('Email')).toHaveValue('jane@example.com');
  await softExpect(page.getByLabel('Role')).toHaveValue('Admin');
});
```

## Custom Timeout with expect.configure()

```typescript
test('slow page load', async ({ page }) => {
  await page.goto('/heavy-report');

  const slowExpect = expect.configure({ timeout: 15_000 });
  await slowExpect(page.getByRole('table')).toBeVisible();
});
```

### Custom Error Messages

Pass a string as the second argument to `expect()` for descriptive failure output.

```typescript
test('login flow', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('user@test.com');
  await page.getByLabel('Password').fill('secret');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(
    page.getByTestId('avatar'),
    'should be visible after login',
  ).toBeVisible();
});
```

## Polling with expect.poll()

Repeatedly invokes an async callback until the chained matcher passes.

```typescript
test('API becomes healthy', async ({ page }) => {
  await expect
    .poll(
      async () => {
        const response = await page.request.get('/api/health');
        return response.status();
      },
      {
        message: 'API should return 200',
        timeout: 30_000,
      },
    )
    .toBe(200);
});
```

### Custom Intervals

```typescript
await expect
  .poll(
    async () => {
      const response = await page.request.get('/api/status');
      return response.status();
    },
    {
      // Default intervals: [100, 250, 500, 1000]
      intervals: [1_000, 2_000, 10_000],
      timeout: 60_000,
    },
  )
  .toBe(200);
```

### Soft Polling

```typescript
const softExpect = expect.configure({ soft: true });

await softExpect
  .poll(
    async () => {
      const response = await page.request.get('/api/status');
      return response.status();
    },
    {
      timeout: 10_000,
    },
  )
  .toBe(200);
```

## Retry Blocks with toPass()

Retries an entire block of code until all inner assertions pass.

**WARNING: `toPass()` has a default timeout of 0 -- it retries forever. Always specify `timeout`.**

```typescript
test('wait for data sync', async ({ page }) => {
  await expect(async () => {
    const response = await page.request.get('/api/status');
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.synced).toBe(true);
  }).toPass({ timeout: 10_000 });
});
```

### Custom Intervals with toPass()

```typescript
await expect(async () => {
  const response = await page.request.get('/api/ready');
  expect(response.status()).toBe(200);
}).toPass({
  // Default intervals: [100, 250, 500, 1000]
  intervals: [1_000, 2_000, 10_000],
  timeout: 60_000,
});
```

## Custom Matchers with expect.extend()

Define domain-specific assertion methods that integrate with Playwright's retry mechanism.

```typescript
import { expect as baseExpect } from '@playwright/test';
import type { Locator } from '@playwright/test';

export { test } from '@playwright/test';

export const expect = baseExpect.extend({
  async toHaveAmount(
    locator: Locator,
    expected: number,
    options?: { timeout?: number },
  ) {
    const assertionName = 'toHaveAmount';
    let pass: boolean;
    let matcherResult: any;
    try {
      const expectation = this.isNot
        ? baseExpect(locator).not
        : baseExpect(locator);
      await expectation.toHaveAttribute(
        'data-amount',
        String(expected),
        options,
      );
      pass = true;
    } catch (e: any) {
      matcherResult = e.matcherResult;
      pass = false;
    }

    if (this.isNot) {
      pass = !pass;
    }

    const message = pass
      ? () =>
          this.utils.matcherHint(assertionName, undefined, undefined, {
            isNot: this.isNot,
          }) +
          `\n\nLocator: ${locator}\n` +
          `Expected: not ${this.utils.printExpected(expected)}\n` +
          (matcherResult
            ? `Received: ${this.utils.printReceived(matcherResult.actual)}`
            : '')
      : () =>
          this.utils.matcherHint(assertionName, undefined, undefined, {
            isNot: this.isNot,
          }) +
          `\n\nLocator: ${locator}\n` +
          `Expected: ${this.utils.printExpected(expected)}\n` +
          (matcherResult
            ? `Received: ${this.utils.printReceived(matcherResult.actual)}`
            : '');

    return {
      message,
      pass,
      name: assertionName,
      expected,
      actual: matcherResult?.actual,
    };
  },
});
```

Usage in tests:

```typescript
import { test, expect } from './fixtures';

test('cart has correct amount', async ({ page }) => {
  await page.goto('/cart');
  await expect(page.getByTestId('cart')).toHaveAmount(5);
  await expect(page.getByTestId('cart')).not.toHaveAmount(0);
});
```

## Merging Custom Matchers with mergeExpects()

Combine custom matchers from multiple fixture files into a single `expect`.

```typescript
import { mergeTests, mergeExpects } from '@playwright/test';
import { test as dbTest, expect as dbExpect } from 'database-test-utils';
import { test as a11yTest, expect as a11yExpect } from 'a11y-test-utils';

export const expect = mergeExpects(dbExpect, a11yExpect);
export const test = mergeTests(dbTest, a11yTest);
```

```typescript
import { test, expect } from './fixtures';

test('dashboard passes all checks', async ({ page, database }) => {
  await expect(database).toHaveDatabaseUser('admin');
  await expect(page).toPassA11yAudit();
});
```

## Test Annotations

### Inline Annotation on test()

```typescript
import { test, expect } from '@playwright/test';

test(
  'test login page',
  {
    annotation: {
      type: 'issue',
      description: 'https://github.com/org/repo/issues/123',
    },
  },
  async ({ page }) => {
    await page.goto('/login');
  },
);
```

### Multiple Annotations

```typescript
test(
  'test full report',
  {
    annotation: [
      { type: 'issue', description: 'https://github.com/org/repo/issues/123' },
      { type: 'docs', description: 'https://example.com/docs/reports' },
    ],
  },
  async ({ page }) => {
    await page.goto('/reports');
  },
);
```

### Runtime Annotations via testInfo

```typescript
test('dashboard', async ({ page }, testInfo) => {
  testInfo.annotations.push({
    type: 'issue',
    description: 'https://github.com/org/repo/issues/456',
  });

  await page.goto('/dashboard');
  await expect(page.getByRole('heading')).toHaveText('Dashboard');
});
```

## Describe-Level Annotations

Apply tags and annotations to an entire `test.describe` group.

```typescript
import { test, expect } from '@playwright/test';

test.describe(
  'reporting suite',
  {
    tag: '@report',
    annotation: {
      type: 'docs',
      description: 'https://example.com/docs/reporting',
    },
  },
  () => {
    test('report header', async ({ page }) => {
      await page.goto('/reports');
      await expect(page.getByRole('heading')).toHaveText('Reports');
    });

    test(
      'full report',
      {
        tag: ['@slow', '@vrt'],
      },
      async ({ page }) => {
        await page.goto('/reports/full');
        await expect(page.getByRole('table')).toBeVisible();
      },
    );
  },
);
```

Run tagged tests:

```bash
npx playwright test --grep @report
npx playwright test --grep @slow
```
