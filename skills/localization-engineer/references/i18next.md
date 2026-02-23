---
title: i18next
description: Runtime i18n framework with plugin ecosystem, supporting React, Vue, Svelte, Angular, Node, and vanilla JS with namespaces, language detection, and backend loading
tags:
  [
    i18next,
    runtime,
    react-i18next,
    vue-i18next,
    plugins,
    namespaces,
    language-detection,
    interpolation,
  ]
---

# i18next

i18next is a runtime internationalization framework for JavaScript. Its plugin architecture supports language detection, translation loading, post-processing, and framework bindings for React, Vue, Svelte, Angular, Node.js, and vanilla JS.

## Installation

```bash
npm install i18next
```

Framework-specific bindings:

```bash
npm install react-i18next
npm install i18next-vue
npm install svelte-i18next
```

## Basic Configuration

```ts
import i18next from 'i18next';

await i18next.init({
  lng: 'en',
  fallbackLng: 'en',
  debug: false,
  interpolation: {
    escapeValue: false,
  },
  resources: {
    en: {
      translation: {
        greeting: 'Hello, {{name}}!',
        item_count_one: '{{count}} item',
        item_count_other: '{{count}} items',
      },
    },
    de: {
      translation: {
        greeting: 'Hallo, {{name}}!',
        item_count_one: '{{count}} Artikel',
        item_count_other: '{{count}} Artikel',
      },
    },
  },
});

i18next.t('greeting', { name: 'World' });
i18next.t('item_count', { count: 5 });
```

## Translation File Structure (JSON v4)

```json
{
  "greeting": "Hello, {{name}}!",
  "nested": {
    "key": "Nested value"
  },
  "reuse": "This reuses $t(greeting, {\"name\": \"World\"})",
  "unescaped": "Raw HTML: {{- value}}",
  "formatted": "Price: {{value, number}}",
  "context_male": "He liked this",
  "context_female": "She liked this",
  "count_one": "{{count}} item",
  "count_other": "{{count}} items",
  "count_zero": "No items",
  "count_two": "{{count}} items",
  "count_few": "{{count}} items",
  "count_many": "{{count}} items"
}
```

## Pluralization

i18next uses CLDR plural categories as key suffixes:

```json
{
  "cart_one": "You have {{count}} item in your cart",
  "cart_other": "You have {{count}} items in your cart"
}
```

For languages with more plural forms (e.g., Arabic):

```json
{
  "cart_zero": "...",
  "cart_one": "...",
  "cart_two": "...",
  "cart_few": "...",
  "cart_many": "...",
  "cart_other": "..."
}
```

Usage:

```ts
i18next.t('cart', { count: 0 });
i18next.t('cart', { count: 1 });
i18next.t('cart', { count: 5 });
```

## Namespaces

Split translations by feature to enable lazy loading:

```ts
await i18next.init({
  ns: ['common', 'dashboard', 'settings'],
  defaultNS: 'common',
  backend: {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
  },
});

i18next.t('save_button');
i18next.t('dashboard:chart_title');
i18next.t('settings:theme_label');
```

Load namespaces on demand:

```ts
await i18next.loadNamespaces('settings');
```

## Language Detection (Browser)

```bash
npm install i18next-browser-languagedetector
```

```ts
import i18next from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18next.use(LanguageDetector).init({
  fallbackLng: 'en',
  detection: {
    order: ['querystring', 'cookie', 'localStorage', 'navigator', 'htmlTag'],
    lookupQuerystring: 'lng',
    lookupCookie: 'i18next',
    lookupLocalStorage: 'i18nextLng',
    caches: ['cookie', 'localStorage'],
  },
});
```

## Backend Loading

```bash
npm install i18next-http-backend
```

```ts
import i18next from 'i18next';
import Backend from 'i18next-http-backend';

i18next.use(Backend).init({
  fallbackLng: 'en',
  backend: {
    loadPath: '/locales/{{lng}}/{{ns}}.json',
    addPath: '/locales/add/{{lng}}/{{ns}}',
  },
});
```

