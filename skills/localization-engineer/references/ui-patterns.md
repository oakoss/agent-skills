---
title: UI Patterns
description: Language switcher component, RTL layout support with CSS logical properties, and browser language detection with localStorage persistence
tags: [language-switcher, rtl, language-detection, ui-components]
---

# UI Patterns

## Language Switcher

```ts
'use client';
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';

const languages = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  { code: 'ja', name: '日本語', flag: '🇯🇵' },
];

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const switchLanguage = (newLocale: string) => {
    const pathWithoutLocale = pathname.replace(`/${locale}`, '');
    router.push(`/${newLocale}${pathWithoutLocale}`);
  };

  return (
    <select
      value={locale}
      onChange={(e) => switchLanguage(e.target.value)}
      className="px-4 py-2 border rounded"
    >
      {languages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.name}
        </option>
      ))}
    </select>
  );
}
```

## RTL (Right-to-Left) Support

```ts
// app/[locale]/layout.tsx
import { useLocale } from 'next-intl';

const rtlLanguages = ['ar', 'he', 'fa'];

export default function LocaleLayout({ children }) {
  const locale = useLocale();
  const isRTL = rtlLanguages.includes(locale);

  return (
    <html lang={locale} dir={isRTL ? 'rtl' : 'ltr'}>
      <body>{children}</body>
    </html>
  );
}
```

### RTL CSS

Use CSS logical properties for automatic RTL support:

```css
/* Automatically flips for RTL */
.container {
  margin-inline-start: 1rem;
  padding-inline-end: 1rem;
}

/* Manual RTL handling */
[dir='rtl'] .menu {
  left: auto;
  right: 0;
}
```

## Language Detection

```ts
// lib/detect-locale.ts
export function detectUserLocale(): string {
  // 1. Check URL parameter
  const urlParams = new URLSearchParams(window.location.search);
  const urlLocale = urlParams.get('lang');
  if (urlLocale) return urlLocale;

  // 2. Check localStorage
  const savedLocale = localStorage.getItem('preferredLocale');
  if (savedLocale) return savedLocale;

  // 3. Check browser language
  const browserLocale = navigator.language.split('-')[0];
  return browserLocale;
}
```
