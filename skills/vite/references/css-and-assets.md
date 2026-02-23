---
title: CSS and Assets
description: CSS handling including PostCSS, CSS modules, preprocessors, Lightning CSS, and static asset management
tags:
  [
    css,
    postcss,
    css-modules,
    sass,
    scss,
    less,
    stylus,
    lightningcss,
    assets,
    static,
    svg,
    fonts,
  ]
---

# CSS and Assets

## CSS Imports

Vite handles CSS imports natively. Imported CSS is injected via `<style>` tags during dev and extracted into files during build:

```ts
import './styles/global.css';
```

## CSS Modules

Files ending in `.module.css` are treated as CSS modules:

```css
/* Button.module.css */
.root {
  padding: 8px 16px;
  border-radius: 4px;
}

.primary {
  background: blue;
  color: white;
}
```

```tsx
import styles from './Button.module.css';

function Button({
  variant = 'primary',
}: {
  variant?: 'primary' | 'secondary';
}) {
  return <button className={`${styles.root} ${styles[variant]}`}>Click</button>;
}
```

### CSS Modules Config

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    modules: {
      localsConvention: 'camelCaseOnly',
      generateScopedName: '[name]__[local]___[hash:base64:5]',
      hashPrefix: 'prefix',
    },
  },
});
```

| Option               | Values                                                       | Purpose                           |
| -------------------- | ------------------------------------------------------------ | --------------------------------- |
| `localsConvention`   | `'camelCase'`, `'camelCaseOnly'`, `'dashes'`, `'dashesOnly'` | Class name export style           |
| `generateScopedName` | String pattern or function                                   | Custom scoped name pattern        |
| `hashPrefix`         | String                                                       | Add prefix to hash for uniqueness |
| `scopeBehaviour`     | `'global'`, `'local'`                                        | Default scope behavior            |

## PostCSS

Vite applies PostCSS automatically if a config file is detected. Supported config files: `postcss.config.js`, `postcss.config.cjs`, `postcss.config.mjs`, `postcss.config.ts`.

```js
// postcss.config.js
export default {
  plugins: {
    autoprefixer: {},
    'postcss-nesting': {},
  },
};
```

Alternatively, configure inline via `css.postcss`:

```ts
import { defineConfig } from 'vite';
import autoprefixer from 'autoprefixer';
import nesting from 'postcss-nesting';

export default defineConfig({
  css: {
    postcss: {
      plugins: [autoprefixer(), nesting()],
    },
  },
});
```

Inline config disables automatic config file detection.

## CSS Preprocessors

Vite supports Sass, Less, and Stylus with zero config (install the preprocessor):

```bash
pnpm add -D sass
pnpm add -D less
pnpm add -D stylus
```

### Preprocessor Options

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/variables" as *;`,
        includePaths: ['./src/styles'],
        api: 'modern-compiler',
      },
      less: {
        math: 'parens-division',
        modifyVars: {
          'primary-color': '#1890ff',
        },
      },
    },
  },
});
```

`additionalData` is prepended to every Sass/Less file. Use `@use` instead of `@import` for modern Sass.

### Sass Modern API

Vite uses the Sass modern API by default. Set `api: 'modern-compiler'` to use the faster embedded compiler, or `api: 'legacy'` for legacy compatibility:

```ts
css: {
  preprocessorOptions: {
    scss: {
      api: 'modern-compiler',
    },
  },
}
```

## Lightning CSS

Use Lightning CSS as an alternative CSS transformer for faster processing and built-in features (nesting, custom media queries, color functions):

```ts
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    transformer: 'lightningcss',
    lightningcss: {
      targets: {
        chrome: 111,
        firefox: 114,
        safari: 16,
      },
      drafts: {
        customMedia: true,
      },
    },
  },
});
```

When using Lightning CSS, PostCSS is bypassed. Configure browser targets via `lightningcss.targets` instead of Autoprefixer.

## Dev Sourcemaps

Enable CSS sourcemaps during development:

```ts
css: {
  devSourcemap: true,
}
```

## Static Asset Handling

Importing assets returns the resolved public URL:

```ts
import imgUrl from './assets/image.png';
// imgUrl = '/assets/image.2d8e4f.png' (with hash in production)

import workerUrl from './worker.js?worker&url';
```

### Asset URL Suffixes

| Suffix    | Result                       |
| --------- | ---------------------------- |
| (none)    | Resolved URL string          |
| `?url`    | Force URL import             |
| `?raw`    | Import as raw string content |
| `?inline` | Force inline as base64       |
| `?worker` | Import as Web Worker         |

### Inline Threshold

Assets smaller than `assetsInlineLimit` (default 4096 bytes) are inlined as base64 data URIs:

```ts
build: {
  assetsInlineLimit: 8192,
}
```

Set to `0` to disable inlining entirely.

## Public Directory

Files in `public/` are served at root and copied as-is during build. They are never processed or hashed:

```text
public/
├── favicon.ico
├── robots.txt
└── og-image.png
```

Reference in HTML or code with absolute paths:

```html
<img src="/og-image.png" />
```

```ts
const url = '/robots.txt';
```

Do not import public files from JavaScript (use `src/assets/` for that).

## JSON Import

JSON files can be imported directly and support named imports for tree-shaking:

```ts
import data from './data.json';

import { version } from './package.json';
```

## SVG Handling

SVGs can be imported as URLs (default) or as React components with `vite-plugin-svgr`:

```ts
import logoUrl from './logo.svg';

import { ReactComponent as Logo } from './logo.svg?react';
```

With `vite-plugin-svgr`:

```ts
import { defineConfig } from 'vite';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
  plugins: [svgr()],
});
```

## Font Handling

Fonts in `src/assets/` are processed and hashed. Fonts in `public/` are copied as-is:

```css
/* Processed and hashed */
@font-face {
  font-family: 'CustomFont';
  src: url('./fonts/custom.woff2') format('woff2');
}
```
