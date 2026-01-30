---
title: Accessibility Guide
description: WCAG 2.1 AA compliance guidelines covering color contrast, keyboard navigation, screen readers, focus states, and comprehensive audit checklists
tags:
  [
    accessibility,
    WCAG,
    keyboard-navigation,
    screen-readers,
    color-contrast,
    ARIA,
  ]
---

# Accessibility Guide

Accessibility ensures that all users, regardless of ability, can effectively use the interface. Target WCAG 2.1 AA compliance as the minimum standard.

## Color Contrast Requirements

| Element                | Minimum Ratio | WCAG Level |
| ---------------------- | ------------- | ---------- |
| Normal text            | 4.5:1         | AA         |
| Large text (18px+)     | 3:1           | AA         |
| UI components          | 3:1           | AA         |
| Normal text (enhanced) | 7:1           | AAA        |
| Large text (enhanced)  | 4.5:1         | AAA        |

**Tips:**

- Test contrast with tools like WebAIM Contrast Checker
- Do not rely on color alone to convey information (use icons or text labels)
- Ensure contrast is sufficient in both light and dark modes

## Keyboard Navigation

All interactive elements must be operable via keyboard alone.

**Required keyboard behaviors:**

| Key        | Expected Behavior                          |
| ---------- | ------------------------------------------ |
| Tab        | Move focus to next interactive element     |
| Shift+Tab  | Move focus to previous interactive element |
| Enter      | Activate buttons, submit forms             |
| Space      | Toggle checkboxes, activate buttons        |
| Escape     | Close modals, dismiss popups               |
| Arrow keys | Navigate within menus, tabs, sliders       |

**Focus management rules:**

- Tab order must follow the visual reading order (top-to-bottom, left-to-right)
- Focus indicators must be visible (at least 2px outline or equivalent)
- Focus should not get trapped in any component (except modals with explicit escape)
- After closing a modal, focus returns to the element that triggered it

## Screen Reader Support

**Semantic HTML first:**

```html
<!-- CORRECT: Semantic elements provide meaning -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<main>
  <article>
    <h1>Page Title</h1>
    <section aria-labelledby="section-heading">
      <h2 id="section-heading">Section</h2>
      <p>Content here.</p>
    </section>
  </article>
</main>

<!-- WRONG: Divs with no semantic meaning -->
<div class="nav">
  <div class="link">Home</div>
</div>
```

**ARIA usage rules:**

- Use semantic HTML before reaching for ARIA attributes
- `aria-label` for icon-only buttons (e.g., close button with X icon)
- `aria-describedby` for form field help text
- `aria-live="polite"` for dynamic content updates (notifications, alerts)
- `aria-expanded` for collapsible sections and dropdown menus
- Never use ARIA to override correct semantic HTML behavior

## Form Accessibility

```html
<!-- CORRECT: Label associated with input -->
<label for="email">Email address</label>
<input id="email" type="email" aria-describedby="email-help" required />
<span id="email-help">We will never share your email.</span>

<!-- Error state -->
<label for="password">Password</label>
<input
  id="password"
  type="password"
  aria-invalid="true"
  aria-describedby="password-error"
/>
<span id="password-error" role="alert"
  >Password must be at least 8 characters.</span
>
```

**Form rules:**

- Every input must have an associated `<label>` element
- Error messages must be programmatically associated with the input
- Required fields must be indicated visually and programmatically
- Form groups should use `<fieldset>` and `<legend>`

## Images and Media

- All meaningful images must have descriptive `alt` text
- Decorative images use `alt=""` (empty) to be skipped by screen readers
- Video content needs captions and transcripts
- Audio content needs transcripts
- No auto-playing media with sound

## Responsive and Zoom

- Content must be usable at 200% zoom
- No horizontal scrolling at standard viewport widths
- Touch targets must be at least 44x44px on mobile devices
- Text must be resizable without breaking layout

## Comprehensive Audit Checklist

- [ ] Color contrast meets 4.5:1 for normal text, 3:1 for large text
- [ ] Keyboard navigation works for all interactive elements (Tab, Enter, Escape)
- [ ] Focus indicators are visible on all focused elements
- [ ] Alt text provided for all meaningful images
- [ ] Form labels associated with inputs via `for`/`id`
- [ ] Semantic HTML used (headings, nav, main, article, section)
- [ ] ARIA labels added for icon-only buttons
- [ ] Screen reader tested (VoiceOver, NVDA, or JAWS)
- [ ] Zoom to 200% works without horizontal scrolling
- [ ] No flashing content faster than 3 times per second (seizure risk)
- [ ] Error messages are descriptive and associated with fields
- [ ] Dynamic content updates announced via `aria-live` regions
- [ ] Modals trap focus and return focus on close
- [ ] Skip navigation link available for keyboard users
