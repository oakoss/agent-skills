---
title: Component Generation
description: Extracting component structure and variants from Figma, generating React components with props, style extraction, and component sync workflows
tags: [figma, component-generation, variants, react, props, styles, sync]
---

# Component Generation

## Extract Component Structure

Use `GET /v1/files/:key/components` and `GET /v1/files/:key/component_sets`:

```ts
import { Api } from 'figma-api';

async function extractComponents() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const { meta } = await api.getFileComponents({ file_key: fileKey });

  for (const component of meta.components) {
    console.log(`${component.name} -- Key: ${component.key}`);
    console.log(`  Description: ${component.description}`);
  }

  const sets = await api.getFileComponentSets({ file_key: fileKey });

  for (const set of sets.meta.component_sets) {
    console.log(`Set: ${set.name}`);
  }
}
```

## Generate Component from Figma Node

Fetch the component node, extract styles, and generate a React component:

```ts
import { Api } from 'figma-api';
import fs from 'fs/promises';

async function generateButtonComponent() {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const { meta } = await api.getFileComponents({ file_key: fileKey });
  const buttonMeta = meta.components.find((c) =>
    c.name.toLowerCase().includes('button'),
  );

  if (!buttonMeta) {
    throw new Error('Button component not found');
  }

  const file = await api.getFile({ file_key: fileKey });
  const buttonNode = findNodeById(file.document, buttonMeta.node_id);

  if (!buttonNode) {
    throw new Error('Button node not found');
  }

  const styles = extractStyles(buttonNode);

  const component = `
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  onClick
}: ButtonProps) {
  const baseStyles = {
    fontFamily: '${styles.fontFamily}',
    fontWeight: ${styles.fontWeight},
    fontSize: '${styles.fontSize}px',
    padding: '${styles.padding}',
    borderRadius: '${styles.borderRadius}px',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s'
  }

  const variantStyles = {
    primary: {
      backgroundColor: '${styles.backgroundColor}',
      color: '${styles.color}'
    },
    secondary: {
      backgroundColor: 'transparent',
      color: '${styles.backgroundColor}',
      border: '2px solid ${styles.backgroundColor}'
    },
    ghost: {
      backgroundColor: 'transparent',
      color: '${styles.color}'
    }
  }

  return (
    <button
      style={{ ...baseStyles, ...variantStyles[variant] }}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
  `.trim();

  await fs.writeFile('components/Button.tsx', component);
}
```

## Style Extraction

Parse visual properties from Figma node data:

```ts
function extractStyles(node: any) {
  return {
    fontFamily: node.style?.fontFamily || 'Inter',
    fontWeight: node.style?.fontWeight || 600,
    fontSize: node.style?.fontSize || 16,
    padding: '12px 24px',
    borderRadius: node.cornerRadius || 8,
    backgroundColor: rgbToHex(
      node.fills?.[0]?.color || { r: 0, g: 0.4, b: 0.8 },
    ),
    color: '#ffffff',
  };
}

function rgbToHex(color: { r: number; g: number; b: number }): string {
  const r = Math.round(color.r * 255)
    .toString(16)
    .padStart(2, '0');
  const g = Math.round(color.g * 255)
    .toString(16)
    .padStart(2, '0');
  const b = Math.round(color.b * 255)
    .toString(16)
    .padStart(2, '0');
  return `#${r}${g}${b}`;
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

## Component Sync Pattern

Keep components in sync with Figma as designs evolve:

```ts
async function syncComponent(componentName: string) {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const { meta } = await api.getFileComponents({ file_key: fileKey });
  const component = meta.components.find((c) => c.name === componentName);

  if (!component) {
    throw new Error(`Component not found: ${componentName}`);
  }

  const file = await api.getFile({ file_key: fileKey });
  const node = findNodeById(file.document, component.node_id);

  if (!node) {
    throw new Error(`Node not found for: ${componentName}`);
  }

  const styles = extractStyles(node);
  const code = generateComponentCode(componentName, styles);
  await fs.writeFile(`components/${componentName}.tsx`, code);
}
```

## Fetching Specific Nodes

For large files, fetch only the nodes you need instead of the entire file:

```ts
async function getComponentNode(fileKey: string, nodeId: string) {
  const api = new Api({
    personalAccessToken: process.env.FIGMA_ACCESS_TOKEN,
  });

  const { nodes } = await api.getFileNodes({
    file_key: fileKey,
    queryParams: { ids: nodeId },
  });

  return nodes[nodeId]?.document;
}
```
