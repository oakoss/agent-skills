---
title: Stealth Mode
description: Anti-bot bypass with stealth plugins, WebDriver masking, human-like behavior, user agent rotation, session persistence, and detection verification
tags:
  [
    stealth,
    anti-bot,
    detection,
    webdriver,
    playwright-extra,
    puppeteer-extra-plugin-stealth,
    fingerprint,
    proxy,
    residential,
  ]
---

# Stealth Mode

Advanced detection systems (Cloudflare Bot Management, PerimeterX, DataDome) now include behavioral analysis, TLS fingerprinting, canvas/WebGL fingerprinting, and HTTP/2 fingerprinting. Stealth plugins are a good starting point, not a complete solution.

## Step 1: Install Stealth Plugin

```bash
npm install playwright-extra puppeteer-extra-plugin-stealth
```

## Step 2: Configure Stealth Mode

```typescript
import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

chromium.use(stealth());

const browser = await chromium.launch({
  headless: true,
  args: [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
  ],
});

const context = await browser.newContext({
  userAgent:
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  viewport: { width: 1920, height: 1080 },
  locale: 'en-US',
  timezoneId: 'America/New_York',
});
```

## Step 3: Mask WebDriver Detection

```typescript
await page.addInitScript(() => {
  Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

  Object.defineProperty(navigator, 'plugins', {
    get: () => [
      { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
      {
        name: 'Chrome PDF Viewer',
        filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai',
      },
      { name: 'Native Client', filename: 'internal-nacl-plugin' },
    ],
  });

  Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

  const originalQuery = window.navigator.permissions.query;
  window.navigator.permissions.query = (parameters) =>
    parameters.name === 'notifications'
      ? Promise.resolve({ state: Notification.permission })
      : originalQuery(parameters);
});
```

## Step 4: Human-Like Mouse Movement

```typescript
async function humanClick(page, selector) {
  const element = await page.locator(selector);
  const box = await element.boundingBox();

  if (box) {
    const x = box.x + box.width * Math.random();
    const y = box.y + box.height * Math.random();

    await page.mouse.move(x, y, { steps: 10 });
    await page.waitForTimeout(100 + Math.random() * 200);
    await page.mouse.click(x, y, { delay: 50 + Math.random() * 100 });
  }
}
```

## Step 5: Rotate User Agents

```typescript
const userAgents = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
];

const randomUA = userAgents[Math.floor(Math.random() * userAgents.length)];
```

Match user agent to actual Chrome version.

## Step 6: Cookie and Session Persistence

```typescript
import fs from 'fs/promises';

// Save session
const cookies = await context.cookies();
await fs.writeFile('session.json', JSON.stringify(cookies, null, 2));
await context.close();

// Restore session
const savedCookies = JSON.parse(await fs.readFile('session.json', 'utf-8'));
const newContext = await browser.newContext();
await newContext.addCookies(savedCookies);
```

## Step 7: Verify Stealth

Test at: `https://bot.sannysoft.com/`

```typescript
await page.goto('https://bot.sannysoft.com/', { waitUntil: 'networkidle' });
await page.screenshot({ path: 'stealth-test.png', fullPage: true });
```

Check: `navigator.webdriver` should be `undefined` (not `false`), Chrome detected, plugins populated, no red flags.

## Detection Vectors

| Vector                | What It Checks                 | Defense                      |
| --------------------- | ------------------------------ | ---------------------------- |
| `navigator.webdriver` | Automation flag                | Stealth plugin / init script |
| Missing plugins       | Real browsers have 3-5 plugins | Mock plugins via init script |
| Chrome DevTools       | `window.chrome` presence       | Delete in init script        |
| WebGL fingerprint     | Renderer/vendor strings        | Context config with screen   |
| Canvas fingerprint    | Consistent pixel output        | Stealth plugin handles this  |
| TLS fingerprint       | JA3/JA4 signatures             | Real browser helps           |
| Timing patterns       | Instant actions = bot          | Random delays + steps        |
| IP reputation         | Datacenter IPs flagged         | Residential proxy            |

## Common Stealth Mistakes

| Mistake            | Fix                             |
| ------------------ | ------------------------------- |
| Same UA every time | Rotate user agents              |
| Fixed viewport     | Randomize slightly              |
| Instant actions    | Add random delays               |
| No cookies         | Accept + persist cookies        |
| Missing referer    | Set referer header              |
| Datacenter IP      | Use residential proxy if needed |

## Residential Proxies

When stealth plugins aren't enough:

```typescript
const context = await browser.newContext({
  proxy: {
    server: 'http://proxy-server:8080',
    username: 'user',
    password: 'pass',
  },
});
```

Providers: Bright Data, Oxylabs, Smartproxy.

## Verification Tools

- `https://bot.sannysoft.com/` — Comprehensive bot detection test
- `https://arh.antoinevastel.com/bots/areyouheadless` — Headless detection
- `https://pixelscan.net/` — Fingerprint analysis
- `https://browserleaks.com/webrtc` — WebRTC leak check
