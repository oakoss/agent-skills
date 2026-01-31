---
title: UI Patterns
description: Language switcher using next-intl navigation, RTL layout support with CSS logical properties, dir attribute configuration, and browser language detection
tags: [language-switcher, rtl, language-detection, ui-components, navigation]
---

# UI Patterns

## Language Switcher

Use navigation APIs created from `next-intl/navigation` with the shared routing config:

```ts
// i18n/navigation.ts
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
```

```tsx
'use client';
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/navigation';

const languages = [
  { code: 'en', name: 'English' },
  { code: 'es', name: 'Español' },
  { code: 'fr', name: 'Français' },
  { code: 'de', name: 'Deutsch' },
  { code: 'ja', name: '日本語' },
];

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  function switchLocale(newLocale: string) {
    router.replace(pathname, { locale: newLocale });
  }

  return (
    <select value={locale} onChange={(e) => switchLocale(e.target.value)}>
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
    </select>
  );
}
```

## RTL (Right-to-Left) Support

Set the `dir` attribute on `<html>` based on locale:

```tsx
// app/[locale]/layout.tsx
import { getLocale } from 'next-intl/server';

const rtlLocales = ['ar', 'he', 'fa'];

export default async function LocaleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const dir = rtlLocales.includes(locale) ? 'rtl' : 'ltr';

  return (
    <html lang={locale} dir={dir}>
      <body>{children}</body>
    </html>
  );
}
```

### RTL CSS

Use CSS logical properties for automatic RTL support without separate stylesheets:

```css
.container {
  margin-inline-start: 1rem;
  padding-inline-end: 1rem;
  border-inline-start: 2px solid;
}

.sidebar {
  inset-inline-start: 0;
  inset-inline-end: auto;
}
```

Physical-to-logical property mapping:

| Physical Property  | Logical Property       |
| ------------------ | ---------------------- |
| `margin-left`      | `margin-inline-start`  |
| `margin-right`     | `margin-inline-end`    |
| `padding-left`     | `padding-inline-start` |
| `padding-right`    | `padding-inline-end`   |
| `left`             | `inset-inline-start`   |
| `right`            | `inset-inline-end`     |
| `text-align: left` | `text-align: start`    |

For cases where logical properties are insufficient:

```css
[dir='rtl'] .icon-arrow {
  transform: scaleX(-1);
}
```

## RTL Languages Reference

| Language | Code | Direction |
| -------- | ---- | --------- |
| Arabic   | ar   | RTL       |
| Hebrew   | he   | RTL       |
| Farsi    | fa   | RTL       |
| Urdu     | ur   | RTL       |
