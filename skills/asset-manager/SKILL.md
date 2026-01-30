---
name: asset-manager
description: 'Organize design assets, optimize images and fonts, maintain brand asset libraries, implement version control for assets, and enforce naming conventions. Use when optimizing images for web, converting fonts to WOFF2, organizing asset directories, setting up responsive image pipelines, or managing logo variants.'
version: 1.0.0
tags: [assets, images, fonts, optimization, organization]
---

# Asset Manager

Organized assets = faster development. Assets should be easy to find, properly named, optimized for production, and version controlled.

## Directory Structure

| Directory                                | Contents                                 |
| ---------------------------------------- | ---------------------------------------- |
| `assets/images/{category}/`              | Products, team, marketing, UI images     |
| `assets/icons/svg/`                      | SVG icon files                           |
| `assets/fonts/{family}/`                 | WOFF2 + WOFF font files                  |
| `assets/videos/`                         | Video assets                             |
| `assets/logos/svg/`, `png/`, `variants/` | Logo formats and color variants          |
| `brand/`                                 | Colors JSON, typography JSON, guidelines |

## Naming Conventions

| Asset Type | Pattern                                    | Example                           |
| ---------- | ------------------------------------------ | --------------------------------- |
| Images     | `{category}-{description}-{size}.{format}` | `product-hero-1920x1080.jpg`      |
| Icons      | `{icon-name}-{variant}.svg`                | `home-outline.svg`                |
| Fonts      | `{font-family}-{weight}.{format}`          | `Inter-Regular.woff2`             |
| Logos      | `logo-{variant}.{format}`                  | `logo-full.svg`, `logo-white.svg` |

## Optimization Targets

| Format | Tool             | Use Case                          |
| ------ | ---------------- | --------------------------------- |
| WebP   | sharp            | Primary web images                |
| AVIF   | sharp            | Modern browsers, best compression |
| JPEG   | sharp + mozjpeg  | Fallback photos                   |
| PNG    | sharp + pngquant | UI elements with transparency     |
| SVG    | SVGO             | Icons and logos                   |
| WOFF2  | woff2_compress   | Primary web fonts                 |
| WOFF   | sfnt2woff        | Font fallback                     |

## Pipeline Steps

| Step              | Action                                                |
| ----------------- | ----------------------------------------------------- |
| Organize          | Sort unsorted assets by naming rules into directories |
| Optimize images   | Resize, compress, generate WebP/AVIF variants         |
| Responsive images | Generate mobile/tablet/desktop breakpoint sizes       |
| Optimize fonts    | Convert TTF/OTF to WOFF2 + WOFF                       |
| Version           | Hash-based tracking with `asset-versions.json`        |

## Common Mistakes

| Mistake                            | Fix                                                 |
| ---------------------------------- | --------------------------------------------------- |
| Committing raw design files to git | Use Git LFS for PSD, AI, Sketch, Figma, video files |
| Serving original-size images       | Generate responsive variants at breakpoints         |
| Using only JPEG/PNG                | Generate WebP + AVIF with fallbacks                 |
| No font subsetting                 | Use Glyphhanger to subset unused glyphs             |
| Missing `font-display: swap`       | Always set on `@font-face` to avoid FOIT            |
| No CDN for assets                  | Prefix asset paths with `CDN_URL` env variable      |

## Tools

| Tool                                                   | Purpose                                |
| ------------------------------------------------------ | -------------------------------------- |
| [Sharp](https://sharp.pixelplumbing.com/)              | Image processing and format conversion |
| [SVGO](https://github.com/svg/svgo)                    | SVG optimization                       |
| [Glyphhanger](https://github.com/zachleat/glyphhanger) | Font subsetting                        |
| [Squoosh](https://squoosh.app/)                        | Online image compression               |

## Delegation

- **Figma exports**: see `figma-developer` skill
- **Brand creation**: see `brand-designer` skill
- **Responsive images in React**: see `responsive-images` skill

## References

- [Organization](references/organization.md)
- [Image Optimization](references/image-optimization.md)
- [Font Management](references/font-management.md)
- [Version Control](references/version-control.md)
- [Brand Library](references/brand-library.md)
- [Best Practices](references/best-practices.md)
