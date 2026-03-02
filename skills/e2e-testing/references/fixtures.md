---
title: Fixtures
description: Advanced fixture patterns — scoping, composition, auto fixtures, boxed fixtures, options, timeouts, and data-driven tests
tags:
  [
    fixtures,
    worker-scope,
    auto-fixtures,
    mergeTests,
    boxed,
    options,
    data-driven,
    parameterized,
  ]
---

# Fixtures

## Fixture Scoping

Test-scoped fixtures (the default) are created fresh for every test. Worker-scoped fixtures are created once per worker process and shared across all tests that worker runs.

```ts
import { test as base } from '@playwright/test';

type WorkerFixtures = {
  dbName: string;
};

const test = base.extend<{}, WorkerFixtures>({
  dbName: [
    async ({}, use, workerInfo) => {
      const name = `test_db_${workerInfo.workerIndex}`;
      await createDatabase(name);
      await use(name);
      await dropDatabase(name);
    },
    { scope: 'worker' },
  ],
});
```

Worker-scoped fixtures get a separate timeout equal to the test timeout. Use them for: database seeding, API auth tokens, expensive one-time setup.

Worker-scoped fixtures cannot depend on test-scoped fixtures. Test-scoped fixtures can depend on worker-scoped ones.

## workerIndex vs parallelIndex

`workerInfo.workerIndex` is unique per worker for the entire test run and never reused. Use it for naming resources that must not collide across workers (temp DB names, log files, ports).

`testInfo.parallelIndex` ranges from 0 to `workers - 1` and is reused across retries. Use it for partitioning a fixed pool of resources (pre-seeded user accounts, pre-allocated ports).

```ts
const test = base.extend<
  {},
  { testAccount: { email: string; password: string } }
>({
  testAccount: [
    async ({}, use, workerInfo) => {
      // parallelIndex reuses indices — maps to pre-seeded accounts
      const accounts = [
        { email: 'user0@test.com', password: 'pass0' },
        { email: 'user1@test.com', password: 'pass1' },
        { email: 'user2@test.com', password: 'pass2' },
        { email: 'user3@test.com', password: 'pass3' },
      ];
      await use(accounts[workerInfo.parallelIndex]);
    },
    { scope: 'worker' },
  ],
});
```

## Automatic Fixtures

`{ auto: true }` runs the fixture for every test without the test explicitly requesting it. Use for cross-cutting concerns: logging, screenshots on failure, performance instrumentation.

```ts
import { test as base } from '@playwright/test';

const test = base.extend<{ serverLogs: void }>({
  serverLogs: [
    async ({}, use, testInfo) => {
      const logs: string[] = [];
      const collector = startLogCollector(logs);

      await use();

      if (testInfo.status !== testInfo.expectedStatus) {
        await testInfo.attach('server-logs', {
          body: logs.join('\n'),
          contentType: 'text/plain',
        });
      }
      collector.stop();
    },
    { auto: true },
  ],
});
```

Auto fixtures can be test-scoped or worker-scoped. Combine `{ auto: true, scope: 'worker' }` for one-time per-worker setup that every test benefits from.

## Composing Fixtures with mergeTests

When multiple fixture modules each export their own `test`, merge them into a single `test` with `mergeTests`:

```ts
import { mergeTests } from '@playwright/test';
import { test as a11yTest } from './a11y-fixtures';
import { test as accountsTest } from './account-fixtures';
import { test as dbTest } from './db-fixtures';

export const test = mergeTests(a11yTest, accountsTest, dbTest);
```

For one or two modules, chain `base.extend()` calls instead:

```ts
import { test as base } from '@playwright/test';

const withDb = base.extend<{ db: Database }>({
  db: async ({}, use) => {
    const db = await connectDb();
    await use(db);
    await db.disconnect();
  },
});

export const test = withDb.extend<{ apiClient: ApiClient }>({
  apiClient: async ({ db }, use) => {
    await use(new ApiClient(db));
  },
});
```

