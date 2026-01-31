---
title: Accessibility
description: WCAG compliance requirements, keyboard navigation, focus management, ARIA patterns, screen reader testing, reduced motion, high contrast, and automated a11y testing
tags:
  [
    accessibility,
    wcag,
    aria,
    keyboard,
    focus,
    screen-reader,
    reduced-motion,
    contrast,
  ]
---

# Accessibility

Accessibility is built into design system foundations, not bolted on after. Every component ships with keyboard support, ARIA semantics, and contrast compliance by default.

## WCAG 2.1 AA Requirements

| Check                 | Requirement                              | Level |
| --------------------- | ---------------------------------------- | ----- |
| Normal text contrast  | 4.5:1 ratio minimum                      | AA    |
| Large text contrast   | 3:1 ratio (18px+ or 14px bold)           | AA    |
| UI component contrast | 3:1 ratio against adjacent colors        | AA    |
| Touch targets         | 44x44px minimum                          | AAA   |
| Focus indicators      | Visible ring on all interactive elements | AA    |
| Reduced motion        | Respect `prefers-reduced-motion`         | AA    |
| Body font size        | 16px minimum on mobile                   | Best  |
| Line length           | 65-75 characters maximum                 | Best  |
| Text spacing          | Support 1.5x line height, 2x paragraph   | AA    |

## Focus Management

Every interactive element needs a visible focus indicator. Use `focus-visible` to show the ring only for keyboard users.

```css
/* Base focus style for all interactive elements */
:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

/* Remove default outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}

/* Ensure buttons, links, inputs all have focus styles */
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

## Keyboard Navigation Patterns

| Component | Keys                      | Behavior                        |
| --------- | ------------------------- | ------------------------------- |
| Button    | Enter, Space              | Activate                        |
| Link      | Enter                     | Navigate                        |
| Menu      | Arrow keys, Escape        | Navigate items, close           |
| Dialog    | Escape, Tab (trapped)     | Close, cycle focus within       |
| Tabs      | Arrow keys, Home, End     | Switch tabs                     |
| Combobox  | Arrow keys, Enter, Escape | Navigate options, select, close |
| Checkbox  | Space                     | Toggle                          |
| Radio     | Arrow keys                | Move selection within group     |

## Focus Trapping in Dialogs

When a dialog opens, trap focus inside it. Return focus to the trigger when it closes.

```tsx
import { useEffect, useRef } from 'react';

function useFocusTrap(isOpen: boolean) {
  const containerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    triggerRef.current = document.activeElement as HTMLElement;

    const focusable = containerRef.current.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    first?.focus();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      triggerRef.current?.focus();
    };
  }, [isOpen]);

  return containerRef;
}
```

## ARIA Patterns for Common Components

### Buttons with Loading State

```tsx
<button disabled={isLoading} aria-busy={isLoading || undefined}>
  {isLoading ? <Spinner aria-hidden="true" /> : null}
  <span className={isLoading ? 'sr-only' : undefined}>Save</span>
</button>
```

### Form Validation

```tsx
<div>
  <label htmlFor="email">Email</label>
  <input
    id="email"
    type="email"
    aria-invalid={!!error}
    aria-describedby={error ? 'email-error' : undefined}
  />
  {error ? (
    <p id="email-error" role="alert">
      {error}
    </p>
  ) : null}
</div>
```

### Live Regions for Notifications

```tsx
<div aria-live="polite" aria-atomic="true" className="sr-only">
  {statusMessage}
</div>
```

Use `aria-live="polite"` for non-urgent updates and `aria-live="assertive"` for critical alerts.

### Skip Navigation

```tsx
<a
  href="#main-content"
  className="sr-only focus:not-sr-only focus:absolute focus:z-50"
>
  Skip to main content
</a>
```

## Screen Reader Only Utility

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

## Reduced Motion

Respect user preference for reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

In JavaScript, check the preference before triggering animations:

```ts
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)',
).matches;

const animationDuration = prefersReducedMotion ? 0 : 300;
```

## High Contrast Mode

Support Windows High Contrast Mode and forced colors:

```css
@media (forced-colors: active) {
  .button {
    border: 1px solid ButtonText;
  }

  .icon {
    forced-color-adjust: auto;
  }
}
```

## Automated Testing

### jest-axe for Unit Tests

```ts
import { axe, toHaveNoViolations } from 'jest-axe';
import { render } from '@testing-library/react';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  expect(await axe(container)).toHaveNoViolations();
});
```

### Storybook a11y Addon

Add `@storybook/addon-a11y` to run axe checks on every story automatically. Violations appear in the Accessibility panel during development.

### Accessibility Audit Checklist

- Color contrast passes in both light and dark themes
- All interactive elements reachable via keyboard
- Focus indicator visible on every focusable element
- Form inputs have associated labels
- Images have descriptive alt text
- Dialogs trap focus and return it on close
- `aria-live` regions announce dynamic content changes
- `prefers-reduced-motion` respected
- Skip navigation link present
- Tested with VoiceOver (macOS), NVDA (Windows), or TalkBack (Android)
