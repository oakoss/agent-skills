---
name: design-system
description: 'Builds scalable design systems with tokens, theming, and component architecture. Use when creating design token hierarchies, theming systems, or component state definitions. Use for color theory, typography scales, accessibility compliance, and CVA variant patterns.'
version: 1.0.0
tags:
  [
    design-system,
    design-tokens,
    theming,
    components,
    accessibility,
    cva,
    tailwind,
  ]
---

# Design System

Single source of truth bringing consistency at scale — shared language between design and engineering.

## Token Hierarchy (Three Layers)

| Layer     | Purpose                              | Example                                                                   |
| --------- | ------------------------------------ | ------------------------------------------------------------------------- |
| Primitive | Raw values, never used in components | `color-blue-500: #3b82f6`, `space-4: 1rem`                                |
| Semantic  | Meaning, theme-switchable            | `interactive-primary: {color-blue-500}`, `text-primary: {color-gray-900}` |
| Component | Specific usage                       | `button-bg: {interactive-primary}`, `card-shadow: {elevation-card}`       |

## Token Categories

| Category   | Primitive                 | Semantic                          | Component                             |
| ---------- | ------------------------- | --------------------------------- | ------------------------------------- |
| Color      | `color-blue-500: #3b82f6` | `color-primary: {blue-500}`       | `button-bg: {color-primary}`          |
| Spacing    | `space-4: 16px`           | `spacing-default: {space-4}`      | `button-padding-x: {spacing-default}` |
| Typography | `font-size-base: 1rem`    | `text-body: {font-size-base}`     | `input-font-size: {text-body}`        |
| Shadow     | `shadow-md: 0 4px 6px...` | `elevation-card: {shadow-md}`     | `card-shadow: {elevation-card}`       |
| Radius     | `radius-md: 0.5rem`       | `radius-interactive: {radius-md}` | `button-radius: {radius-interactive}` |

## Accessibility Minimums

| Check                 | Requirement                              |
| --------------------- | ---------------------------------------- |
| Normal text contrast  | 4.5:1 ratio (WCAG AA)                    |
| Large text contrast   | 3:1 ratio                                |
| UI component contrast | 3:1 ratio                                |
| Touch targets         | 44x44px minimum                          |
| Focus indicators      | Visible ring on all interactive elements |
| Reduced motion        | Respect `prefers-reduced-motion`         |
| Body font size        | 16px minimum on mobile                   |
| Line length           | 65-75 characters max                     |

## Component States

| State          | Visual                              | ARIA                  |
| -------------- | ----------------------------------- | --------------------- |
| Default        | Base styles                         | —                     |
| Hover          | Background/shadow shift             | —                     |
| Focus          | Visible ring (`outline: 2px solid`) | —                     |
| Active/Pressed | Darker shade                        | —                     |
| Disabled       | 50% opacity, `cursor: not-allowed`  | `aria-disabled`       |
| Loading        | Spinner overlay, text hidden        | `aria-busy="true"`    |
| Error          | Red border, error message           | `aria-invalid="true"` |

## Anti-Patterns

| Anti-Pattern                                | Fix                                                    |
| ------------------------------------------- | ------------------------------------------------------ |
| Hardcoded hex/px in components              | Use semantic tokens                                    |
| Flat token list (no layers)                 | Use primitive > semantic > component hierarchy         |
| Primitive tokens in components (`blue-500`) | Use semantic names (`interactive-primary`)             |
| No focus states                             | Add `focus-visible:ring-2` on all interactive elements |
| `scale` transforms on hover                 | Use `translateY(-1px)` + shadow changes                |
| No `prefers-reduced-motion`                 | Wrap animations in media query                         |
| Circular token references                   | Audit token dependency graph                           |
| Deep CSS nesting for overrides              | Use CSS custom properties                              |
| `color: gray-400` for body text             | Use `gray-600`+ (fails contrast in light mode)         |

## Common Mistakes

| Mistake                                                    | Correct Pattern                                                          |
| ---------------------------------------------------------- | ------------------------------------------------------------------------ |
| Using primitive tokens directly in components (`blue-500`) | Reference semantic tokens (`interactive-primary`) that map to primitives |
| Skipping focus states on interactive elements              | Add `focus-visible:ring-2` on every button, link, and input              |
| Setting body text to `gray-400`                            | Use `gray-600` or darker to meet WCAG AA contrast ratios in light mode   |
| Circular token references between layers                   | Audit the token dependency graph; tokens should flow one direction only  |
| Ignoring `prefers-reduced-motion`                          | Wrap all animations in a reduced-motion media query                      |

## Delegation

- **Explore existing codebase for hardcoded values that should be tokens**: Use `Explore` agent
- **Migrate an entire component library to a token-based design system**: Use `Task` agent
- **Plan a multi-brand theming architecture with token layers**: Use `Plan` agent

## References

- [Design Tokens](references/design-tokens.md)
- [Theming](references/theming.md)
- [Color and Typography](references/color-and-typography.md)
- [Component Architecture](references/component-architecture.md)
- [Motion and Layout](references/motion-and-layout.md)
- [Tooling](references/tooling.md)
- [Troubleshooting](references/troubleshooting.md)
