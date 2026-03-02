---
title: Input and Actions
description: Actionability auto-wait, text input, checkboxes, selects, file upload/download, click variants, drag and drop, keyboard, scrolling, iframes, dialogs, new tabs, and test modifiers
tags:
  [
    actionability,
    auto-wait,
    fill,
    pressSequentially,
    click,
    dblclick,
    check,
    uncheck,
    setChecked,
    selectOption,
    setInputFiles,
    dragTo,
    hover,
    focus,
    keyboard,
    scroll,
    download,
    iframe,
    frameLocator,
    dialog,
    popup,
    test.skip,
    test.fixme,
    test.fail,
    test.slow,
  ]
---

# Input and Actions

## Actionability Auto-Wait

Every action method auto-waits for specific checks before proceeding. If an element is detached during checks, the action retries from locator resolution.

| Action                                         | Visible | Stable | Enabled | Receives Events | Editable |
| ---------------------------------------------- | ------- | ------ | ------- | --------------- | -------- |
| `click`, `dblclick`, `check`, `uncheck`, `tap` | Yes     | Yes    | Yes     | Yes             | --       |
| `setChecked`                                   | Yes     | Yes    | Yes     | Yes             | --       |
| `hover`, `dragTo`                              | Yes     | Yes    | --      | Yes             | --       |
| `fill`, `clear`                                | Yes     | --     | Yes     | --              | Yes      |
| `selectOption`                                 | Yes     | --     | Yes     | --              | --       |
| `screenshot`, `selectText`                     | Yes     | --     | --      | --              | --       |
| `setInputFiles`                                | --      | --     | --      | --              | --       |
| `focus`, `blur`, `press`, `type`               | --      | --     | --      | --              | --       |
| `dispatchEvent`                                | --      | --     | --      | --              | --       |

`opacity: 0` passes the visibility check — Playwright considers it visible. Only `display: none` and `visibility: hidden` fail the check.

## Text Input

### fill() — Default Choice

Focuses the element, clears existing content, and sets the value in one step. Triggers `input` and `change` events.

```typescript
await page.getByLabel('Username').fill('jane');
await page.getByLabel('Start date').fill('2025-06-15');
await page.locator('[contenteditable]').fill('Rich text content');
```

Works on `<input>`, `<textarea>`, date/time inputs, and `[contenteditable]` elements.

### pressSequentially() — Per-Keystroke Input

Types one character at a time, firing full `keydown`/`keypress`/`keyup` events per character. Use only when the app has per-keystroke handling (autocomplete, debounced search, character validation).

```typescript
await page.getByLabel('Search').pressSequentially('playwright', { delay: 100 });
```

`fill()` is faster and more reliable — default to it unless you specifically need keystroke events.

## Checkboxes and Radio Buttons

### setChecked() — Idempotent, Preferred

```typescript
await page.getByLabel('I agree').setChecked(true);
await page.getByLabel('Newsletter').setChecked(false);
```

### check() / uncheck() — When You Know the State

```typescript
await page.getByRole('checkbox', { name: 'Terms' }).check();
await page.getByRole('checkbox', { name: 'Marketing' }).uncheck();

await expect(page.getByLabel('Terms')).toBeChecked();
```

## Select Dropdowns

```typescript
// By value attribute
await page.getByLabel('Country').selectOption('us');

// By visible label text
await page.getByLabel('Country').selectOption({ label: 'United States' });

// By zero-based index
await page.getByLabel('Country').selectOption({ index: 2 });

// Multiple selections
await page.getByLabel('Colors').selectOption(['red', 'green', 'blue']);
```

## File Upload

### Static Input

```typescript
import path from 'path';

await page
  .getByLabel('Upload')
  .setInputFiles(path.join(__dirname, 'report.pdf'));

await page
  .getByLabel('Upload')
  .setInputFiles([
    path.join(__dirname, 'file1.txt'),
    path.join(__dirname, 'file2.txt'),
  ]);

// Clear selection
await page.getByLabel('Upload').setInputFiles([]);

// Upload a directory
await page
  .getByLabel('Upload directory')
  .setInputFiles(path.join(__dirname, 'mydir'));
```

### In-Memory Buffer

```typescript
await page.getByLabel('Upload').setInputFiles({
  name: 'data.csv',
  mimeType: 'text/csv',
  buffer: Buffer.from('id,name\n1,Alice\n2,Bob'),
});
```

### Dynamic File Chooser

When the file input is created dynamically or triggered by a click:

```typescript
const fileChooserPromise = page.waitForEvent('filechooser');
await page.getByRole('button', { name: 'Upload' }).click();
const fileChooser = await fileChooserPromise;
await fileChooser.setFiles(path.join(__dirname, 'myfile.pdf'));
```

## Click Variants

```typescript
await page.getByRole('button', { name: 'Submit' }).click();
await page.getByRole('button', { name: 'Submit' }).dblclick();
await page.getByRole('button', { name: 'Options' }).click({ button: 'right' });

// Modifier keys
await page.getByRole('link', { name: 'Docs' }).click({ modifiers: ['Shift'] });
await page.getByText('Select me').click({ modifiers: ['ControlOrMeta'] });

// Click at specific position relative to top-left of element
await page.locator('canvas').click({ position: { x: 100, y: 200 } });

// Force click (skip actionability checks)
await page.getByRole('button', { name: 'Hidden' }).click({ force: true });
```

