---
title: Design Tokens
description: Extracting design tokens from Figma styles and variables, generating CSS variables, JSON output, and TypeScript types
tags:
  [
    figma,
    design-tokens,
    css-variables,
    typography,
    colors,
    spacing,
    type-safety,
  ]
---

# Design Tokens

Design tokens are design decisions (colors, typography, spacing) stored as code -- single source of truth, consistent across platforms, type-safe.

## Extract Tokens from Figma Styles

There is no built-in "extract tokens" endpoint. Parse styles from the file response:

```ts
import { Api } from 'figma-api';
import fs from 'fs/promises';

async function extractTokensFromStyles() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await api.getFile({ file_key: fileKey });
  const styles = file.styles ?? {};

  const colors: Array<{ name: string; hex: string }> = [];
  const typography: Array<{
    name: string;
    family: string;
    size: number;
    weight: number;
  }> = [];

  for (const [nodeId, style] of Object.entries(styles)) {
    if (style.styleType === 'FILL') {
      const node = findNodeById(file.document, nodeId);
      if (node?.fills?.[0]?.color) {
        const c = node.fills[0].color;
        colors.push({
          name: normalizeTokenName(style.name),
          hex: rgbToHex(c.r, c.g, c.b),
        });
      }
    }

    if (style.styleType === 'TEXT') {
      const node = findNodeById(file.document, nodeId);
      if (node?.style) {
        typography.push({
          name: normalizeTokenName(style.name),
          family: node.style.fontFamily,
          size: node.style.fontSize,
          weight: node.style.fontWeight,
        });
      }
    }
  }

  return { colors, typography };
}
```

## Extract Tokens from Figma Variables

Figma Variables provide a more structured source for tokens:

```ts
async function extractTokensFromVariables() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const { meta } = await api.getLocalVariables({ file_key: fileKey });
  const variables = Object.values(meta.variables);
  const collections = meta.variableCollections;

  const tokens: Array<{ name: string; value: unknown; collection: string }> =
    [];

  for (const variable of variables) {
    const collection = collections[variable.variableCollectionId];
    const modeId = Object.keys(variable.valuesByMode)[0];
    const value = variable.valuesByMode[modeId];

    tokens.push({
      name: normalizeTokenName(variable.name),
      value,
      collection: collection.name,
    });
  }

  return tokens;
}
```

## Generate CSS Variables

```ts
function generateCSS(
  colors: Array<{ name: string; hex: string }>,
  typography: Array<{
    name: string;
    family: string;
    size: number;
    weight: number;
  }>,
): string {
  const lines = [':root {'];

  lines.push('  /* Colors */');
  for (const color of colors) {
    lines.push(`  --color-${color.name}: ${color.hex};`);
  }

  lines.push('');
  lines.push('  /* Typography */');
  for (const t of typography) {
    lines.push(`  --font-${t.name}-family: ${t.family};`);
    lines.push(`  --font-${t.name}-size: ${t.size}px;`);
    lines.push(`  --font-${t.name}-weight: ${t.weight};`);
  }

  lines.push('}');
  return lines.join('\n');
}
```

## CSS Variables Output

```css
:root {
  /* Colors */
  --color-primary: #0066cc;
  --color-secondary: #10b981;
  --color-neutral-100: #f9fafb;
  --color-neutral-900: #111827;

  /* Typography */
  --font-heading-family: Inter;
  --font-heading-size: 48px;
  --font-heading-weight: 700;

  /* Spacing */
  --space-4: 16px;
  --space-8: 32px;
}
```

## Using Tokens in Components

```tsx
export function Button({ children }: { children: React.ReactNode }) {
  return (
    <button
      style={{
        backgroundColor: 'var(--color-primary)',
        color: 'white',
        padding: 'var(--space-4)',
        fontFamily: 'var(--font-heading-family)',
        fontWeight: 'var(--font-heading-weight)',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
      }}
    >
      {children}
    </button>
  );
}
```

## Generate TypeScript Types

Create type-safe token references:

```ts
function generateTokenTypes(
  colors: Array<{ name: string }>,
  spacing: Array<{ name: string }>,
): string {
  return `
export type ColorToken =
  ${colors.map((c) => `| '${c.name}'`).join('\n  ')}

export type SpacingToken =
  ${spacing.map((s) => `| '${s.name}'`).join('\n  ')}
`.trim();
}
```

Usage:

```ts
import { type ColorToken } from '@/types/tokens';

interface ButtonProps {
  color: ColorToken;
}
```

## Style Dictionary Integration

Use `style-dictionary` to transform tokens across platforms:

```ts
import StyleDictionary from 'style-dictionary';

const sd = new StyleDictionary({
  source: ['src/styles/design-tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'src/styles/',
      files: [{ destination: 'variables.css', format: 'css/variables' }],
    },
  },
});

await sd.buildAllPlatforms();
```

## Utilities

```ts
function normalizeTokenName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function rgbToHex(r: number, g: number, b: number): string {
  const toHex = (v: number) =>
    Math.round(v * 255)
      .toString(16)
      .padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

function findNodeById(node: any, id: string): any {
  if (node.id === id) return node;
  if (node.children) {
    for (const child of node.children) {
      const found = findNodeById(child, id);
      if (found) return found;
    }
  }
  return null;
}
```
