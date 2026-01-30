---
title: Advanced Features
description: 3D content with Three.js, charts, Mapbox maps, Zod parameters, transparent video, Lottie, and DOM measurement in Remotion
tags:
  [
    three,
    3d,
    charts,
    maps,
    mapbox,
    parameters,
    zod,
    transparent,
    lottie,
    measurement,
  ]
---

## 3D Content (Three.js)

```bash
pnpm exec remotion add @remotion/three
```

Wrap 3D content in `<ThreeCanvas>` with explicit `width` and `height`:

```tsx
import { ThreeCanvas } from '@remotion/three';
import { useVideoConfig, useCurrentFrame } from 'remotion';

const { width, height } = useVideoConfig();
const frame = useCurrentFrame();
const rotationY = frame * 0.02;

<ThreeCanvas width={width} height={height}>
  <ambientLight intensity={0.4} />
  <directionalLight position={[5, 5, 5]} intensity={0.8} />
  <mesh rotation={[0, rotationY, 0]}>
    <boxGeometry args={[2, 2, 2]} />
    <meshStandardMaterial color="#4a9eff" />
  </mesh>
</ThreeCanvas>;
```

`useFrame()` from `@react-three/fiber` is forbidden. All animations must use `useCurrentFrame()`. Shaders and models must not animate on their own.

Any `<Sequence>` inside `<ThreeCanvas>` must have `layout="none"`.

## Charts

Use regular HTML/SVG or D3.js. Disable all third-party animations -- they cause flickering. Drive all chart animations from `useCurrentFrame()`.

### Staggered Bar Chart

```tsx
const STAGGER_DELAY = 5;
const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const bars = data.map((item, i) => {
  const progress = spring({
    frame: frame - i * STAGGER_DELAY - 10,
    fps,
    config: { damping: 18, stiffness: 80 },
  });
  const barHeight = ((item.value - minValue) / range) * chartHeight * progress;
  return (
    <div key={item.label} style={{ height: barHeight, opacity: progress }} />
  );
});
```

### Pie Chart with SVG

Animate segments using `stroke-dashoffset`:

```tsx
const circumference = 2 * Math.PI * radius;
const segmentLength = (value / total) * circumference;
const progress = interpolate(frame, [0, 100], [0, 1]);
const offset = interpolate(progress, [0, 1], [segmentLength, 0]);

<circle
  r={radius}
  cx={center}
  cy={center}
  fill="none"
  stroke={color}
  strokeWidth={strokeWidth}
  strokeDasharray={`${segmentLength} ${circumference}`}
  strokeDashoffset={offset}
  transform={`rotate(-90 ${center} ${center})`}
/>;
```

## Mapbox Maps

Install `mapbox-gl` and `@turf/turf`. Set `REMOTION_MAPBOX_TOKEN` in `.env`.

Key Remotion rules for maps:

- Set `interactive: false` and `fadeDuration: 0` on the Map
- Use `useDelayRender()` to wait for map load
- The map container MUST have explicit `width`, `height`, and `position: "absolute"`
- Do not add `_map.remove()` cleanup
- Render with `--gl=angle --concurrency=1`

Animate the camera along a line using `@turf/turf`:

```tsx
const progress = interpolate(frame / fps, [0, duration], [0, 1], {
  easing: Easing.inOut(Easing.sin),
  extrapolateLeft: 'clamp',
  extrapolateRight: 'clamp',
});

const alongRoute = turf.along(
  turf.lineString(lineCoordinates),
  routeDistance * progress,
).geometry.coordinates;

const camera = map.getFreeCameraOptions();
camera.lookAtPoint({ lng: alongRoute[0], lat: alongRoute[1] });
map.setFreeCameraOptions(camera);
```

For straight lines on the map, use linear interpolation between coordinates (not turf geodesic functions which appear curved on Mercator projections).

## Parameters with Zod

Requires `zod@3.22.3`. Define a schema alongside the component:

```tsx
import { z } from 'zod';

export const MyCompositionSchema = z.object({
  title: z.string(),
});

const MyComponent: React.FC<z.infer<typeof MyCompositionSchema>> = (props) => {
  return <h1>{props.title}</h1>;
};
```

Pass to composition with `schema` prop. For color pickers, use `zColor()` from `@remotion/zod-types`.

## Transparent Video

### WebM (VP9) -- for browser playback

```bash
npx remotion render --image-format=png --pixel-format=yuva420p --codec=vp9 MyComp out.webm
```

### ProRes 4444 -- for editing software

```bash
npx remotion render --image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444 MyComp out.mov
```

Set defaults per composition via `calculateMetadata`:

```tsx
const calculateMetadata: CalculateMetadataFunction<Props> = async () => ({
  defaultCodec: 'vp8',
  defaultVideoImageFormat: 'png',
  defaultPixelFormat: 'yuva420p',
});
```

## Lottie Animations

```bash
pnpm exec remotion add @remotion/lottie
```

Fetch the Lottie JSON, use `delayRender`/`continueRender`, and render with `<Lottie>`:

```tsx
import { Lottie, type LottieAnimationData } from '@remotion/lottie';

<Lottie animationData={animationData} style={{ width: 400, height: 400 }} />;
```

## DOM Measurement

Remotion applies a `scale()` transform. Divide `getBoundingClientRect()` values by `useCurrentScale()`:

```tsx
import { useCurrentScale } from 'remotion';

const scale = useCurrentScale();
const rect = ref.current.getBoundingClientRect();
const realWidth = rect.width / scale;
const realHeight = rect.height / scale;
```

## Text Measurement

```bash
pnpm exec remotion add @remotion/layout-utils
```

```tsx
import { measureText, fitText, fillTextBox } from '@remotion/layout-utils';

const { width, height } = measureText({
  text: 'Hello',
  fontFamily: 'Arial',
  fontSize: 32,
  fontWeight: 'bold',
});

const { fontSize } = fitText({
  text: 'Hello World',
  withinWidth: 600,
  fontFamily: 'Inter',
});
```

Load fonts before measuring. Use `validateFontIsLoaded: true` to catch errors. Match font properties between measurement and rendering.

Use `outline` instead of `border` to prevent layout differences in measured text.