`mergeExpects` works the same way for combining custom matchers:

```ts
import { mergeExpects } from '@playwright/test';
import { expect as a11yExpect } from './a11y-matchers';
import { expect as snapshotExpect } from './snapshot-matchers';

export const expect = mergeExpects(a11yExpect, snapshotExpect);
```

## Boxed Fixtures

`{ box: true }` hides fixture setup steps from the HTML report. When a boxed fixture fails, the report shows the failure at the test level rather than buried inside fixture internals.

```ts
const test = base.extend<{ page: Page }>({
  page: [
    async ({ browser }, use) => {
      const context = await browser.newContext();
      const page = await context.newPage();
      await use(page);
      await context.close();
    },
    { box: true },
  ],
});
```

Use for infrastructure fixtures where the internal steps are noise in test reports.

## Fixture Options

`{ option: true }` makes a fixture configurable via `playwright.config.ts` or `test.use()`:

```ts
type Options = {
  defaultLocale: string;
  currencyCode: string;
};

const test = base.extend<Options>({
  defaultLocale: ['en-US', { option: true }],
  currencyCode: ['USD', { option: true }],
});

export default test;
```

Override per-project in config:

```ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'en',
      use: { defaultLocale: 'en-US', currencyCode: 'USD' },
    },
    {
      name: 'de',
      use: { defaultLocale: 'de-DE', currencyCode: 'EUR' },
    },
  ],
});
```

Override per-describe block:

```ts
test.describe('Japanese locale', () => {
  test.use({ defaultLocale: 'ja-JP', currencyCode: 'JPY' });

  test('formats prices in yen', async ({
    page,
    defaultLocale,
    currencyCode,
  }) => {
    // ...
  });
});
```

Use options for: locale, currency, feature-flag variants, API base URLs. Avoids duplicating test logic across configurations.

## Fixture Timeout

Set an independent timeout on slow fixtures, separate from the test timeout:

```ts
const test = base.extend<{}, { heavySeed: void }>({
  heavySeed: [
    async ({}, use) => {
      await seedLargeDataset();
      await use();
    },
    { scope: 'worker', timeout: 60_000 },
  ],
});
```

If a fixture exceeds its timeout, the test fails with a clear message identifying which fixture timed out.

## Data-Driven Tests

Generate parameterized tests with `for...of`. Each iteration becomes a separate named test in the report:

```ts
const cases = [
  { type: 'checking', label: 'Checking Account' },
  { type: 'savings', label: 'Savings Account' },
  { type: 'money-market', label: 'Money Market Account' },
];

for (const { type, label } of cases) {
  test(`creates a ${type} account`, async ({ page }) => {
    await page.goto('/accounts/new');
    await page
      .getByRole('combobox', { name: 'Account type' })
      .selectOption(type);
    await page.getByRole('button', { name: 'Create' }).click();
    await expect(page.getByRole('heading')).toHaveText(label);
  });
}
```

For CSV-driven tests, read the file and parse it:

```ts
import fs from 'node:fs';
import path from 'node:path';
import { test, expect } from '@playwright/test';

const csv = fs.readFileSync(path.join(__dirname, 'test-data.csv'), 'utf-8');
const rows = csv
  .trim()
  .split('\n')
  .slice(1)
  .map((line) => {
    const [email, name, role] = line.split(',');
    return { email, name, role };
  });

for (const { email, name, role } of rows) {
  test(`user ${email} has role ${role}`, async ({ page }) => {
    await page.goto(`/admin/users?search=${email}`);
    await expect(page.getByRole('cell', { name })).toBeVisible();
    await expect(page.getByRole('cell', { name: role })).toBeVisible();
  });
}
```

Wrap data-driven tests in `test.describe` to group them in the report:

```ts
test.describe('account creation', () => {
  for (const { type, label } of cases) {
    test(`creates a ${type} account`, async ({ page }) => {
      // ...
    });
  }
});
```
