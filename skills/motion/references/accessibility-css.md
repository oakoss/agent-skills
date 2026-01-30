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

### Per-Component

```tsx
import { useReducedMotion } from 'motion/react';

const shouldReduce = useReducedMotion();

<motion.div
  initial={{ opacity: 0, y: shouldReduce ? 0 : 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: shouldReduce ? 0 : 0.4 }}
/>;
```

### Known Issue: AnimatePresence + Reduced Motion

MotionConfig `reducedMotion` doesn't disable AnimatePresence animations (GitHub issue #1567). Workaround — manual media query check:

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

### Testing Reduced Motion

- **macOS**: System Settings → Accessibility → Display → Reduce motion
- **Windows**: Settings → Ease of Access → Display → Show animations
- **iOS**: Settings → Accessibility → Motion
- **Android 9+**: Settings → Accessibility → Remove animations

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
      },
      animation: {
        'fade-in': 'fade-in 0.5s ease-out',
      },
    },
  },
};
```

Usage: `<div className="animate-fade-in">Fades in</div>`
