---
title: Troubleshooting
description: Common design system issues including generic UI, mobile breakage, dark mode problems, token sprawl, accessibility failures, theme flash, hover layout shift, and pre-delivery checklist
tags:
  [
    troubleshooting,
    dark-mode,
    accessibility,
    responsive,
    tokens,
    theming,
    checklist,
  ]
---

# Troubleshooting

## UI Looks Generic / Lacks Identity

**Cause**: No visual direction or custom tokens.
**Fix**: Define specific color palette (60/30/10 rule), choose intentional font pairing, apply consistent spacing scale. Avoid default framework styles without customization.

## Layout Breaks on Mobile

**Cause**: Missing responsive grid rules or breakpoint definitions.
**Fix**: Define breakpoints (640/768/1024/1280px), use mobile-first approach. Test at 375px, 768px, 1024px, 1440px. Ensure touch targets are 44x44px minimum.

## Inconsistent Components Across Screens

**Cause**: Raw values used instead of tokens; no variant system.
**Fix**: Reference all visual values from tokens. Use CVA for variant management. Define component states systematically (default, hover, focus, active, disabled, loading, error).

## Dark Mode Colors Look Wrong

**Cause**: Semantic token layer missing; primitive tokens used directly.
**Fix**: Create semantic token layer mapping to different primitives per theme. Never use `#ffffff` or `#000000` — use off-white (`#f9fafb`) and dark gray (`#111827`). Re-verify contrast ratios in both themes.

## Token Sprawl (Too Many Tokens)

**Cause**: No hierarchy or naming convention; ad-hoc creation.
**Fix**: Audit tokens into three layers (primitive, semantic, component). Remove unused tokens. Enforce naming review in PRs. Use `color-mix()` for derived values instead of new tokens.

## Accessibility Audit Failures

**Cause**: Contrast ratios not checked at semantic token layer; missing ARIA attributes.
**Fix**: Verify contrast where foreground meets background. Use automated tools (axe, jest-axe). Check both light and dark themes. Add `aria-invalid`, `aria-busy`, `aria-describedby` where appropriate.

## Flash of Wrong Theme on Load

**Cause**: Theme resolved client-side after paint.
**Fix**: Inject theme script in `<head>` before body renders. Read from `localStorage` or cookie synchronously. For SSR frameworks, set `data-theme` on the server response.

## Hover States Cause Layout Shift

**Cause**: Using `scale()` or `width`/`height` transforms on hover.
**Fix**: Use `translateY(-1px)` and `box-shadow` changes. Avoid `transform: scale()` on interactive cards. Animate only `transform` and `opacity` for GPU-accelerated rendering.

## Components Not Tree-Shakeable

**Cause**: Barrel file re-exports everything; bundler cannot eliminate unused code.
**Fix**: Use named exports per component. Ensure `sideEffects: false` in `package.json`. Use `tsup` or `rollup` with proper ESM output.

## Tokens Not Syncing from Figma

**Cause**: Token naming mismatch between Figma and code.
**Fix**: Use Tokens Studio with a shared naming convention. Automate the sync via CI (push to branch, run Style Dictionary, create PR). Validate token names on both sides match.

## Pre-Delivery Checklist

**Tokens**: Primitive/semantic/component layers defined, dark mode overrides, all colors meet WCAG contrast, consistent naming, no circular references.

**Components**: All states implemented (default/hover/focus/active/disabled/loading/error), TypeScript types exported, sensible defaults, `focus-visible` ring on all interactive elements.

**Responsiveness**: Mobile-first, tested at 375/768/1024/1440px, 44x44px touch targets, no horizontal scroll, fluid or responsive text scaling.

**Accessibility**: `prefers-reduced-motion` respected, `prefers-color-scheme` supported, all images have alt text, form inputs have labels, keyboard navigation works, ARIA attributes present, skip navigation link, tested with screen reader.

**Governance**: Changelog updated, version bumped, Storybook stories for new components, migration guide for breaking changes.
