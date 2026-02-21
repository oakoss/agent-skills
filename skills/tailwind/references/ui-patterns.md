---
title: UI Patterns
description: Tailwind-native component patterns for buttons, forms, navigation, cards, and typography with variants, states, and accessibility
tags:
  [
    ui-components,
    buttons,
    forms,
    navigation,
    cards,
    typography,
    accessibility,
    states,
  ]
---

# UI Patterns

## Buttons

Base button with accessibility built-in:

```tsx
<button className="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50">
  Button
</button>
```

Key: `focus-visible:ring-2` (keyboard), `disabled:pointer-events-none` (prevent clicks), `transition-colors` (smooth states).

### Variants

```tsx
<button className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md">Primary</button>
<button className="bg-secondary text-secondary-foreground hover:bg-secondary/80 px-4 py-2 rounded-md">Secondary</button>
<button className="border border-input bg-background hover:bg-accent px-4 py-2 rounded-md">Outline</button>
<button className="hover:bg-accent hover:text-accent-foreground px-4 py-2 rounded-md">Ghost</button>
<button className="bg-destructive text-destructive-foreground hover:bg-destructive/90 px-4 py-2 rounded-md">Delete</button>
<button className="text-primary underline-offset-4 hover:underline">Link</button>
```

### Sizes

```tsx
<button className="h-9 px-3 text-sm">Small</button>
<button className="h-10 px-4 py-2">Default</button>
<button className="h-11 px-8">Large</button>
<button className="h-10 w-10" aria-label="Settings"><svg className="h-5 w-5">⚙</svg></button>
```

Minimum touch target: 44x44px (h-11/w-11). Use `aria-label` for icon-only buttons.

### States

```tsx
<button disabled className="disabled:pointer-events-none disabled:opacity-50">Disabled</button>
<button disabled className="flex items-center gap-2"><svg className="h-4 w-4 animate-spin">⟳</svg> Loading</button>
<button className="flex items-center gap-2"><svg className="h-4 w-4">📥</svg> Download</button>
```

## Form Inputs

### Text Input

```tsx
<div className="space-y-2">
  <label htmlFor="name" className="text-sm font-medium">
    Name
  </label>
  <input
    id="name"
    type="text"
    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
    placeholder="Enter your name"
  />
</div>
```

Always pair inputs with `<label>` using `htmlFor`/`id`. Use `focus-visible:ring-2` for keyboard focus.

### Input Types

```tsx
<input type="email" placeholder="you@example.com" className="..." />
<input type="password" className="..." />
<div className="relative">
  <input type="search" placeholder="Search..." className="pl-10 ..." />
  <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground">🔍</svg>
</div>
```

### Textarea and Select

```tsx
<textarea rows={4} className="flex min-h-20 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" />
<select className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
  <option>Select option</option>
</select>
```

### Checkbox and Radio

```tsx
<div className="flex items-center space-x-2">
  <input id="terms" type="checkbox" className="h-4 w-4 rounded border-border text-primary focus:ring-2 focus:ring-primary focus:ring-offset-2" />
  <label htmlFor="terms" className="text-sm">I agree</label>
</div>

<fieldset className="space-y-3">
  <legend className="text-sm font-medium mb-2">Plan</legend>
  <div className="flex items-center space-x-2">
    <input id="free" type="radio" name="plan" className="h-4 w-4 border-border text-primary focus:ring-2 focus:ring-primary" />
    <label htmlFor="free" className="text-sm">Free</label>
  </div>
</fieldset>
```

Minimum size: 16x16px (h-4/w-4). Use `<fieldset>` and `<legend>` for grouped controls.

### Validation States

```tsx
<div className="space-y-2">
  <label htmlFor="email" className="text-sm font-medium">Email</label>
  <input
    id="email"
    type="email"
    className="border border-destructive focus-visible:ring-destructive ..."
    aria-invalid="true"
    aria-describedby="email-error"
  />
  <p id="email-error" className="text-sm text-destructive">Invalid email</p>
</div>

<div className="space-y-2">
  <input className="border border-success focus-visible:ring-success ..." />
  <p className="text-sm text-success flex items-center gap-1"><svg className="h-4 w-4">✓</svg> Available</p>
</div>
```

Use `aria-invalid` and `aria-describedby` for screen readers.

## Navigation

### Sticky Header

