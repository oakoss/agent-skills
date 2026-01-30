---
title: Quick Start
description: Installation, basic page scraping, local vs Cloudflare comparison, and critical setup rules
tags:
  [
    install,
    setup,
    chromium,
    launch,
    goto,
    headless,
    networkidle,
    close,
    browser,
  ]
---

# Quick Start

## Installation

**Node.js:**

```bash
npm install -D playwright
npx playwright install chromium
```

**Python:**

```bash
pip install playwright
playwright install chromium
```

- `playwright install` downloads browser binaries (~400MB for Chromium)
- Install only needed browsers: `chromium`, `firefox`, or `webkit`
- Binaries stored in `~/.cache/ms-playwright/`

## Basic Page Scrape

```typescript
import { chromium } from 'playwright';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();

await page.goto('https://example.com', { waitUntil: 'networkidle' });
const title = await page.title();
const content = await page.textContent('body');

await browser.close();
console.log({ title, content });
```

**Critical rules:**

- Always close browser with `await browser.close()` to avoid zombie processes
- Use `waitUntil: 'networkidle'` for dynamic content (SPAs)
- Default timeout is 30 seconds — adjust with `timeout: 60000` if needed

## Local vs Cloudflare Browser Rendering

| Feature                 | Playwright Local            | Cloudflare Browser Rendering    |
| ----------------------- | --------------------------- | ------------------------------- |
| **IP Address**          | Residential (your ISP)      | Datacenter (easily detected)    |
| **Stealth Plugins**     | Full support                | Not available                   |
| **Rate Limits**         | None                        | 2,000 requests/day free tier    |
| **Cost**                | Free (your CPU)             | $5/10k requests after free tier |
| **Browser Control**     | All Playwright features     | Limited API                     |
| **Session Persistence** | Full cookie/storage control | Limited session management      |

**Use Cloudflare:** Serverless environments, simple scraping, cost-efficient at scale.
**Use Local:** Anti-bot bypass needed, residential IP required, complex automation.

## Critical Rules

### Always Do

- Use `waitUntil: 'networkidle'` for SPAs (React, Vue, Angular)
- Close browsers with `await browser.close()` to prevent memory leaks
- Wrap automation in try/catch/finally blocks
- Set explicit timeouts for unreliable sites
- Save screenshots on errors for debugging
- Use `page.waitForSelector()` before interacting with elements
- Test with `headless: false` first, then switch to `headless: true`

### Never Do

- Use `page.click()` without waiting for element
- Rely on fixed `setTimeout()` for waits — use `waitForSelector`, `waitForLoadState`
- Scrape without rate limiting — add delays between requests
- Use same user agent for all requests — rotate agents
- Ignore navigation errors — catch and retry with backoff
- Store credentials in code — use environment variables
