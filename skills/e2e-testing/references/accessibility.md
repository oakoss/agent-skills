---
title: Accessibility Testing
description: Accessibility auditing with AxeBuilder from @axe-core/playwright, WCAG tag filtering, element exclusion, reusable fixtures, and CI integration
tags: [accessibility, axe-core, AxeBuilder, wcag, a11y, audit, fixtures]
---

# Accessibility Testing

## Setup

Install the official axe-core Playwright integration:

```bash
npm install -D @axe-core/playwright
```

Import `AxeBuilder` in test files:

```ts
import AxeBuilder from '@axe-core/playwright';
```

## Basic Full-Page Scan

Run a full accessibility scan and assert no violations:

```ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage has no accessibility violations', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page }).analyze();

  expect(results.violations).toEqual([]);
});
```

## Filtering by WCAG Standards

Target specific WCAG success criteria with `.withTags()`:

```ts
test('meets WCAG 2.1 AA standards', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

Common tag groups:

| Tags            | Standard                           |
| --------------- | ---------------------------------- |
| `wcag2a`        | WCAG 2.0 Level A                   |
| `wcag2aa`       | WCAG 2.0 Level AA                  |
| `wcag21a`       | WCAG 2.1 Level A                   |
| `wcag21aa`      | WCAG 2.1 Level AA                  |
| `best-practice` | axe-core best practices (not WCAG) |

## Scanning Specific Sections

Limit scans to a part of the page with `.include()` and `.exclude()`:

```ts
test('navigation menu is accessible', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .include('#navigation-menu')
    .analyze();

  expect(results.violations).toEqual([]);
});
```

Exclude known problematic elements (third-party widgets, ads):

```ts
const results = await new AxeBuilder({ page })
  .exclude('[id^="google_ads_iframe_"]')
  .exclude('#third-party-chat-widget')
  .analyze();
```

## Reusable Accessibility Fixture

Create a shared fixture with pre-configured rules:

```ts
import { test as base } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

type AxeFixture = {
  makeAxeBuilder: () => AxeBuilder;
};

export const test = base.extend<AxeFixture>({
  makeAxeBuilder: async ({ page }, use) => {
    const makeAxeBuilder = () =>
      new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .exclude('#known-issue-banner');

    await use(makeAxeBuilder);
  },
});

export { expect } from '@playwright/test';
```

Use in tests:

```ts
import { test, expect } from './fixtures';

test('dashboard is accessible', async ({ page, makeAxeBuilder }) => {
  await page.goto('/dashboard');

  const results = await makeAxeBuilder().analyze();

  expect(results.violations).toEqual([]);
});

test('settings page is accessible', async ({ page, makeAxeBuilder }) => {
  await page.goto('/settings');

  const results = await makeAxeBuilder().include('#settings-form').analyze();

  expect(results.violations).toEqual([]);
});
```

## Integrating with User Flow Tests

Add accessibility checks to existing E2E tests at key interaction points:

```ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('checkout flow is accessible at each step', async ({ page }) => {
  await page.goto('/cart');

  await test.step('cart page accessibility', async () => {
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });

  await page.getByRole('button', { name: 'Checkout' }).click();

  await test.step('payment page accessibility', async () => {
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
});
```

## Handling Violations in Reports

Log detailed violation info when tests fail:

```ts
test('page is accessible', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page }).analyze();

  for (const violation of results.violations) {
    console.log(
      `${violation.id}: ${violation.help} (${violation.impact})`,
      violation.nodes.map((n) => n.html),
    );
  }

  expect(results.violations).toEqual([]);
});
```

## Disabling Specific Rules

Disable rules that produce false positives in your context:

```ts
const results = await new AxeBuilder({ page })
  .disableRules(['color-contrast'])
  .analyze();
```

Use sparingly. Document why a rule is disabled.

## Limitations

- Automated tools detect roughly 30-50% of WCAG issues
- Cannot verify subjective criteria like alt text quality or logical reading order
- Cannot test keyboard navigation flow or screen reader announcements
- Complement automated scans with manual testing for full coverage
