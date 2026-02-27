---
title: Site-Specific Blocking and Bypasses
description: Blocking patterns for Cloudflare, Google, LinkedIn, Amazon, and other sites, captcha solving, IP rotation, and legal considerations
tags:
  [
    blocking,
    bypass,
    Cloudflare,
    Google,
    LinkedIn,
    Amazon,
    captcha,
    hCaptcha,
    reCAPTCHA,
    2captcha,
    proxy,
    residential,
    legal,
    robots.txt,
  ]
---

# Site-Specific Blocking and Bypasses

## Cloudflare

**Detection:** navigator.webdriver, timing analysis, TLS fingerprinting, JavaScript challenge.

```typescript
import { chromium } from 'playwright-extra';
import stealth from 'puppeteer-extra-plugin-stealth';

chromium.use(stealth());

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled'],
});

const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  viewport: { width: 1920, height: 1080 },
});

const page = await context.newPage();
await page.goto(url);
await page.waitForTimeout(8000); // Mimics human reading time — critical for Cloudflare
```

Success rate: ~85% with residential IP, ~40% with datacenter IP.

## Google

**Detection:** Query rate limiting, account throttling, captcha challenges.

```typescript
for (const query of queries) {
  await page.goto(
    `https://www.google.com/search?q=${encodeURIComponent(query)}`,
  );
  const results = await page.locator('h3').allTextContents();

  // 10-15 second delay between searches
  await page.waitForTimeout(10000 + Math.random() * 5000);
}
```

**Better alternative:** Google Custom Search API (official, legal).

## LinkedIn

**Detection:** Login state verification, rate limiting, behavior analysis.

```typescript
await page.goto('https://www.linkedin.com/login');
await page.locator('#username').fill(process.env.LINKEDIN_EMAIL);
await page.locator('#password').fill(process.env.LINKEDIN_PASSWORD);
await page.locator('[type="submit"]').click();
await page.waitForURL('**/feed/', { timeout: 10000 });

// Respect limits: 80-100 profile views/day, 20 connections/day, 3-5s between actions
```

LinkedIn Terms prohibit automated scraping. Use official API.

## Amazon

**Detection:** Bot protection via Cloudflare/Akamai, price scraping detection.

```typescript
const context = await browser.newContext({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  extraHTTPHeaders: {
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    Referer: 'https://www.amazon.com/',
  },
});

// 1 request per 3-5 seconds
await page.waitForTimeout(3000 + Math.random() * 2000);
```

**Better alternative:** Product Advertising API.

## General E-Commerce

Respect robots.txt crawl-delay:

```typescript
const robotsTxt = await fetch(new URL('/robots.txt', url)).then((r) =>
  r.text(),
);
const delayMatch = robotsTxt.match(/Crawl-delay:\s*(\d+)/i);
const delay = delayMatch ? parseInt(delayMatch[1]) * 1000 : 2000;

for (const product of products) {
  await page.goto(product.url);
  await page.waitForTimeout(delay);
}
```

## Captcha Solving

### hCaptcha / reCAPTCHA Services

- 2captcha.com (~$2.99/1000 solves)
- anti-captcha.com
- capsolver.com

### Avoiding Captcha Triggers

- Use residential IP
- Add human-like delays
- Limit request rate
- Solve interactively once, persist session

## IP Rotation

### Residential Proxies

```typescript
const proxies = [
  'http://user:pass@proxy1.example.com:8080',
  'http://user:pass@proxy2.example.com:8080',
];

for (const url of urls) {
  const proxy = proxies[Math.floor(Math.random() * proxies.length)];
  const context = await browser.newContext({ proxy: { server: proxy } });
  const page = await context.newPage();

  await page.goto(url);
  await context.close();
}
```

Datacenter proxies are cheaper but more likely to be blocked.

## Legal Considerations

| Site      | Scraping Policy         | Legal Alternative       |
| --------- | ----------------------- | ----------------------- |
| Google    | Terms prohibit scraping | Custom Search API       |
| Twitter   | Terms prohibit scraping | Twitter API v2          |
| LinkedIn  | Terms prohibit scraping | LinkedIn API            |
| Amazon    | Terms prohibit scraping | Product Advertising API |
| Instagram | Terms prohibit scraping | Instagram Graph API     |
| Facebook  | Terms prohibit scraping | Facebook Graph API      |

**Always check robots.txt and Terms of Service before scraping.**

## When All Else Fails

1. Contact the site — ask for API access or data export
2. Check for RSS feeds
3. Use official APIs — usually free tier available
4. Consider alternative data sources
5. Respect rate limits — don't overwhelm servers
