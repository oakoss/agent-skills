---
title: Icon Accessibility
description: Patterns for accessible icon usage including decorative icons, meaningful icons, aria attributes, and screen reader handling
tags: [accessibility, aria, screen-reader, decorative, semantic]
---

# Icon Accessibility

Proper handling of icons for screen readers and assistive technologies.

## Decorative vs Meaningful Icons

Icons fall into two categories with different accessibility requirements.

### Decorative Icons (Next to Text)

Icons alongside visible text are decorative -- the text already provides meaning. Hide them from screen readers:

```tsx
<span className="flex items-center gap-2">
  <Phone aria-hidden="true" className="w-4 h-4" />
  <span>Call us</span>
</span>
```

### Meaningful Icons (Standalone)

Icons conveying information without accompanying text need an accessible label:

```tsx
<CheckCircle aria-label="Completed" className="w-5 h-5 text-green-600" />
```

## Icon-Only Buttons

Buttons containing only an icon need `aria-label` on the button element:

```tsx
<button aria-label="Open menu" className="p-2 rounded-lg hover:bg-muted">
  <Menu className="w-6 h-6" />
</button>

<button aria-label="Close dialog" className="p-2 rounded-lg hover:bg-muted">
  <X className="w-5 h-5" />
</button>

<button aria-label="Search" className="p-2 rounded-lg hover:bg-muted">
  <Search className="w-5 h-5" />
</button>
```

## Icon-Only Links

Links containing only an icon follow the same pattern:

```tsx
<a href="/settings" aria-label="Settings">
  <Settings className="w-5 h-5" />
</a>
```

## Tooltip Wrapping for Lucide

Lucide icons do not accept HTML attributes like `title` directly. Wrap in a container:

```tsx
<span title="Award Winner">
  <Trophy aria-hidden="true" className="w-5 h-5" />
</span>
```

## Status Icons with Screen Reader Text

For status indicators, provide screen-reader-only text:

```tsx
<span className="flex items-center gap-1.5">
  <CheckCircle aria-hidden="true" className="w-4 h-4 text-green-600" />
  <span>Active</span>
</span>
```

When there is no visible text, use visually hidden text:

```tsx
<span className="flex items-center">
  <AlertTriangle aria-hidden="true" className="w-4 h-4 text-yellow-600" />
  <span className="sr-only">Warning status</span>
</span>
```

## Color and Contrast

Icons must meet WCAG contrast requirements:

- Icons conveying information need 3:1 contrast ratio against background
- Decorative icons have no contrast requirement
- Do not rely on color alone to convey meaning -- pair with text or shape differences

```tsx
<span className="flex items-center gap-1.5">
  <XCircle aria-hidden="true" className="w-4 h-4 text-destructive" />
  <span className="text-destructive">Error: Upload failed</span>
</span>
```

## Focus Indicators

Icon-only interactive elements must have visible focus indicators:

```tsx
<button
  aria-label="Delete item"
  className="p-2 rounded-lg hover:bg-muted focus-visible:outline-2 focus-visible:outline-primary"
>
  <Trash2 className="w-5 h-5" />
</button>
```

## Common Mistakes

| Mistake                                    | Fix                                              |
| ------------------------------------------ | ------------------------------------------------ |
| Icon-only button without `aria-label`      | Add `aria-label="Description"` to the button     |
| Decorative icon without `aria-hidden`      | Add `aria-hidden="true"` to icons alongside text |
| Using `title` directly on Lucide component | Wrap in a `<span title="...">` element           |
| Relying on color alone for icon meaning    | Pair icons with text or use distinct shapes      |
| Missing focus indicator on icon buttons    | Use `focus-visible:outline-*` Tailwind utilities |
