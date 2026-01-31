---
title: Visual Testing
description: Visual regression with Playwright screenshots, dynamic content masking, tolerance thresholds, time mocking, baseline management, and full-page screenshots
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

If the screenshot differs from the baseline beyond the tolerance threshold, the test fails. On the first run, Playwright creates the baseline automatically.

## Full-Page Screenshots

Capture the entire scrollable page:

```ts
await expect(page).toHaveScreenshot('full-page.png', {
  fullPage: true,
});
```

## Element-Level Screenshots

Capture a specific element instead of the full page:

```ts
const card = page.getByTestId('pricing-card');
await expect(card).toHaveScreenshot('pricing-card.png');
```

## Handling Dynamic Content

Dynamic content like timestamps, avatars, or random IDs cause flaky visual tests.

### Masking

Hide specific elements with a solid color before taking the screenshot:

```ts
await expect(page).toHaveScreenshot('dashboard.png', {
  mask: [
    page.getByTestId('timestamp'),
    page.getByRole('img', { name: 'Avatar' }),
    page.locator('.random-ad'),
  ],
  maskColor: '#FF00FF',
});
```

### Mocking Time

Freeze the clock so date-dependent UI renders consistently:

```ts
test('dashboard with frozen time', async ({ page }) => {
  await page.clock.install({ time: new Date('2025-01-15T12:00:00') });
  await page.goto('/dashboard');

  await expect(page).toHaveScreenshot('dashboard-frozen.png');
});
```

### Hiding Animations

Disable CSS animations and transitions to prevent timing-based differences:

```ts
await expect(page).toHaveScreenshot('page.png', {
  animations: 'disabled',
});
```

## Tolerance Thresholds

Small rendering differences due to OS, GPU, or font version should not fail the build:

- `maxDiffPixels`: Maximum number of pixels that can be different
- `maxDiffPixelRatio`: Maximum ratio of pixels that can be different (0 to 1)
- `threshold`: Per-pixel color difference threshold (0 to 1, default 0.2)

```ts
await expect(page).toHaveScreenshot('chart.png', {
  maxDiffPixelRatio: 0.01,
});
```

```ts
await expect(page).toHaveScreenshot('hero.png', {
  maxDiffPixels: 100,
});
```

Choose thresholds based on UI complexity. Simple layouts can use tighter thresholds; data-heavy dashboards may need more tolerance.

Configure defaults globally in `playwright.config.ts`:

```ts
export default defineConfig({
  expect: {
    toHaveScreenshot: {
      maxDiffPixelRatio: 0.01,
      animations: 'disabled',
    },
  },
});
```

## Baseline Management

- Store baselines in Git (use Git LFS for large binary files)
- Update baselines only after manual verification: `npx playwright test --update-snapshots`
- Use separate snapshot directories per platform if OS-level rendering differs
- Review baseline changes in PRs with visual diffs

### Platform-Specific Baselines

Playwright stores snapshots in directories named after the project. Configure different expectations per platform:

```ts
export default defineConfig({
  snapshotPathTemplate:
    '{testDir}/__screenshots__/{testFilePath}/{arg}{-projectName}{ext}',
});
```

## Comparing Screenshots Programmatically

For custom comparison workflows:

```ts
test('compare two states', async ({ page }) => {
  await page.goto('/before');
  const before = await page.screenshot();

  await page.goto('/after');
  const after = await page.screenshot();

  expect(before).not.toEqual(after);
});
```

## CI Considerations

- Run visual tests on a consistent OS (Linux containers) to avoid cross-platform rendering differences
- Use Docker images with fixed font packages for deterministic rendering
- Consider running visual tests as a separate CI job with `--grep @visual` tags
- Upload diff images as CI artifacts for easy review
