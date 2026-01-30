---
title: Font Management
description: Font optimization with WOFF2 conversion, font-face declarations, preloading strategy, and subsetting
tags: [fonts, woff2, optimization, font-face, preload, subsetting]
---

# Font Management

## Font Optimization

Convert TTF/OTF to WOFF2 (best compression) + WOFF (fallback):

```ts
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

async function optimizeFonts(inputDir: string, outputDir: string) {
  const files = await fs.readdir(inputDir);

  for (const file of files) {
    const inputPath = path.join(inputDir, file);
    const ext = path.extname(file).toLowerCase();

    if (ext !== '.ttf' && ext !== '.otf') continue;

    const name = path.basename(file, ext);

    const woff2Path = path.join(outputDir, `${name}.woff2`);
    await convertToWOFF2(inputPath, woff2Path);

    const woffPath = path.join(outputDir, `${name}.woff`);
    await convertToWOFF(inputPath, woffPath);
  }
}

async function convertToWOFF2(input: string, output: string) {
  await execAsync(`woff2_compress ${input}`);
  const woff2File = input.replace(/\.(ttf|otf)$/, '.woff2');
  await fs.rename(woff2File, output);
}

async function convertToWOFF(input: string, output: string) {
  await execAsync(`sfnt2woff ${input}`);
  const woffFile = input.replace(/\.(ttf|otf)$/, '.woff');
  await fs.rename(woffFile, output);
}
```

Prerequisites: `brew install woff2` for `woff2_compress`, `sfnt2woff` for WOFF conversion.

## Font-Face Declarations

```css
@font-face {
  font-family: 'Inter';
  src:
    url('/fonts/Inter-Regular.woff2') format('woff2'),
    url('/fonts/Inter-Regular.woff') format('woff');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}

@font-face {
  font-family: 'Inter';
  src:
    url('/fonts/Inter-Bold.woff2') format('woff2'),
    url('/fonts/Inter-Bold.woff') format('woff');
  font-weight: 700;
  font-style: normal;
  font-display: swap;
}
```

Always use `font-display: swap` to show fallback text immediately (avoids Flash of Invisible Text).

## Preloading Critical Fonts

```html
<head>
  <link
    rel="preload"
    href="/fonts/Inter-Regular.woff2"
    as="font"
    type="font/woff2"
    crossorigin
  />
  <link
    rel="preload"
    href="/fonts/Inter-Bold.woff2"
    as="font"
    type="font/woff2"
    crossorigin
  />
</head>
```

Only preload fonts used above the fold. The `crossorigin` attribute is required even for same-origin fonts.
