---
title: Troubleshooting
description: Common Figma API issues including token name normalization, RGB color conversion, API rate limiting, expired image URLs, and large file handling
tags: [figma, troubleshooting, color-conversion, rate-limiting, cache, naming]
---

# Troubleshooting

## Token Names Don't Match

Figma style names contain spaces, slashes, and special characters. Normalize before using as CSS variable names:

```ts
function normalizeTokenName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
```

Example: `Primary/500` becomes `primary-500`, `Heading/Large` becomes `heading-large`.

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

For colors with alpha, handle the `a` property separately:

```ts
function rgbaToHex(color: {
  r: number;
  g: number;
  b: number;
  a: number;
}): string {
  const hex = rgbToHex(color);
  const alpha = Math.round(color.a * 255)
    .toString(16)
    .padStart(2, '0');
  return color.a < 1 ? `${hex}${alpha}` : hex;
}
```

## API Rate Limiting

Cache Figma API responses to avoid hitting rate limits:

```ts
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 60_000;

async function getCachedFile(api: any, fileKey: string) {
  const cached = cache.get(fileKey);

  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const file = await api.getFile({ file_key: fileKey });
  cache.set(fileKey, { data: file, timestamp: Date.now() });
  return file;
}
```

Use a 60-second TTL for development. For CI, caching is less important since runs are infrequent.

## Expired Image URLs

Image URLs from `GET /v1/images/:key` expire after 14 days. Do not persist these URLs in databases or config files. Always re-fetch before use:

```ts
async function getIconUrl(api: any, fileKey: string, nodeId: string) {
  const { images } = await api.getImages({
    file_key: fileKey,
    queryParams: {
      ids: nodeId,
      format: 'svg',
    },
  });
  return images[nodeId];
}
```

## Large File Responses

For large Figma files, fetching the entire document tree is slow and memory-intensive. Use node-specific endpoints instead:

```ts
const { nodes } = await api.getFileNodes({
  file_key: fileKey,
  queryParams: {
    ids: '1:23,4:56',
    depth: 2,
  },
});
```

The `depth` parameter limits how deep into the tree the response goes, reducing payload size.

## Authentication Errors

Common token issues:

| Error                   | Cause                                   | Fix                                          |
| ----------------------- | --------------------------------------- | -------------------------------------------- |
| 403 Forbidden           | Token lacks required scope              | Regenerate token with `file_content:read`    |
| 404 Not Found           | File key is wrong or token lacks access | Verify file key from the Figma URL           |
| 429 Too Many Requests   | Rate limit exceeded                     | Add caching and request throttling           |
| Token starts with `fig` | Using old token format                  | Regenerate; current tokens start with `figd` |
