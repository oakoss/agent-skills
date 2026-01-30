---
title: Testing
description: Keyboard-only testing procedure, screen reader testing with VoiceOver and NVDA, axe DevTools scanning, Lighthouse audits, and jest-axe unit tests
tags:
  [testing, keyboard, screen-reader, voiceover, nvda, axe, jest-axe, lighthouse]
---

# Testing

## Keyboard-Only Testing (5 minutes)

1. Hide or unplug mouse
2. Tab through entire page — can you reach all interactive elements?
3. Enter/Space to activate buttons and links
4. Escape to close dialogs and menus
5. Arrow keys within tabs, menus, radio groups
6. Verify focus order is logical

## Screen Reader Testing (10 minutes)

**VoiceOver (Mac, built-in):** Cmd+F5 to start, VO+Right/Left to navigate (VO = Ctrl+Option), VO+A to read all.

**NVDA (Windows, free):** Ctrl+Alt+N to start, arrow keys or Tab to navigate, NVDA+Down to read.

**Screen reader shortcuts:** H/Shift+H to navigate by heading, D/Shift+D to navigate by landmark.

**Verify:** interactive elements announced correctly, images described, form labels read with inputs, dynamic updates announced, heading structure navigable.

## Automated Testing

**axe DevTools** (browser extension): F12 then axe DevTools tab then Scan.

**Lighthouse** (Chrome built-in): F12 then Lighthouse tab, select Accessibility, generate report. Target score 90+.

## jest-axe Unit Tests

```ts
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('has no accessibility violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

## Troubleshooting

### Focus indicators not visible

**Cause:** CSS reset removed outlines or insufficient contrast on indicator.
**Fix:** Add `*:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }`

### Screen reader not announcing updates

**Cause:** No `aria-live` region.
**Fix:** Wrap dynamic content in `<div aria-live="polite">` or use `role="alert"` for errors.

### Dialog focus escapes to background

**Cause:** No focus trap implemented.
**Fix:** Trap focus within dialog, close on Escape, restore focus on close.

### Form errors not announced

**Cause:** Missing `aria-invalid` or `role="alert"`.
**Fix:** Set `aria-invalid="true"` on input, point `aria-describedby` to error element with `role="alert"`.

### Keyboard cannot reach interactive element

**Cause:** Using `<div>` with `onClick` instead of `<button>`.
**Fix:** Use semantic HTML. If custom element unavoidable, add `role="button"`, `tabIndex={0}`, and `onKeyDown` for Enter/Space.

### Heading hierarchy broken

**Cause:** Headings chosen for visual size instead of semantic level.
**Fix:** Use h1-h6 in order. Style with CSS classes, not heading levels.
