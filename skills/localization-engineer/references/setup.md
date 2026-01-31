---
title: Setup & Configuration
description: next-intl installation, defineRouting for centralized locale config, createMiddleware for locale negotiation, getRequestConfig for server-side message loading, and translation file structure
tags:
  [
    next-intl,
    setup,
    middleware,
    defineRouting,
    configuration,
    translation-files,
  ]
---

# Setup & Configuration

## Installation

```bash
npm install next-intl
```

## Routing Configuration

Define routing centrally so middleware and navigation share the same config:

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'es', 'fr', 'de', 'ja'],
  defaultLocale: 'en',
});
```

With localized pathnames:

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'es', 'fr', 'de'],
  defaultLocale: 'en',
  localePrefix: 'as-needed',
  pathnames: {
    '/': '/',
    '/about': {
      en: '/about',
      es: '/acerca-de',
      fr: '/a-propos',
      de: '/ueber-uns',
    },
  },
});
```

## Middleware

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: '/((?!api|trpc|_next|_vercel|.*\\..*).*)',
};
```

## Request Config

The `requestLocale` parameter must be awaited. This runs once per request via React `cache`:

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
```

## Translation File Structure

Organize messages by namespace in flat JSON files per locale:

```json
// messages/en.json
{
  "common": {
    "welcome": "Welcome",
    "loading": "Loading...",
    "error": "Something went wrong"
  },
  "navigation": {
    "home": "Home",
    "about": "About",
    "contact": "Contact"
  },
  "auth": {
    "login": "Log in",
    "logout": "Log out",
    "signUp": "Sign up",
    "emailPlaceholder": "Enter your email",
    "passwordPlaceholder": "Enter your password"
  }
}
```

```json
// messages/es.json
{
  "common": {
    "welcome": "Bienvenido",
    "loading": "Cargando...",
    "error": "Algo salió mal"
  },
  "navigation": {
    "home": "Inicio",
    "about": "Acerca de",
    "contact": "Contacto"
  },
  "auth": {
    "login": "Iniciar sesión",
    "logout": "Cerrar sesión",
    "signUp": "Registrarse",
    "emailPlaceholder": "Ingrese su correo electrónico",
    "passwordPlaceholder": "Ingrese su contraseña"
  }
}
```

## Next.js Layout Integration

Wrap the app with `NextIntlClientProvider` in the locale layout:

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```
