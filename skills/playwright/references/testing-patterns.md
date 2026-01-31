---
title: Testing Patterns
description: E2E test writing with Playwright Test including fixtures, assertions, locators, API testing, aria snapshots, test steps, and authentication
tags:
  [
    test,
    expect,
    fixture,
    assertion,
    locator,
    getByRole,
    getByLabel,
    getByText,
    toBeVisible,
    toContainClass,
    toMatchAriaSnapshot,
    API,
    request,
    auth,
    storageState,
    IndexedDB,
    test.step,
    beforeAll,
    beforeEach,
  ]
---

# Testing Patterns

## Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';

test('user can submit a form', async ({ page }) => {
  await page.goto('/contact');
  await page.getByLabel('Name').fill('Jane Doe');
  await page.getByLabel('Email').fill('jane@example.com');
  await page.getByRole('button', { name: 'Submit' }).click();

  await expect(page.getByText('Thank you')).toBeVisible();
});
```

Playwright auto-waits for elements before acting and auto-retries assertions.

## Test Organization

```typescript
import { test, expect } from '@playwright/test';

test.describe('checkout flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/shop');
  });

  test('add item to cart', async ({ page }) => {
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');
  });

  test('remove item from cart', async ({ page }) => {
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await page.getByRole('button', { name: 'Remove' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('0');
  });
});
```

## Locator Priority (Best to Worst)

1. `page.getByRole('button', { name: 'Submit' })` -- accessible, resilient
2. `page.getByLabel('Email')` -- form inputs by label
3. `page.getByPlaceholder('Search...')` -- placeholder text
4. `page.getByText('Welcome')` -- visible text content
5. `page.getByTestId('submit-btn')` -- data-testid attributes
6. `page.locator('button.submit')` -- CSS selectors (last resort)

## Common Assertions

```typescript
import { test, expect } from '@playwright/test';

test('assertion examples', async ({ page }) => {
  await page.goto('/dashboard');

  // Visibility
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('Loading')).not.toBeVisible();

  // Text content
  await expect(page.getByRole('status')).toHaveText('Active');
  await expect(page.getByRole('status')).toContainText('Act');

  // CSS class (v1.52+)
  await expect(page.getByRole('tab', { name: 'Settings' })).toContainClass(
    'active',
  );

  // Input values
  await expect(page.getByLabel('Email')).toHaveValue('jane@example.com');

  // Attributes
  await expect(page.getByRole('link', { name: 'Docs' })).toHaveAttribute(
    'href',
    '/docs',
  );

  // URL and title
  await expect(page).toHaveURL('/dashboard');
  await expect(page).toHaveTitle(/Dashboard/);

  // Count
  await expect(page.getByRole('listitem')).toHaveCount(3);

  // Accessible error message
  await expect(page.getByLabel('Email')).toHaveAccessibleErrorMessage(
    'Invalid email',
  );
});
```

## Aria Snapshot Assertions (v1.50+)

Validate accessibility tree structure using YAML templates:

```typescript
test('page has correct accessible structure', async ({ page }) => {
  await page.goto('/');

  await expect(page.locator('body')).toMatchAriaSnapshot(`
    - banner:
      - heading "My App" [level=1]
      - navigation:
        - link "Home"
        - link "About"
    - main:
      - heading "Welcome" [level=2]
  `);
});
```

Generate snapshots automatically with test generator or `locator.ariaSnapshot()`.

## Filtering Locators

```typescript
test('filter visible elements', async ({ page }) => {
  // Only match visible elements (v1.51+)
  const visibleButtons = page.getByRole('button').filter({ visible: true });

  // Filter by text content
  const saveButton = page.getByRole('button').filter({ hasText: 'Save' });

  // Filter by child locator
  const cardWithImage = page
    .locator('.card')
    .filter({ has: page.locator('img') });

  await saveButton.click();
});
```

## Test Steps with Timeout and Skip (v1.50+)

```typescript
test('multi-step checkout', async ({ page }) => {
  await test.step('fill shipping address', async (step) => {
    await page.getByLabel('Street').fill('123 Main St');
    await page.getByLabel('City').fill('Springfield');
    await page.getByRole('button', { name: 'Continue' }).click();
  });

  await test.step(
    'enter payment details',
    async (step) => {
      await page.getByLabel('Card number').fill('4242424242424242');
      await page.getByRole('button', { name: 'Pay' }).click();
    },
    { timeout: 15000 },
  );

  await test.step('verify confirmation', async (step) => {
    await expect(page.getByText('Order confirmed')).toBeVisible();

    // Attach screenshot to step for reporting
    const screenshot = await page.screenshot();
    await step.attach('confirmation', {
      body: screenshot,
      contentType: 'image/png',
    });
  });
});
```

## Authentication with Storage State

Authenticate once and reuse across tests:

```typescript
// auth.setup.ts
import { test as setup, expect } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill(process.env.PASSWORD);
  await page.getByRole('button', { name: 'Sign in' }).click();

  await expect(page.getByText('Dashboard')).toBeVisible();

  // Save authentication state (includes cookies and localStorage)
  await page.context().storageState({ path: '.auth/user.json' });
});
```

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'tests',
      dependencies: ['setup'],
      use: { storageState: '.auth/user.json' },
    },
  ],
});
```

