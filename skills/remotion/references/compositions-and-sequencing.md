---
title: Compositions and Sequencing
description: Defining compositions, stills, folders, sequences, series, trimming, and dynamic metadata in Remotion
tags:
  [composition, sequence, series, still, folder, calculateMetadata, trimming]
---

## Compositions

A `<Composition>` defines the component, width, height, fps, and duration of a renderable video. Place it in `src/Root.tsx`:

```tsx
import { Composition } from 'remotion';
import { MyComposition } from './MyComposition';

export const RemotionRoot = () => {
  return (
    <Composition
      id="MyComposition"
      component={MyComposition}
      durationInFrames={100}
      fps={30}
      width={1080}
      height={1080}
    />
  );
};
```

### Default Props

Pass `defaultProps` for initial values. Values must be JSON-serializable. Use `type` declarations (not `interface`) for prop type safety:

```tsx
<Composition
  id="MyComposition"
  component={MyComposition}
  durationInFrames={100}
  fps={30}
  width={1080}
  height={1080}
  defaultProps={
    { title: 'Hello World', color: '#ff0000' } satisfies MyCompositionProps
  }
/>
```

### Folders

Organize compositions in the sidebar:

```tsx
import { Composition, Folder } from 'remotion';

<Folder name="Marketing">
  <Composition id="Promo" /* ... */ />
  <Composition id="Ad" /* ... */ />
</Folder>;
```

### Stills

Use `<Still>` for single-frame images. No `durationInFrames` or `fps` required:

```tsx
import { Still } from 'remotion';
<Still id="Thumbnail" component={Thumbnail} width={1280} height={720} />;
```

## Calculate Metadata

Use `calculateMetadata` to dynamically set duration, dimensions, and props before rendering:

```tsx
import { type CalculateMetadataFunction } from 'remotion';

const calculateMetadata: CalculateMetadataFunction<Props> = async ({
  props,
  abortSignal,
}) => {
  const data = await fetch(`https://api.example.com/video/${props.videoId}`, {
    signal: abortSignal,
  }).then((res) => res.json());

  return {
    durationInFrames: Math.ceil(data.duration * 30),
    props: { ...props, videoUrl: data.url },
  };
};
```

Return fields (all optional): `durationInFrames`, `width`, `height`, `fps`, `props`, `defaultOutName`, `defaultCodec`.

The `abortSignal` cancels stale requests when props change in the Studio.

## Sequences

Use `<Sequence>` to delay when an element appears:

```tsx
import { Sequence, useVideoConfig } from 'remotion';

const { fps } = useVideoConfig();

<Sequence from={1 * fps} durationInFrames={2 * fps} premountFor={1 * fps}>
  <Title />
</Sequence>;
```

Always premount sequences with `premountFor` to preload components.

Inside a `<Sequence>`, `useCurrentFrame()` returns the local frame starting at 0, not the composition frame.

By default, sequences wrap children in an absolute fill. Set `layout="none"` to disable:

```tsx
<Sequence layout="none">
  <Title />
</Sequence>
```

### Nesting Compositions

Embed a composition within another using `<Sequence>` with explicit dimensions:

```tsx
<AbsoluteFill>
  <Sequence width={COMPOSITION_WIDTH} height={COMPOSITION_HEIGHT}>
    <CompositionComponent />
  </Sequence>
</AbsoluteFill>
```

## Series

Use `<Series>` for sequential playback without overlap:

```tsx
import { Series } from 'remotion';

<Series>
  <Series.Sequence durationInFrames={45}>
    <Intro />
  </Series.Sequence>
  <Series.Sequence durationInFrames={60}>
    <MainContent />
  </Series.Sequence>
  <Series.Sequence durationInFrames={30}>
    <Outro />
  </Series.Sequence>
</Series>;
```

Use negative `offset` for overlapping sequences:

```tsx
<Series.Sequence offset={-15} durationInFrames={60}>
  <SceneB />
</Series.Sequence>
```

## Trimming

### Trim the Beginning

A negative `from` shifts time backwards:

```tsx
<Sequence from={-0.5 * fps}>
  <MyAnimation />
</Sequence>
```

Inside `MyAnimation`, `useCurrentFrame()` starts at 15 (for 30fps \* 0.5s) instead of 0.

### Trim the End

Use `durationInFrames` to unmount after a set duration:

```tsx
<Sequence durationInFrames={1.5 * fps}>
  <MyAnimation />
</Sequence>
```

### Trim and Delay

Nest sequences for both trimming and delaying:

```tsx
<Sequence from={30}>
  <Sequence from={-15}>
    <MyAnimation />
  </Sequence>
</Sequence>
```
