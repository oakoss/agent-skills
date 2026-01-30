---
title: Library Selection Guide
description: Motion vs AutoAnimate decision guide with feature comparison, bundle size analysis, use-case breakdown, and recommendations for e-commerce, blog, SaaS, and landing page projects
tags: [auto-animate, motion, library-selection, bundle-size, comparison]
---

# Motion vs AutoAnimate Selection Guide

## Quick Decision

Use **AutoAnimate** (3.28 KB, zero config) when:

- Animating list add/remove/sort operations
- Simple accordion expand/collapse
- Toast notifications, form validation errors
- Bundle size is critical
- Multi-framework (Vue, Svelte, vanilla JS)

Use **Motion** when:

- Gestures (drag, hover with fine control)
- Scroll-based animations or parallax
- Layout/shared element transitions
- SVG path morphing or line drawing
- Spring physics customization
- Complex choreographed animations

**Rule of thumb**: AutoAnimate for 80–90% of cases, Motion for the rest.

## Feature Comparison

| Feature                | AutoAnimate            | Motion                 |
| ---------------------- | ---------------------- | ---------------------- |
| List add/remove        | Automatic              | Manual setup           |
| List reorder           | Automatic              | Manual setup           |
| Accordion              | Automatic              | Manual setup           |
| Drag gestures          | Not supported          | Full control           |
| Hover/tap states       | Not supported          | whileHover, whileTap   |
| Scroll animations      | Not supported          | whileInView, useScroll |
| Parallax               | Not supported          | useTransform           |
| Layout/shared elements | Not supported          | layout prop, layoutId  |
| SVG animations         | Not supported          | path, line drawing     |
| Spring physics         | Not customizable       | Full control           |
| Exit animations        | Automatic              | AnimatePresence        |
| prefers-reduced-motion | Automatic              | Manual (MotionConfig)  |
| Framework support      | React, Vue, Svelte, JS | React only             |

## Bundle Size

| Package                  | Size    | Best For               |
| ------------------------ | ------- | ---------------------- |
| AutoAnimate              | 3.28 KB | Simple list animations |
| Motion useAnimate mini   | 2.3 KB  | Smallest React option  |
| Motion LazyMotion        | 4.6 KB  | Recommended default    |
| Motion useAnimate hybrid | 17 KB   | Imperative + stagger   |
| Motion full              | 34 KB   | All features           |

## AutoAnimate Usage

```tsx
import { useAutoAnimate } from '@formkit/auto-animate/react';

const [parent] = useAutoAnimate();

return (
  <ul ref={parent}>
    {items.map((item) => (
      <li key={item.id}>{item.text}</li>
    ))}
  </ul>
);
```

3 lines of code, zero configuration.

## Use-Case Recommendations

### E-commerce

- **AutoAnimate**: Shopping cart items, product filter results, notification toasts
- **Motion**: Product image carousel (drag), hero parallax, product detail transitions (shared elements)

### Blog / Content Site

- **AutoAnimate**: Article list filtering, comment threads, tag selection
- **Motion**: Hero parallax, scroll-triggered reveals, image lightbox modals

### Dashboard / SaaS

- **AutoAnimate**: Sidebar accordion, data table row add/remove, toast notifications
- **Motion**: Kanban drag-to-reorder, chart animations, complex modal transitions

### Landing Page / Marketing

- **AutoAnimate**: FAQ accordion, feature comparison filtering
- **Motion**: Hero section (parallax, scroll effects), scroll-triggered reveals, interactive demos

## Using Both Together

They complement each other well:

```tsx
const [listRef] = useAutoAnimate();

return (
  <>
    {/* Motion for hero parallax */}
    <motion.div style={{ y: parallaxY }}>Hero section</motion.div>

    {/* AutoAnimate for product list */}
    <ul ref={listRef}>
      {products.map((product) => (
        <li key={product.id}>{product.name}</li>
      ))}
    </ul>

    {/* Motion for carousel */}
    <motion.div drag="x">
      {images.map((img) => (
        <img src={img.url} />
      ))}
    </motion.div>
  </>
);
```

Combined bundle: 3.28 KB (AutoAnimate) + 4.6 KB (LazyMotion) = ~8 KB total.

## Migration

### AutoAnimate → Motion

1. Install: `pnpm add motion`
2. Replace `<div ref={parent}>` with `<motion.div>`
3. Add `initial`, `animate`, `exit` props
4. Wrap in `<AnimatePresence>` for exit animations
5. Add `layout` prop for reordering

### Motion → AutoAnimate

1. Install: `pnpm add @formkit/auto-animate`
2. Remove Motion props (initial, animate, exit, layout)
3. Remove AnimatePresence wrapper
4. Add `useAutoAnimate` hook and attach ref to parent
5. Bundle savings: 34 KB → 3.28 KB (~90% reduction)
