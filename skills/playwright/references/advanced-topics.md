---
title: Advanced Topics
description: Playwright Agents for LLM-driven testing, MCP Server for AI integration, parallel browser contexts, browser fingerprinting defense, and network interception
tags:
  [
    MCP,
    mcp-server,
    agents,
    planner,
    generator,
    healer,
    LLM,
    parallel,
    contexts,
    concurrency,
    fingerprint,
    defense,
    network,
    route,
    intercept,
  ]
---

# Advanced Topics

## Playwright Agents (v1.56+)

Playwright provides three custom agent definitions designed to guide LLMs through building and maintaining tests:

- **Planner** -- explores the app and produces a Markdown test plan
- **Generator** -- transforms the plan into Playwright Test files
- **Healer** -- executes the test suite and automatically repairs failing tests

```bash
npx playwright init-agents
```

This generates agent configuration files for VS Code Copilot, Claude Desktop, and other AI coding tools.

## Playwright MCP Server

Microsoft provides an official [Playwright MCP Server](https://github.com/microsoft/playwright-mcp) for AI agent integration:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Key features:**

- Uses accessibility tree instead of screenshots (faster, more reliable)
- LLM-friendly structured data format
- Model Context Protocol (MCP) compliant
- Works with Claude Desktop, VS Code Copilot, and other MCP clients

## Copy Prompt for AI Debugging (v1.51+)

When a test fails, the HTML reporter and UI mode show a "Copy prompt" button that generates a structured debugging prompt. Paste it into an AI tool for assistance fixing the failure.

Disable in config if needed:

```typescript
export default defineConfig({
  reporter: [['html', { copyPrompt: false }]],
});
```

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

Separate contexts provide cookie/storage isolation between concurrent operations.

## Network Interception

### Route Requests

```typescript
// Block images and fonts for faster scraping
await page.route('**/*.{png,jpg,jpeg,gif,svg,woff,woff2}', (route) =>
  route.abort(),
);

// Modify request headers
await page.route('**/api/**', (route) =>
  route.continue({
    headers: { ...route.request().headers(), 'X-Custom': 'value' },
  }),
);
```

Note: as of v1.52, glob patterns in `page.route()` no longer support `?` and `[]`. Use regex instead:

```typescript
await page.route(/\/api\/items\/\d+/, (route) => route.fulfill({ body: '{}' }));
```

### Intercept and Modify Responses

```typescript
await page.route('**/api/config', async (route) => {
  const response = await route.fetch();
  const json = await response.json();

  json.featureFlag = true;

  await route.fulfill({
    response,
    body: JSON.stringify(json),
  });
});
```

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

## Service Worker Routing (v1.57+, Chromium)

Service Worker network requests are now reported and routable through BrowserContext:

```typescript
// Route service worker requests
await context.route('**/api/**', (route) => route.continue());

// Listen to service worker console messages
context.on('serviceworker', (worker) => {
  worker.on('console', (msg) => console.log('SW:', msg.text()));
});
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

Claude Code workflow: write script, run via `npx tsx scrape.ts URL`, capture JSON, analyze results.

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

Claude Code can run the script, read the screenshot, analyze visual layout, and suggest improvements.

## Cookie Partitioning (v1.54+)

Save and restore partitioned cookies (CHIPS):

```typescript
const cookies = await context.cookies();
// cookies may include partitionKey for cross-site partitioned cookies

await context.addCookies(
  cookies.map((c) => ({
    ...c,
    partitionKey: c.partitionKey,
  })),
);
```

## Media Emulation

```typescript
// Emulate color scheme
await page.emulateMedia({ colorScheme: 'dark' });

// Emulate reduced motion
await page.emulateMedia({ reducedMotion: 'reduce' });

// Emulate contrast preference (v1.51+)
await page.emulateMedia({ contrast: 'more' });
```

## Dynamic Content Handling

Wait for content to stabilize (no changes for 2 seconds):

```typescript
async function waitForDynamicContent(page, selector: string) {
  const locator = page.locator(selector);
  await locator.waitFor();

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
