---
title: Captions and Text
description: Transcription, SRT import, TikTok-style captions, word highlighting, and text animation patterns in Remotion
tags: [captions, subtitles, transcription, text-animations, typewriter, srt]
---

## Transcription Options

Remotion provides three transcription approaches:

- **`@remotion/install-whisper-cpp`** -- Local server transcription via Whisper.cpp. Fast and free, requires server infrastructure.
- **`@remotion/whisper-web`** -- Browser-based transcription via WebAssembly. No server needed, free, slower.
- **`@remotion/openai-whisper`** -- Cloud transcription via OpenAI Whisper API. Fast, no server, paid.

## Importing SRT Subtitles

```bash
pnpm exec remotion add @remotion/captions
```

```tsx
import { useState, useEffect, useCallback } from 'react';
import { AbsoluteFill, staticFile, useDelayRender } from 'remotion';
import { parseSrt } from '@remotion/captions';
import type { Caption } from '@remotion/captions';

export const MyComponent: React.FC = () => {
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const fetchCaptions = useCallback(async () => {
    try {
      const response = await fetch(staticFile('subtitles.srt'));
      const text = await response.text();
      const { captions: parsed } = parseSrt({ input: text });
      setCaptions(parsed);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [continueRender, cancelRender, handle]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  if (!captions) return null;
  return <AbsoluteFill>{/* Use captions here */}</AbsoluteFill>;
};
```

## TikTok-Style Captions

Group captions into pages using `createTikTokStyleCaptions()`:

```tsx
import { useMemo } from 'react';
import { createTikTokStyleCaptions } from '@remotion/captions';

const SWITCH_CAPTIONS_EVERY_MS = 1200;

const { pages } = useMemo(() => {
  return createTikTokStyleCaptions({
    captions,
    combineTokensWithinMilliseconds: SWITCH_CAPTIONS_EVERY_MS,
  });
}, [captions]);
```

Render pages as sequences:

```tsx
import { Sequence, useVideoConfig, AbsoluteFill } from 'remotion';

const { fps } = useVideoConfig();

<AbsoluteFill>
  {pages.map((page, index) => {
    const nextPage = pages[index + 1] ?? null;
    const startFrame = (page.startMs / 1000) * fps;
    const endFrame = Math.min(
      nextPage ? (nextPage.startMs / 1000) * fps : Infinity,
      startFrame + (SWITCH_CAPTIONS_EVERY_MS / 1000) * fps,
    );
    const durationInFrames = endFrame - startFrame;
    if (durationInFrames <= 0) return null;

    return (
      <Sequence
        key={index}
        from={startFrame}
        durationInFrames={durationInFrames}
      >
        <CaptionPage page={page} />
      </Sequence>
    );
  })}
</AbsoluteFill>;
```

## Word Highlighting

Highlight the currently spoken word using page tokens:

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import type { TikTokPage } from '@remotion/captions';

const HIGHLIGHT_COLOR = '#39E508';

const CaptionPage: React.FC<{ page: TikTokPage }> = ({ page }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTimeMs = (frame / fps) * 1000;
  const absoluteTimeMs = page.startMs + currentTimeMs;

  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center' }}>
      <div style={{ fontSize: 80, fontWeight: 'bold', whiteSpace: 'pre' }}>
        {page.tokens.map((token) => {
          const isActive =
            token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;
          return (
            <span
              key={token.fromMs}
              style={{ color: isActive ? HIGHLIGHT_COLOR : 'white' }}
            >
              {token.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
```

## Text Animations

### Typewriter Effect

Use string slicing driven by `useCurrentFrame()`. Never use per-character opacity.

```tsx
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

const FULL_TEXT = 'From prompt to motion graphics. This is Remotion.';
const CHAR_FRAMES = 2;

export const Typewriter = () => {
  const frame = useCurrentFrame();
  const typedChars = Math.min(
    FULL_TEXT.length,
    Math.floor(frame / CHAR_FRAMES),
  );
  const typedText = FULL_TEXT.slice(0, typedChars);

  const cursorOpacity = interpolate(frame % 16, [0, 8, 16], [1, 0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#fff' }}>
      <div style={{ color: '#000', fontSize: 72, fontWeight: 700 }}>
        <span>{typedText}</span>
        <span style={{ opacity: cursorOpacity }}>{'\u258C'}</span>
      </div>
    </AbsoluteFill>
  );
};
```

### Word Highlight Wipe

Animate a highlight background behind a word using spring:

```tsx
import { spring, useCurrentFrame, useVideoConfig } from 'remotion';

const frame = useCurrentFrame();
const { fps } = useVideoConfig();

const highlightProgress = spring({
  fps,
  frame,
  config: { damping: 200 },
  delay: 30,
  durationInFrames: 18,
});

<span style={{ position: 'relative', display: 'inline-block' }}>
  <span
    style={{
      position: 'absolute',
      left: 0,
      right: 0,
      top: '50%',
      height: '1.05em',
      transform: `translateY(-50%) scaleX(${highlightProgress})`,
      transformOrigin: 'left center',
      backgroundColor: '#A7C7E7',
      borderRadius: '0.18em',
      zIndex: 0,
    }}
  />
  <span style={{ position: 'relative', zIndex: 1 }}>Remotion</span>
</span>;
```
