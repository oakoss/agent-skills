---
title: SEO & Translation Management
description: Multilingual SEO with hreflang alternate links using generateMetadata, translation service sync patterns, and missing translation fallback handling with IntlErrorCode
tags:
  [
    seo,
    hreflang,
    translation-management,
    fallback,
    IntlErrorCode,
    generateMetadata,
  ]
---

# SEO & Translation Management

## Multilingual SEO

Use `getTranslations` (not `useTranslations`) in `generateMetadata` since it runs in an async server context:

```ts
// app/[locale]/layout.tsx
import { getTranslations } from 'next-intl/server';
import { routing } from '@/i18n/routing';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'metadata' });

  return {
    title: t('title'),
    description: t('description'),
    alternates: {
      canonical: `/${locale}`,
      languages: Object.fromEntries(routing.locales.map((l) => [l, `/${l}`])),
    },
  };
}
```

Generated HTML:

```html
<link rel="canonical" href="https://example.com/en" />
<link rel="alternate" hreflang="en" href="https://example.com/en" />
<link rel="alternate" hreflang="es" href="https://example.com/es" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr" />
```

## Static Params Generation

Generate static pages for all locales:

```ts
// app/[locale]/layout.tsx
import { routing } from '@/i18n/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}
```

## Missing Translation Handling

Configure `onError` and `getMessageFallback` in the request config. Use `IntlErrorCode` to differentiate missing translations from bugs:

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { IntlErrorCode } from 'next-intl';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,

    onError(error) {
      if (error.code === IntlErrorCode.MISSING_MESSAGE) {
        console.warn('Missing translation:', error.message);
      } else {
        console.error('Intl error:', error);
      }
    },

    getMessageFallback({ namespace, key, error }) {
      const path = [namespace, key].filter(Boolean).join('.');

      if (error.code === IntlErrorCode.MISSING_MESSAGE) {
        return `[Missing: ${path}]`;
      }
      return `[Error: ${path}]`;
    },
  };
});
```

## Translation Service Sync

Example pattern for syncing translations from a service like Lokalise:

```ts
// scripts/sync-translations.ts
import { writeFile } from 'node:fs/promises';

async function syncTranslations() {
  const response = await fetch(
    'https://api.lokalise.com/api2/projects/PROJECT_ID/files/download',
    {
      headers: {
        'X-Api-Token': process.env.LOKALISE_API_KEY!,
      },
    },
  );

  if (!response.ok) {
    throw new Error(`Lokalise sync failed: ${response.status}`);
  }

  const data = await response.json();
  await writeFile('./messages/en.json', JSON.stringify(data.en, null, 2));
  console.log('Translations synced');
}

syncTranslations().catch(console.error);
```

## Translation Management Services

| Service  | Use Case                     |
| -------- | ---------------------------- |
| Lokalise | Team translation workflows   |
| Crowdin  | Open-source projects         |
| Phrase   | Enterprise translation       |
| Manual   | Small projects (< 5 locales) |
