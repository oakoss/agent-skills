---
title: Test Organization
description: Test organization with tags, annotations, test.step, describe blocks, project configuration, and folder structure patterns
tags: [tags, annotations, test-step, describe, projects, organization, grep]
---

# Test Organization

## Tags

Tags categorize tests for selective execution. Use the `tag` property:

```ts
test('quick login check', { tag: ['@smoke'] }, async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading')).toBeVisible();
});

test(
  'full checkout flow',
  { tag: ['@regression', '@slow'] },
  async ({ page }) => {
    // ...
  },
);
```

Apply tags to a group of tests:

```ts
test.describe('payment flows', { tag: ['@payments'] }, () => {
  test('credit card payment', async ({ page }) => {
    // ...
  });

  test('PayPal payment', async ({ page }) => {
    // ...
  });
});
```

### Running Tagged Tests

```bash
npx playwright test --grep @smoke
npx playwright test --grep @regression
npx playwright test --grep-invert @slow
```

Configure in `playwright.config.ts`:

```ts
export default defineConfig({
  grep: /@smoke/,
  grepInvert: /@slow/,
});
```

### Recommended Tags

| Tag           | Purpose                   |
| ------------- | ------------------------- |
| `@smoke`      | Fast critical path checks |
| `@regression` | Full regression suite     |
| `@slow`       | Long-running tests        |
| `@visual`     | Visual regression tests   |
| `@a11y`       | Accessibility audits      |

## Annotations

Built-in annotations control test execution:

```ts
test.skip('feature not implemented yet', async ({ page }) => {
  // Skipped entirely
});

test.fixme('known bug - crashes on Safari', async ({ page }) => {
  // Skipped, marked as needing fix
});

test('known failure', async ({ page }) => {
  test.fail();
  // Playwright runs this and expects it to fail
});

test('heavy computation', async ({ page }) => {
  test.slow();
  // Triples the test timeout
});
```

### Conditional Annotations

Skip based on conditions:

```ts
test('Safari-only feature', async ({ page, browserName }) => {
  test.skip(browserName !== 'webkit', 'Safari-only test');
  // ...
});
```

### Custom Annotations

Add metadata visible in reports:

```ts
test('checkout flow', async ({ page }) => {
  test.info().annotations.push({
    type: 'issue',
    description: 'https://github.com/org/repo/issues/123',
  });
  // ...
});
```

## test.step

Break complex tests into named steps visible in traces and reports:

```ts
test('complete purchase flow', async ({ page }) => {
  await test.step('add item to cart', async () => {
    await page.goto('/products');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByText('Added to cart')).toBeVisible();
  });

  await test.step('proceed to checkout', async () => {
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();
  });

  await test.step('complete payment', async () => {
    await page.getByLabel('Card number').fill('4242424242424242');
    await page.getByRole('button', { name: 'Pay' }).click();
    await expect(page.getByText('Order confirmed')).toBeVisible();
  });
});
```

Steps nest for complex workflows:

```ts
await test.step('fill shipping address', async () => {
  await test.step('enter street address', async () => {
    await page.getByLabel('Street').fill('123 Main St');
  });
  await test.step('enter city and zip', async () => {
    await page.getByLabel('City').fill('Springfield');
    await page.getByLabel('ZIP').fill('62701');
  });
});
```

### Boxed Steps

Box a step to make error stack traces point to the step call site instead of the internal failure:

```ts
await test.step(
  'login',
  async () => {
    await loginPage.login('user@example.com', 'pass');
  },
  { box: true },
);
```

## Describe Blocks

Group related tests:

```ts
test.describe('authenticated user', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
  });

  test('sees welcome message', async ({ page }) => {
    await expect(page.getByText('Welcome back')).toBeVisible();
  });

  test('can update profile', async ({ page }) => {
    await page.getByRole('link', { name: 'Settings' }).click();
    // ...
  });
});
```

### Serial Mode

Force tests within a describe to run sequentially:

```ts
test.describe.configure({ mode: 'serial' });

test.describe('onboarding wizard', () => {
  test('step 1: create account', async ({ page }) => {
    // ...
  });

  test('step 2: choose plan', async ({ page }) => {
    // ...
  });
});
```

Use serial mode sparingly. Prefer independent, isolated tests.

## Projects for Test Organization

Use Playwright projects to run different test configurations:

```ts
export default defineConfig({
  projects: [
    {
      name: 'smoke',
      grep: /@smoke/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'regression',
      grep: /@regression/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'mobile',
      use: { ...devices['iPhone 14'] },
    },
  ],
});
```

## Config-Level Test Tags (v1.57+)

Apply tags to all tests in a project via `testConfig.tag`:

```ts
export default defineConfig({
  projects: [
    {
      name: 'smoke',
      testMatch: /smoke\/.*\.spec\.ts/,
      use: { ...devices['Desktop Chrome'] },
      tag: '@smoke',
    },
    {
      name: 'regression',
      use: { ...devices['Desktop Chrome'] },
      tag: '@regression',
    },
  ],
});
```

Tests in the `smoke` project automatically receive the `@smoke` tag without annotating individual tests. Combine with `--grep @smoke` to run all smoke tests across projects.

## Folder Structure

```sh
tests/
├── fixtures.ts              # Custom test fixtures
├── pages/                   # Page Object Model classes
│   ├── base-page.ts
│   ├── login-page.ts
│   └── dashboard-page.ts
├── auth.setup.ts            # Authentication setup
├── smoke/                   # Smoke tests
│   └── critical-paths.spec.ts
├── features/                # Feature tests
│   ├── checkout.spec.ts
│   ├── search.spec.ts
│   └── settings.spec.ts
└── visual/                  # Visual regression tests
    └── screenshots.spec.ts
```

## Hooks

```ts
test.beforeAll(async () => {
  // Runs once before all tests in the file
});

test.beforeEach(async ({ page }) => {
  // Runs before each test
});

test.afterEach(async ({ page }) => {
  // Runs after each test
});

test.afterAll(async () => {
  // Runs once after all tests in the file
});
```

Prefer fixtures over hooks for reusable setup. Hooks are best for file-scoped shared state.
