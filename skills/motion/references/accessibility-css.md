---
title: Accessibility & CSS Animations
description: prefers-reduced-motion with MotionConfig and useReducedMotion, CSS keyframes, and Tailwind custom animation configuration
tags: [accessibility, reduced-motion, css-animations, keyframes, tailwind]
---

# Accessibility & CSS Animations

## prefers-reduced-motion

### Global (Recommended)

```tsx
import { MotionConfig } from 'motion/react';

<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>;
```

Options: `"user"` (respects OS setting), `"always"` (force instant), `"never"` (ignore preference).

Place in root layout or app entry point so all Motion components inherit the setting.

### Per-Component

```tsx
import { useReducedMotion } from 'motion/react';

function AnimatedCard() {
  const shouldReduce = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduce ? 0 : 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: shouldReduce ? 0 : 0.4 }}
    />
  );
}
```

### Manual Media Query (Custom Behavior)

For cases where you need full control beyond MotionConfig:

```tsx
const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

useEffect(() => {
  const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
  setPrefersReducedMotion(mq.matches);
  const handler = () => setPrefersReducedMotion(mq.matches);
  mq.addEventListener('change', handler);
  return () => mq.removeEventListener('change', handler);
}, []);

<motion.div
  initial={{ opacity: prefersReducedMotion ? 1 : 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: prefersReducedMotion ? 1 : 0 }}
  transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
/>;
```

### Accessibility Patterns

When reduced motion is enabled, preserve meaning while removing movement:

```tsx
function AccessibleReveal({ children }: { children: ReactNode }) {
  const shouldReduce = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduce ? 0 : 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: shouldReduce ? 0.1 : 0.5 }}
    >
      {children}
    </motion.div>
  );
}
```

Key principle: keep opacity fade (instant or near-instant) for content reveal, but remove spatial movement (`y`, `x`, `scale`) when reduced motion is preferred.

### Testing Reduced Motion

- **macOS**: System Settings > Accessibility > Display > Reduce motion
- **Windows**: Settings > Ease of Access > Display > Show animations
- **iOS**: Settings > Accessibility > Motion
- **Android 9+**: Settings > Accessibility > Remove animations
- **Chrome DevTools**: Rendering tab > Emulate CSS media feature `prefers-reduced-motion`

## CSS-Only Animations

For cases where Motion is not needed.

### CSS Keyframes

```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .fade-in {
    animation: none;
    opacity: 1;
  }
}
```

### Tailwind Custom Animations

```ts
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(100%)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
    },
  },
};
```

Usage: `<div className="animate-fade-in">Fades in</div>`

### Tailwind v4 CSS Theme

In Tailwind v4, define custom animations in CSS:

```css
@theme {
  --animate-fade-in: fade-in 0.5s ease-out;
  --animate-slide-up: slide-up 0.3s ease-out;

  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slide-up {
    from {
      opacity: 0;
      transform: translateY(100%);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
```

## When to Use CSS vs Motion

| Use CSS When                     | Use Motion When                      |
| -------------------------------- | ------------------------------------ |
| Simple hover effects             | Complex gesture interactions         |
| Basic enter animations           | Exit animations needed               |
| No JavaScript interaction needed | Scroll-linked values                 |
| Performance-critical (0 JS)      | Spring physics or layout transitions |
| Server-rendered static content   | Orchestrated sequences               |
