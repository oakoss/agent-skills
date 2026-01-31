---
title: Modern Image Formats
description: WebP and AVIF format comparison, quality settings, conversion tools, and fallback patterns
tags: [webp, avif, jpeg, png, formats, compression, sharp, imagemagick]
---

# Modern Image Formats

## Format Comparison

| Format | Quality   | File Size | Transparency | Browser Support |
| ------ | --------- | --------- | ------------ | --------------- |
| JPEG   | Good      | Medium    | No           | 100%            |
| PNG    | Lossless  | Large     | Yes          | 100%            |
| WebP   | Excellent | Small     | Yes          | 96%+            |
| AVIF   | Excellent | Smallest  | Yes          | 93%+            |

**Real Example** (1920x1080 photo): JPEG 500KB, WebP 250KB (-50%), AVIF 150KB (-70%).

**Recommended Strategy**: AVIF, WebP, JPEG fallback using `<picture>`.

## AVIF with WebP and JPEG Fallback (Recommended)

```html
<picture>
  <source
    srcset="/image-400.avif 400w, /image-800.avif 800w, /image-1200.avif 1200w"
    sizes="(max-width: 768px) 100vw, 800px"
    type="image/avif"
  />
  <source
    srcset="/image-400.webp 400w, /image-800.webp 800w, /image-1200.webp 1200w"
    sizes="(max-width: 768px) 100vw, 800px"
    type="image/webp"
  />
  <img
    src="/image-800.jpg"
    srcset="/image-400.jpg 400w, /image-800.jpg 800w, /image-1200.jpg 1200w"
    sizes="(max-width: 768px) 100vw, 800px"
    alt="Image"
    width="800"
    height="600"
    loading="lazy"
  />
</picture>
```

## Quality Recommendations

### AVIF Quality Scale

| Use Case    | Quality | File Size vs JPEG |
| ----------- | ------- | ----------------- |
| Thumbnails  | 50-65   | -70%              |
| Most images | 65-75   | -60%              |
| Hero images | 75-85   | -50%              |

AVIF quality scale differs from JPEG/WebP. AVIF at 70 is roughly equivalent to JPEG at 90.

### WebP Quality Scale

| Use Case    | Quality | File Size vs JPEG |
| ----------- | ------- | ----------------- |
| Thumbnails  | 70-80   | -50%              |
| Most images | 80-90   | -40%              |
| Hero images | 90-95   | -30%              |

## File Size Targets

| Image Type            | Target Size | Max Size |
| --------------------- | ----------- | -------- |
| Hero image (1600w)    | 150-250 KB  | 500 KB   |
| Content image (800w)  | 80-120 KB   | 200 KB   |
| Card thumbnail (600w) | 40-80 KB    | 150 KB   |
| Thumbnail (300w)      | 15-30 KB    | 50 KB    |
| Icon/logo (150w)      | 5-15 KB     | 30 KB    |

## Generating Modern Formats

### Using Sharp (Node.js)

```javascript
import sharp from 'sharp';

// Generate AVIF
await sharp('input.jpg').avif({ quality: 70 }).toFile('output.avif');

// Generate WebP
await sharp('input.jpg').webp({ quality: 80 }).toFile('output.webp');

// Generate responsive set
const widths = [400, 800, 1200, 1600];
await Promise.all(
  widths.map((width) =>
    sharp('input.jpg')
      .resize(width)
      .avif({ quality: 70 })
      .toFile(`output-${width}.avif`),
  ),
);
```

### Using ImageMagick

```bash
# Convert to WebP
magick input.jpg -quality 80 output.webp

# Convert to AVIF
magick input.jpg -quality 70 output.avif

# Batch convert directory
for file in *.jpg; do
  magick "$file" -quality 80 "${file%.jpg}.webp"
  magick "$file" -quality 70 "${file%.jpg}.avif"
done
```

### Using cwebp (Official WebP Tool)

```bash
# Install cwebp
brew install webp  # macOS
apt install webp   # Ubuntu

# Convert to WebP
cwebp -q 80 input.jpg -o output.webp

# Lossless WebP
cwebp -lossless input.png -o output.webp
```

### Using Cloudflare Images

```typescript
const imageUrl = new URL(
  'https://imagedelivery.net/account-hash/image-id/public',
);
imageUrl.searchParams.set('format', 'auto');
imageUrl.searchParams.set('quality', '80');
imageUrl.searchParams.set('width', '800');
// Cloudflare serves AVIF to Chrome 85+, WebP to Safari 14+, JPEG to older
```

## Format Selection Decision Tree

```text
Need transparency or animation?
├── Yes -> AVIF/WebP with PNG fallback
└── No
    ├── Photo? -> AVIF -> WebP -> JPEG
    └── Simple graphic? -> SVG (if possible)
```

## Common Mistakes

- **Only serving JPEG** -- Missing 50-70% potential size savings
- **WebP without JPEG fallback** -- Breaks in older browsers without WebP support
- **Wrong source order** -- JPEG before WebP means browser picks JPEG first
- **Missing type attribute** -- Browser downloads all sources to check format

## Feature Detection (JavaScript)

```javascript
async function supportsWebP() {
  const webp =
    'data:image/webp;base64,UklGRiQAAABXRUJQVlA4IBgAAAAwAQCdASoBAAEAAwA0JaQAA3AA/vuUAAA=';
  const blob = await fetch(webp).then((r) => r.blob());
  return blob.type === 'image/webp';
}
```

## CSS Modern Format Backgrounds

Use `image-set()` for format negotiation in CSS backgrounds:

```css
.hero {
  background-image: url('/hero.jpg');
  background-image: image-set(
    url('/hero.avif') type('image/avif'),
    url('/hero.webp') type('image/webp'),
    url('/hero.jpg') type('image/jpeg')
  );
}
```
