---
title: Troubleshooting
description: Common Figma API issues including token name normalization, RGB color conversion, and API rate limiting with caching
tags: [figma, troubleshooting, color-conversion, rate-limiting, cache, naming]
---

# Troubleshooting

## Token Names Don't Match

Figma style names contain spaces and special characters. Normalize before using as CSS variable names:

```ts
function normalizeTokenName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
```

## Colors Look Different

Figma uses 0-1 RGB values, not 0-255. Multiply and round before hex conversion:

```ts
function rgbToHex(color: { r: number; g: number; b: number }): string {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}
```

## API Rate Limiting

Cache Figma API responses to avoid hitting rate limits:

```ts
const cache = new Map<string, { data: any; timestamp: number }>();

async function getCachedFile(fileKey: string) {
  const cached = cache.get(fileKey);

  if (cached && Date.now() - cached.timestamp < 60000) {
    return cached.data;
  }

  const file = await client.getFile(fileKey);
  cache.set(fileKey, { data: file, timestamp: Date.now() });
  return file;
}
```

Use a 60-second TTL for development. For CI, cache is less important since runs are infrequent.
