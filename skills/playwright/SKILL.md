---
name: playwright
description: |
  Playwright browser automation API, web scraping, and tooling. Covers locator strategies, assertions, API testing, stealth mode, anti-bot bypass, authenticated sessions, screenshots/PDFs, Docker deployment, configuration, debugging, and MCP integration with AI agents. Prevents documented errors including CI timeout hangs, extension testing failures, and navigation issues.

  Use when automating browsers, scraping protected sites, bypassing bot detection, generating screenshots/PDFs, configuring Playwright Test, troubleshooting Playwright errors, or learning Playwright API patterns. For E2E test architecture, Page Object Models, CI sharding strategies, or test organization patterns, use the e2e-testing skill instead.
license: MIT
metadata:
  author: oakoss
  version: '1.1'
user-invocable: false
---

# Playwright

## Overview

Playwright is a browser automation framework for Node.js and Python supporting Chromium, Firefox, and WebKit with a single API. It provides auto-waiting, web-first assertions, and full test isolation for reliable end-to-end testing.

**When to use:** Browser automation, web scraping, screenshot/PDF generation, API testing, configuring Playwright Test, troubleshooting Playwright errors, stealth mode and anti-bot bypass.

**When NOT to use:** Simple HTTP requests (use `fetch`), unit testing (use Vitest/Jest), serverless scraping at scale (consider Cloudflare Browser Rendering). For E2E test architecture (Page Object Models, CI sharding, test organization, authentication patterns), use the `e2e-testing` skill.

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
| Screenshot            | `page.screenshot({ fullPage: true })`                 | Wait for key elements to load first                |
| PDF generation        | `page.pdf({ format: 'A4' })`                          | Chromium only, set `printBackground: true`         |
| Clock API             | `page.clock`                                          | Freeze, fast-forward, or simulate time in tests    |
| A11y assertions       | `toHaveAccessibleName`, `toHaveRole`                  | Native assertions without axe-core dependency      |
| Viewport assertion    | `expect(locator).toBeInViewport()`                    | Assert element is within the visible viewport      |
| Changed tests only    | `--only-changed=$GITHUB_BASE_REF`                     | Run only test files changed since base branch      |
| Docker                | `mcr.microsoft.com/playwright:v1.58.2-noble`          | Use `--init --ipc=host` flags                      |
| Debug methods         | `page.consoleMessages()` / `page.requests()` (v1.56+) | No event listeners needed                          |
| Speedboard            | HTML reporter (v1.57+)                                | Identifies slow tests and bottlenecks              |
| Playwright Agents     | `npx playwright init-agents`                          | Planner, generator, healer for LLM-driven testing  |
| Flaky test detection  | `--fail-on-flaky-tests` (v1.50+)                      | Exit code 1 on flaky tests in CI                   |
| Modify live responses | `route.fetch()` + `route.fulfill()`                   | Intercept real response, tweak JSON, return it     |
| Soft assertions       | `expect.soft(locator)`                                | Don't stop test on failure, report all at end      |
| Retry block           | `expect(async () => {}).toPass()`                     | Default timeout is 0 (forever) — always set one    |
| Custom matchers       | `expect.extend()` / `mergeExpects()`                  | Define or combine custom assertion methods         |
| Actionability matrix  | Per-action auto-wait checks                           | click: all 5 checks, fill: 3, focus/blur: none     |
| Test modifiers        | `test.fixme()` / `test.fail()` / `test.slow()`        | fixme=skip+track, fail=assert failure, slow=3x     |
| Parallel modes        | `test.describe.configure({ mode: 'serial' })`         | serial, parallel, or default per-describe block    |
| Teardown projects     | `teardown` option on setup projects                   | Auto-cleanup after all dependents finish           |

## Common Mistakes

| Mistake                                         | Correct Pattern                                                                                |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Using CSS selectors over role selectors         | Prefer `getByRole`, `getByLabel`, `getByText` for resilience                                   |
| Not closing browser                             | Always `await browser.close()` in `finally` block                                              |
| Using `setTimeout` for waits                    | Use locator auto-wait or `waitForLoadState`                                                    |
| `page.pause()` left in CI code                  | Guard with `if (!process.env.CI)` — hangs CI indefinitely                                      |
| Clicking without waiting                        | Use `locator().click()` with built-in auto-wait                                                |
| Shared state between tests                      | Each test gets fresh context via fixtures                                                      |
| Testing implementation details                  | Assert user-visible behavior, not DOM structure                                                |
| Hardcoded waits for dynamic content             | Wait for selector appearance or content stabilization                                          |
| Missing `await` on assertions                   | All `expect()` assertions return promises — must be awaited                                    |
| Same user agent for all scraping                | Rotate user agents for high-volume scraping                                                    |
| Using `setTimeout` for time-dependent tests     | Use `page.clock` API to freeze/fast-forward time                                               |
| Installing axe-core for simple a11y checks      | Use native `toHaveAccessibleName`/`toHaveRole` assertions                                      |
| Using `toPass()` without explicit timeout       | Always pass `{ timeout: 10_000 }` — default is 0 (forever)                                     |
| Service worker silently blocking `page.route()` | Set `serviceWorkers: 'block'` in context config when using MSW                                 |
| Using `fill()` for autocomplete/debounce inputs | Use `pressSequentially()` with optional delay for per-keystroke handling                       |
| `storageState` losing sessionStorage            | `storageState` only saves cookies + localStorage — inject sessionStorage via `addInitScript()` |

## Delegation

- **Selector troubleshooting**: Use `Explore` agent
- **Test pattern review**: Use `Task` agent
- **Code review**: Delegate to `code-reviewer` agent

> For E2E test architecture, Page Object Model patterns, CI sharding strategies, authentication flows, visual regression workflows, or test organization, use the `e2e-testing` skill.

## References

- [Quick start and installation](references/quick-start.md)
- [E2E testing patterns and assertions](references/testing-patterns.md)
- [Selector strategies and best practices](references/selector-strategies.md)
- [Configuration and Docker deployment](references/configuration.md)
- [Docker and CI](references/docker-and-ci.md)
- [Debug methods and performance analysis](references/debug-and-performance.md)
- [Common automation patterns](references/common-patterns.md)
- [Stealth mode and anti-bot bypass](references/stealth-mode.md)
- [Known issues and solutions](references/known-issues.md)
- [Site-specific blocking and bypasses](references/blocking-and-bypasses.md)
- [Troubleshooting common problems](references/troubleshooting.md)
- [Network testing, mocking, and API patterns](references/network-testing.md)
- [Input patterns, actionability, and test modifiers](references/input-and-actions.md)
- [Advanced assertions, polling, custom matchers, and annotations](references/advanced-assertions.md)
- [Advanced topics: MCP, AI agents, parallel contexts](references/advanced-topics.md)