## React Integration

```tsx
import i18next from 'i18next';
import { initReactI18next, useTranslation, Trans } from 'react-i18next';

i18next.use(initReactI18next).init({
  lng: 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
  resources: {
    en: { translation: { greeting: 'Hello, {{name}}!' } },
  },
});

function Greeting() {
  const { t, i18n } = useTranslation();

  return (
    <div>
      <h1>{t('greeting', { name: 'World' })}</h1>
      <button onClick={() => i18n.changeLanguage('de')}>Deutsch</button>
    </div>
  );
}
```

### Rich Text with Trans Component

```tsx
import { Trans } from 'react-i18next';

function Terms() {
  return (
    <Trans i18nKey="terms">
      By signing up, you agree to our <a href="/terms">Terms</a> and{' '}
      <a href="/privacy">Privacy Policy</a>.
    </Trans>
  );
}
```

### Lazy-Loading Namespaces in React

```tsx
import { useTranslation } from 'react-i18next';

function Settings() {
  const { t, ready } = useTranslation('settings', { useSuspense: false });

  if (!ready) return <div>Loading...</div>;

  return <h1>{t('page_title')}</h1>;
}
```

## Vue Integration

```ts
import i18next from 'i18next';
import I18NextVue from 'i18next-vue';
import { createApp } from 'vue';
import App from './App.vue';

await i18next.init({
  lng: 'en',
  resources: {
    en: { translation: { greeting: 'Hello, {{name}}!' } },
  },
});

const app = createApp(App);
app.use(I18NextVue, { i18next });
app.mount('#app');
```

```html
<template>
  <h1>{{ $t('greeting', { name: 'World' }) }}</h1>
  <button @click="$i18next.changeLanguage('de')">Deutsch</button>
</template>
```

## Svelte Integration

```ts
import i18next from 'i18next';
import { createI18nStore } from 'svelte-i18next';

await i18next.init({
  lng: 'en',
  resources: {
    en: { translation: { greeting: 'Hello, {{name}}!' } },
  },
});

export const i18n = createI18nStore(i18next);
```

```svelte
<script>
  import { i18n } from './i18n';
</script>

<h1>{$i18n.t('greeting', { name: 'World' })}</h1>
```

## Server-Side Rendering

Create a separate i18next instance per request to prevent locale leaking:

```ts
import i18next from 'i18next';

export async function createI18nInstance(locale: string) {
  const instance = i18next.createInstance();
  await instance.init({
    lng: locale,
    fallbackLng: 'en',
    resources: await loadResources(locale),
  });
  return instance;
}

export async function handleRequest(request: Request) {
  const locale = detectLocaleFromRequest(request);
  const i18n = await createI18nInstance(locale);
  return renderApp(i18n);
}
```

## TypeScript Setup

```ts
import 'i18next';
import type translation from '../locales/en/translation.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'translation';
    resources: {
      translation: typeof translation;
    };
  }
}
```

This enables autocomplete for translation keys and catches missing keys at compile time.

## ICU Format Plugin

To use ICU MessageFormat syntax instead of i18next's native format:

```bash
npm install i18next-icu intl-messageformat
```

```ts
import i18next from 'i18next';
import ICU from 'i18next-icu';

i18next.use(ICU).init({
  lng: 'en',
  resources: {
    en: {
      translation: {
        items: '{count, plural, one {# item} other {# items}}',
        role: '{gender, select, male {He} female {She} other {They}} is an admin.',
      },
    },
  },
});
```

## When to Choose i18next

- Existing projects that need i18n added incrementally
- Applications requiring broad framework support (React, Vue, Svelte, Angular, vanilla)
- Teams that need a large plugin ecosystem (backends, detectors, post-processors)
- Projects using translation management platforms with i18next integration (Locize, Crowdin, Phrase)
- Server-side applications (Express, Fastify, Hono) with Node.js backend
