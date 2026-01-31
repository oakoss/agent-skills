---
name: playwright
description: |
  Playwright browser automation, E2E testing, and web scraping. Covers test fixtures, locator assertions, API testing, stealth mode, anti-bot bypass, authenticated sessions, screenshots/PDFs, Docker deployment, and MCP integration with AI agents. Prevents documented errors including CI timeout hangs, extension testing failures, and navigation issues.

  Use when writing E2E tests, automating browsers, scraping protected sites, bypassing bot detection, generating screenshots/PDFs, configuring Playwright Test, or troubleshooting Playwright errors.
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Playwright

## Overview

Playwright is a browser automation framework for Node.js and Python supporting Chromium, Firefox, and WebKit with a single API. It provides auto-waiting, web-first assertions, and full test isolation for reliable end-to-end testing.

**When to use:** E2E testing, browser automation, web scraping, screenshot/PDF generation, API testing, visual regression testing, accessibility validation.

**When NOT to use:** Simple HTTP requests (use `fetch`), unit testing (use Vitest/Jest), serverless scraping at scale (consider Cloudflare Browser Rendering).

## Quick Reference

| Pattern               | API / Config                                          | Key Points                                         |
| --------------------- | ----------------------------------------------------- | -------------------------------------------------- |
| Basic test            | `test('name', async ({ page }) => {})`                | Auto-wait, web-first assertions, test isolation    |
| Locator               | `page.getByRole()` / `page.locator()`                 | Prefer role/label/text selectors over CSS          |
| Assertion             | `expect(locator).toBeVisible()`                       | Auto-retrying, configurable timeout                |
| API testing           | `request` fixture / `apiRequestContext`               | Send HTTP requests, validate responses             |
| Aria snapshot         | `expect(locator).toMatchAriaSnapshot()`               | Validate accessibility tree structure via YAML     |
| Class assertion       | `expect(locator).toContainClass('active')`            | Match individual CSS class names (v1.52+)          |
| Visible filter        | `locator.filter({ visible: true })`                   | Match only visible elements (v1.51+)               |
| Test step             | `test.step('name', async (step) => {})`               | Timeout, skip, and attachments (v1.50+)            |
| Stealth mode          | `playwright-extra` + stealth plugin                   | Patches 20+ detection vectors                      |
| Authenticated session | `context.cookies()` + `addCookies()`                  | Save/restore cookies and IndexedDB for persistence |
| Screenshot            | `page.screenshot({ fullPage: true })`                 | Use `waitUntil: 'networkidle'` first               |
| PDF generation        | `page.pdf({ format: 'A4' })`                          | Chromium only, set `printBackground: true`         |
| Docker                | `mcr.microsoft.com/playwright:v1.58.0-noble`          | Use `--init --ipc=host` flags                      |
| Debug methods         | `page.consoleMessages()` / `page.requests()` (v1.56+) | No event listeners needed                          |
| Speedboard            | HTML reporter (v1.57+)                                | Identifies slow tests and bottlenecks              |
| Playwright Agents     | `npx playwright init-agents`                          | Planner, generator, healer for LLM-driven testing  |
| Flaky test detection  | `--fail-on-flaky-tests` (v1.50+)                      | Exit code 1 on flaky tests in CI                   |

## Common Mistakes

| Mistake                                 | Correct Pattern                                              |
| --------------------------------------- | ------------------------------------------------------------ |
| Using CSS selectors over role selectors | Prefer `getByRole`, `getByLabel`, `getByText` for resilience |
| Not closing browser                     | Always `await browser.close()` in `finally` block            |
| Using `setTimeout` for waits            | Use `waitForSelector`, `waitForLoadState`, auto-wait         |
| `page.pause()` left in CI code          | Guard with `if (!process.env.CI)` — hangs CI indefinitely    |
| Clicking without waiting                | Use `locator().click()` with built-in auto-wait              |
| Shared state between tests              | Each test gets fresh context via fixtures                    |
| Testing implementation details          | Assert user-visible behavior, not DOM structure              |
| Hardcoded waits for dynamic content     | Wait for selector appearance or content stabilization        |
| Missing `await` on assertions           | All `expect()` assertions return promises — must be awaited  |
| Same user agent for all scraping        | Rotate user agents for high-volume scraping                  |

## Delegation

- **Selector troubleshooting**: Use `Explore` agent
- **Test pattern review**: Use `Task` agent
- **Code review**: Delegate to `code-reviewer` agent

## References

- [Quick start and installation](references/quick-start.md)
- [E2E testing patterns and assertions](references/testing-patterns.md)
- [Selector strategies and best practices](references/selector-strategies.md)
- [Configuration and Docker deployment](references/configuration.md)
- [Debug methods and performance analysis](references/debug-and-performance.md)
- [Common automation patterns](references/common-patterns.md)
- [Stealth mode and anti-bot bypass](references/stealth-mode.md)
- [Known issues and solutions](references/known-issues.md)
- [Site-specific blocking and bypasses](references/blocking-and-bypasses.md)
- [Troubleshooting common problems](references/troubleshooting.md)
- [Advanced topics: MCP, AI agents, parallel contexts](references/advanced-topics.md)
