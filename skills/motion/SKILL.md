---
name: motion
description: |
  Web animations with Motion (Framer Motion) and CSS -- gestures, scroll effects, spring physics, layout animations, SVG, micro-interactions, loading states.

  Use when: drag-and-drop, scroll animations, modals, carousels, parallax, page transitions, hover effects, staggered lists, loading spinners, number counters.
  Troubleshoot: AnimatePresence exit, list performance, Tailwind conflicts, Next.js "use client", layout in scaled containers.
---

# Motion & Web Animation

## Library Selection

| Need                          | Solution                                   |
| ----------------------------- | ------------------------------------------ |
| Simple list add/remove        | AutoAnimate (3.28 KB, zero config)         |
| Gestures, scroll, layout, SVG | Motion (`motion` package)                  |
| CSS-only animation            | Tailwind keyframes or `@keyframes`         |
| 3D animations                 | Three.js / React Three Fiber               |
| Complex drag-and-drop         | DnD Kit for multi-row/column cases         |
| Both simple + complex         | AutoAnimate for lists, Motion for the rest |

**Import**: `import { motion, AnimatePresence } from "motion/react"`

**Package**: `motion` (renamed from `framer-motion` in late 2024 — always use `motion/react` imports)

## Bundle Size Options

| Approach                  | Size   | Use Case              |
| ------------------------- | ------ | --------------------- |
| useAnimate mini           | 2.3 KB | Smallest React option |
| LazyMotion + domAnimation | 4.6 KB | Recommended default   |
| LazyMotion + domMax       | ~6 KB  | Includes SVG paths    |
| useAnimate hybrid         | 17 KB  | Imperative + stagger  |
| Full `motion` component   | 34 KB  | All features          |

## Core Animation Patterns

| Pattern                | Key Props / Hooks                                       |
| ---------------------- | ------------------------------------------------------- |
| Fade in on mount       | `initial`, `animate`, `transition`                      |
| Exit animations        | `AnimatePresence` + `exit` prop (unique `key` required) |
| Staggered list         | `variants` with `staggerChildren`                       |
| Hover / tap            | `whileHover`, `whileTap`                                |
| Modal dialog           | `AnimatePresence` + backdrop + dialog                   |
| Scroll-triggered       | `whileInView`, `viewport={{ once: true }}`              |
| Scroll-linked/parallax | `useScroll`, `useTransform`                             |
| Progress indicator     | `scrollYProgress` + `scaleX`                            |
| Layout animation       | `layout` prop (FLIP technique)                          |
| Shared element         | `layoutId` (same ID across views)                       |
| Drag                   | `drag`, `dragConstraints`, `dragElastic`                |
| Page transition        | `AnimatePresence` + `key={pathname}`                    |
| Loading spinner        | `animate={{ rotate: 360 }}` + `repeat: Infinity`        |
| SVG path drawing       | `pathLength` on `motion.path`                           |
| Animated counter       | `useSpring` + `useTransform`                            |
| Notification badge     | Spring with high stiffness (500) and low damping (15)   |

## Anti-Patterns

| Anti-Pattern                              | Fix                                              |
| ----------------------------------------- | ------------------------------------------------ |
| AnimatePresence inside conditional        | Keep AnimatePresence mounted, conditional inside |
| Missing `key` on AnimatePresence children | Add unique `key` to each direct child            |
| Tailwind `transition-*` + Motion animate  | Remove Tailwind transition classes               |
| Animating `width`/`height` directly       | Use `layout` prop or `transform: scale`          |
| 50+ animated items without virtualization | Use react-window or @tanstack/react-virtual      |
| Full 34 KB bundle for simple animations   | Use LazyMotion + domAnimation (4.6 KB)           |
| `framer-motion` import                    | Use `motion/react` (renamed late 2024)           |
| No `prefers-reduced-motion` handling      | Wrap app in `MotionConfig reducedMotion="user"`  |

## Duration Guidelines

| Range     | Effect                 |
| --------- | ---------------------- |
| < 100ms   | Too fast (abrupt)      |
| 200–400ms | Sweet spot for most UI |
| > 500ms   | Too slow (sluggish)    |

## GPU-Accelerated Properties

| Animate (good)                    | Avoid (triggers reflow)          |
| --------------------------------- | -------------------------------- |
| `transform` (x, y, scale, rotate) | `width`, `height`                |
| `opacity`                         | `top`, `left`, `right`, `bottom` |
| `filter` (blur, brightness)       | `padding`, `margin`              |

## Common Mistakes

| Mistake                                                                                     | Correct Pattern                                                                |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Placing `AnimatePresence` inside a conditional instead of wrapping the conditional children | Keep `AnimatePresence` always mounted; place the conditional content inside it |
| Forgetting unique `key` props on `AnimatePresence` direct children                          | Add a unique `key` to each direct child so exit animations trigger correctly   |
| Combining Tailwind `transition-*` classes with Motion animate props                         | Remove Tailwind transition classes when using Motion to avoid conflicts        |
| Importing from `framer-motion` instead of the renamed package                               | Use `import { motion } from "motion/react"` (renamed late 2024)                |
| Animating 50+ items without virtualization                                                  | Use react-window or @tanstack/react-virtual for large animated lists           |

## Delegation

- **Audit animation performance and bundle size across the app**: Use `Explore` agent to identify heavy imports, missing LazyMotion usage, and reflow-triggering properties
- **Implement complex multi-step animations with scroll and layout**: Use `Task` agent to build scroll-linked parallax, shared layout transitions, and staggered sequences
- **Plan animation architecture and library selection for a new project**: Use `Plan` agent to evaluate Motion vs AutoAnimate vs CSS-only based on requirements and bundle budget

## References

- [Core Patterns](references/core-patterns.md) — All animation pattern code examples
- [Performance](references/performance.md) — Bundle optimization, runtime perf, large lists, production checklist
- [Accessibility & CSS](references/accessibility-css.md) — prefers-reduced-motion, CSS keyframes, Tailwind custom animations
- [Next.js Integration](references/nextjs-integration.md) — App Router patterns, Pages Router, known issues
- [Library Selection Guide](references/library-selection.md) — Motion vs AutoAnimate decision guide with use-case breakdown
- [Troubleshooting](references/troubleshooting.md) — Common issues, naming migration, React 19 bugs
