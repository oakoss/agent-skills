---
title: Design Patterns
description: Glassmorphism, neumorphism, and bento grid implementations with Tailwind CSS including legibility standards, interaction states, and responsive adaptation
tags:
  [
    glassmorphism,
    neumorphism,
    bento-grid,
    Tailwind,
    design-systems,
    visual-hierarchy,
  ]
---

## Glassmorphism

Glassmorphism creates depth through blur, transparency, and edge lighting. Focus on legibility and visual hierarchy rather than pure transparency effects.

### The Formula

- **Blur**: High backdrop blur (`backdrop-blur-xl`)
- **Transparency**: Medium opacity (`bg-white/70` light, `bg-black/40` dark)
- **Edge Lighting**: Subtle bright border (`border-white/20`)

### Implementation

```tsx
<div className="bg-white/70 dark:bg-slate-900/40 backdrop-blur-xl border border-white/20 dark:border-slate-800/50 rounded-2xl p-6 shadow-xl">
  <h3 className="text-lg font-semibold">Glass Card</h3>
  <p className="text-slate-600 dark:text-slate-400">
    Content that feels integrated.
  </p>
</div>
```

### Legibility Standards

Never place critical text over high-contrast glass backgrounds. Use an overlay layer with 80%+ opacity if the background image is busy.

### Layering and Z-Index

- **Lower layer**: Subtle blur, lower opacity
- **Higher layer (modal)**: High blur, higher opacity, prominent white border

### Micro-interactions

- Add a CSS shine effect on hover to simulate moving glass
- Pair with 150ms transitions for a "liquid" response

## Neumorphism

Neumorphism creates a tactile, pressed/raised effect using dual-direction shadows. Focus on restraint and accessibility.

### Tailwind Custom Shadows

```css
@theme {
  --shadow-neumorphic-up: 5px 5px 10px #bebebe, -5px -5px 10px #ffffff;
  --shadow-neumorphic-down:
    inset 5px 5px 10px #bebebe, inset -5px -5px 10px #ffffff;
}
```

### Best Practices

- **Strategic use**: Apply only to buttons, toggles, and cards that need a tactile feel. Do not apply to every element.
- **Accessibility**: Include a 1px border (`border-slate-200/50`) to define shape for low-vision users. Stark neumorphism often fails contrast tests.
- **Light mode only**: Neumorphism works best in light mode. For dark mode, use glassmorphism instead since shadows are harder to perceive on dark backgrounds.

### Interaction States

- **Normal**: `shadow-neumorphic-up`
- **Active/Pressed**: `shadow-neumorphic-down` + slight background darkening

## Bento Grid

Bento grids organize content into modular, responsive cells with visual hierarchy through size variation.

### Core Principles

- **Modular cells**: Each content piece lives in its own container
- **Visual hierarchy**: Important cells occupy more columns or rows
- **Consistent spacing**: Standard gap (`gap-4` or `gap-6`)
- **Exaggerated rounding**: `rounded-3xl` is a hallmark of the bento style

### Implementation

```tsx
<div className="grid grid-cols-1 md:grid-cols-4 grid-rows-2 gap-4">
  {/* Hero cell spans 2 columns and 2 rows */}
  <div className="md:col-span-2 md:row-span-2 bg-slate-100 rounded-3xl p-8">
    <h2 className="text-3xl font-bold">Main Insight</h2>
  </div>

  {/* Medium cell */}
  <div className="md:col-span-2 bg-slate-50 rounded-3xl p-6">
    <p>Metric A</p>
  </div>

  {/* Small cells */}
  <div className="bg-white border rounded-3xl p-6">
    <p>Sub-metric B</p>
  </div>
  <div className="bg-white border rounded-3xl p-6">
    <p>Sub-metric C</p>
  </div>
</div>
```

### Interaction and Depth

- Subtle scale-up on hover: `hover:scale-[1.02]`
- Shadow progression: `shadow-sm` at rest, `shadow-md` on hover

### Responsive Adaptation

On mobile, bento grids collapse to a single-column stack. Keep the hero cell at the top. Design each cell to be consumed in under 5 seconds with clear typography and high-contrast icons.
