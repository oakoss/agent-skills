---
title: Common Patterns
description: Authenticated session scraping, infinite scroll with deduplication, multi-tab orchestration, screenshots, PDF generation, form automation, and retry with backoff
tags:
  [
    auth,
    login,
    session,
    cookies,
    infinite-scroll,
    multi-tab,
    screenshot,
    pdf,
    form,
    retry,
    backoff,
    pattern,
  ]
---

# Common Patterns

## Pattern 1: Authenticated Session Scraping

```typescript
import { chromium } from 'playwright';
import fs from 'fs/promises';

async function scrapeWithAuth() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Login
  await page.goto('https://example.com/login');
  await page.fill('input[name="email"]', process.env.EMAIL);
  await page.fill('input[name="password"]', process.env.PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });

  // Save session for reuse
  const cookies = await context.cookies();
  await fs.writeFile('session.json', JSON.stringify(cookies));

  // Navigate to protected page
  await page.goto('https://example.com/protected-data');
  const data = await page.locator('.data-table').textContent();

  await browser.close();
  return data;
}
```

## Pattern 2: Infinite Scroll with Deduplication

```typescript
async function scrapeInfiniteScroll(page, selector) {
  const items = new Set();
  let previousCount = 0;
  let noChangeCount = 0;

  while (noChangeCount < 3) {
    const elements = await page.locator(selector).all();

    for (const el of elements) {
      const text = await el.textContent();
      items.add(text);
    }

    if (items.size === previousCount) {
      noChangeCount++;
    } else {
      noChangeCount = 0;
    }

    previousCount = items.size;

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1500);
  }

  return Array.from(items);
}
```

Use for: Twitter feeds, product listings, news sites with infinite scroll.

## Pattern 3: Multi-Tab Orchestration

```typescript
async function scrapeMultipleTabs(urls: string[]) {
  const browser = await chromium.launch();
  const context = await browser.newContext();

  const results = await Promise.all(
    urls.map(async (url) => {
      const page = await context.newPage();
      await page.goto(url);
      const title = await page.title();
      await page.close();
      return { url, title };
    }),
  );

  await browser.close();
  return results;
}
```

10 URLs in parallel takes ~same time as 1 URL.

## Pattern 4: Screenshot Full Page

```typescript
async function captureFullPage(url: string, outputPath: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 1920, height: 1080 },
  });

  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: outputPath, fullPage: true, type: 'png' });

  await browser.close();
}
```

## Pattern 5: PDF Generation

```typescript
async function generatePDF(url: string, outputPath: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(url, { waitUntil: 'networkidle' });
  await page.pdf({
    path: outputPath,
    format: 'A4',
    printBackground: true,
    margin: { top: '1cm', right: '1cm', bottom: '1cm', left: '1cm' },
  });

  await browser.close();
}
```

Chromium only — Firefox and WebKit do not support `page.pdf()`.

## Pattern 6: Form Automation with Validation

```typescript
async function fillFormWithValidation(page) {
  await page.fill('input[name="firstName"]', 'John');
  await page.fill('input[name="lastName"]', 'Doe');
  await page.fill('input[name="email"]', 'john@example.com');

  await page.selectOption('select[name="country"]', 'US');
  await page.check('input[name="terms"]');

  // Wait for client-side validation
  await page.waitForSelector('input[name="email"]:valid');

  await page.click('button[type="submit"]');
  await page.waitForSelector('.success-message', { timeout: 10000 });
}
```

## Pattern 7: Retry with Exponential Backoff

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s
      console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }
  throw new Error('Unreachable');
}

// Usage
await retryWithBackoff(async () => {
  await page.goto('https://unreliable-site.com');
});
```

## Pattern 8: Dynamic Content Stabilization

Wait for content to stop changing before extracting:

```typescript
async function waitForStableContent(page, selector: string) {
  await page.waitForSelector(selector);

  let previousContent = '';
  let stableCount = 0;

  while (stableCount < 4) {
    await page.waitForTimeout(500);
    const currentContent = await page.locator(selector).textContent();

    if (currentContent === previousContent) {
      stableCount++;
    } else {
      stableCount = 0;
    }

    previousContent = currentContent;
  }

  return previousContent;
}
```
