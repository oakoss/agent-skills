---
title: CLI and Registry
description: shadcn CLI commands for initialization, component management, project creation, diff checking, and custom registry setup
tags: [cli, registry, init, add, create, diff, build, monorepo, namespaced]
---

# CLI and Registry

The shadcn CLI manages component installation, project setup, and registry distribution. It auto-detects your framework and adapts accordingly.

## CLI Commands

### init -- Initialize a Project

```bash
npx shadcn@latest init
```

Sets up configuration, installs dependencies, adds the `cn` utility, and configures CSS variables. Supports framework auto-detection.

```bash
npx shadcn@latest init --defaults
npx shadcn@latest init --base-color slate --template next
npx shadcn@latest init button card dialog
```

Key flags:

| Flag               | Description                                         |
| ------------------ | --------------------------------------------------- |
| `--defaults`       | Use default settings (Next.js, TypeScript, neutral) |
| `-t, --template`   | Framework template (next, next-monorepo)            |
| `-b, --base-color` | Base color (neutral, gray, zinc, stone, slate)      |
| `-y, --yes`        | Skip confirmation prompt                            |
| `-f, --force`      | Overwrite existing configuration                    |

### add -- Add Components

```bash
npx shadcn@latest add button
npx shadcn@latest add dialog sheet field
npx shadcn@latest add @acme/custom-button
```

Copies component source code into your project and resolves all dependencies.

| Flag              | Description                      |
| ----------------- | -------------------------------- |
| `-a, --all`       | Install all available components |
| `-o, --overwrite` | Overwrite existing files         |
| `-y, --yes`       | Skip confirmation                |
| `-s, --silent`    | Mute output                      |

### create -- Custom Project Setup

```bash
npx shadcn@latest create
```

Interactive setup that lets you choose:

- **Component library**: Radix or Base UI
- **Visual style**: Vega, Nova, Maia, Lyra, or Mira
- **Icons, fonts, base color, and theme**

This goes beyond theming -- the config rewrites component code to match your setup.

### diff -- Check for Updates

```bash
npx shadcn@latest diff
npx shadcn@latest diff button
```

Shows what has changed upstream since you added a component. Useful before customizing components to see if updates are available.

### build -- Build Registry

```bash
npx shadcn@latest build
npx shadcn@latest build ./registry.json --output ./public/r
```

Reads `registry.json` and generates registry JSON files for distribution.

| Flag           | Description                                   |
| -------------- | --------------------------------------------- |
| `-o, --output` | Destination directory (default: `./public/r`) |
| `-c, --cwd`    | Working directory                             |

### search -- Browse Registries

```bash
npx shadcn@latest search @acme
npx shadcn@latest list @acme
```

Search and browse items from namespaced registries. `list` is an alias for `search`.

### view -- Preview Before Installing

```bash
npx shadcn@latest view button
npx shadcn@latest view @acme/custom-card
```

Preview a component from the registry before adding it to your project.

## Namespaced Registries

Install from community or private registries using the `@namespace/item` format:

```bash
npx shadcn@latest add @acme/custom-button
npx shadcn@latest add @shadcn-blocks/hero-01
```

The CLI auto-detects your component library (Radix or Base UI) and applies the right transformations.

## Creating a Custom Registry

Create a `registry.json` in your project root:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json",
  "name": "acme",
  "homepage": "https://ui.acme.com",
  "items": [
    {
      "name": "fancy-button",
      "type": "registry:ui",
      "title": "Fancy Button",
      "description": "A button with animated gradient borders",
      "files": [
        {
          "path": "registry/fancy-button.tsx",
          "type": "registry:ui"
        }
      ],
      "dependencies": ["class-variance-authority"]
    }
  ]
}
```

Build and serve the registry:

```bash
npx shadcn@latest build
```

This generates JSON files in `public/r/` that can be served over HTTP for others to install from.

## Universal Registry Items

Registry items can be distributed to any project -- no framework, `components.json`, Tailwind, or React required:

```json
{
  "name": "eslint-config",
  "type": "registry:file",
  "description": "Shared ESLint configuration",
  "files": [
    {
      "path": "registry/eslint.config.js",
      "type": "registry:file",
      "target": "eslint.config.js"
    }
  ]
}
```

This enables distributing configs, rules, docs, and any code to any project.

## Local File Support

The CLI supports local files for proprietary or private components:

```bash
npx shadcn@latest init --from ./local-registry.json
npx shadcn@latest add --from ./local-registry.json custom-component
```

## Monorepo Setup

The CLI auto-detects monorepo structure. Running `add` installs components to the correct package:

```bash
npx shadcn@latest init --template next-monorepo
npx shadcn@latest add button
```

In a monorepo:

- UI components go to `packages/ui/`
- Page-level compositions go to `apps/web/components/`

Import from the shared package:

```tsx
import { Button } from '@workspace/ui/components/button';
```

## components.json Configuration

The `components.json` file (created by `init`) stores your project configuration:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "tailwind": {
    "config": "",
    "css": "src/styles/globals.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui"
  }
}
```

## Updating Components

To update a component to the latest upstream version:

```bash
npx shadcn@latest diff button
npx shadcn@latest add button --overwrite
```

Always check `diff` first to see what changed, especially if you have customized the component.
