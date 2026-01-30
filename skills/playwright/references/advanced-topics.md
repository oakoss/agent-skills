---
title: Advanced Topics
description: Playwright MCP Server for AI agents, Claude Code integration, parallel browser contexts, browser fingerprinting defense, and dynamic content handling
tags:
  [
    MCP,
    mcp-server,
    claude-code,
    parallel,
    contexts,
    concurrency,
    fingerprint,
    defense,
    dynamic-content,
    evaluate,
  ]
---

# Advanced Topics

## Playwright MCP Server (v1.56+)

Microsoft provides an official [Playwright MCP Server](https://github.com/microsoft/playwright-mcp) for AI agent integration:

```bash
npx playwright init-agents
```

This generates configuration for VS Code Copilot, Claude Desktop, and opencode.

**Key features:**

- Uses accessibility tree instead of screenshots (faster, more reliable)
- LLM-friendly structured data format
- Model Context Protocol (MCP) compliant

**MCP Server setup:**

```bash
npm install -g @anthropic/mcp-playwright
```

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@anthropic/mcp-playwright"]
    }
  }
}
```

## Claude Code Integration

### Scraping Workflow

```typescript
// scrape.ts
import { chromium } from 'playwright';

async function scrape(url: string) {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(url);
  const data = await page.evaluate(() => ({
    title: document.title,
    headings: Array.from(document.querySelectorAll('h1, h2')).map(
      (el) => el.textContent,
    ),
  }));

  await browser.close();
  console.log(JSON.stringify(data, null, 2));
}

scrape(process.argv[2]);
```

Claude Code workflow: write script → run via `npx tsx scrape.ts URL` → capture JSON → analyze results.

### Screenshot Review Workflow

```typescript
import { chromium } from 'playwright';

async function captureForReview(url: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto(url);
  await page.screenshot({ path: '/tmp/review.png', fullPage: true });
  await browser.close();

  console.log('Screenshot saved to /tmp/review.png');
}

captureForReview(process.argv[2]);
```

Claude Code can run script, read screenshot, analyze visual layout, and suggest improvements.

## Parallel Browser Contexts

Use separate contexts for isolation when scraping multiple URLs:

```typescript
import { chromium } from 'playwright';

async function scrapeConcurrently(urls: string[]) {
  const browser = await chromium.launch();

  const results = await Promise.all(
    urls.map(async (url) => {
      const context = await browser.newContext();
      const page = await context.newPage();

      await page.goto(url);
      const title = await page.title();

      await context.close();
      return { url, title };
    }),
  );

  await browser.close();
  return results;
}
```

Separate contexts provide cookie/storage isolation between concurrent scrapes.

## Browser Fingerprinting Defense

```typescript
async function setupStealthContext(browser) {
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    viewport: {
      width: 1920 + Math.floor(Math.random() * 100),
      height: 1080 + Math.floor(Math.random() * 100),
    },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    screen: { width: 1920, height: 1080 },
    geolocation: { longitude: -74.006, latitude: 40.7128 },
    permissions: ['geolocation'],
  });

  return context;
}
```

Randomize viewport dimensions slightly to avoid fingerprint consistency.

## Dynamic Content Handling

Wait for content to stabilize (no changes for 2 seconds):

```typescript
async function waitForDynamicContent(page, selector: string) {
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
