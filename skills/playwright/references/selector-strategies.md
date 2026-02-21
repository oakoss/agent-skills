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
await page.click('button'); // Tag
await page.click('#submit'); // ID
await page.click('.btn-primary'); // Class
await page.click('[type="submit"]'); // Attribute

// Combinators
await page.click('form > button'); // Child
await page.click('form button'); // Descendant
await page.click('label + input'); // Adjacent sibling

// Pseudo-classes
await page.click('button:first-child');
await page.click('button:nth-child(2)');
await page.click('input:checked');

// Attribute patterns
await page.click('[href^="https"]'); // Starts with
await page.click('[href$=".pdf"]'); // Ends with
await page.click('[href*="example"]'); // Contains
```

## XPath Selectors

Prefix with `xpath=`:

```typescript
await page.click('xpath=//button[text()="Submit"]');
await page.click('xpath=//button[contains(text(), "Sub")]');
await page.click('xpath=//button[@class="submit"]');
await page.click('xpath=(//button)[1]'); // First
await page.click('xpath=(//button)[last()]'); // Last
await page.click('xpath=//button[@type="submit" and contains(text(), "Save")]');
```

## Text Selectors

```typescript
await page.click('text=Submit'); // Exact match
await page.click('text="Submit form"'); // Full string
await page.click('text=/submit/i'); // Case-insensitive
await page.click('text=/^Submit/'); // Regex
```

## Role Selectors (getByRole)

```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('textbox', { name: 'Email' }).fill('user@example.com');
```

## Playwright-Specific Pseudo-Classes

```typescript
// has-text: element containing text
await page.click('button:has-text("Submit")');
await page.click('article:has-text("Breaking News")');

// has: element containing selector
await page.click('article:has(img.thumbnail)');
await page.click('div:has(> button.primary)');

// is: filter match
await page.click('button:is(.submit, .confirm)');

// not: exclude match
await page.click('button:not(.disabled)');
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

| Problem                 | Cause                    | Fix                                    |
| ----------------------- | ------------------------ | -------------------------------------- |
| Selector finds multiple | Not specific enough      | Add parent context or unique attribute |
| Element not found       | Wrong selector or timing | Use `waitForSelector()` first          |
| Stale element           | DOM re-rendered          | Re-query after navigation              |
| Slow selectors          | Complex XPath            | Simplify or use CSS                    |
| Flaky tests             | Timing issues            | Add explicit waits                     |
