---
title: Setup & Configuration
description: next-intl installation, request config for loading locale messages, middleware for locale routing, and translation file structure
tags: [next-intl, setup, middleware, configuration, translation-files]
---

# Setup & Configuration

## Installation

```bash
npm install next-intl
```

## Request Config

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';

export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`../messages/${locale}.json`)).default,
}));
```

## Middleware

```ts
// middleware.ts
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['en', 'es', 'fr', 'de', 'ja'],
  defaultLocale: 'en',
});

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
```

## Translation File Structure

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
