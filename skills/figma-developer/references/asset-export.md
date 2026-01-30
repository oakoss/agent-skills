---
title: Asset Export
description: Exporting icons as SVG from Figma, generating React icon components, creating barrel exports, and tree traversal utilities
tags: [figma, icons, svg, react-components, export, barrel-export]
---

# Asset Export

## Export Icons as SVG

```ts
import { FigmaClient } from '@/integrations/design-tools/figma/client';
import fs from 'fs/promises';

async function exportIcons() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await client.getFile(fileKey);
  const iconsFrame = findNode(file.document, 'Icons');

  if (!iconsFrame || !iconsFrame.children) {
    throw new Error('Icons frame not found');
  }

  const iconIds = iconsFrame.children.map((child) => child.id);
  const svgs = await client.exportImages(fileKey, iconIds, {
    format: 'svg',
  });

  for (const svg of svgs) {
    const response = await fetch(svg.url);
    const content = await response.text();
    await fs.writeFile(`public/icons/${svg.name}.svg`, content);
  }
}
```

## Generate React Icon Components

```ts
async function generateIconComponents() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await client.getFile(fileKey);
  const iconsFrame = findNode(file.document, 'Icons');

  if (!iconsFrame || !iconsFrame.children) {
    throw new Error('Icons frame not found');
  }

  const iconIds = iconsFrame.children.map((child) => child.id);
  const svgs = await client.exportImages(fileKey, iconIds, {
    format: 'svg',
  });

  for (const svg of svgs) {
    const response = await fetch(svg.url);
    const svgContent = await response.text();

    const componentName = toPascalCase(svg.name);
    const component = `
import React from 'react'

export function ${componentName}Icon(props: React.SVGProps<SVGSVGElement>) {
  return (
    ${svgContent.replace('<svg', '<svg {...props}')}
  )
}
    `.trim();

    await fs.writeFile(`components/icons/${componentName}Icon.tsx`, component);
  }

  const indexContent = svgs
    .map((svg) => {
      const componentName = toPascalCase(svg.name);
      return `export { ${componentName}Icon } from './${componentName}Icon'`;
    })
    .join('\n');

  await fs.writeFile('components/icons/index.ts', indexContent);
}
```

## Usage

```tsx
import { HomeIcon, UserIcon, SettingsIcon } from '@/components/icons';

export function Navigation() {
  return (
    <nav>
      <HomeIcon width={24} height={24} />
      <UserIcon width={24} height={24} />
      <SettingsIcon width={24} height={24} />
    </nav>
  );
}
```

## Tree Traversal Utility

```ts
function findNode(node: any, name: string): any {
  if (node.name === name) return node;
  if (node.children) {
    for (const child of node.children) {
      const found = findNode(child, name);
      if (found) return found;
    }
  }
  return null;
}

function toPascalCase(str: string): string {
  return str
    .split(/[-_\s]+/)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}
```
