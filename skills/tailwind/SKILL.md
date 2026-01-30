---
name: tailwind
description: 'Tailwind CSS v4 patterns and design systems. Use when configuring Tailwind themes, migrating from v3, building components with shadcn/ui, implementing design tokens, or fixing colors/dark mode/build errors.'
---

# Tailwind CSS (v4+)

Comprehensive Tailwind CSS v4 skill covering CSS-first configuration, design tokens, component patterns, shadcn/ui integration, dark mode, migration from v3, and advanced design systems.

## v4 Do's and Don'ts

| Don't                                   | Do                                   |
| :-------------------------------------- | :----------------------------------- |
| `tailwind.config.js`                    | `@theme { ... }` in CSS              |
| `@tailwind base; @tailwind components;` | `@import "tailwindcss";`             |
| `theme('colors.brand')`                 | `var(--color-brand)`                 |
| `require()` in plugins                  | `@plugin "@tailwindcss/typography";` |
| `tailwindcss-animate`                   | `tw-animate-css`                     |
| `hsl(var(--background))` double-wrap    | `var(--background)` direct reference |
| `:root`/`.dark` inside `@layer base`    | `:root`/`.dark` at root level        |
| `@apply` with `@layer components`       | `@utility` directive                 |
| Raw colors like `bg-blue-500`           | Semantic tokens like `bg-primary`    |

## Spacing Scale

| Usage       | Classes          | Value         |
| ----------- | ---------------- | ------------- |
| Tight       | `gap-2 p-2`      | 0.5rem (8px)  |
| Standard    | `gap-4 p-4`      | 1rem (16px)   |
| Comfortable | `gap-6 p-6`      | 1.5rem (24px) |
| Loose       | `gap-8 p-8`      | 2rem (32px)   |
| Section     | `py-16 sm:py-24` | 4rem/6rem     |

## Responsive Breakpoints (Mobile-First)

| Breakpoint | Min Width | Example          |
| ---------- | --------- | ---------------- |
| Base       | 0px       | `text-base`      |
| sm         | 640px     | `sm:text-lg`     |
| md         | 768px     | `md:grid-cols-2` |
| lg         | 1024px    | `lg:px-8`        |
| xl         | 1280px    | `xl:max-w-7xl`   |
| 2xl        | 1536px    | `2xl:text-6xl`   |

## Semantic Color Tokens (Dark Mode Auto-Adapts)

| Token                   | Light       | Dark                  |
| ----------------------- | ----------- | --------------------- |
| `bg-background`         | White       | Dark gray             |
| `text-foreground`       | Dark gray   | White                 |
| `bg-card`               | White       | Slightly lighter gray |
| `text-muted-foreground` | Gray        | Light gray            |
| `border-border`         | Light gray  | Dark gray             |
| `bg-primary`            | Brand color | Lighter brand         |

## Built-in v4 Features (No Plugins)

| Feature           | Usage                                       |
| ----------------- | ------------------------------------------- |
| Container queries | `@container` parent + `@md:` child variants |
| Line clamp        | `line-clamp-3`                              |
| 3D transforms     | `perspective-1000 hover:rotate-y-12`        |
| Dynamic utilities | `grid-cols-(--my-grid-count)`               |

## Design Token Hierarchy

| Level     | Example     | Purpose                  |
| --------- | ----------- | ------------------------ |
| Brand     | `blue-500`  | Abstract color values    |
| Semantic  | `primary`   | Purpose-driven tokens    |
| Component | `button-bg` | Specific component usage |

## Anti-Patterns

| Anti-Pattern                                   | Fix                                          |
| ---------------------------------------------- | -------------------------------------------- |
| `tailwind.config.js` in v4                     | CSS-only via `@theme`                        |
| `hsl(var(--background))` double-wrap           | `var(--background)` directly                 |
| `:root`/`.dark` inside `@layer base`           | Define at root level                         |
| `@theme inline` for multi-theme                | `@theme` without `inline`                    |
| `@apply` with `@layer components`              | `@utility` directive                         |
| `dark:` variants with semantic tokens          | Tokens auto-adapt via CSS variables          |
| Raw colors (`bg-blue-500`)                     | Semantic tokens (`bg-primary`)               |
| Arbitrary values (`text-[16px]`)               | Define in `@theme`                           |
| Missing `transition-*` on interactive elements | Add smooth state changes                     |
| Inconsistent spacing                           | Stick to 4-based scale (4, 6, 8, 12, 16, 24) |

## Common Mistakes

| Mistake                                                 | Correct Pattern                                                       |
| ------------------------------------------------------- | --------------------------------------------------------------------- |
| Using `tailwind.config.js` in v4 projects               | Configure via `@theme { ... }` in CSS — v4 is CSS-first               |
| Double-wrapping HSL variables: `hsl(var(--background))` | Reference directly: `var(--background)` — v4 stores full color values |
| Placing `:root`/`.dark` selectors inside `@layer base`  | Define `:root` and `.dark` at root level, outside any `@layer`        |
| Using `@apply` with `@layer components`                 | Use `@utility` directive for custom utilities in v4                   |
| Using raw colors like `bg-blue-500` throughout          | Define semantic tokens (`bg-primary`) that auto-adapt for dark mode   |

## Delegation

- **Tailwind class pattern discovery and usage examples**: Use `Explore` agent
- **v3 to v4 migration across multiple files**: Use `Task` agent
- **Design token hierarchy and theming architecture**: Use `Plan` agent

## References

- [Configuration](references/configuration.md) — CSS-first config, @theme, @theme inline, plugins, @utility, OKLCH colors
- [Design Tokens](references/design-tokens.md) — Complete token system, dark mode, multi-theme, fluid typography, monorepo
- [Component Patterns](references/component-patterns.md) — Layouts, grids, cards, sticky headers, CVA variants
- [shadcn/ui Integration](references/shadcn-integration.md) — Four-step architecture, components.json, dark mode setup
- [Troubleshooting](references/troubleshooting.md) — Common errors, v3 → v4 migration steps, build fixes