```tsx
<header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex h-16 items-center justify-between">
      <a href="/" className="font-bold text-xl">
        Brand
      </a>
      <nav className="hidden md:flex gap-6">
        <a
          href="#features"
          className="text-sm hover:text-primary transition-colors"
        >
          Features
        </a>
      </nav>
    </div>
  </div>
</header>
```

`z-50` keeps header above content. `backdrop-blur` creates glass effect.

### Mobile Menu

```tsx
'use client';
import { useState } from 'react';

export function MobileNav() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        onClick={() => setOpen(!open)}
        className="md:hidden p-2"
        aria-label="Toggle menu"
        aria-expanded={open}
      >
        <svg className="h-6 w-6">{open ? '✕' : '☰'}</svg>
      </button>
      {open && (
        <div className="md:hidden border-t border-border">
          <nav className="px-4 py-6 space-y-4">
            <a href="#features" className="block text-sm hover:text-primary">
              Features
            </a>
          </nav>
        </div>
      )}
    </>
  );
}
```

Use `aria-expanded` to communicate menu state.

### Sidebar

```tsx
<aside className="w-64 border-r border-border bg-card p-6 h-screen sticky top-0">
  <nav className="space-y-1">
    <a
      href="/dashboard"
      className="flex items-center gap-3 px-3 py-2 rounded-md bg-primary text-primary-foreground"
      aria-current="page"
    >
      <svg className="h-5 w-5">📊</svg>
      <span className="text-sm font-medium">Dashboard</span>
    </a>
    <a
      href="/projects"
      className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted"
    >
      <svg className="h-5 w-5">📁</svg>
      <span className="text-sm">Projects</span>
    </a>
  </nav>
</aside>
```

Use `aria-current="page"` for active items.

### Breadcrumbs

```tsx
<nav aria-label="Breadcrumb">
  <ol className="flex items-center gap-2 text-sm text-muted-foreground">
    <li>
      <a href="/" className="hover:text-primary">
        Home
      </a>
    </li>
    <li aria-hidden="true">
      <svg className="h-4 w-4">›</svg>
    </li>
    <li>
      <a href="/blog" className="hover:text-primary">
        Blog
      </a>
    </li>
    <li aria-hidden="true">
      <svg className="h-4 w-4">›</svg>
    </li>
    <li aria-current="page" className="font-medium text-foreground">
      Article
    </li>
  </ol>
</nav>
```

### Tabs

```tsx
<div className="border-b border-border">
  <nav className="-mb-px flex gap-8" role="tablist">
    <button className="border-b-2 border-primary text-sm font-medium py-4" aria-selected="true" role="tab">Overview</button>
    <button className="border-b-2 border-transparent text-sm text-muted-foreground py-4" role="tab">Details</button>
  </nav>
</div>

<nav className="inline-flex gap-2 p-1 bg-muted rounded-lg" role="tablist">
  <button className="px-4 py-2 text-sm font-medium bg-background rounded-md shadow" role="tab">Overview</button>
  <button className="px-4 py-2 text-sm text-muted-foreground" role="tab">Details</button>
</nav>
```

### Pagination

```tsx
<nav className="flex items-center gap-2" aria-label="Pagination">
  <button
    className="px-3 py-2 rounded-md border border-border hover:bg-muted disabled:opacity-50"
    disabled
  >
    Previous
  </button>
  <button
    className="px-3 py-2 rounded-md bg-primary text-primary-foreground"
    aria-current="page"
  >
    1
  </button>
  <button className="px-3 py-2 rounded-md border border-border hover:bg-muted">
    2
  </button>
  <span className="px-3 py-2" aria-hidden="true">
    ...
  </span>
  <button className="px-3 py-2 rounded-md border border-border hover:bg-muted">
    10
  </button>
  <button className="px-3 py-2 rounded-md border border-border hover:bg-muted">
    Next
  </button>
</nav>
```

## Cards

### Base and Interactive

```tsx
<div className="bg-card text-card-foreground rounded-lg border border-border p-6">
  <h3 className="text-lg font-semibold mb-2">Card Title</h3>
  <p className="text-muted-foreground text-sm">Description</p>
</div>

<a href="/details" className="block bg-card rounded-lg border border-border p-6 transition-all hover:shadow-lg hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
  <h3 className="text-lg font-semibold mb-2">Clickable Card</h3>
  <p className="text-muted-foreground text-sm">Click to view</p>
</a>
```

Use `<a>` for navigation, `<button>` for actions.

