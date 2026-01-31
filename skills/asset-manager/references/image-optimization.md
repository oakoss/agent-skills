---
title: Image Optimization
description: Image optimization with Sharp for multi-format generation (WebP, AVIF), SVG optimization with SVGO v4, and responsive image generation for breakpoints
tags: [images, optimization, sharp, webp, avif, svg, svgo, responsive]
---

# Image Optimization

## Dependencies

```bash
npm install sharp svgo
```

## Multi-Format Optimization

```ts
import sharp from 'sharp';
import fs from 'fs/promises';
import path from 'path';

interface OptimizeOptions {
  quality?: number;
  maxWidth?: number;
  formats?: ('jpg' | 'png' | 'webp' | 'avif')[];
}

async function optimizeImages(
  inputDir: string,
  outputDir: string,
  options: OptimizeOptions = {},
) {
  const {
    quality = 80,
    maxWidth = 2000,
    formats = ['jpg', 'png', 'webp'],
  } = options;

  const files = await fs.readdir(inputDir);

  for (const file of files) {
    const inputPath = path.join(inputDir, file);
    const stat = await fs.stat(inputPath);

    if (stat.isDirectory()) continue;

    const ext = path.extname(file).toLowerCase();
    const name = path.basename(file, ext);

    if (ext === '.svg') {
      await optimizeSVG(inputPath, outputDir);
      continue;
    }

    if (!['.jpg', '.jpeg', '.png'].includes(ext)) continue;

    const image = sharp(inputPath);
    const metadata = await image.metadata();

    if (metadata.width && metadata.width > maxWidth) {
      image.resize(maxWidth, null, {
        withoutEnlargement: true,
        fit: 'inside',
      });
    }

    for (const format of formats) {
      const outputPath = path.join(outputDir, `${name}.${format}`);

      if (format === 'jpg') {
        await image.jpeg({ quality, mozjpeg: true }).toFile(outputPath);
      } else if (format === 'png') {
        await image.png({ quality, compressionLevel: 9 }).toFile(outputPath);
      } else if (format === 'webp') {
        await image.webp({ quality }).toFile(outputPath);
      } else if (format === 'avif') {
        await image.avif({ quality }).toFile(outputPath);
      }
    }
  }
}
```

## SVG Optimization

SVGO v4 disables `removeViewBox` and `removeTitle` by default for better accessibility.

```ts
import { optimize } from 'svgo';

async function optimizeSVG(inputPath: string, outputDir: string) {
  const fileName = path.basename(inputPath);
  const outputPath = path.join(outputDir, fileName);
  const svgString = await fs.readFile(inputPath, 'utf-8');

  const result = optimize(svgString, {
    multipass: true,
    plugins: [
      {
        name: 'preset-default',
      },
      'removeDimensions',
    ],
  });

  await fs.writeFile(outputPath, result.data);
}
```

## Responsive Image Generation

```ts
const breakpoints = [
  { name: 'mobile', width: 640 },
  { name: 'tablet', width: 768 },
  { name: 'desktop', width: 1920 },
];

async function generateResponsiveImages(inputPath: string) {
  const ext = path.extname(inputPath);
  const name = path.basename(inputPath, ext);
  const dir = path.dirname(inputPath);

  for (const bp of breakpoints) {
    const image = sharp(inputPath);

    image.resize(bp.width, null, {
      withoutEnlargement: true,
      fit: 'inside',
    });

    const webpPath = path.join(dir, `${name}-${bp.name}.webp`);
    await image.webp({ quality: 80 }).toFile(webpPath);

    const avifPath = path.join(dir, `${name}-${bp.name}.avif`);
    await image.avif({ quality: 80 }).toFile(avifPath);
  }
}
```
