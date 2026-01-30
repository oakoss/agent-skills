---
name: figma-developer
description: 'Extracts components from Figma and converts designs to React code. Use when syncing Figma tokens to CSS variables, exporting icons as SVG components, or generating code from Figma designs. Use for design-to-code automation, token extraction, and CI-based Figma sync.'
version: 1.0.0
tags: [figma, design-to-code, design-tokens, component-generation]
---

# Figma Developer

Design is the single source of truth. Automate the Figma-to-code bridge.

## Workflow

| Phase      | Action                                         | Output                                  |
| ---------- | ---------------------------------------------- | --------------------------------------- |
| Setup      | Auth token + FigmaClient init                  | API connection                          |
| Tokens     | Extract colors, typography, spacing            | CSS variables + JSON + TypeScript types |
| Assets     | Export icons as SVG, generate React components | `components/icons/` barrel export       |
| Components | Extract structure + variants from Figma        | Generated React components with props   |
| Automation | GitHub Actions cron or webhook                 | Auto-sync PRs on Figma updates          |

## Figma File Organization

| Section    | Contents                                            |
| ---------- | --------------------------------------------------- |
| Colors     | All color styles with `/` hierarchy (`Primary/500`) |
| Typography | Text styles (`Heading/Large`, `Body/Regular`)       |
| Spacing    | Spacing guide values                                |
| Components | Variant groups (`Button/Primary`, `Card/Default`)   |
| Icons      | All icons in one exportable frame                   |

## Key APIs

| Method                                    | Purpose                             |
| ----------------------------------------- | ----------------------------------- |
| `client.getFile(fileKey)`                 | Fetch full Figma file               |
| `client.extractDesignTokens(fileKey)`     | Extract colors, typography, spacing |
| `client.exportTokensAsCSS(fileKey)`       | Generate CSS custom properties      |
| `client.exportImages(fileKey, ids, opts)` | Export nodes as SVG/PNG             |
| `client.getFileComponents(fileKey)`       | List all components and variants    |
| `client.getComponentSets(fileKey)`        | Get variant groupings               |

## Common Mistakes

| Mistake                                         | Fix                                                       |
| ----------------------------------------------- | --------------------------------------------------------- |
| Hardcoding Figma values instead of using tokens | Extract tokens to CSS variables, reference with `var()`   |
| Not normalizing Figma style names               | Lowercase + replace special chars with hyphens            |
| Forgetting Figma uses 0-1 RGB not 0-255         | Multiply by 255 and round before hex conversion           |
| No API response caching                         | Cache with TTL to avoid rate limits                       |
| Manual icon exports                             | Automate with `exportImages` + React component generation |
| No CI sync workflow                             | GitHub Actions cron + `create-pull-request` action        |

## Libraries

| Package                | Purpose                           |
| ---------------------- | --------------------------------- |
| `@figma/rest-api-spec` | TypeScript types for Figma API    |
| `figma-api`            | Alternative Figma client          |
| `style-dictionary`     | Transform tokens across platforms |

## Delegation

- **Design systems**: see `design-system` skill
- **Asset optimization**: see `asset-manager` skill

## References

- [Setup and Authentication](references/setup.md)
- [Design Tokens](references/design-tokens.md)
- [Asset Export](references/asset-export.md)
- [Component Generation](references/component-generation.md)
- [CI Automation](references/ci-automation.md)
- [Troubleshooting](references/troubleshooting.md)
