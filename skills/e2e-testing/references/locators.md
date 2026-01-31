---
title: Locators and Auto-Waiting
description: Role-based locator strategy, getByRole, getByText, getByLabel, chaining, filtering, auto-waiting assertions, shadow DOM piercing, and locator picker
tags:
  [
    locators,
    getByRole,
    getByText,
    getByLabel,
    auto-waiting,
    shadow-dom,
    chaining,
    filtering,
  ]
---

# Locators and Auto-Waiting

## Locator Priority

Prioritize locators that match how users and screen readers perceive the UI. Playwright recommends this order:

1. **`getByRole`** — matches ARIA roles (preferred for all interactive elements)
2. **`getByLabel`** — matches form fields by their associated label
3. **`getByPlaceholder`** — matches inputs by placeholder text
4. **`getByText`** — matches by visible text content
5. **`getByAltText`** — matches images by alt text
6. **`getByTitle`** — matches by title attribute
7. **`getByTestId`** — last resort fallback when no accessible attribute exists

## getByRole (Preferred)

Matches elements by their ARIA role and accessible name:

```ts
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('heading', { level: 1 }).toBeVisible();
await page.getByRole('link', { name: 'Documentation' }).click();
await page.getByRole('checkbox', { name: 'Accept terms' }).check();
await page.getByRole('textbox', { name: 'Search' }).fill('playwright');
```

Common roles: `button`, `link`, `heading`, `textbox`, `checkbox`, `radio`, `combobox`, `listbox`, `option`, `tab`, `tabpanel`, `dialog`, `alert`, `navigation`, `main`.

## getByLabel

Best for form fields with visible labels:

```ts
await page.getByLabel('Username').fill('john_doe');
await page.getByLabel('Password').fill('secret');
await page.getByLabel('Remember me').check();
```

## getByText

Best for verifying content and clicking non-interactive elements:

```ts
await expect(page.getByText('Success! Your order is placed.')).toBeVisible();
await page.getByText('Read more', { exact: true }).click();
```

Use `{ exact: true }` to prevent partial matches.

## getByTestId

Use only when no accessible attribute exists. Configure the test ID attribute in `playwright.config.ts`:

```ts
export default defineConfig({
  use: {
    testIdAttribute: 'data-testid',
  },
});
```

Then use in tests:

```ts
await page.getByTestId('nav-menu').click();
```

If you need `getByTestId`, consider fixing the accessibility tree first.

## Chaining and Filtering

Narrow locators by chaining or filtering to find elements within a specific scope:

```ts
const productCard = page.locator('.product-card').filter({
  hasText: 'Running Shoes',
});
await productCard.getByRole('button', { name: 'Add to cart' }).click();
```

Filter by another locator:

```ts
const row = page.getByRole('row').filter({
  has: page.getByRole('cell', { name: 'John' }),
});
await row.getByRole('button', { name: 'Edit' }).click();
```

Chain locators to scope within a parent:

```ts
const dialog = page.getByRole('dialog');
await dialog.getByRole('button', { name: 'Confirm' }).click();
```

## Locator Strictness

Locators are strict by default. If multiple elements match, the action throws. Use `.first()`, `.last()`, or `.nth(index)` to disambiguate:

```ts
await page.getByRole('button', { name: 'Delete' }).first().click();
await page.getByRole('listitem').nth(2).click();
```

## Why Avoid CSS/XPath

- **Fragile**: Changing `div.btn-primary` to `button.cta` breaks a CSS selector, but `getByRole('button')` continues to work
- **Not accessible**: Role-based locators enforce accessible HTML. If an element cannot be found by role, it is probably not accessible to screen readers
- **Coupled to implementation**: CSS selectors expose internal DOM structure that changes during refactors

## Auto-Waiting (Web-First Assertions)

Playwright automatically waits for elements to be actionable before performing actions. Web-first assertions retry until the condition is met or the timeout expires (default 5 seconds):

```ts
await expect(page.getByRole('alert')).toContainText('Error');
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
await expect(page.getByRole('dialog')).toBeVisible();
await expect(page.getByText('Loading')).toBeHidden();
```

Never use manual timeouts:

```ts
await page.waitForTimeout(3000);
```

Configure the assertion timeout globally in `playwright.config.ts`:

```ts
export default defineConfig({
  expect: {
    timeout: 10_000,
  },
});
```

## Shadow DOM

Playwright locators pierce the Shadow DOM by default. No special configuration is needed for Web Components:

```ts
await page.getByRole('button', { name: 'Shadow Button' }).click();
```

## Using the Locator Picker

Playwright provides tools to help find the best locator:

- **Codegen**: Run `npx playwright codegen <url>` to generate tests interactively. Playwright picks the most resilient locator automatically.
- **VS Code extension**: Use the Pick Locator button to click any element and get a recommended locator.
- **Inspector**: Run `npx playwright test --debug` to step through tests and inspect locators.
