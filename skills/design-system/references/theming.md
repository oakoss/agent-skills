---
title: Theming
description: Theme provider with React context, dark mode via semantic tokens, multi-brand theming, Tailwind v4 CSS-first theming, and z-index scale
tags: [theming, dark-mode, theme-provider, tailwind-v4, multi-brand, z-index]
---

# Theming

## Dark Mode via Semantic Tokens

```css
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

- Reduce pure white (#fff) to off-white (#f9fafb)
- Reduce pure black (#000) to dark gray (#111827)
- Increase contrast on dark backgrounds
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

## Multi-Brand Theming

Apply brand tokens at runtime:

```ts
function applyTheme(theme: {
  colors: Record<string, string>;
  fontFamily: string;
}) {
  Object.entries(theme.colors).forEach(([key, value]) => {
    document.documentElement.style.setProperty(`--color-${key}`, value);
  });
  document.documentElement.style.setProperty('--font-base', theme.fontFamily);
}
```

## Tailwind v4 CSS-First Theme

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

### TW4 Monorepo Pattern

Centralized theme package (`@repo/design-tokens`):

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

```css
:root {
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-modal: 300;
  --z-toast: 400;
  --z-tooltip: 500;
}
```
