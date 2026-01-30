---
title: Tools and Resources
description: Design tools, prototyping platforms, usability testing services, and accessibility checkers for UX design workflows
tags: [design-tools, figma, prototyping, usability-testing, accessibility-tools]
---

# Tools and Resources

## Design Tools

| Tool         | Strength                     | Best For                    |
| ------------ | ---------------------------- | --------------------------- |
| Figma        | Collaborative, browser-based | Team design, design systems |
| Tailwind CSS | Utility-first CSS framework  | Rapid UI implementation     |
| shadcn/ui    | Copy-paste component library | React component scaffolding |
| Heroicons    | Clean, minimal SVG icons     | Navigation, UI elements     |
| Lucide       | Open-source icon set         | General-purpose iconography |

## Prototyping Platforms

| Tool     | Strength                    | Best For                         |
| -------- | --------------------------- | -------------------------------- |
| Figma    | Built-in prototyping        | Standard user flow prototypes    |
| Framer   | Code-based, advanced motion | Complex interactions, animations |
| ProtoPie | Multi-device, sensor-based  | Complex micro-interactions       |

## Usability Testing Services

| Tool        | Type                         | Best For                         |
| ----------- | ---------------------------- | -------------------------------- |
| Maze        | Remote, unmoderated          | Quick quantitative testing       |
| UserTesting | Moderated and unmoderated    | In-depth qualitative research    |
| Hotjar      | Session recordings, heatmaps | Understanding real user behavior |
| Lyssna      | Remote, task-based           | Card sorting, tree testing       |

## Accessibility Tools

| Tool            | Type                    | Best For                            |
| --------------- | ----------------------- | ----------------------------------- |
| WAVE            | Browser extension       | Quick page-level accessibility scan |
| axe DevTools    | Browser extension       | Detailed WCAG violation detection   |
| Lighthouse      | Chrome built-in         | Automated accessibility scoring     |
| WebAIM Contrast | Web tool                | Color contrast ratio checking       |
| Screen readers  | OS-level assistive tech | Real-world accessibility testing    |

**Screen reader testing:**

| Platform | Screen Reader | How to Activate           |
| -------- | ------------- | ------------------------- |
| macOS    | VoiceOver     | Cmd + F5                  |
| Windows  | NVDA          | Install from nvaccess.org |
| Windows  | JAWS          | Commercial license        |
| iOS      | VoiceOver     | Settings > Accessibility  |
| Android  | TalkBack      | Settings > Accessibility  |

## Design System Components

When building a design system, include these component categories:

| Category     | Components                                               |
| ------------ | -------------------------------------------------------- |
| Primitives   | Button, Input, Textarea, Select, Checkbox, Radio, Switch |
| Layout       | Container, Grid, Stack, Separator, Spacer                |
| Navigation   | Tabs, Breadcrumb, Pagination, Sidebar, Navbar            |
| Feedback     | Alert, Toast, Progress, Skeleton, Spinner                |
| Overlay      | Modal, Dialog, Drawer, Popover, Tooltip, Dropdown        |
| Data Display | Table, Card, Badge, Avatar, List, Accordion              |
| Forms        | Form, FormField, Label, ErrorMessage, FieldGroup         |

## Design Token Structure

Organize design tokens for systematic theming:

```text
Colors:
  primary/    -- Brand primary (50-950 scale)
  secondary/  -- Brand secondary
  neutral/    -- Grays for text, borders, backgrounds
  semantic/   -- error, success, warning, info

Typography:
  h1-h6       -- Heading sizes and weights
  body        -- Default text (sm, base, lg)
  caption     -- Small supporting text

Spacing:
  4pt grid    -- 4, 8, 12, 16, 20, 24, 32, 40, 48, 64

Breakpoints:
  sm: 640px   -- Mobile landscape
  md: 768px   -- Tablet
  lg: 1024px  -- Desktop
  xl: 1280px  -- Large desktop
```

## Responsive Breakpoint Strategy

| Breakpoint  | Target Device    | Design Approach        |
| ----------- | ---------------- | ---------------------- |
| < 640px     | Mobile portrait  | Single column, stacked |
| 640-767px   | Mobile landscape | Single column, wider   |
| 768-1023px  | Tablet           | Two columns, sidebar   |
| 1024-1279px | Desktop          | Multi-column, full nav |
| 1280px+     | Large desktop    | Max-width container    |
