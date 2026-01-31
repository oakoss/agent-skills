---
title: Library Comparison
description: Detailed comparison of Lucide, Heroicons, and Phosphor icon libraries with installation, usage, and bundle size analysis
tags: [lucide, heroicons, phosphor, comparison, bundle-size, tree-shaking]
---

# Library Comparison

Detailed comparison of Lucide, Heroicons, and Phosphor icon libraries.

## Overview

| Feature            | Lucide            | Heroicons                       | Phosphor                |
| ------------------ | ----------------- | ------------------------------- | ----------------------- |
| **Icons**          | 1,500+            | 316                             | 7,000+                  |
| **Weights**        | 1                 | 4 (outline, solid, mini, micro) | 6 (thin to fill)        |
| **Package**        | `lucide-react`    | `@heroicons/react`              | `@phosphor-icons/react` |
| **Size (gzip)**    | ~5KB per icon set | ~3KB                            | ~7KB                    |
| **Tree-shakeable** | Yes               | Yes                             | Yes                     |
| **License**        | ISC               | MIT                             | MIT                     |
| **Origin**         | Fork of Feather   | Tailwind Labs                   | Independent             |

## Lucide (Default Recommendation)

Best for React/Vue/Svelte projects, general-purpose applications, and teams familiar with Feather Icons.

```bash
npm install lucide-react
```

```tsx
import { Home, Settings, User } from 'lucide-react'

<Home className="w-6 h-6" />
<Settings className="w-6 h-6" strokeWidth={1.5} />
```

Strengths: Large library with frequent updates, excellent React integration, PascalCase component names, customizable stroke width.

Limitations: No weight variations (outline only), some inconsistency from community contributions.

## Heroicons

Best for Tailwind CSS projects, minimal aesthetic, and projects using Tailwind UI components.

```bash
npm install @heroicons/react
```

```tsx
import { HomeIcon } from '@heroicons/react/24/outline';
import { HomeIcon } from '@heroicons/react/24/solid';
import { HomeIcon } from '@heroicons/react/20/solid';
import { HomeIcon } from '@heroicons/react/16/solid';

<HomeIcon className="w-6 h-6" />;
```

Strengths: Official Tailwind integration, consistent design, four styles per icon (outline, solid, mini, micro), three sizes (16, 20, 24px).

Limitations: Smaller library (316 icons), verbose import paths.

## Phosphor

Best for weight variations (thin, light, regular, bold, fill, duotone), large icon needs, and design-heavy projects.

```bash
npm install @phosphor-icons/react
```

```tsx
import { House, Gear, User } from '@phosphor-icons/react'

<House size={24} />
<House size={24} weight="thin" />
<House size={24} weight="bold" />
<House size={24} weight="fill" />
<House size={24} weight="duotone" />
```

Strengths: Largest library (7,000+ icons), 6 weight variations per icon, consistent design language, unique duotone variant.

Limitations: Larger bundle if using multiple weights, less React-ecosystem adoption.

## Tree-Shaking Patterns

All three libraries support tree-shaking with specific imports:

```tsx
import { Home, User, Settings } from 'lucide-react';
import { HomeIcon, UserIcon } from '@heroicons/react/24/outline';
import { House, User, Gear } from '@phosphor-icons/react';
```

Never use wildcard imports -- they bundle all icons:

```tsx
import * as Icons from 'lucide-react';
const Icon = Icons[iconName];
```

Use an explicit map instead:

```tsx
import { Home, User, Settings, type LucideIcon } from 'lucide-react';

const ICON_MAP: Record<string, LucideIcon> = {
  home: Home,
  user: User,
  settings: Settings,
};

const Icon = ICON_MAP[iconName];
```

## Bundle Size (20 Icons)

| Library                  | Bundle Impact |
| ------------------------ | ------------- |
| Lucide                   | ~15KB         |
| Heroicons                | ~12KB         |
| Phosphor (single weight) | ~18KB         |
| Phosphor (6 weights)     | ~100KB        |

## Recommendation Matrix

| Project Type                   | Recommended Library |
| ------------------------------ | ------------------- |
| React + Tailwind               | Heroicons or Lucide |
| React general                  | Lucide              |
| Vue/Svelte                     | Lucide              |
| Design-heavy, brand-consistent | Phosphor            |
| Minimal bundle size            | Heroicons           |
| Maximum icon variety           | Phosphor            |
| Legacy Feather migration       | Lucide              |
