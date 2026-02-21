---
title: Animation and Micro-interactions
description: CSS transitions, micro-interaction patterns, loading states, page transitions, spring animations, reduced motion, and Tailwind animation utilities
tags:
  [
    animation,
    transitions,
    micro-interactions,
    loading,
    reduced-motion,
    tailwind,
    performance,
  ]
---

## CSS Transition Fundamentals

### Timing Functions

Choose timing functions based on the direction of motion:

| Direction        | Timing Function | Reason                                    |
| ---------------- | --------------- | ----------------------------------------- |
| Enter/appear     | `ease-out`      | Starts fast, decelerates — feels snappy   |
| Exit/disappear   | `ease-in`       | Starts slow, accelerates — feels natural  |
| Move/reposition  | `ease-in-out`   | Smooth start and end for spatial movement |
| Instant feedback | `linear`        | Consistent speed for progress indicators  |

### Duration Guidelines

| Category | Duration  | Use Case                                    |
| -------- | --------- | ------------------------------------------- |
| Micro    | 100-150ms | Button press, toggle, color shift           |
| Small    | 150-300ms | Hover states, focus rings, tooltip show     |
| Medium   | 300-500ms | Layout shifts, accordion expand, card flip  |
| Large    | 500-800ms | Page transitions, modal enter, route change |

Anything over 300ms should be interruptible. Never exceed 1000ms for UI transitions.

### Base Transition Pattern

```css
.interactive-element {
  transition-property: transform, opacity, box-shadow;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}
```

## Hover and Focus State Transitions

### Button Hover

```tsx
<button className="bg-blue-600 text-white px-4 py-2 rounded-lg transition-all duration-150 ease-out hover:bg-blue-700 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0 active:shadow-sm">
  Save Changes
</button>
```

### Card Hover with Lift Effect

```tsx
<div className="rounded-2xl bg-white p-6 shadow-sm transition-all duration-200 ease-out hover:shadow-lg hover:-translate-y-1">
  <h3 className="text-lg font-semibold">Card Title</h3>
</div>
```

### Focus Ring with Transition

```tsx
<input className="rounded-lg border border-gray-300 px-3 py-2 transition-all duration-150 ease-out focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none" />
```

### Icon Hover Rotation

```tsx
<button className="group p-2 rounded-full transition-colors duration-150 hover:bg-gray-100">
  <svg className="h-5 w-5 transition-transform duration-200 ease-out group-hover:rotate-12" />
</button>
```

## Loading State Patterns

### Skeleton Screen

```tsx
function SkeletonCard() {
  return (
    <div className="animate-pulse space-y-4 rounded-2xl bg-white p-6">
      <div className="h-4 w-3/4 rounded bg-gray-200" />
      <div className="h-4 w-1/2 rounded bg-gray-200" />
      <div className="h-32 rounded-lg bg-gray-200" />
    </div>
  );
}
```

### Shimmer Effect

```css
@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-shimmer {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

### Spinner with Accessible Label

```tsx
<div className="flex items-center gap-2">
  <svg
    className="h-5 w-5 animate-spin text-blue-600"
    viewBox="0 0 24 24"
    fill="none"
  >
    <circle
      className="opacity-25"
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="4"
    />
    <path
      className="opacity-75"
      fill="currentColor"
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
    />
  </svg>
  <span className="sr-only">Loading</span>
</div>
```

### Progress Bar

```tsx
function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
      <div
        className="h-full rounded-full bg-blue-600 transition-all duration-300 ease-out"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={100}
      />
    </div>
  );
}
```

## Micro-interactions

### Button Press Feedback

```tsx
<button className="transform rounded-lg bg-blue-600 px-4 py-2 text-white transition-all duration-100 ease-out hover:bg-blue-700 active:scale-95">
  Submit
</button>
```

### Toggle Switch

```tsx
function Toggle({
  checked,
  onChange,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <button
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ease-out ${checked ? 'bg-blue-600' : 'bg-gray-300'}`}
    >
      <span
        className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200 ease-out ${checked ? 'translate-x-6' : 'translate-x-1'}`}
      />
    </button>
  );
}
```

### Form Input Focus

```tsx
<div className="group relative">
  <label className="absolute -top-2.5 left-3 bg-white px-1 text-xs text-gray-500 transition-all duration-150 ease-out group-focus-within:text-blue-600">
    Email
  </label>
  <input className="w-full rounded-lg border border-gray-300 px-3 py-2 transition-all duration-150 ease-out focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none" />
