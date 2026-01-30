---
title: Visual Testing
description: Visual regression with Playwright screenshots, dynamic content masking, tolerance thresholds, time mocking, and baseline management in Git
tags:
  [
    visual-regression,
    screenshots,
    masking,
    tolerance,
    baselines,
    snapshot-testing,
  ]
---

# Visual Testing

## Snapshot Testing

Visual regression compares a screenshot of the current UI with a baseline (golden) image:

```ts
await expect(page).toHaveScreenshot('dashboard.png');
```

If the screenshot differs from the baseline beyond the tolerance threshold, the test fails.

## Handling Dynamic Data

Dynamic content like timestamps, usernames, or random IDs cause flaky visual tests.

### Masking

Hide specific elements with a solid color before taking the screenshot:

```ts
await expect(page).toHaveScreenshot({
  mask: [page.getByTestId('timestamp'), page.getByRole('complementary')],
});
```

### Mocking Time

Use `page.addInitScript` to freeze or mock the system time so date-dependent UI renders consistently across runs.

## Tolerance Thresholds

Small rendering differences due to OS or font version should not fail the build:

- `maxDiffPixels`: Maximum number of pixels that can be different
- `maxDiffPixelRatio`: Maximum ratio of pixels that can be different (0 to 1)

```ts
await expect(page).toHaveScreenshot({ maxDiffPixelRatio: 0.1 });
```

Choose thresholds based on your UI complexity. Simple layouts can use tighter thresholds; data-heavy dashboards may need more tolerance.

## Baseline Management

- Store baselines in Git (use LFS for large binary files)
- Update baselines only after manual verification: `npx playwright test --update-snapshots`
- Use separate baselines for different browsers or OS if they render significantly differently
- Review baseline changes in PRs with visual diffs
