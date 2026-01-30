---
title: Locators and Auto-Waiting
description: Role-based locator strategy, getByRole, getByText, getByLabel, auto-waiting assertions, shadow DOM piercing, and why CSS/XPath is legacy
tags:
  [
    locators,
    getByRole,
    getByText,
    getByLabel,
    auto-waiting,
    shadow-dom,
    accessibility,
  ]
---

# Locators and Auto-Waiting

## Role-Based Locator Strategy

Prioritize locators that match how a human or screen reader perceives the UI.

### getByRole (Preferred)

Matches elements based on their ARIA role:

```ts
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('heading', { level: 1 }).toBeVisible();
```

### getByText

Best for verifying content:

```ts
await expect(page.getByText('Success! Your order is placed.')).toBeVisible();
```

### getByLabel

Best for form fields:

```ts
await page.getByLabel('Username').fill('john_doe');
```

## Why Avoid CSS/XPath

- **Implementation Detail**: Changing `div.btn-primary` to `button.cta` breaks a CSS selector, but `getByRole('button')` continues to work
- **Accessibility**: Using role-based locators forces accessible HTML. If you cannot find an element by role, it is probably not accessible to screen readers either.

## Auto-Waiting (Web-First Assertions)

Playwright automatically waits for elements to be actionable (visible, stable, enabled, editable):

```ts
await expect(page.getByRole('alert')).toContainText('Error');
```

Never use manual timeouts:

```ts
await page.waitForTimeout(3000);
```

Web-first assertions automatically retry until the condition is met or the timeout expires (default 5 seconds).

## Shadow DOM

Playwright locators pierce the Shadow DOM by default. No special configuration is needed for modern Web Components.
