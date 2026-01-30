---
title: Translations & Variables
description: Using useTranslations in client and server components, variable interpolation, ICU pluralization, and locale-specific content patterns
tags: [translations, useTranslations, variables, pluralization, icu-format]
---

# Translations & Variables

## Client Component

```ts
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

```ts
import { useTranslations } from 'next-intl';

export default function HomePage() {
  const t = useTranslations('common');

  return (
    <div>
      <h1>{t('welcome')}</h1>
    </div>
  );
}
```

## Variables

```json
{
  "welcome": "Welcome, {name}!",
  "itemsInCart": "You have {count} {count, plural, one {item} other {items}} in your cart",
  "priceDisplay": "Price: {price, number, ::currency/USD}"
}
```

```ts
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
// Output: "Welcome, John!" / "You have 3 items in your cart" / "Price: $49.99"
```

## Pluralization

```json
{
  "items": {
    "count": "{count, plural, =0 {No items} one {# item} other {# items}}"
  }
}
```

```ts
'use client';
import { useTranslations } from 'next-intl';

export function ItemCounter({ count }: { count: number }) {
  const t = useTranslations('items');
  return <p>{t('count', { count })}</p>;
}
// count = 0: "No items" | count = 1: "1 item" | count = 5: "5 items"
```

## Locale-Specific Content

```ts
import { useLocale } from 'next-intl';

export default function HomePage() {
  const locale = useLocale();

  const content = {
    en: { hero: 'Build amazing apps', description: 'The best platform for developers' },
    es: { hero: 'Crea aplicaciones increíbles', description: 'La mejor plataforma para desarrolladores' },
    ja: { hero: '素晴らしいアプリを作成', description: '開発者のための最高のプラットフォーム' },
  };

  return (
    <div>
      <h1>{content[locale].hero}</h1>
      <p>{content[locale].description}</p>
    </div>
  );
}
```
