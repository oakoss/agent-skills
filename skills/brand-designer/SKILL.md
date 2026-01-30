---
name: brand-designer
description: 'Creates cohesive brand identities, logos, and visual brand systems. Use when designing a logo, building a color palette, setting up typography systems, creating brand guidelines, generating social media templates, or organizing brand asset files.'
version: 1.0.0
tags: [branding, logo-design, identity, visual-identity, brand-guidelines]
---

# Brand Designer

Create cohesive brand identities, logos, and visual brand systems.

## Brand Discovery Checklist

| Question                            | Purpose                                 |
| ----------------------------------- | --------------------------------------- |
| What does the company do?           | Industry context                        |
| Who is the target audience?         | Demographic and psychographic targeting |
| What are the brand values?          | Core identity pillars                   |
| What feeling should the logo evoke? | Emotional direction                     |
| Any colors/symbols to avoid?        | Constraints                             |
| Who are the competitors?            | Differentiation opportunities           |

## Logo Types

| Type            | Description                      | Best For           | Examples        |
| --------------- | -------------------------------- | ------------------ | --------------- |
| Wordmark        | Clean typography of company name | Established brands | Google, Netflix |
| Lettermark      | Distinctive initials             | Long company names | IBM, HBO, CNN   |
| Icon + Wordmark | Symbol + company name            | Most versatile     | Nike, Apple     |

## Logo Requirements

| Rule         | Detail                                                         |
| ------------ | -------------------------------------------------------------- |
| Monochrome   | Must work in single color                                      |
| Scalable     | From 16px favicon to billboard                                 |
| Timeless     | Modern, not trendy                                             |
| Variants     | Full, icon-only, wordmark-only                                 |
| Clear space  | Equal to height of tallest letter                              |
| Minimum size | Digital: 120px full / 40px icon; Print: 1in full / 0.25in icon |

## Color Palette Structure

| Layer            | Example                    | Usage                         |
| ---------------- | -------------------------- | ----------------------------- |
| Primary          | Brand Blue #0066CC         | Buttons, links, active states |
| Secondary/Accent | Accent Orange #FF9100      | CTAs, highlights              |
| Neutral          | Gray scale 50-900          | Text, borders, backgrounds    |
| Semantic         | Success/Warning/Error/Info | System feedback               |

## Typography System

| Element | Size            | Weight         | Line Height    |
| ------- | --------------- | -------------- | -------------- |
| H1      | 48px (3rem)     | Bold (700)     | Tight (1.25)   |
| H2      | 36px (2.25rem)  | Semibold (600) | Tight (1.25)   |
| H3      | 30px (1.875rem) | Semibold (600) | Tight (1.25)   |
| Body    | 16px (1rem)     | Regular (400)  | Normal (1.5)   |
| Caption | 14px (0.875rem) | Regular (400)  | Normal (1.5)   |
| Small   | 12px (0.75rem)  | Regular (400)  | Relaxed (1.75) |

## Asset File Organization

| Directory       | Contents                                        |
| --------------- | ----------------------------------------------- |
| `logo/svg/`     | logo-full.svg, logo-icon.svg, logo-wordmark.svg |
| `logo/png/`     | @1x, @2x, @3x raster exports                    |
| `logo/favicon/` | 16x16, 32x32, favicon.ico                       |
| `colors/`       | palette.json                                    |
| `fonts/`        | .woff2 files                                    |
| `templates/`    | Social, business card SVGs                      |
| `guidelines/`   | Brand guidelines PDF                            |

## Common Anti-Patterns

| Anti-Pattern                                | Fix                                    |
| ------------------------------------------- | -------------------------------------- |
| Rotating or distorting logo                 | Use approved variants only             |
| Adding effects (shadows, gradients) to logo | Logo is used as-is                     |
| Using brand color for large backgrounds     | 60/30/10 rule — primary is 60% neutral |
| No monochrome variant                       | Always design in monochrome first      |
| Too many fonts                              | Maximum two font families              |

## Common Mistakes

| Mistake                                                      | Correct Pattern                                                                        |
| ------------------------------------------------------------ | -------------------------------------------------------------------------------------- |
| Designing the logo in color first                            | Design in monochrome first; the logo must work in a single color before adding palette |
| Skipping the brand discovery checklist                       | Always gather company values, audience, competitors, and constraints before designing  |
| Using more than two font families                            | Limit to one display font and one body font for cohesion                               |
| Not providing logo variants (full, icon-only, wordmark-only) | Create all three variants plus monochrome versions at required minimum sizes           |
| Exporting logos only as PNG                                  | Always provide SVG as primary format; add PNG at @1x, @2x, @3x for raster needs        |

## Delegation

When working on brand design, delegate to:

- `design-system` — Token hierarchy and component architecture
- `asset-manager` — Image optimization and asset pipeline
- `figma-developer` — Figma-to-code implementation

## References

- [Logo Design](references/logo-design.md) — SVG logo component with variants, usage patterns
- [Color Palette](references/color-palette.md) — Brand color definitions, Tailwind config, usage guidelines
- [Typography](references/typography.md) — Font selection, CSS custom properties, React typography components
- [Brand Guidelines](references/brand-guidelines.md) — Complete guidelines template with voice, tone, and visual rules
- [Templates](references/templates.md) — Social media, business card, and profile image SVG templates
- [Asset Management](references/asset-management.md) — File organization, favicon generation, HTML meta tags
