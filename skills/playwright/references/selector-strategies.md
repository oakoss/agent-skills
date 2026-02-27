---
title: Selector Strategies
description: CSS, XPath, text, role, and data-testid selectors with chaining, Playwright-specific pseudo-classes, shadow DOM, debugging, and performance tips
tags:
  [
    selector,
    CSS,
    XPath,
    text,
    role,
    data-testid,
    locator,
    has-text,
    nth,
    shadow-DOM,
    getByRole,
    chaining,
  ]
---

# Selector Strategies

## Selector Hierarchy (Best to Worst)

1. **Role** — accessible, semantic (`getByRole`, `getByLabel`)
2. **Label / Text** — visible text content (`getByText`, `getByPlaceholder`)
3. **data-testid** — stable, survives refactors (`getByTestId`)
4. **CSS** — class or attribute selectors (`page.locator('.btn')`)
5. **XPath** — last resort (`xpath=//button`)

## CSS Selectors

```typescript
// Basic
await page.locator('button').click(); // Tag
await page.locator('#submit').click(); // ID
await page.locator('.btn-primary').click(); // Class
await page.locator('[type="submit"]').click(); // Attribute

// Combinators
await page.locator('form > button').click(); // Child
await page.locator('form button').click(); // Descendant
await page.locator('label + input').click(); // Adjacent sibling

// Pseudo-classes
await page.locator('button:first-child').click();
await page.locator('button:nth-child(2)').click();
await page.locator('input:checked').click();

// Attribute patterns
await page.locator('[href^="https"]').click(); // Starts with
await page.locator('[href$=".pdf"]').click(); // Ends with
await page.locator('[href*="example"]').click(); // Contains
```

## XPath Selectors

Prefix with `xpath=`:

```typescript
await page.locator('xpath=//button[text()="Submit"]').click();
await page.locator('xpath=//button[contains(text(), "Sub")]').click();
await page.locator('xpath=//button[@class="submit"]').click();
await page.locator('xpath=(//button)[1]').click(); // First
await page.locator('xpath=(//button)[last()]').click(); // Last
await page
  .locator('xpath=//button[@type="submit" and contains(text(), "Save")]')
  .click();
```

## Text Selectors

```typescript
await page.locator('text=Submit').click(); // Exact match
await page.locator('text="Submit form"').click(); // Full string
await page.locator('text=/submit/i').click(); // Case-insensitive
await page.locator('text=/^Submit/').click(); // Regex
```

## Role Selectors (getByRole)

```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
```

## Playwright-Specific Pseudo-Classes

```typescript
// has-text: element containing text
await page.locator('button:has-text("Submit")').click();
await page.locator('article:has-text("Breaking News")').click();

// has: element containing selector
await page.locator('article:has(img.thumbnail)').click();
await page.locator('div:has(> button.primary)').click();

// is: filter match
await page.locator('button:is(.submit, .confirm)').click();

// not: exclude match
await page.locator('button:not(.disabled)').click();
```

## Chaining Selectors

```typescript
// Parent → child
await page.locator('article').locator('button.submit').click();

// Text context → child
await page.locator('div:has-text("Settings")').locator('button').click();

// Role within section
await page
  .locator('section.checkout')
  .getByRole('button', { name: 'Pay' })
  .click();
```

## List Item Selection

```typescript
await page.locator('.product-card').nth(2).click(); // 3rd item (0-indexed)
await page.locator('.product-card').first().click();
await page.locator('.product-card').last().click();
```

## Shadow DOM

Playwright pierces shadow DOM automatically:

```typescript
await page.click('custom-element .shadow-button');
```

## Debugging Selectors

```typescript
// Count matches
const count = await page.locator('button').count();
console.log(`Found ${count} buttons`);

// Get all matching elements
const elements = await page.locator('.item').all();
for (const el of elements) {
  console.log(await el.textContent());
}

// Visual inspector
// PWDEBUG=1 npx playwright test
```

## Performance

| Selector | Speed   | Notes                    |
| -------- | ------- | ------------------------ |
| ID       | Fastest | Browser-native           |
| Class    | Fast    | Browser-native           |
| Tag      | Fast    | Browser-native           |
| XPath    | Slower  | Parsed by Playwright     |
| Text     | Slower  | Must traverse text nodes |

For high-volume scraping, prefer CSS selectors.

## Common Pitfalls

| Problem                 | Cause                    | Fix                                       |
| ----------------------- | ------------------------ | ----------------------------------------- |
| Selector finds multiple | Not specific enough      | Add parent context or unique attribute    |
| Element not found       | Wrong selector or timing | Use locator API (auto-waits for elements) |
| Stale element           | DOM re-rendered          | Re-query after navigation                 |
| Slow selectors          | Complex XPath            | Simplify or use CSS                       |
| Flaky tests             | Timing issues            | Add explicit waits                        |
