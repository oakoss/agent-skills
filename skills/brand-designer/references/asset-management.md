---
title: Asset Management
description: Brand asset file organization, favicon generation script with Sharp, and HTML meta tags for favicons
tags: [assets, favicon, file-organization, sharp, meta-tags]
---

# Asset Management

## File Organization

```sh
brand-assets/
├── logo/
│   ├── svg/
│   │   ├── logo-full.svg
│   │   ├── logo-icon.svg
│   │   └── logo-wordmark.svg
│   ├── png/
│   │   ├── logo-full@1x.png
│   │   ├── logo-full@2x.png
│   │   └── logo-full@3x.png
│   └── favicon/
│       ├── favicon-16x16.png
│       ├── favicon-32x32.png
│       └── favicon.ico
├── colors/
│   └── palette.json
├── fonts/
│   ├── Inter-Regular.woff2
│   ├── Inter-Bold.woff2
│   └── JetBrainsMono-Regular.woff2
├── templates/
│   ├── social-profile.svg
│   ├── social-post.svg
│   └── business-card.svg
└── guidelines/
    └── brand-guidelines.pdf
```

## Favicon Generation

```typescript
import sharp from 'sharp';

async function generateFavicons() {
  const sizes = [16, 32, 48, 64, 128, 256];

  for (const size of sizes) {
    await sharp('logo-icon.svg')
      .resize(size, size)
      .png()
      .toFile(`public/favicon-${size}x${size}.png`);

    console.log(`Generated ${size}x${size} favicon`);
  }
}

generateFavicons();
```

## Favicon HTML

```html
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
<link rel="manifest" href="/site.webmanifest" />
```
