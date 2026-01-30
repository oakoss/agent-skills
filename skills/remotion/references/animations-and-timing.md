---
title: Animations and Timing
description: Interpolation, spring animations, easing curves, and frame-driven animation patterns in Remotion
tags: [animations, interpolate, spring, easing, useCurrentFrame, timing]
---

All animations in Remotion MUST be driven by `useCurrentFrame()`. CSS transitions, CSS animations, and Tailwind animation classes are forbidden -- they cause flickering during rendering.

## Basic Interpolation

```tsx
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const opacity = interpolate(frame, [0, 2 * fps], [0, 1], {
  extrapolateRight: 'clamp',
});
```

By default, values are not clamped and can exceed the target range. Always use `extrapolateRight: 'clamp'` (and optionally `extrapolateLeft: 'clamp'`) to prevent this.

Write animations in seconds and multiply by `fps` for frame counts.

## Spring Animations

Springs produce natural motion and animate from 0 to 1.

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const scale = spring({ frame, fps });
```

### Common Spring Configurations

```tsx
const smooth = { damping: 200 };
const snappy = { damping: 20, stiffness: 200 };
const bouncy = { damping: 8 };
const heavy = { damping: 15, stiffness: 80, mass: 2 };
```

The default config is `mass: 1, damping: 10, stiffness: 100` (slight bounce). Use `{ damping: 200 }` for smooth motion without bounce.

### Spring Delay and Duration

```tsx
const entrance = spring({
  frame,
  fps,
  delay: 20,
  durationInFrames: 40,
});
```

### Combining Spring with Interpolate

Map spring output (0-1) to custom ranges:

```tsx
const springProgress = spring({ frame, fps });
const rotation = interpolate(springProgress, [0, 1], [0, 360]);

<div style={{ rotate: rotation + 'deg' }} />;
```

### Entrance and Exit

```tsx
const { fps, durationInFrames } = useVideoConfig();

const inAnimation = spring({ frame, fps });
const outAnimation = spring({
  frame,
  fps,
  durationInFrames: 1 * fps,
  delay: durationInFrames - 1 * fps,
});

const scale = inAnimation - outAnimation;
```

## Easing Functions

Add easing to `interpolate()`:

```tsx
import { interpolate, Easing } from 'remotion';

const value = interpolate(frame, [0, 100], [0, 1], {
  easing: Easing.inOut(Easing.quad),
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

Convexities: `Easing.in`, `Easing.out`, `Easing.inOut`

Curves (most linear to most curved): `Easing.quad`, `Easing.sin`, `Easing.exp`, `Easing.circle`

Cubic bezier curves:

```tsx
const value = interpolate(frame, [0, 100], [0, 1], {
  easing: Easing.bezier(0.8, 0.22, 0.96, 0.65),
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});
```

## Staggered Animations

Animate multiple items with incremental delays:

```tsx
const STAGGER_DELAY = 5;

const bars = data.map((item, i) => {
  const delay = i * STAGGER_DELAY;
  const height = spring({
    frame,
    fps,
    delay,
    config: { damping: 200 },
  });
  return <div style={{ height: height * item.value }} />;
});
```