</div>
```

### Success State

```tsx
<div className="flex items-center gap-2 rounded-lg bg-green-50 px-4 py-3 text-green-700 animate-in fade-in slide-in-from-top-2 duration-300">
  <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
    <path
      fillRule="evenodd"
      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
      clipRule="evenodd"
    />
  </svg>
  <span>Changes saved successfully</span>
</div>
```

### Error Shake

```css
@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20%,
  60% {
    transform: translateX(-4px);
  }
  40%,
  80% {
    transform: translateX(4px);
  }
}

.shake {
  animation: shake 400ms ease-out;
}
```

## Page Transition Patterns

### Fade Transition

```css
.page-enter {
  opacity: 0;
}

.page-enter-active {
  opacity: 1;
  transition: opacity 300ms ease-out;
}

.page-exit {
  opacity: 1;
}

.page-exit-active {
  opacity: 0;
  transition: opacity 200ms ease-in;
}
```

### Slide Transition

```css
.slide-enter {
  transform: translateX(100%);
  opacity: 0;
}

.slide-enter-active {
  transform: translateX(0);
  opacity: 1;
  transition:
    transform 300ms ease-out,
    opacity 300ms ease-out;
}

.slide-exit-active {
  transform: translateX(-30%);
  opacity: 0;
  transition:
    transform 200ms ease-in,
    opacity 200ms ease-in;
}
```

### Cross-fade Between Views

```tsx
function CrossFade({
  show,
  children,
}: {
  show: boolean;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`transition-all duration-300 ease-out ${show ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'}`}
    >
      {children}
    </div>
  );
}
```

## Spring Animations with CSS

Approximate spring physics using `cubic-bezier`. Real spring motion overshoots then settles.

### Common Spring Curves

```css
:root {
  --spring-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --spring-smooth: cubic-bezier(0.22, 1, 0.36, 1);
  --spring-snappy: cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Bounce-in Effect

```tsx
<div className="transition-transform duration-500 [transition-timing-function:cubic-bezier(0.34,1.56,0.64,1)] hover:scale-105">
  Bouncy Card
</div>
```

### Modal Enter with Spring

```css
@keyframes spring-in {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(8px);
  }
  70% {
    transform: scale(1.02) translateY(-2px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-enter {
  animation: spring-in 400ms cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
```

## Reduced Motion

Always respect user preferences. Provide functional alternatives, not just removal.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Tailwind Approach

```tsx
<div className="transition-transform duration-300 hover:-translate-y-1 motion-reduce:transition-none motion-reduce:hover:translate-y-0">
  Respects user preferences
</div>
```

### JavaScript Detection

```ts
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)',
).matches;
```

## Tailwind CSS Animation Utilities

### Built-in Animations

| Class            | Effect              | Use Case            |
| ---------------- | ------------------- | ------------------- |
| `animate-spin`   | Continuous rotation | Loading spinners    |
| `animate-ping`   | Scale + fade out    | Notification badges |
| `animate-pulse`  | Opacity oscillation | Skeleton screens    |
| `animate-bounce` | Vertical bounce     | Scroll indicators   |

### Custom Keyframes in Tailwind Config

```ts
export default {
  theme: {
    extend: {
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 300ms ease-out',
        'slide-up': 'slide-up 300ms ease-out',
      },
    },
  },
};
```

### Transition Utilities

```tsx
<div className="transition-all duration-200 ease-out">All properties</div>
<div className="transition-colors duration-150">Color changes only</div>
<div className="transition-transform duration-300">Transform only</div>
<div className="transition-opacity duration-200">Opacity only</div>
```

## Performance

### Compositor-Only Properties

Prefer animating properties the browser can handle on the GPU without triggering layout or paint:

| Safe (compositor) | Unsafe (triggers layout)         |
| ----------------- | -------------------------------- |
| `transform`       | `width`, `height`                |
| `opacity`         | `top`, `left`, `right`, `bottom` |
| `filter`          | `margin`, `padding`              |
|                   | `border-width`, `font-size`      |

### Promoting to GPU Layer

```css
.animated-element {
  will-change: transform;
}
```

Use `will-change` sparingly. Apply it just before the animation starts and remove it after completion. Overuse creates excessive GPU memory consumption.

### Avoiding Layout Thrashing

Never read layout properties and write styles in the same synchronous block. Batch reads and writes separately, or use `requestAnimationFrame`.

### Staggered Animations

Stagger child animations to reduce simultaneous GPU work and create visual rhythm:

```tsx
<ul>
  {items.map((item, i) => (
    <li
      key={item.id}
      className="animate-fade-in opacity-0"
      style={{ animationDelay: `${i * 50}ms`, animationFillMode: 'forwards' }}
    >
      {item.name}
    </li>
  ))}
</ul>
```
