---
title: Translations & Variables
description: Using useTranslations in Client Components, getTranslations in async Server Components, variable interpolation, ICU pluralization, rich text with React components, and message existence checks
tags:
  [
    translations,
    useTranslations,
    getTranslations,
    variables,
    pluralization,
    icu-format,
    rich-text,
  ]
---

# Translations & Variables

## Client Component

Use `useTranslations` for synchronous translation access in Client Components:

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function LoginForm() {
  const t = useTranslations('auth');

  return (
    <form>
      <input type="email" placeholder={t('emailPlaceholder')} />
      <input type="password" placeholder={t('passwordPlaceholder')} />
      <button>{t('login')}</button>
    </form>
  );
}
```

## Server Component

Use `getTranslations` from `next-intl/server` for async Server Components:

```tsx
import { getTranslations } from 'next-intl/server';

export default async function HomePage() {
  const t = await getTranslations('common');

  return (
    <div>
      <h1>{t('welcome')}</h1>
    </div>
  );
}
```

## ICU Message Syntax

next-intl uses ICU MessageFormat for interpolation, pluralization, and selection. The ICU MessageFormat 2.0 specification reached stable status in CLDR 47 (March 2025), introducing extensible formatters and a new data model. next-intl currently uses the ICU MessageFormat 1.0 syntax shown below, which remains fully supported.

## Variables

Message files use ICU message syntax for interpolation:

```json
{
  "welcome": "Welcome, {name}!",
  "itemsInCart": "You have {count} {count, plural, one {item} other {items}} in your cart",
  "priceDisplay": "Price: {price, number, ::currency/USD}"
}
```

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function Greeting({ userName }: { userName: string }) {
  const t = useTranslations();

  return (
    <div>
      <h1>{t('welcome', { name: userName })}</h1>
      <p>{t('itemsInCart', { count: 3 })}</p>
      <p>{t('priceDisplay', { price: 49.99 })}</p>
    </div>
  );
}
```

## Pluralization

ICU plural format supports `=0`, `one`, `other`, and language-specific categories (`two`, `few`, `many`):

```json
{
  "items": {
    "count": "{count, plural, =0 {No items} one {# item} other {# items}}"
  }
}
```

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function ItemCounter({ count }: { count: number }) {
  const t = useTranslations('items');
  return <p>{t('count', { count })}</p>;
}
```

## Rich Text

Embed React components inside translations using `t.rich()`:

```json
{
  "terms": "By signing up, you agree to our <link>Terms of Service</link> and <bold>Privacy Policy</bold>."
}
```

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function TermsNotice() {
  const t = useTranslations();

  return (
    <p>
      {t.rich('terms', {
        link: (chunks) => <a href="/terms">{chunks}</a>,
        bold: (chunks) => <strong>{chunks}</strong>,
      })}
    </p>
  );
}
```

## Message Existence Check

Check whether a translation key exists before rendering:

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function OptionalBanner() {
  const t = useTranslations('promo');

  if (!t.has('banner')) return null;

  return <div>{t('banner')}</div>;
}
```

## Raw Messages

Access raw message content (HTML strings or other non-text formats):

```tsx
'use client';
import { useTranslations } from 'next-intl';

export function LegalDisclaimer() {
  const t = useTranslations('legal');

  return <div dangerouslySetInnerHTML={{ __html: t.raw('disclaimer') }} />;
}
```
