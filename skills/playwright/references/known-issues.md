---
title: Known Issues
description: 10 documented Playwright issues with symptoms, sources, and prevention patterns
tags:
  [
    errors,
    issues,
    target-closed,
    timeout,
    detached-frame,
    bot-detection,
    download,
    infinite-scroll,
    websocket,
    page-pause,
    CI,
    extension,
    permissions,
  ]
---

# Known Issues

## Issue 1: Target Closed Error

- **Error:** `Protocol error (Target.sendMessageToTarget): Target closed.`
- **Source:** [GitHub Issue #2938](https://github.com/microsoft/playwright/issues/2938)
- **Cause:** Page closed before action completed, or browser crashed
- **Fix:**

```typescript
try {
  await page.goto(url, { timeout: 30000 });
} catch (error) {
  if (error.message.includes('Target closed')) {
    await browser.close();
    browser = await chromium.launch();
  }
}
```

## Issue 2: Element Not Found

- **Error:** `TimeoutError: waiting for selector "button" failed: timeout 30000ms exceeded`
- **Cause:** Element doesn't exist, wrong selector, or page hasn't loaded
- **Fix:**

```typescript
// Locators auto-wait for elements to appear
await page.locator('button.submit').click();

// With custom timeout
await page.locator('button.submit').click({ timeout: 10000 });
```

## Issue 3: Navigation Timeout

- **Error:** `TimeoutError: page.goto: Timeout 30000ms exceeded.`
- **Cause:** Slow page load, infinite spinner, or firewall blocking
- **Fix:**

```typescript
try {
  await page.goto(url, {
    waitUntil: 'domcontentloaded', // Less strict than networkidle
    timeout: 60000,
  });
} catch (error) {
  if (error.name === 'TimeoutError') {
    const title = await page.title();
    if (title) console.log('Page loaded despite timeout');
  }
}
```

## Issue 4: Detached Frame Error

- **Error:** `Error: Execution context was destroyed, most likely because of a navigation.`
- **Source:** [GitHub Issue #3934](https://github.com/microsoft/playwright/issues/3934)
- **Cause:** SPA navigation re-rendered the element
- **Fix:** Use locators (they re-query automatically) and wait for navigation

```typescript
async function safeClick(page, selector) {
  await page.locator(selector).click();
  await page.waitForLoadState('domcontentloaded');
}
```

## Issue 5: Bot Detection (403/Captcha)

- **Symptom:** Page returns 403 or shows captcha
- **Cause:** Site detects `navigator.webdriver`, datacenter IP, or fingerprint mismatch
- **Fix:** Use stealth mode + residential IP (see stealth-mode.md)

## Issue 6: File Download Not Completing

- **Cause:** Download event not awaited, file stream not closed
- **Fix:**

```typescript
const [download] = await Promise.all([
  page.waitForEvent('download'),
  page.locator('a.download-link').click(),
]);

await download.saveAs('./downloads/' + download.suggestedFilename());
```

## Issue 7: Infinite Scroll Not Loading More

- **Cause:** Scroll event not triggered correctly, or scrolling too fast
- **Fix:**

```typescript
let previousHeight = 0;
while (true) {
  const currentHeight = await page.evaluate(() => document.body.scrollHeight);
  if (currentHeight === previousHeight) break;

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(2000);
  previousHeight = currentHeight;
}
```

## Issue 8: WebSocket Connection Failed

- **Error:** `WebSocket connection to 'ws://...' failed`
- **Cause:** Browser launched without `--no-sandbox` in restrictive environments
- **Fix:**

```typescript
const browser = await chromium.launch({
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});
```

## Issue 9: page.pause() Disables Timeout in Headless Mode

- **Error:** Tests hang indefinitely in CI when `page.pause()` is present
- **Source:** [GitHub Issue #38754](https://github.com/microsoft/playwright/issues/38754)
- **Cause:** `page.pause()` is ignored in headless mode but disables test timeout
- **Impact:** HIGH — causes CI pipelines to hang indefinitely
- **Fix:**

```typescript
if (!process.env.CI && !process.env.HEADLESS) {
  await page.pause();
}
```

## Issue 10: Permission Prompts Block Extension Testing in CI

- **Error:** Tests hang on permission prompts when testing browser extensions
- **Source:** [GitHub Issue #38670](https://github.com/microsoft/playwright/issues/38670)
- **Cause:** `launchPersistentContext` with extensions shows non-dismissible permission prompts
- **Impact:** HIGH — blocks automated extension testing in CI/CD
- **Fix:**

```typescript
// Use regular context instead of persistent context for CI
const context = await browser.newContext({
  permissions: [
    'clipboard-read',
    'clipboard-write',
    'notifications',
    'geolocation',
  ],
});
```
