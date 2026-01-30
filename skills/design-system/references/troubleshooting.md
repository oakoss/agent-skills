---
title: Troubleshooting
description: Common design system issues including generic UI, mobile breakage, dark mode problems, token sprawl, accessibility failures, theme flash, and hover layout shift
tags: [troubleshooting, dark-mode, accessibility, responsive, tokens, theming]
---

# Troubleshooting

## UI Looks Generic / Lacks Identity

**Cause**: No visual direction or custom tokens.
**Fix**: Define specific color palette (60/30/10 rule), choose intentional font pairing, apply consistent spacing scale.

## Layout Breaks on Mobile

**Cause**: Missing responsive grid rules or breakpoint definitions.
**Fix**: Define breakpoints (640/768/1024/1280px), use mobile-first approach. Test at 375px, 768px, 1024px, 1440px.

## Inconsistent Components Across Screens

**Cause**: Raw values used instead of tokens; no variant system.
**Fix**: Reference all visual values from tokens. Use CVA for variant management. Define component states systematically.

## Dark Mode Colors Look Wrong

**Cause**: Semantic token layer missing; primitive tokens used directly.
**Fix**: Create semantic token layer mapping to different primitives per theme. Never use `#ffffff` or `#000000` — use off-white and dark gray.

## Token Sprawl (Too Many Tokens)

**Cause**: No hierarchy or naming convention; ad-hoc creation.
**Fix**: Audit tokens into three layers (primitive, semantic, component). Remove unused tokens. Enforce naming review in PRs.

## Accessibility Audit Failures

**Cause**: Contrast ratios not checked at semantic token layer.
**Fix**: Verify contrast where foreground meets background. Use automated tools (axe, jest-axe). Check both light and dark themes.

## Flash of Wrong Theme on Load

**Cause**: Theme resolved client-side after paint.
**Fix**: Inject theme script in `<head>` before body renders. Read from `localStorage` or cookie synchronously.

## Hover States Cause Layout Shift

**Cause**: Using `scale()` or `width`/`height` transforms.
**Fix**: Use `translateY(-1px)` and `box-shadow` changes. Avoid `transform: scale()` on interactive cards.

## Pre-Delivery Checklist

**Tokens**: Primitive/semantic/component layers defined, dark mode overrides, all colors meet WCAG contrast, consistent naming.

**Components**: All states implemented (default/hover/focus/active/disabled/loading/error), TypeScript types, sensible defaults, focus-visible ring.

**Responsiveness**: Mobile-first, tested at 375/768/1024/1440px, 44x44px touch targets, no horizontal scroll, fluid text scaling.

**Accessibility**: `prefers-reduced-motion` respected, `prefers-color-scheme` supported, all images have alt text, form inputs have labels, keyboard navigation works, ARIA attributes where needed.
