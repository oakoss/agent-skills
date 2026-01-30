---
name: playwright
description: |
  Playwright browser automation and web scraping. Covers stealth mode, anti-bot bypass, authenticated sessions, infinite scroll, screenshots/PDFs, virtualization, Docker deployment, and MCP server integration. Prevents 10 documented errors including CI timeout hangs, extension testing failures, and Ubuntu compatibility issues.

  Use when automating browsers, scraping protected sites, testing with real IPs, bypassing bot detection, generating screenshots/PDFs, or troubleshooting Playwright errors.
---

# Playwright

## Overview

Playwright is a browser automation library for Node.js and Python. It supports Chromium, Firefox, and WebKit with a single API.

**When to use:** Browser automation, web scraping, E2E testing, screenshot/PDF generation, anti-bot bypass with stealth plugins, authenticated session scraping.

**When NOT to use:** Simple HTTP requests (use `fetch`), serverless scraping at scale (consider Cloudflare Browser Rendering), spreadsheet-like data (use APIs directly).

## Quick Reference

| Pattern                | API / Config                                              | Key Points                                         |
| ---------------------- | --------------------------------------------------------- | -------------------------------------------------- |
| Basic scrape           | `chromium.launch()` + `page.goto()`                       | Always close browser, use `waitUntil`              |
| Stealth mode           | `playwright-extra` + stealth plugin                       | Patches 20+ detection vectors                      |
| Authenticated session  | `context.cookies()` + `addCookies()`                      | Save/restore cookies for session persistence       |
| Infinite scroll        | `page.evaluate(() => window.scrollTo(...))` + dedup loop  | Track `scrollHeight` changes, break after 3 stalls |
| Screenshot             | `page.screenshot({ fullPage: true })`                     | Use `waitUntil: 'networkidle'` first               |
| PDF generation         | `page.pdf({ format: 'A4' })`                              | Chromium only, set `printBackground: true`         |
| Server-side pagination | `manualPagination: true` + query key with state           | All table state in query key                       |
| Docker                 | `mcr.microsoft.com/playwright:v1.57.0-noble`              | Use `--init --ipc=host` flags                      |
| Debug methods          | `page.consoleMessages()` / `page.requests()` (v1.56+)     | No event listeners needed                          |
| Mouse steps            | `click({ steps: 10 })` / `dragTo({ steps: 20 })` (v1.57+) | Anti-detection via realistic movement              |
| MCP Server             | `npx playwright init-agents`                              | Uses accessibility tree, not screenshots           |
| Speedboard             | HTML reporter (v1.57+)                                    | Identifies slow tests and bottlenecks              |

## Selector Strategies

| Strategy    | Example                                   | Best For             |
| ----------- | ----------------------------------------- | -------------------- |
| data-testid | `[data-testid="submit"]`                  | Test automation      |
| CSS         | `button.submit`                           | Standard elements    |
| Text        | `text=Submit`                             | When text is unique  |
| Role        | `getByRole('button', { name: 'Submit' })` | Accessible selectors |
| XPath       | `xpath=//button[text()="Submit"]`         | Complex DOM queries  |

## Wait Strategies

| Method                          | Use Case                   |
| ------------------------------- | -------------------------- |
| `waitUntil: 'networkidle'`      | SPAs (React, Vue, Angular) |
| `waitUntil: 'domcontentloaded'` | Faster, for slow sites     |
| `page.waitForSelector()`        | Wait for specific element  |
| `page.waitForLoadState()`       | After navigation           |

## Common Mistakes

| Mistake                                 | Correct Pattern                                              |
| --------------------------------------- | ------------------------------------------------------------ |
| Not closing browser                     | Always `await browser.close()` in `finally` block            |
| Using `setTimeout` for waits            | Use `waitForSelector`, `waitForLoadState`                    |
| Same user agent for all requests        | Rotate user agents for high-volume scraping                  |
| `page.pause()` left in CI code          | Guard with `if (!process.env.CI)` — hangs CI indefinitely    |
| Clicking without waiting                | Use `locator().click()` with auto-wait or `waitForSelector`  |
| Fixed delays for dynamic content        | Wait for `scrollHeight` stabilization or selector appearance |
| No error handling for navigation        | Wrap in try/catch with retry logic                           |
| Running headless without testing headed | Debug with `headless: false` first                           |

## Delegation

- **Selector troubleshooting**: Use `Explore` agent
- **Test pattern review**: Use `Task` agent
- **Code review**: Delegate to `code-reviewer` agent

## References

- [Quick start and installation](references/quick-start.md)
- [Stealth mode and anti-bot bypass](references/stealth-mode.md)
- [Known issues and solutions (10 documented)](references/known-issues.md)
- [Configuration and Docker deployment](references/configuration.md)
- [Common automation patterns](references/common-patterns.md)
- [Debug methods and performance analysis](references/debug-and-performance.md)
- [Selector strategies and best practices](references/selector-strategies.md)
- [Advanced topics: MCP, parallel contexts, fingerprinting](references/advanced-topics.md)
- [Site-specific blocking and bypasses](references/blocking-and-bypasses.md)
- [Troubleshooting common problems](references/troubleshooting.md)
