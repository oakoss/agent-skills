---
name: shadcn-ui
description: 'Builds accessible, customizable component libraries using shadcn/ui with Radix UI, Tailwind CSS 4, and React 19. Covers component ownership, CSS-first theming, type-safe forms with Zod, and direct ref patterns. Use when adding shadcn/ui components, configuring themes, migrating to Tailwind 4, building forms with Zod, or fixing Radix accessibility issues.'
---

# shadcn/ui

## Overview

Guides building accessible, customizable UI with shadcn/ui as a code generation template (not an npm dependency). Covers Radix UI primitives for accessibility, Tailwind CSS 4 CSS-first configuration, React 19 direct ref patterns, and type-safe form validation with Zod.

**When to use:** Adding shadcn/ui components, theming with CSS variables, migrating from Tailwind config to CSS-first, building forms with Server Actions, composing accessible component variants.

**When NOT to use:** Non-React frameworks, projects using a different component library (MUI, Chakra), projects not using Tailwind CSS.

## Quick Reference

| Pattern           | API / Approach                                     | Key Points                                         |
| ----------------- | -------------------------------------------------- | -------------------------------------------------- |
| Add component     | `bun x shadcn-ui@canary add [name]`                | CLI copies source code into your project           |
| Theme tokens      | `@theme { --color-primary: ... }` in `globals.css` | CSS-first config replaces `tailwind.config.js`     |
| Global import     | `@import "tailwindcss";`                           | Replaces `@tailwind base/components/utilities`     |
| Custom utility    | `@utility focus-ring { @apply ... }`               | Define reusable utility classes in CSS             |
| Component variant | `cva()` from `class-variance-authority`            | Type-safe variant definitions                      |
| Polymorphic slot  | `asChild` prop with `<Slot>` from Radix            | Merge props onto child element                     |
| Direct ref        | `ref` as a regular prop                            | `forwardRef` is deprecated in React 19             |
| Form validation   | `useForm` + Zod schema + shadcn `Form`             | Type-safe validation with Server Actions           |
| Form status       | `useFormStatus()` from `react-dom`                 | Pending state for submit buttons                   |
| Optimistic UI     | `useOptimistic()` hook                             | Instant feedback during Server Actions             |
| Dark mode         | HSL CSS variables in `globals.css`                 | Toggle via `.dark` class or `data-theme` attribute |
| Class merging     | `cn()` utility wrapping `clsx` + `twMerge`         | Safely merge Tailwind classes without conflicts    |

## Common Mistakes

| Mistake                                                        | Correct Pattern                                                                  |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Installing shadcn/ui as an npm dependency                      | Use the CLI (`bun x shadcn-ui@canary add`) to copy source code into your project |
| Using `forwardRef` with React 19 components                    | Pass `ref` directly as a prop -- `forwardRef` is deprecated in React 19          |
| Defining theme tokens in `tailwind.config.js` for v4           | Use `@theme { ... }` in `globals.css` with CSS-first configuration               |
| Wrapping HSL variables with `hsl()` (`hsl(var(--background))`) | Reference CSS variables directly: `var(--background)`                            |
| Skipping Zod validation in shadcn/ui Form components           | Always pair Form components with Zod schemas for type-safe validation            |
| Using `div` elements for interactive controls                  | Use Radix primitives (`Button`, `Slot`) for semantic HTML and accessibility      |
| Modifying components in `node_modules`                         | Components live in `src/components/ui` -- own and customize the source code      |

## Delegation

- **Component discovery and Radix primitive lookup**: Use `Explore` agent
- **Theme migration or multi-file refactoring**: Use `Task` agent
- **Design system architecture planning**: Use `Plan` agent

## References

- [Tailwind 4 CSS-first migration](references/tailwind-4-migration.md)
- [React 19 form patterns with Server Actions](references/react-19-forms.md)
- [Component patterns and variants](references/component-patterns.md)
