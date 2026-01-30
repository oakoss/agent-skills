---
title: Media and Assets
description: Audio, video, images, GIFs, fonts, and static file handling in Remotion
tags: [audio, video, images, fonts, staticFile, gif, assets, media]
---

## Static Files

Place assets in `public/` and reference with `staticFile()`:

```tsx
import { Img, staticFile } from 'remotion';
<Img src={staticFile('logo.png')} />;
```

Remote URLs work directly without `staticFile()`:

```tsx
<Img src="https://example.com/image.png" />
```

## Audio

Install `@remotion/media` first:

```bash
pnpm exec remotion add @remotion/media
```

```tsx
import { Audio } from '@remotion/media';
import { staticFile } from 'remotion';

<Audio src={staticFile('audio.mp3')} />;
```

### Trimming, Delay, Volume, Speed, Pitch

```tsx
const { fps } = useVideoConfig();

<Audio
  src={staticFile('audio.mp3')}
  trimBefore={2 * fps}
  trimAfter={10 * fps}
/>

<Sequence from={1 * fps}>
  <Audio src={staticFile('audio.mp3')} />
</Sequence>

<Audio src={staticFile('audio.mp3')} volume={0.5} />

<Audio
  src={staticFile('audio.mp3')}
  volume={(f) =>
    interpolate(f, [0, 1 * fps], [0, 1], { extrapolateRight: 'clamp' })
  }
/>

<Audio src={staticFile('audio.mp3')} playbackRate={2} />

<Audio src={staticFile('audio.mp3')} loop loopVolumeCurveBehavior="extend" />

<Audio src={staticFile('audio.mp3')} toneFrequency={1.5} />
```

Pitch shifting (`toneFrequency`) only works during server-side rendering, not in Studio or `<Player />`.

## Video

```tsx
import { Video } from '@remotion/media';

<Video src={staticFile('video.mp4')} />;
```

Video supports the same props as Audio: `trimBefore`, `trimAfter`, `volume`, `muted`, `playbackRate`, `loop`, `toneFrequency`. Additionally use `style` for sizing:

```tsx
<Video
  src={staticFile('video.mp4')}
  style={{ width: 500, height: 300, objectFit: 'cover' }}
/>
```

## Images

Always use `<Img>` from `remotion`. Never use native `<img>`, Next.js `<Image>`, or CSS `background-image` -- `<Img>` ensures images are loaded before rendering.

```tsx
import { Img, staticFile } from 'remotion';

<Img src={staticFile('photo.png')} />;
```

Dynamic paths:

```tsx
<Img src={staticFile(`frames/frame${frame}.png`)} />
```

Get image dimensions:

```tsx
import { getImageDimensions, staticFile } from 'remotion';
const { width, height } = await getImageDimensions(staticFile('photo.png'));
```

## Animated Images (GIFs)

Use `<AnimatedImage>` for GIF, APNG, AVIF, or WebP synchronized with the timeline:

```tsx
import { AnimatedImage, staticFile } from 'remotion';

<AnimatedImage src={staticFile('animation.gif')} width={500} height={500} />;
```

Control playback: `playbackRate`, `loopBehavior` (`"loop"`, `"pause-after-finish"`, `"clear-after-finish"`), `fit` (`"fill"`, `"contain"`, `"cover"`).

Get GIF duration (requires `@remotion/gif`):

```tsx
import { getGifDurationInSeconds } from '@remotion/gif';
const duration = await getGifDurationInSeconds(staticFile('animation.gif'));
```

## Fonts

### Google Fonts

```bash
pnpm exec remotion add @remotion/google-fonts
```

```tsx
import { loadFont } from '@remotion/google-fonts/Roboto';

const { fontFamily } = loadFont('normal', {
  weights: ['400', '700'],
  subsets: ['latin'],
});
```

### Local Fonts

```bash
pnpm exec remotion add @remotion/fonts
```

```tsx
import { loadFont } from '@remotion/fonts';
import { staticFile } from 'remotion';

await loadFont({
  family: 'MyFont',
  url: staticFile('MyFont-Regular.woff2'),
  weight: '400',
});
```

Load multiple weights with the same family name and different `weight` values.

Call `loadFont()` at the top level of your component or in a separate file imported early.

## Mediabunny Utilities

Mediabunny provides browser/Node/Bun utilities for media metadata:

### Get Video/Audio Duration

```tsx
import { Input, ALL_FORMATS, UrlSource } from 'mediabunny';

export const getMediaDuration = async (src: string) => {
  const input = new Input({
    formats: ALL_FORMATS,
    source: new UrlSource(src, { getRetryDelay: () => null }),
  });
  return input.computeDuration();
};
```

### Get Video Dimensions

```tsx
const videoTrack = await input.getPrimaryVideoTrack();
const width = videoTrack.displayWidth;
const height = videoTrack.displayHeight;
```

### Check Decode Compatibility

```tsx
const videoTrack = await input.getPrimaryVideoTrack();
if (videoTrack && !(await videoTrack.canDecode())) {
  return false;
}
```
