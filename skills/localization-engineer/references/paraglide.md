---
title: Paraglide JS
description: Compile-time i18n with typed message functions, tree-shakable output, framework adapters for SvelteKit, TanStack Start, React Router, and Astro
tags:
  [
    paraglide,
    compile-time,
    type-safe,
    tree-shaking,
    sveltekit,
    tanstack-start,
    react-router,
    inlang,
  ]
---

# Paraglide JS

Paraglide JS is a compiler-based i18n library that generates typed, tree-shakable message functions. Only messages used in the application are included in the bundle, resulting in up to 70% smaller i18n payloads compared to runtime libraries.

## Installation

```bash
npx @inlang/paraglide-js@latest init
```

The init command creates `project.inlang/settings.json`, generates message files, detects the bundler, and configures the appropriate plugin.

## Project Configuration

```json
{
  "baseLocale": "en",
  "locales": ["en", "de", "fr", "ar"],
  "plugins": [
    {
      "pluginId": "@inlang/plugin-message-format",
      "pathPattern": "./messages/{locale}.json"
    }
  ]
}
```

## Message Files

Messages live in `messages/{locale}.json`:

```json
{
  "greeting": "Hello, {name}!",
  "item_count": "{count, plural, one {# item} other {# items}}",
  "welcome_back": "Welcome back, {name}. You have {count, plural, one {# notification} other {# notifications}}."
}
```

## Basic Usage

The compiler generates typed functions in the output directory:

```ts
import { m } from './paraglide/messages.js';
import { getLocale, setLocale } from './paraglide/runtime.js';

const message = m.greeting({ name: 'World' });

setLocale('de');
const german = m.greeting({ name: 'Welt' });

const current = getLocale();
```

## Bundler Plugins

### Vite

```ts
import { defineConfig } from 'vite';
import { paraglideVitePlugin } from '@inlang/paraglide-js';

export default defineConfig({
  plugins: [
    paraglideVitePlugin({
      project: './project.inlang',
      outdir: './src/paraglide',
      strategy: ['cookie', 'localStorage', 'baseLocale'],
    }),
  ],
});
```

### Webpack

```ts
const { paraglideWebpackPlugin } = require('@inlang/paraglide-js');

module.exports = {
  plugins: [
    paraglideWebpackPlugin({
      project: './project.inlang',
      outdir: './src/paraglide',
      strategy: ['cookie', 'baseLocale'],
    }),
  ],
};
```

## Locale Strategies

The `strategy` array defines locale resolution order. The compiler tries each strategy in sequence until one returns a locale:

```ts
paraglideVitePlugin({
  project: './project.inlang',
  outdir: './src/paraglide',
  strategy: ['cookie', 'globalVariable', 'baseLocale'],
});
```

Built-in strategies: `cookie`, `localStorage`, `globalVariable`, `baseLocale`, `url`, `preferredLanguage`.

### Custom Server Strategy

```ts
import { defineCustomServerStrategy } from './paraglide/runtime.js';

defineCustomServerStrategy('custom-header', {
  getLocale: (request) => {
    return request?.headers.get('X-User-Locale') ?? undefined;
  },
});

defineCustomServerStrategy('custom-database', {
  getLocale: async (request) => {
    const userId = extractUserId(request);
    if (!userId) return undefined;
    const prefs = await getUserPreferences(userId);
    return prefs?.locale;
  },
});
```

## Server-Side Rendering

Use `AsyncLocalStorage` to scope locale per request and prevent race conditions:

```ts
import { overwriteGetLocale, baseLocale } from './paraglide/runtime.js';
import { AsyncLocalStorage } from 'node:async_hooks';

const localeStorage = new AsyncLocalStorage<string>();

overwriteGetLocale(() => {
  return localeStorage.getStore() ?? baseLocale;
});

export function onRequest(
  request: Request,
  next: () => Promise<Response>,
): Promise<Response> {
  const locale = detectLocaleFromRequest(request);
  return localeStorage.run(locale, () => next());
}
```

## SvelteKit Integration

### Vite Config

```ts
import { sveltekit } from '@sveltejs/kit/vite';
import { paraglideVitePlugin } from '@inlang/paraglide-js';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    sveltekit(),
    paraglideVitePlugin({
      project: './project.inlang',
      outdir: './src/lib/paraglide',
    }),
  ],
});
```

### Server Hooks

```ts
import type { Handle } from '@sveltejs/kit';
import { paraglideMiddleware } from '$lib/paraglide/server';

const paraglideHandle: Handle = ({ event, resolve }) =>
  paraglideMiddleware(
    event.request,
    ({ request: localizedRequest, locale }) => {
      event.request = localizedRequest;
      return resolve(event, {
        transformPageChunk: ({ html }) => html.replace('%lang%', locale),
      });
    },
  );

export const handle: Handle = paraglideHandle;
```

### Using Messages in Svelte Components

```svelte
<script>
  import { m } from '$lib/paraglide/messages.js';
  import { getLocale } from '$lib/paraglide/runtime.js';
</script>

<h1>{m.greeting({ name: 'World' })}</h1>
<p>{m.item_count({ count: 5 })}</p>
<p>Current locale: {getLocale()}</p>
```

## TanStack Start / React Router Integration

### Vite Config

```ts
import { defineConfig } from 'vite';
import { tanstackStart } from '@tanstack/start/plugin';
import { paraglideVitePlugin } from '@inlang/paraglide-js';

export default defineConfig({
  plugins: [
    tanstackStart(),
    paraglideVitePlugin({
      project: './project.inlang',
      outdir: './src/paraglide',
      strategy: ['cookie', 'baseLocale'],
    }),
  ],
});
```

### Root Component with SSR

```tsx
import {
  assertIsLocale,
  baseLocale,
  isLocale,
  overwriteGetLocale,
} from './paraglide/runtime';
import { createContext, useContext } from 'react';

const LocaleContext = createContext(baseLocale);

if (import.meta.env.SSR) {
  overwriteGetLocale(() => assertIsLocale(useContext(LocaleContext)));
}

export default function App({
  loaderData,
}: {
  loaderData: { locale: string };
}) {
  return (
    <LocaleContext.Provider value={loaderData.locale}>
      <Outlet />
    </LocaleContext.Provider>
  );
}
```

### Using Messages in React Components

```tsx
import { m } from './paraglide/messages.js';
import { getLocale, setLocale } from './paraglide/runtime.js';

function Dashboard() {
  return (
    <div>
      <h1>{m.welcome_back({ name: 'Alice', count: 3 })}</h1>
      <button onClick={() => setLocale('de')}>Deutsch</button>
      <p>Current: {getLocale()}</p>
    </div>
  );
}
```

## ICU Message Format Plugin

For ICU MessageFormat 1 syntax instead of the default inlang format:

```json
{
  "baseLocale": "en",
  "locales": ["en", "de"],
  "plugins": [
    {
      "pluginId": "inlang-icu-messageformat-1",
      "pathPattern": "./messages/{locale}.json"
    }
  ]
}
```

## Tooling

- **Sherlock VS Code extension** -- inline message previews, click-to-edit translations
- **Fink editor** -- visual translation editor for non-developer translators
- **inlang CLI** -- `npx @inlang/cli lint` to check for missing translations, unused keys

## When to Choose Paraglide

- New projects where bundle size and type safety are priorities
- Applications using SvelteKit, TanStack Start, React Router, or Astro
- Teams that want compile-time guarantees for translation completeness
- Projects where tree-shaking unused translations matters (mobile web, performance-critical)
