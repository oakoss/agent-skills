---
title: Transitions
description: Scene transitions with fade, slide, wipe, flip, clock-wipe, timing options, and duration calculation in Remotion
tags: [transitions, fade, slide, wipe, flip, TransitionSeries, timing]
---

## Prerequisites

```bash
pnpm exec remotion add @remotion/transitions
```

## Basic Usage

Use `<TransitionSeries>` to animate between scenes:

```tsx
import { TransitionSeries, linearTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';

<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneA />
  </TransitionSeries.Sequence>
  <TransitionSeries.Transition
    presentation={fade()}
    timing={linearTiming({ durationInFrames: 15 })}
  />
  <TransitionSeries.Sequence durationInFrames={60}>
    <SceneB />
  </TransitionSeries.Sequence>
</TransitionSeries>;
```

## Available Transition Types

```tsx
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { wipe } from '@remotion/transitions/wipe';
import { flip } from '@remotion/transitions/flip';
import { clockWipe } from '@remotion/transitions/clock-wipe';
```

## Slide with Direction

```tsx
import { slide } from '@remotion/transitions/slide';

<TransitionSeries.Transition
  presentation={slide({ direction: 'from-left' })}
  timing={linearTiming({ durationInFrames: 20 })}
/>;
```

Directions: `"from-left"`, `"from-right"`, `"from-top"`, `"from-bottom"`

## Timing Options

```tsx
import { linearTiming, springTiming } from '@remotion/transitions';

linearTiming({ durationInFrames: 20 });

springTiming({ config: { damping: 200 }, durationInFrames: 25 });
```

For `springTiming` without explicit `durationInFrames`, the duration depends on `fps` because it calculates when the spring settles.

## Duration Calculation

Transitions overlap adjacent scenes, making the total composition shorter:

```text
Two 60-frame scenes + 15-frame transition:
Without transitions: 60 + 60 = 120 frames
With transition: 60 + 60 - 15 = 105 frames
```

### Getting Transition Duration

```tsx
const timing = linearTiming({ durationInFrames: 20 });
const duration = timing.getDurationInFrames({ fps: 30 });
```

### Calculating Total Composition Duration

```tsx
const scene1Duration = 60;
const scene2Duration = 60;
const scene3Duration = 60;

const timing1 = linearTiming({ durationInFrames: 15 });
const timing2 = linearTiming({ durationInFrames: 20 });

const totalDuration =
  scene1Duration +
  scene2Duration +
  scene3Duration -
  timing1.getDurationInFrames({ fps: 30 }) -
  timing2.getDurationInFrames({ fps: 30 });
```
