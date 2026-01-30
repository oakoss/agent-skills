---
title: Sensory Validation
description: Automated DOM verification techniques for detecting silent hydration failures including flash detection, mutation monitoring, and environment simulation
tags:
  [
    sensory-validation,
    DOM-audit,
    mutation-observer,
    hydration-flash,
    environment-simulation,
  ]
---

# Sensory Validation

Sensory validation verifies that the rendered DOM exactly matches the expected React state, especially in complex SSR/ISR environments. Many hydration errors are "soft" failures that do not crash the app but degrade performance.

## The Invisible Hydration Bug

React may recover from a hydration mismatch by re-rendering the entire sub-tree. This preserves functionality but destroys performance and causes visual artifacts.

**Key indicators of soft failures:**

- Increased Time to Interactive (TTI) from main thread re-rendering
- State loss (input focus or scroll position) during the re-render "flash"
- Lighthouse "Total Blocking Time" increases

## Hydration Audit Script

Run this script via Chrome DevTools or browser automation to detect silent hydration warnings that do not appear as visible errors.

```js
(function auditHydration() {
  const hook = window.__REACT_DEVTOOLS_GLOBAL_HOOK__;
  const warnings = hook?.getErrors?.() || [];
  const hydrationErrors = warnings.filter((w) =>
    w.message.includes('hydration'),
  );

  if (hydrationErrors.length > 0) {
    console.error('AUDIT: Hydration failures detected!', hydrationErrors);
    return { status: 'FAIL', errors: hydrationErrors };
  }

  console.log('AUDIT: Hydration clean.');
  return { status: 'PASS', errors: [] };
})();
```

## Flash Detection Script

Monitor for DOM mutations within the first 500ms after page load. A high mutation count indicates a hydration mismatch causing a full sub-tree re-render.

```js
let mutations = 0;
const observer = new MutationObserver((list) => {
  mutations += list.length;
});
observer.observe(document.body, { childList: true, subtree: true });

window.addEventListener('load', () => {
  setTimeout(() => {
    observer.disconnect();
    if (mutations > 50) {
      console.warn(
        `AUDIT: High mutation count (${mutations}) detected during hydration.`,
      );
    } else {
      console.log(`AUDIT: Mutation count (${mutations}) within threshold.`);
    }
  }, 500);
});
```

**Thresholds:**

| Mutation Count | Assessment                                |
| -------------- | ----------------------------------------- |
| 0-10           | Clean hydration                           |
| 11-50          | Minor mismatches; investigate             |
| 51+            | Significant hydration flash; fix required |

## Server-Side Sensory Validation (SSSV)

Next.js provides server-side prediction of potential hydration mismatches by simulating the client environment during the pre-render phase.

```ts
// next.config.ts
export default {
  experimental: {
    sssv: {
      strictMode: true,
      warnOnExtensionConflict: true,
    },
  },
};
```

## Environment Simulation

Hydration errors often hide in specific conditions. Test across these scenarios:

### Date/Time Traps

```tsx
// WRONG: Non-deterministic date in render
function Clock() {
  return <div>{new Date().toLocaleTimeString()}</div>;
}

// CORRECT: Deterministic date from server-synced context
import { useDate } from '@/hooks/use-deterministic';

function Clock() {
  const date = useDate();
  return <div>{date.toLocaleTimeString()}</div>;
}
```

### Currency/Locale Traps

Always use the `Intl` API with an explicit locale passed from server metadata. Never rely on the browser's default locale.

```tsx
// WRONG: Browser locale may differ from server
function Price({ amount }: { amount: number }) {
  return (
    <span>
      {amount.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
    </span>
  );
}

// CORRECT: Locale from server context
function Price({ amount, locale }: { amount: number; locale: string }) {
  return (
    <span>
      {amount.toLocaleString(locale, { style: 'currency', currency: 'USD' })}
    </span>
  );
}
```

### Browser Extension Testing

Test with common DOM-polluting extensions active:

- Translation extensions (Google Translate, DeepL)
- Dark mode toggles (Dark Reader)
- Ad blockers that modify DOM structure
- Password managers that inject elements

## Validation Checklist

- [ ] Browser console free of `react-dom` hydration warnings
- [ ] Mutation observer count below 10 for static sections
- [ ] Input focus maintained if hydration happens while typing
- [ ] CSS-in-JS styles injected before first paint (no unstyled flash)
- [ ] Dates and currencies render identically on server and client
- [ ] App functions correctly with translation extensions active
- [ ] Lighthouse Total Blocking Time within acceptable range
