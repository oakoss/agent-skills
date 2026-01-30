---
title: Best Practices
description: Web optimization strategies including lazy loading, CDN configuration, and automated asset pipeline orchestration
tags: [optimization, lazy-loading, cdn, pipeline, automation, web-performance]
---

# Best Practices

## Format Selection

| Asset Type  | Primary     | Fallback       |
| ----------- | ----------- | -------------- |
| Photos      | WebP / AVIF | JPEG           |
| UI elements | WebP / AVIF | PNG            |
| Icons       | SVG sprite  | Individual SVG |
| Fonts       | WOFF2       | WOFF           |
| Videos      | MP4 (H.265) | MP4 (H.264)    |

## Lazy Loading

```tsx
<img src="placeholder.jpg" data-src="hero.jpg" loading="lazy" alt="Hero" />
```

With Next.js:

```tsx
import Image from 'next/image';

<Image
  src="/hero.jpg"
  width={1920}
  height={1080}
  placeholder="blur"
  alt="Hero"
/>;
```

## CDN Configuration

```ts
const CDN_URL = process.env.CDN_URL || '';

export function getAssetUrl(path: string): string {
  if (CDN_URL) {
    return `${CDN_URL}${path}`;
  }
  return path;
}
```

Usage:

```tsx
<img src={getAssetUrl('/images/hero.jpg')} alt="Hero" />
```

## Automated Pipeline

Orchestrate all optimization steps in sequence:

```ts
async function runAssetPipeline() {
  await organizeAssets('./unsorted');

  await optimizeImages('./assets/images/raw', './assets/images/optimized', {
    quality: 85,
    maxWidth: 1920,
    formats: ['jpg', 'webp', 'avif'],
  });

  await generateResponsiveImages('./assets/images/optimized');

  await optimizeFonts('./assets/fonts/raw', './assets/fonts/optimized');

  const manager = new AssetVersionManager();
  await manager.load();
  await manager.trackDirectory('./assets');
  await manager.save();
}
```

Add to package.json:

```json
{
  "scripts": {
    "assets:optimize": "tsx scripts/optimize-images.ts",
    "assets:fonts": "tsx scripts/optimize-fonts.ts",
    "assets:pipeline": "tsx scripts/asset-pipeline.ts"
  }
}
```
