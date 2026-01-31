---
title: Theming
description: Dark mode via semantic tokens, React theme provider, multi-brand theming, Tailwind v4 CSS-first configuration, SSR flash prevention, and z-index scale
tags:
  [theming, dark-mode, theme-provider, tailwind-v4, multi-brand, z-index, ssr]
---

# Theming

## Dark Mode via Semantic Tokens

Override semantic tokens per theme — components reference semantic tokens and automatically adapt.

```css
:root,
[data-theme='light'] {
  --text-primary: var(--color-gray-900);
  --text-secondary: var(--color-gray-600);
  --surface-default: #f9fafb;
  --surface-elevated: var(--color-gray-50);
  --border-default: var(--color-gray-200);
  --interactive-primary: var(--color-blue-500);
}

[data-theme='dark'] {
  --text-primary: var(--color-gray-50);
  --text-secondary: var(--color-gray-400);
  --surface-default: var(--color-gray-900);
  --surface-elevated: var(--color-gray-800);
  --border-default: var(--color-gray-700);
  --interactive-primary: var(--color-blue-400);
}
```

Dark mode checklist:

- Reduce pure white (`#fff`) to off-white (`#f9fafb`)
- Reduce pure black (`#000`) to dark gray (`#111827`)
- Lighten interactive colors for dark backgrounds (blue-500 becomes blue-400)
- Re-verify all contrast ratios in both themes
- Support system preference via `prefers-color-scheme`

## Theme Provider (React)

```tsx
import { createContext, useContext, useEffect, useState } from 'react';

type Theme = 'light' | 'dark' | 'system';

interface ThemeContextValue {
  theme: Theme;
  resolvedTheme: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem('theme') as Theme) || 'system';
    }
    return 'system';
  });

  const [resolvedTheme, setResolvedTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    const root = document.documentElement;
    const applyTheme = (isDark: boolean) => {
      root.classList.remove('light', 'dark');
      root.classList.add(isDark ? 'dark' : 'light');
      root.setAttribute('data-theme', isDark ? 'dark' : 'light');
      setResolvedTheme(isDark ? 'dark' : 'light');
    };

    if (theme === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      applyTheme(mediaQuery.matches);
      const handler = (e: MediaQueryListEvent) => applyTheme(e.matches);
      mediaQuery.addEventListener('change', handler);
      return () => mediaQuery.removeEventListener('change', handler);
    } else {
      applyTheme(theme === 'dark');
    }
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
};
```

## SSR Flash Prevention

Theme resolution on the client causes a flash of the wrong theme. Inject a blocking script in `<head>` before the body renders.

```html
<head>
  <script>
    (function () {
      var theme = localStorage.getItem('theme') || 'system';
      var resolved = theme;
      if (theme === 'system') {
        resolved = window.matchMedia('(prefers-color-scheme: dark)').matches
          ? 'dark'
          : 'light';
      }
      document.documentElement.setAttribute('data-theme', resolved);
      document.documentElement.classList.add(resolved);
    })();
  </script>
</head>
```

For cookie-based SSR (Next.js, Remix), read the theme from a cookie on the server and set `data-theme` in the initial HTML response to avoid any flash.

## Multi-Brand Theming

Override semantic tokens per brand at runtime:

```ts
interface BrandTheme {
  colors: Record<string, string>;
  fontFamily: string;
  spacing?: { unit: number };
}

function applyBrandTheme(theme: BrandTheme) {
  const root = document.documentElement;
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value);
  });
  root.style.setProperty('--font-base', theme.fontFamily);
  if (theme.spacing) {
    root.style.setProperty('--space-unit', `${theme.spacing.unit}px`);
  }
}
```

Brand definitions share the same token interface — only values differ:

```ts
const acmeBrand: BrandTheme = {
  colors: { primary: '#3b82f6', secondary: '#8b5cf6' },
  fontFamily: 'Inter, sans-serif',
};

const contosoBrand: BrandTheme = {
  colors: { primary: '#dc2626', secondary: '#f59e0b' },
  fontFamily: 'Roboto, sans-serif',
};
```

## Tailwind v4 CSS-First Theme

Tailwind v4 replaces `tailwind.config.js` with CSS `@theme` blocks. Tokens become native CSS custom properties.

```css
@import 'tailwindcss';

@theme {
  --color-blue-500: #3b82f6;
  --color-brand-primary: var(--color-blue-500);
  --color-action-hover: color-mix(
    in srgb,
    var(--color-brand-primary),
    black 10%
  );
  --button-radius: var(--radius-lg);
}
```

### Tailwind v4 Monorepo Pattern

Centralize tokens in a shared package:

```css
/* @repo/design-tokens/base.css */
@import 'tailwindcss';

@theme {
  --color-brand: #7c3aed;
  --font-sans: 'Geist', sans-serif;
}
```

Consuming apps import the shared theme:

```css
/* apps/web/src/globals.css */
@import '@repo/design-tokens/base.css';
```

## Z-Index Scale

Define a consistent z-index system to avoid arbitrary stacking conflicts.

```css
:root {
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal-backdrop: 250;
  --z-modal: 300;
  --z-toast: 400;
  --z-tooltip: 500;
}
```

Components reference these tokens instead of hardcoded z-index values.
