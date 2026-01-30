---
title: Design Tokens
description: Extracting design tokens from Figma, exporting as CSS variables and JSON, generating TypeScript types, and using tokens in React components
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

Design tokens are design decisions (colors, typography, spacing) stored as code — single source of truth, consistent across platforms, type-safe.

## Extract Tokens

```ts
import { FigmaClient } from '@/integrations/design-tools/figma/client';
import fs from 'fs/promises';

async function syncDesignTokens() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const tokens = await client.extractDesignTokens(fileKey);

  const css = await client.exportTokensAsCSS(fileKey);
  await fs.writeFile('src/styles/design-tokens.css', css);

  const json = await client.exportTokensAsJSON(fileKey);
  await fs.writeFile('src/styles/design-tokens.json', json);
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
const types = `
export type ColorToken =
  ${tokens.colors.map((c) => `| '${c.name}'`).join('\n  ')}

export type SpacingToken =
  ${tokens.spacing.map((s) => `| '${s.name}'`).join('\n  ')}
`.trim();

await fs.writeFile('src/types/tokens.ts', types);
```

Usage:

```ts
import { ColorToken } from '@/types/tokens';

interface ButtonProps {
  color: ColorToken;
}
```
