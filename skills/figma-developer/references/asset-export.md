---
title: Asset Export
description: Exporting icons as SVG from Figma using the Images API, generating React icon components with SVGR, creating barrel exports, and tree traversal utilities
tags: [figma, icons, svg, react-components, export, barrel-export, svgr]
---

# Asset Export

## Export Icons as SVG

Use the Figma Images API (`GET /v1/images/:key`) to export nodes as SVG:

```ts
import { Api } from 'figma-api';
import fs from 'fs/promises';

async function exportIcons() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await api.getFile({ file_key: fileKey });
  const iconsFrame = findNode(file.document, 'Icons');

  if (!iconsFrame || !iconsFrame.children) {
    throw new Error('Icons frame not found');
  }

  const iconIds = iconsFrame.children.map((child: any) => child.id);

  const { images } = await api.getImages({
    file_key: fileKey,
    queryParams: {
      ids: iconIds.join(','),
      format: 'svg',
    },
  });

  for (const [nodeId, url] of Object.entries(images)) {
    if (!url) continue;
    const response = await fetch(url);
    const content = await response.text();
    const node = iconsFrame.children.find((c: any) => c.id === nodeId);
    const name = normalizeFileName(node?.name ?? nodeId);
    await fs.writeFile(`public/icons/${name}.svg`, content);
  }
}
```

## Generate React Icon Components

```ts
async function generateIconComponents() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const file = await api.getFile({ file_key: fileKey });
  const iconsFrame = findNode(file.document, 'Icons');

  if (!iconsFrame || !iconsFrame.children) {
    throw new Error('Icons frame not found');
  }

  const iconIds = iconsFrame.children.map((child: any) => child.id);

  const { images } = await api.getImages({
    file_key: fileKey,
    queryParams: {
      ids: iconIds.join(','),
      format: 'svg',
    },
  });

  const exports: string[] = [];

  for (const [nodeId, url] of Object.entries(images)) {
    if (!url) continue;
    const response = await fetch(url);
    const svgContent = await response.text();
    const node = iconsFrame.children.find((c: any) => c.id === nodeId);
    const componentName = toPascalCase(node?.name ?? nodeId);

    const component = `
export function ${componentName}Icon(props: React.SVGProps<SVGSVGElement>) {
  return (
    ${svgContent.replace('<svg', '<svg {...props}')}
  )
}
    `.trim();

    await fs.writeFile(`components/icons/${componentName}Icon.tsx`, component);
    exports.push(
      `export { ${componentName}Icon } from './${componentName}Icon'`,
    );
  }

  await fs.writeFile('components/icons/index.ts', exports.join('\n'));
}
```

## Using SVGR for Component Generation

For more robust SVG-to-React conversion, use `@svgr/core`:

```ts
import { transform } from '@svgr/core';

async function svgToReactComponent(
  svgContent: string,
  componentName: string,
): Promise<string> {
  const code = await transform(svgContent, {
    typescript: true,
    plugins: ['@svgr/plugin-svgo', '@svgr/plugin-jsx'],
    svgoConfig: {
      plugins: [
        { name: 'removeViewBox', active: false },
        { name: 'removeDimensions', active: true },
      ],
    },
  });

  return code.replace('function SvgComponent', `function ${componentName}`);
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

## Image Export Formats

The `GET /v1/images/:key` endpoint supports multiple formats:

```ts
const svgExport = await api.getImages({
  file_key: fileKey,
  queryParams: { ids: nodeIds.join(','), format: 'svg' },
});

const pngExport = await api.getImages({
  file_key: fileKey,
  queryParams: { ids: nodeIds.join(','), format: 'png', scale: 2 },
});

const pdfExport = await api.getImages({
  file_key: fileKey,
  queryParams: { ids: nodeIds.join(','), format: 'pdf' },
});
```

Image URLs returned by this endpoint expire after 14 days. Do not cache URLs long-term.

## Tree Traversal Utilities

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

function normalizeFileName(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}
```