IndexedDB can also be persisted (v1.51+):

```typescript
await page.context().storageState({
  path: '.auth/user.json',
  indexedDB: true,
});
```

## API Testing

Test APIs directly without browser overhead:

```typescript
import { test, expect } from '@playwright/test';

test('create and verify user via API', async ({ request }) => {
  // Create user
  const response = await request.post('/api/users', {
    data: { name: 'Jane', email: 'jane@example.com' },
  });
  expect(response.ok()).toBeTruthy();
  expect(response.status()).toBe(201);

  const user = await response.json();
  expect(user.name).toBe('Jane');

  // Verify user exists
  const getResponse = await request.get(`/api/users/${user.id}`);
  expect(getResponse.ok()).toBeTruthy();
});
```

## API Preconditions in UI Tests

```typescript
import { test, expect } from '@playwright/test';

let apiContext;

test.beforeAll(async ({ playwright }) => {
  apiContext = await playwright.request.newContext({
    baseURL: 'https://api.example.com',
    extraHTTPHeaders: {
      Authorization: `Bearer ${process.env.API_TOKEN}`,
    },
  });
});

test.afterAll(async () => {
  await apiContext.dispose();
});

test('new item appears in list', async ({ page }) => {
  // Set up precondition via API
  const response = await apiContext.post('/api/items', {
    data: { title: 'Test Item' },
  });
  expect(response.ok()).toBeTruthy();

  // Verify via UI
  await page.goto('/items');
  await expect(page.getByText('Test Item')).toBeVisible();
});
```

## Network Mocking

```typescript
test('display mocked data', async ({ page }) => {
  // Mock API response
  await page.route('**/api/users', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 1, name: 'Mock User' }]),
    }),
  );

  await page.goto('/users');
  await expect(page.getByText('Mock User')).toBeVisible();
});

test('simulate server error', async ({ page }) => {
  await page.route('**/api/data', (route) =>
    route.fulfill({ status: 500, body: 'Server Error' }),
  );

  await page.goto('/data');
  await expect(page.getByText('Something went wrong')).toBeVisible();
});
```

## Custom Fixtures

```typescript
import { test as base, expect } from '@playwright/test';

type MyFixtures = {
  adminPage: import('@playwright/test').Page;
};

const test = base.extend<MyFixtures>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: '.auth/admin.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

test('admin can manage users', async ({ adminPage }) => {
  await adminPage.goto('/admin/users');
  await expect(adminPage.getByRole('heading')).toHaveText('User Management');
});

export { test, expect };
```

## Visual Regression Testing

```typescript
test('homepage visual regression', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png');
});

test('component visual regression', async ({ page }) => {
  await page.goto('/components');
  await expect(page.getByTestId('card')).toHaveScreenshot('card.png', {
    maxDiffPixelRatio: 0.05,
  });
});
```

Update snapshots: `npx playwright test --update-snapshots`

## Flaky Test Detection (v1.50+)

```bash
npx playwright test --fail-on-flaky-tests
```

In config:

```typescript
export default defineConfig({
  retries: 2,
  failOnFlakyTests: true,
});
```

Tests that fail then pass on retry are flagged as flaky, and the run exits with code 1.

## Common Test Patterns

| Pattern             | Implementation                                        |
| ------------------- | ----------------------------------------------------- |
| Wait for navigation | `await page.waitForURL('/next-page')`                 |
| Wait for response   | `page.waitForResponse('**/api/data')`                 |
| File upload         | `page.getByLabel('Upload').setInputFiles('file.pdf')` |
| File download       | `const dl = await page.waitForEvent('download')`      |
| Dialog handling     | `page.on('dialog', d => d.accept())`                  |
| Emulate mobile      | `use: { ...devices['iPhone 15'] }`                    |
| Emulate dark mode   | `use: { colorScheme: 'dark' }`                        |
| Geolocation         | `use: { geolocation: { latitude, longitude } }`       |
| Timezone            | `use: { timezoneId: 'America/New_York' }`             |
