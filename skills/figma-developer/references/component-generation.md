---
title: Component Generation
description: Extracting component structure and variants from Figma, generating React components with props, style extraction, and component sync workflows
tags: [figma, component-generation, variants, react, props, styles, sync]
---

# Component Generation

## Extract Component Structure

```ts
import { FigmaClient } from '@/integrations/design-tools/figma/client';

async function extractComponents() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const components = await client.getFileComponents(fileKey);

  for (const [key, component] of Object.entries(components)) {
    console.log(`${component.name} — Key: ${component.key}`);
  }

  const componentSets = await client.getComponentSets(fileKey);

  for (const [setId, variants] of Object.entries(componentSets)) {
    for (const variant of variants) {
      console.log(`  ${variant.name}`);
    }
  }
}
```

## Generate Component from Figma Node

```ts
async function generateButtonComponent() {
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const components = await client.getFileComponents(fileKey);
  const buttonComponent = Object.values(components).find((c) =>
    c.name.toLowerCase().includes('button'),
  );

  if (!buttonComponent) {
    throw new Error('Button component not found');
  }

  const file = await client.getFile(fileKey);
  const buttonNode = findNodeById(file.document, buttonComponent.key);

  if (!buttonNode) {
    throw new Error('Button node not found');
  }

  const styles = extractStyles(buttonNode);

  const component = `
import React from 'react'

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
  const client = new FigmaClient();
  const fileKey = 'YOUR_FIGMA_FILE_KEY';

  const components = await client.getFileComponents(fileKey);
  const component = Object.values(components).find(
    (c) => c.name === componentName,
  );

  if (!component) {
    throw new Error(`Component not found: ${componentName}`);
  }

  const code = await generateComponentCode(component);
  await fs.writeFile(`components/${componentName}.tsx`, code);
}
```
