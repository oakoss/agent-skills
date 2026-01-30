---
name: e2e-testing
description: 'Builds end-to-end test suites with Playwright. Use when writing E2E tests, setting up visual regression, or configuring CI sharding. Use for Page Object Model architecture, accessibility auditing with Axe-core, network mocking, trace-based debugging, role-based locators, and HAR replay.'
---

# E2E Testing

## Overview

Builds resilient end-to-end test suites using Playwright with auto-waiting, role-based locators, and the Page Object Model. Covers visual regression testing, accessibility auditing via Axe-core, network mocking, CI sharding for parallel execution, and trace-based forensic debugging.

**When to use:** Writing E2E tests, setting up visual regression, configuring CI sharding, mocking network requests, auditing accessibility, debugging test failures.

**When NOT to use:** Unit testing (use Vitest/Jest), API-only testing (use integration tests), component testing in isolation (use component test runners).

## Quick Reference

| Pattern              | API/Tool                                     | Key Points                                |
| -------------------- | -------------------------------------------- | ----------------------------------------- |
| Role-based locators  | `getByRole`, `getByText`, `getByLabel`       | Preferred over CSS/XPath selectors        |
| Page Object Model    | Classes in `tests/models/`                   | Encapsulate all page-specific locators    |
| Visual regression    | `expect(page).toHaveScreenshot()`            | Mask dynamic content to prevent flakes    |
| Accessibility audit  | `@axe-core/playwright`                       | `injectAxe` + `checkA11y` on key flows    |
| Trace debugging      | `trace: 'on-first-retry'`                    | Full DOM snapshots and network logs       |
| Network mocking      | `page.route()`                               | Stable tests without third-party deps     |
| HAR replay           | `page.routeFromHAR()`                        | High-fidelity mocks from recorded traffic |
| Image blocking       | `page.route('**/*.{png,jpg}', abort)`        | Speed up tests by skipping images         |
| CI sharding          | `--shard=1/4`                                | Split suite across parallel machines      |
| Blob reports         | `--reporter=blob` + `merge-reports`          | Merge sharded results into single report  |
| Browser caching      | `actions/cache` for `~/.cache/ms-playwright` | Speed up CI with cached browser binaries  |
| Web-first assertions | `expect(element).toBeVisible()`              | Auto-wait instead of `waitForTimeout`     |

## Mandatory Protocols

1. **User-Visible Locators First**: Always use `getByRole`, `getByText`, or `getByLabel`. If unreachable via standard role, fix the accessibility tree instead of adding `data-testid`.
2. **Page Object Model**: Never write raw locators in test files. Encapsulate in POM classes under `tests/models/`.
3. **Visual Regression with Masking**: Use `toHaveScreenshot()` for critical UI. Mask dynamic content (dates, usernames) to prevent false positives.
4. **Trace-Based Debugging**: Configure `trace: 'on-first-retry'` in CI. Never debug via screenshots or videos alone.
5. **Accessibility on Every Flow**: Use `@axe-core/playwright` to run accessibility audits during key user flows.

## Common Mistakes

| Mistake                                                  | Correct Pattern                                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Using `page.waitForTimeout()` for element visibility     | Use web-first assertions like `expect(element).toBeVisible()` which auto-wait |
| Writing raw locators directly in test files              | Encapsulate all selectors in Page Object Model classes under `tests/models/`  |
| Testing third-party APIs (Stripe, Auth0) directly        | Mock external services with `page.route()` for stable, fast tests             |
| Debugging CI failures with screenshots instead of traces | Configure `trace: 'on-first-retry'` and use Playwright Trace Viewer           |
| Sharing state between tests via global variables         | Use a fresh `BrowserContext` per test for full isolation                      |
| Running all tests in a single CI job                     | Use Playwright sharding (`--shard=1/N`) across parallel machines              |
| Using CSS/XPath selectors for element location           | Use role-based locators that survive refactors and enforce accessibility      |

## Delegation

- **Discover which user flows lack E2E coverage**: Use `Explore` agent
- **Build a full Page Object Model test suite for an application**: Use `Task` agent
- **Plan a CI sharding strategy for a large test suite**: Use `Plan` agent

## References

- [Role-based locators, auto-waiting, shadow DOM piercing, and locator strategy](references/locators.md)
- [Network mocking, route interception, HAR replay, and WebSocket mocking](references/mocking.md)
- [CI sharding, parallelism, blob reports, and browser caching](references/ci-sharding.md)
- [Visual regression, snapshot testing, masking, tolerance thresholds, and baseline management](references/visual-testing.md)
