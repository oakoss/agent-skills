---
title: Validation Techniques
description: Automated DOM verification techniques for detecting silent hydration failures including mutation monitoring, onRecoverableError, flash detection, and production monitoring
tags:
  [
    validation,
    mutation-observer,
    onRecoverableError,
    hydration-flash,
    monitoring,
    devtools,
  ]
---

# Validation Techniques

Many hydration errors are "soft" failures that do not crash the app. React recovers by re-rendering the affected subtree, which preserves functionality but destroys performance and causes visual artifacts. These techniques detect silent hydration issues.

## Production Error Monitoring with onRecoverableError

The most important validation technique. Configure `hydrateRoot` to report every hydration recovery event.

```tsx
import { hydrateRoot } from 'react-dom/client';

const root = hydrateRoot(document.getElementById('root')!, <App />, {
  onRecoverableError(error, errorInfo) {
    if (error.message.includes('hydrat')) {
      reportToMonitoring({
        type: 'hydration-recovery',
        message: error.message,
        cause: (error as any).cause?.message,
        componentStack: errorInfo.componentStack,
        url: window.location.href,
        timestamp: Date.now(),
      });
    }
  },
  onCaughtError(error, errorInfo) {
    reportToMonitoring({
      type: 'caught-error',
      message: error.message,
      componentStack: errorInfo.componentStack,
    });
  },
});
```

**Why this matters:** In production, React does not show console warnings for hydration mismatches. Without `onRecoverableError`, silent hydration failures go completely undetected.

## Hydration Audit Script

Run via Chrome DevTools console or browser automation to detect silent hydration warnings in development.

```js
(function auditHydration() {
  const originalError = console.error;
  const hydrationErrors = [];

  console.error = function (...args) {
    const message = args.join(' ');
    if (
      message.includes('hydrat') ||
      message.includes('did not match') ||
      message.includes('server-rendered')
    ) {
      hydrationErrors.push({ message, timestamp: Date.now() });
    }
    originalError.apply(console, args);
  };

  setTimeout(() => {
    console.error = originalError;
    if (hydrationErrors.length > 0) {
      console.warn(
        `AUDIT: ${hydrationErrors.length} hydration issue(s) detected`,
        hydrationErrors,
      );
    } else {
      console.log('AUDIT: Hydration clean.');
    }
  }, 3000);
})();
```

Run this before page load (via DevTools snippets or injection) to capture hydration warnings that appear during the initial render.

## Flash Detection via Mutation Monitoring

Monitor DOM mutations during the hydration window. A high mutation count indicates React is re-rendering subtrees to recover from mismatches.

```js
(function detectHydrationFlash() {
  let mutations = 0;
  const observer = new MutationObserver((list) => {
    mutations += list.length;
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
  });

  window.addEventListener('load', () => {
    setTimeout(() => {
      observer.disconnect();
      const status =
        mutations <= 10
          ? 'CLEAN'
          : mutations <= 50
            ? 'INVESTIGATE'
            : 'FIX REQUIRED';

      console.log(`AUDIT: Mutation count: ${mutations} (${status})`);
    }, 500);
  });
})();
```

**Thresholds:**

| Mutation Count | Assessment                  | Action                                   |
| -------------- | --------------------------- | ---------------------------------------- |
| 0-10           | Clean hydration             | No action needed                         |
| 11-50          | Minor mismatches            | Investigate specific components          |
| 51+            | Significant hydration flash | Fix required; users see visual artifacts |

## Environment Simulation Checklist

Hydration errors often appear only under specific conditions. Test across these scenarios:

### Timezone Testing

```bash
# Run dev server with different timezone
TZ='America/New_York' npm run dev
TZ='Asia/Tokyo' npm run dev
TZ='UTC' npm run dev
```

Verify that date-dependent components produce identical server and client output regardless of timezone.

### Locale Testing

Test with browser language settings that differ from the server. Number formatting, currency symbols, and date formats vary by locale.

```tsx
// Deterministic locale: pass from server metadata
function Price({
  amount,
  locale,
  currency,
}: {
  amount: number;
  locale: string;
  currency: string;
}) {
  return (
    <span>
      {new Intl.NumberFormat(locale, {
        style: 'currency',
        currency,
      }).format(amount)}
    </span>
  );
}
```

### Browser Extension Testing

Test with these common DOM-polluting extensions active:

| Extension         | DOM Impact                                | Detection                                  |
| ----------------- | ----------------------------------------- | ------------------------------------------ |
| Google Translate  | Wraps text in `<font>` tags               | Check for unexpected `<font>` elements     |
| Dark Reader       | Injects `<style>`, modifies inline styles | Check for injected style elements          |
| Ad blockers       | Remove/hide DOM elements                  | Check for missing expected elements        |
| Password managers | Inject input overlays                     | Check for unexpected elements near inputs  |
| Grammarly         | Adds wrapper spans around text            | Check for `<grammarly-extension>` elements |

### Slow Network Simulation

Use Chrome DevTools Network throttling (Slow 3G) to reveal race conditions where the client hydrates before all resources are available.

## Comparing Server HTML vs Client DOM

Open the page and compare:

1. **Server HTML:** `view-source:http://localhost:3000/page` (raw server output)
2. **Client DOM:** DevTools Elements panel (post-hydration state)

Differences indicate hydration mismatches. Focus on:

- Text content differences
- Missing or extra attributes
- Different element structure
- Style differences

## React DevTools Profiler

Use the React DevTools Profiler to identify components that re-render during hydration:

1. Open React DevTools Profiler tab
2. Enable "Record why each component rendered"
3. Reload the page
4. Look for components that rendered with reason "Hydration mismatch"

## Automated CI Validation

Integrate hydration checks into CI by capturing console errors during E2E tests.

```ts
// Playwright example
import { test, expect } from '@playwright/test';

test('no hydration errors on homepage', async ({ page }) => {
  const hydrationErrors: string[] = [];

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      const text = msg.text();
      if (
        text.includes('hydrat') ||
        text.includes('did not match') ||
        text.includes('server-rendered')
      ) {
        hydrationErrors.push(text);
      }
    }
  });

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  expect(hydrationErrors).toEqual([]);
});
```

## Validation Checklist

- Browser console free of `react-dom` hydration warnings
- `onRecoverableError` configured and reporting to monitoring
- Mutation observer count below 10 for static page sections
- Input focus maintained if hydration happens while user is typing
- CSS-in-JS styles injected before first paint (no unstyled flash)
- Dates and currencies render identically on server and client
- App functions correctly with translation extensions active
- E2E tests assert zero hydration errors on critical pages
- Lighthouse Total Blocking Time within acceptable range