### Card with Image

```tsx
<div className="bg-card rounded-lg border border-border overflow-hidden">
  <img src="/image.jpg" alt="Card image" className="w-full h-48 object-cover" />
  <div className="p-6">
    <h3 className="text-lg font-semibold mb-2">Title</h3>
    <p className="text-muted-foreground text-sm">Description</p>
  </div>
</div>
```

Use `overflow-hidden` to preserve rounded corners when images touch edges.

### Card Grid

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map((item) => (
    <div key={item.id} className="bg-card rounded-lg border border-border p-6">
      <h3 className="text-lg font-semibold">{item.title}</h3>
    </div>
  ))}
</div>
```

## Typography

### Heading Hierarchy

```tsx
<h1 className="text-4xl sm:text-5xl font-bold tracking-tight">Page Title</h1>
<h2 className="text-3xl sm:text-4xl font-bold tracking-tight">Section</h2>
<h3 className="text-2xl font-semibold tracking-tight">Subsection</h3>
<h4 className="text-xl font-semibold">Component Title</h4>
```

Use `tracking-tight` for large headings.

### Body Text

```tsx
<p className="text-lg text-muted-foreground leading-relaxed">Intro paragraph</p>
<p className="text-base text-muted-foreground">Body text</p>
<p className="text-sm text-muted-foreground">Caption text</p>
```

### Prose (Long-form Content)

```tsx
<article className="prose prose-slate dark:prose-invert max-w-none">
  <h1>Article Title</h1>
  <p>Content with automatic typography...</p>
</article>
```

Install: `pnpm add @tailwindcss/typography`, load with `@plugin "@tailwindcss/typography";`.

### Code

```tsx
<code className="px-1.5 py-0.5 bg-muted rounded text-sm font-mono">className</code>

<pre className="bg-muted p-4 rounded-lg overflow-x-auto">
  <code className="text-sm font-mono">{`function hello() {
  console.log("Hello");
}`}</code>
</pre>
```

## Accessibility

### Focus Management

Use `focus-visible` for keyboard-only focus:

```tsx
<button className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Button
</button>
```

Never remove focus without replacement. `focus-visible` shows for keyboard, not mouse.

### Touch Targets

Minimum sizes:

- Buttons: 44x44px (h-11/w-11)
- Checkboxes/radios: 16x16px (h-4/w-4)
- Add padding to small icons to increase touch area

### ARIA Patterns

```tsx
<button aria-label="Close"><svg className="h-4 w-4">✕</svg></button>
<input aria-invalid="true" aria-describedby="error-id" />
<p id="error-id">Error message</p>
<button aria-expanded={open}>Menu</button>
<a href="/page" aria-current="page">Page</a>
<button role="tab" aria-selected="true">Tab 1</button>
```

### Semantic HTML

Use proper elements:

- `<button>` for actions
- `<a>` for navigation
- `<label>` for form inputs
- `<fieldset>` + `<legend>` for grouped controls
- `<nav>` for navigation
- Never use `<div>` or `<span>` for interactive elements

## Common Patterns

### Button Group

```tsx
<div className="inline-flex rounded-md shadow-xs">
  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-l-md">
    Left
  </button>
  <button className="px-4 py-2 bg-primary text-primary-foreground border-l border-primary-foreground/20">
    Middle
  </button>
  <button className="px-4 py-2 bg-primary text-primary-foreground border-l border-primary-foreground/20 rounded-r-md">
    Right
  </button>
</div>
```

### Status Badge

```tsx
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success">Active</span>
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning/10 text-warning">Pending</span>
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-destructive/10 text-destructive">Error</span>
```

### Loading Skeleton

```tsx
<div className="bg-card rounded-lg border border-border p-6 animate-pulse">
  <div className="h-12 w-12 bg-muted rounded-lg mb-4" />
  <div className="h-4 bg-muted rounded w-3/4 mb-2" />
  <div className="h-3 bg-muted rounded w-full mb-1" />
  <div className="h-3 bg-muted rounded w-5/6" />
</div>
```

### Hover Effects

```tsx
<div className="transition-transform hover:scale-105">Lift</div>
<div className="transition-shadow hover:shadow-lg">Shadow</div>
<div className="transition-colors hover:border-primary">Border</div>
<div className="transition-all hover:shadow-lg hover:border-primary hover:-translate-y-1">Combined</div>
```

Always add `transition-*` for smooth state changes.
