---
title: Dark Mode
description: Tailwind v4 dark mode setup with @custom-variant, class-based toggling, multi-theme systems with data attributes, ThemeProvider component, and semantic color tokens
tags: [dark-mode, custom-variant, multi-theme, theme-provider, css-variables]
---

# Dark Mode

## Class-Based Dark Mode (v4)

Override the default `prefers-color-scheme` behavior with `@custom-variant`:

```css
@import 'tailwindcss';

@custom-variant dark (&:where(.dark, .dark *));
```

This enables the `dark:` variant to respond to a `.dark` class on an ancestor element (typically `<html>`).

## Semantic Token Approach

Define CSS variables that auto-adapt, eliminating the need for `dark:` variants in markup:

```css
@theme {
  --color-surface: oklch(1 0 0);
  --color-surface-raised: oklch(0.98 0 0);
  --color-text: oklch(0.15 0 0);
  --color-text-muted: oklch(0.45 0 0);
  --color-border: oklch(0.9 0 0);
}

.dark {
  --color-surface: oklch(0.12 0.02 260);
  --color-surface-raised: oklch(0.18 0.02 260);
  --color-text: oklch(0.95 0 0);
  --color-text-muted: oklch(0.65 0 0);
  --color-border: oklch(0.28 0.02 260);
}
```

Usage requires no `dark:` prefix:

```tsx
<div className="bg-surface text-text border border-border">
  <p className="text-text-muted">Adapts automatically</p>
</div>
```

## ThemeProvider Component

Toggle `.dark` class on the document element:

```tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'dark' | 'light' | 'system';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  resolvedTheme: 'dark' | 'light';
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: Theme;
  storageKey?: string;
}

function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'theme',
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme);
  const [resolvedTheme, setResolvedTheme] = useState<'dark' | 'light'>('light');

  useEffect(() => {
    const stored = localStorage.getItem(storageKey) as Theme | null;
    if (stored) setTheme(stored);
  }, [storageKey]);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');

    let resolved: 'dark' | 'light';
    if (theme === 'system') {
      resolved = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
    } else {
      resolved = theme;
    }

    root.classList.add(resolved);
    setResolvedTheme(resolved);
  }, [theme]);

  const value = {
    theme,
    setTheme: (newTheme: Theme) => {
      localStorage.setItem(storageKey, newTheme);
      setTheme(newTheme);
    },
    resolvedTheme,
  };

  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}

function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}

export { ThemeProvider, useTheme };
```

## Theme Toggle Button

```tsx
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '@/components/theme-provider';

function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();

  return (
    <button
      onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
      className="rounded-md p-2 hover:bg-accent transition-colors"
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </button>
  );
}
```

## Media Query Dark Mode (Default)

Without `@custom-variant`, Tailwind uses `prefers-color-scheme` automatically:

```css
@import 'tailwindcss';

/* No @custom-variant needed -- dark: uses prefers-color-scheme by default */
```

Apply the `@variant` directive in custom CSS:

```css
.my-element {
  background: white;

  @variant dark {
    background: black;
  }
}
```

## Multi-Theme Systems

For themes beyond light/dark, use `@theme` (without `inline`) and data attributes:

```css
@import 'tailwindcss';

@custom-variant theme-ocean (&:where([data-theme="ocean"], [data-theme="ocean"] *));
@custom-variant theme-forest (&:where([data-theme="forest"], [data-theme="forest"] *));

@theme {
  --color-primary: oklch(0.6 0.2 250);
  --color-secondary: oklch(0.7 0.15 200);
  --color-accent: oklch(0.75 0.18 30);
}

[data-theme='ocean'] {
  --color-primary: oklch(0.55 0.2 220);
  --color-secondary: oklch(0.65 0.15 200);
  --color-accent: oklch(0.7 0.18 180);
}

[data-theme='forest'] {
  --color-primary: oklch(0.5 0.18 145);
  --color-secondary: oklch(0.6 0.12 120);
  --color-accent: oklch(0.75 0.15 85);
}
```

### Theme Switcher

```ts
const themes = ['default', 'ocean', 'forest'] as const;

function setTheme(theme: string) {
  if (theme === 'default') {
    document.documentElement.removeAttribute('data-theme');
  } else {
    document.documentElement.setAttribute('data-theme', theme);
  }
  localStorage.setItem('theme', theme);
}

function initTheme() {
  const saved = localStorage.getItem('theme') ?? 'default';
  setTheme(saved);
}
```

## `@theme inline` vs `@theme` for Dark Mode

**`@theme inline`** bakes variable values at build time. Dark mode works when CSS variables change, but `@theme inline` has already inlined the original values. This breaks multi-theme switching.

**`@theme`** (without `inline`) keeps variable references at runtime, allowing dark mode and theme switching to work by overriding the underlying CSS variables.

| Scenario                         | Use                   |
| -------------------------------- | --------------------- |
| Single theme + shadcn light/dark | `@theme inline` works |
| Multi-theme (data attributes)    | `@theme` required     |
| Dynamic theme switching          | `@theme` required     |

## Key Rules

- Define `:root` and `.dark` at root level, never inside `@layer base`
- Use `hsl()` or `oklch()` wrappers in variable definitions, not in references
- Never double-wrap: use `var(--background)`, not `hsl(var(--background))`
- Semantic tokens eliminate most `dark:` variants from markup
- Verify `.dark` class toggles on the `<html>` element