## Hover and Focus

```typescript
// Trigger tooltip or dropdown menu
await page.getByRole('link', { name: 'Products' }).hover();
await expect(page.getByRole('menu')).toBeVisible();

// Trigger focus/blur validation
await page.getByLabel('Email').focus();
await page.getByLabel('Email').blur();
await expect(page.getByText('Email is required')).toBeVisible();
```

## Drag and Drop

### High-Level API

```typescript
const source = page.getByTestId('drag-item');
const target = page.getByTestId('drop-zone');
await source.dragTo(target);
```

### Low-Level Fallback

For custom drag implementations that don't work with the high-level API:

```typescript
await page.getByTestId('drag-item').hover();
await page.mouse.down();
await page.getByTestId('drop-zone').hover();
await page.mouse.up();
```

## Keyboard

```typescript
// Press a key on a focused element
await page.getByLabel('Name').press('Tab');

// Global keyboard actions
await page.keyboard.press('Escape');
await page.keyboard.press('Control+a');
await page.keyboard.press('Meta+c');

// Key combinations
await page.keyboard.press('Shift+ArrowDown');

// Type and submit
await page.getByLabel('Search').fill('query');
await page.getByLabel('Search').press('Enter');
```

## Scrolling

```typescript
// Scroll element into view (auto-called by most actions)
await page.getByTestId('footer').scrollIntoViewIfNeeded();

// Mouse wheel scroll
await page.mouse.wheel(0, 500);

// Programmatic scroll
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
```

## File Downloads

```typescript
const downloadPromise = page.waitForEvent('download');
await page.getByRole('link', { name: 'Export CSV' }).click();
const download = await downloadPromise;

const filename = download.suggestedFilename();
await download.saveAs(path.join('downloads', filename));
```

Downloaded files are deleted when the browser context closes — always call `saveAs()` before the test ends.

## New Tabs and Popups

### target="\_blank" Links

```typescript
const pagePromise = context.waitForEvent('page');
await page.getByRole('link', { name: 'External docs' }).click();
const newPage = await pagePromise;
await newPage.waitForLoadState();
await expect(newPage).toHaveURL(/docs/);
```

### window.open() Popups

```typescript
const popupPromise = page.waitForEvent('popup');
await page.getByRole('button', { name: 'Open preview' }).click();
const popup = await popupPromise;
await popup.waitForLoadState();
```

### List Open Pages

```typescript
const allPages = context.pages();
```

## Iframes

### frameLocator() — Scoped Locators

```typescript
const frame = page.frameLocator('#payment-iframe');
await frame.getByLabel('Card number').fill('4242424242424242');
await frame.getByRole('button', { name: 'Pay' }).click();
```

### Imperative Access

```typescript
const frame = page.frame('checkout');
const frame2 = page.frame({ url: /stripe\.com/ });
```

## Dialog Handling

Dialogs must be handled — failing to call `accept()` or `dismiss()` hangs the action that triggered the dialog.

```typescript
// Alert / confirm
page.once('dialog', async (dialog) => {
  await dialog.accept();
});
await page.getByRole('button', { name: 'Delete' }).click();

// Dismiss instead of accept
page.once('dialog', async (dialog) => {
  await dialog.dismiss();
});

// Prompt with input
page.once('dialog', async (dialog) => {
  await dialog.accept('My answer');
});
await page.getByRole('button', { name: 'Rename' }).click();
```

Register the handler **before** the action that triggers the dialog. Use `page.once()` to avoid handling the next dialog unintentionally.

### beforeunload Dialogs

```typescript
// Triggers beforeunload — dialog must be handled separately
await page.close({ runBeforeUnload: true });
```

## Test Modifiers

```typescript
import { test, expect } from '@playwright/test';

// Skip unconditionally
test.skip('not yet implemented', async ({ page }) => {});

// Skip conditionally
test('mobile feature', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'Mobile-only feature');
  // ...test body
});

// Mark as known failure — test runs and asserts it DOES fail
test('known regression', async ({ page }) => {
  test.fail();
  await page.goto('/broken-page');
  await expect(page.getByText('Welcome')).toBeVisible();
});

// Mark as fixme — skipped but tracked in report as needing fix
test.fixme('flaky date picker', async ({ page }) => {});

// Triple the timeout for slow tests
test('large data export', async ({ page }) => {
  test.slow();
  // ...test with 3x default timeout
});
```

### Conditional Skip in beforeEach

```typescript
test.beforeEach(async ({ page }, testInfo) => {
  if (testInfo.project.name === 'firefox') {
    test.skip();
  }
  await page.goto('/');
});
```

| Modifier       | Behavior                                                |
| -------------- | ------------------------------------------------------- |
| `test.skip()`  | Skips the test, shown as skipped in report              |
| `test.fixme()` | Skips the test, shown as "fixme" in report              |
| `test.fail()`  | Runs the test and asserts it fails — fails if it passes |
| `test.slow()`  | Triples the test timeout                                |
