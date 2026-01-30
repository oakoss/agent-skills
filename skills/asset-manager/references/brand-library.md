---
title: Brand Library
description: Brand kit directory structure, asset manifest with TypeScript types for logos, colors, and typography
tags: [brand, logos, colors, typography, manifest, library]
---

# Brand Library

## Brand Kit Structure

```sh
brand/
├── logos/
│   ├── primary/
│   │   ├── logo-full.svg
│   │   ├── logo-icon.svg
│   │   └── logo-wordmark.svg
│   ├── variations/
│   │   ├── logo-white.svg
│   │   ├── logo-black.svg
│   │   └── logo-inverted.svg
│   └── exports/
│       ├── png/
│       ├── pdf/
│       └── eps/
├── colors/
│   ├── colors.json
│   ├── colors.css
│   └── colors.scss
├── typography/
│   ├── fonts/
│   └── typography.json
└── guidelines/
    ├── brand-guidelines.pdf
    ├── logo-usage.pdf
    └── color-usage.pdf
```

## Brand Asset Manifest

```ts
export interface BrandAssets {
  version: string;
  lastUpdated: string;
  logos: LogoAsset[];
  colors: ColorAsset[];
  typography: TypographyAsset[];
}

export interface LogoAsset {
  name: string;
  variants: {
    full: string;
    icon: string;
    wordmark: string;
  };
  formats: {
    svg: string;
    png: { [size: string]: string };
    pdf: string;
  };
}

export interface ColorAsset {
  name: string;
  hex: string;
  rgb: { r: number; g: number; b: number };
  usage: string;
}

export interface TypographyAsset {
  name: string;
  family: string;
  weights: number[];
  formats: string[];
}

export const brandAssets: BrandAssets = {
  version: '2.0.0',
  lastUpdated: '2024-01-15',
  logos: [
    {
      name: 'Primary Logo',
      variants: {
        full: '/brand/logos/logo-full.svg',
        icon: '/brand/logos/logo-icon.svg',
        wordmark: '/brand/logos/logo-wordmark.svg',
      },
      formats: {
        svg: '/brand/logos/logo-full.svg',
        png: {
          '1x': '/brand/logos/exports/png/logo-full@1x.png',
          '2x': '/brand/logos/exports/png/logo-full@2x.png',
          '3x': '/brand/logos/exports/png/logo-full@3x.png',
        },
        pdf: '/brand/logos/exports/pdf/logo-full.pdf',
      },
    },
  ],
  colors: [
    {
      name: 'Primary',
      hex: '#0066cc',
      rgb: { r: 0, g: 102, b: 204 },
      usage: 'Primary actions, links, brand elements',
    },
  ],
  typography: [
    {
      name: 'Inter',
      family: 'Inter',
      weights: [400, 600, 700],
      formats: ['woff2', 'woff'],
    },
  ],
};
```
