---
title: Accessibility
description: WCAG 2.2 AA standards, semantic HTML landmarks, ARIA attributes, inclusive design patterns, reduced motion, contrast ratios, and form accessibility
tags:
  [
    accessibility,
    WCAG,
    ARIA,
    semantic-HTML,
    inclusive-design,
    contrast,
    reduced-motion,
  ]
---

## WCAG 2.2 Level AA

### The Four Principles (POUR)

1. **Perceivable**: Provide text alternatives for non-text content
2. **Operable**: Make all functionality available from a keyboard
3. **Understandable**: Make text readable and interface predictable
4. **Robust**: Maximize compatibility with assistive technologies

### Key Success Criteria

| Criterion                   | Requirement                                                     |
| --------------------------- | --------------------------------------------------------------- |
| Normal text contrast        | 4.5:1 minimum                                                   |
| Large text contrast (18pt+) | 3:1 minimum                                                     |
| UI component contrast       | 3:1 for borders, icons, focus rings                             |
| Target size                 | Minimum 24x24 pixels for interactive elements                   |
| Focus visibility            | Focus indicator always visible, not obscured by sticky elements |
| Redundant entry             | Do not require re-entering previously provided information      |

### Reduced Motion

Always respect the user's system motion preferences:

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Semantic HTML

### Landmark Elements

| Element    | Purpose                             |
| ---------- | ----------------------------------- |
| `<header>` | Global site navigation and branding |
| `<main>`   | Unique content of the page          |
| `<nav>`    | Navigation links                    |
| `<aside>`  | Complementary content (sidebar)     |
| `<footer>` | Site-wide links and metadata        |

### Heading Hierarchy

- Only one `<h1>` per page
- Never skip heading levels (do not go from `<h2>` to `<h4>`)
- Headings create a logical outline for screen readers

### Native Elements Over ARIA

The first rule of ARIA: if a native HTML element provides the semantics you need, use it instead.

```html
<!-- Bad -->
<div role="button" onclick="handleClick()">Submit</div>

<!-- Good -->
<button type="submit">Submit</button>
```

## Essential ARIA Attributes

| Attribute          | Use Case                                      |
| ------------------ | --------------------------------------------- |
| `aria-label`       | Icon-only buttons                             |
| `aria-expanded`    | Accordions and dropdowns                      |
| `aria-live`        | Dynamic content updates (toast notifications) |
| `aria-invalid`     | Form validation errors                        |
| `aria-describedby` | Additional field descriptions                 |

### Form Accessibility

```html
<label for="email-input">Email Address</label>
<input id="email-input" type="email" aria-describedby="email-hint" required />
<p id="email-hint">We'll never share your email.</p>
```

## Inclusive Design Patterns

### Multiple Methods of Success

Provide different ways for users to achieve a goal: text search, voice input, and visual selection.

### Error Forgiveness

- Provide "Undo" options for destructive actions
- Use clear, non-judgmental error messages that suggest a path forward

### Cognitive Accessibility

- Use plain language and avoid unnecessary jargon
- Keep interactive elements in predictable locations
- Offer focus mode to hide non-essential UI during deep tasks

### Dark/Light Mode Parity

Neither mode should feel like an afterthought. Check contrast and visual hierarchy in both modes. Use CSS variables or Tailwind theme tokens for consistent switching.

### Situational Inclusion

Design for temporary and situational disabilities:

| Situation         | Accommodation                    |
| ----------------- | -------------------------------- |
| Broken arm        | Full keyboard navigation support |
| Noisy environment | Captions for all video content   |
| Bright sunlight   | High-contrast mode               |
| Slow connection   | Meaningful loading states        |

## Testing Tools

| Tool                                   | Purpose                             |
| -------------------------------------- | ----------------------------------- |
| axe-core                               | Automated accessibility audits      |
| Screen readers (NVDA, JAWS, VoiceOver) | Manual assistive technology testing |
| Keyboard-only navigation               | Navigate entire app without a mouse |
| Color contrast analyzer                | Verify contrast ratios meet WCAG    |
