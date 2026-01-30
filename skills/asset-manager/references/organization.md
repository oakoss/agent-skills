---
title: Organization
description: Asset directory structure, naming conventions, and automated organization scripts with pattern-based file sorting
tags: [assets, organization, naming, directory-structure, automation]
---

# Organization

## Directory Structure

```sh
assets/
├── images/
│   ├── products/
│   ├── team/
│   ├── marketing/
│   └── ui/
├── icons/
│   ├── svg/
│   └── png/
├── fonts/
│   ├── primary/
│   └── secondary/
├── videos/
├── logos/
│   ├── svg/
│   ├── png/
│   └── variants/
└── brand/
    ├── colors.json
    ├── typography.json
    └── guidelines.pdf
```

## Naming Conventions

Images:

```text
{category}-{description}-{size}.{format}

product-hero-1920x1080.jpg
team-sarah-400x400.jpg
ui-background-pattern.png
```

Icons:

```text
{icon-name}-{variant}.svg

home-outline.svg
home-filled.svg
user-circle.svg
```

Fonts:

```text
{font-family}-{weight}.{format}

Inter-Regular.woff2
Inter-Bold.woff2
Poppins-SemiBold.woff2
```

## Automated Organization

Pattern-based file sorting into directories:

```ts
import fs from 'fs/promises';
import path from 'path';

interface AssetRule {
  pattern: RegExp;
  destination: string;
}

const rules: AssetRule[] = [
  { pattern: /product-/i, destination: 'images/products' },
  { pattern: /team-/i, destination: 'images/team' },
  { pattern: /icon-/i, destination: 'icons/svg' },
  { pattern: /logo-/i, destination: 'logos' },
];

async function organizeAssets(sourceDir: string) {
  const files = await fs.readdir(sourceDir);

  for (const file of files) {
    const sourcePath = path.join(sourceDir, file);
    const stat = await fs.stat(sourcePath);

    if (stat.isDirectory()) continue;

    const rule = rules.find((r) => r.pattern.test(file));

    if (rule) {
      const destDir = path.join('assets', rule.destination);
      await fs.mkdir(destDir, { recursive: true });

      const destPath = path.join(destDir, file);
      await fs.rename(sourcePath, destPath);
    }
  }
}
```
