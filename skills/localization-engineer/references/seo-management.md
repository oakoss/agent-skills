---
title: SEO & Translation Management
description: Multilingual SEO with hreflang alternate links, translation service sync (Lokalise, Crowdin), and missing translation fallback handling
tags: [seo, hreflang, translation-management, lokalise, crowdin, fallback]
---

# SEO & Translation Management

## Multilingual SEO

```ts
// app/[locale]/layout.tsx
import { useLocale } from 'next-intl';

export async function generateMetadata({ params: { locale } }) {
  const t = await useTranslations('metadata');

  return {
    title: t('title'),
    description: t('description'),
    alternates: {
      canonical: `/${locale}`,
      languages: {
        en: '/en',
        es: '/es',
        fr: '/fr',
        de: '/de',
        ja: '/ja',
      },
    },
  };
}
```

**Generated HTML**:

```html
<link rel="canonical" href="https://example.com/en" />
<link rel="alternate" hreflang="en" href="https://example.com/en" />
<link rel="alternate" hreflang="es" href="https://example.com/es" />
<link rel="alternate" hreflang="fr" href="https://example.com/fr" />
```

## Translation Service Sync

```ts
// scripts/sync-translations.ts
async function syncTranslations() {
  const response = await fetch(
    'https://api.lokalise.com/api2/projects/PROJECT_ID/files/download',
    {
      headers: {
        'X-Api-Token': process.env.LOKALISE_API_KEY!,
      },
    },
  );

  const data = await response.json();
  await fs.writeFile('./messages/en.json', JSON.stringify(data.en, null, 2));
  console.log('Translations synced!');
}
```

## Missing Translation Handling

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../messages/${locale}.json`)).default,
  onError: (error) => {
    console.error('Translation error:', error);
  },
  getMessageFallback: ({ namespace, key, error }) => {
    return `${namespace}.${key}`;
  },
}));
```
