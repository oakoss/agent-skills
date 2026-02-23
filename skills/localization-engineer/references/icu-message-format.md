---
title: ICU Message Format
description: Universal i18n patterns for ICU message syntax, CLDR pluralization, RTL layout, locale negotiation, hreflang SEO, and translation workflow management
tags:
  [
    icu,
    cldr,
    pluralization,
    rtl,
    hreflang,
    locale-detection,
    seo,
    logical-properties,
    translation-workflow,
  ]
---

# ICU Message Format and Universal i18n Patterns

## ICU Message Syntax

ICU MessageFormat is a standard for locale-aware message formatting. Both Paraglide (via plugin) and i18next (via `i18next-icu`) support it.

### Simple Interpolation

```text
Hello, {name}! You have {count} new messages.
```

### Plural

Uses CLDR plural categories. Available categories vary by language:

```text
{count, plural,
  zero {No items}
  one {# item}
  two {# items}
  few {# items}
  many {# items}
  other {# items}
}
```

English uses `one` and `other`. Arabic uses all six. Polish uses `one`, `few`, `many`, and `other`. Always include `other` as the fallback.

### Select (Gender / Variants)

```text
{gender, select,
  male {He left a comment}
  female {She left a comment}
  other {They left a comment}
}
```

### Nested Plural + Select

```text
{gender, select,
  male {{count, plural,
    one {He has # notification}
    other {He has # notifications}
  }}
  female {{count, plural,
    one {She has # notification}
    other {She has # notifications}
  }}
  other {{count, plural,
    one {They have # notification}
    other {They have # notifications}
  }}
}
```

### SelectOrdinal

```text
{rank, selectordinal,
  one {#st place}
  two {#nd place}
  few {#rd place}
  other {#th place}
}
```

## CLDR Plural Rules by Language

| Language | Categories Used                  |
| -------- | -------------------------------- |
| English  | one, other                       |
| French   | one, other                       |
| German   | one, other                       |
| Arabic   | zero, one, two, few, many, other |
| Polish   | one, few, many, other            |
| Russian  | one, few, many, other            |
| Japanese | other                            |
| Chinese  | other                            |

## Number and Date Formatting

Use the platform `Intl` API for locale-aware formatting:

### Numbers

```ts
const formatter = new Intl.NumberFormat('de-DE', {
  style: 'currency',
  currency: 'EUR',
});
formatter.format(1234.56);

new Intl.NumberFormat('en-US', { style: 'percent' }).format(0.85);

new Intl.NumberFormat('en-US', {
  notation: 'compact',
  compactDisplay: 'short',
}).format(1500000);
```

### Dates

```ts
const date = new Date();

new Intl.DateTimeFormat('en-US', {
  dateStyle: 'full',
  timeStyle: 'short',
}).format(date);

new Intl.DateTimeFormat('ja-JP', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
}).format(date);
```

### Relative Time

```ts
const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
rtf.format(-1, 'day');
rtf.format(3, 'hour');
```

### List Formatting

```ts
const lf = new Intl.ListFormat('en', { style: 'long', type: 'conjunction' });
lf.format(['Alice', 'Bob', 'Charlie']);
```

## RTL Layout Support

### HTML Direction

Set `dir` and `lang` on the `<html>` element:

```html
<html dir="rtl" lang="ar"></html>
```

Detect direction from locale:

```ts
const RTL_LOCALES = new Set(['ar', 'he', 'fa', 'ur', 'ps', 'ku', 'sd', 'yi']);

function getDirection(locale: string): 'ltr' | 'rtl' {
  const lang = locale.split('-')[0];
  return RTL_LOCALES.has(lang) ? 'rtl' : 'ltr';
}
```

Using `Intl.Locale` (modern browsers):

```ts
function getDirection(locale: string): 'ltr' | 'rtl' {
  const { textInfo } = new Intl.Locale(locale);
  return textInfo?.direction === 'rtl' ? 'rtl' : 'ltr';
}
```

### CSS Logical Properties

Replace physical properties with logical equivalents:

```css
/* Physical (breaks in RTL) */
.card {
  margin-left: 16px;
  padding-right: 8px;
  text-align: left;
  border-left: 2px solid blue;
  float: left;
}

/* Logical (works in both LTR and RTL) */
.card {
  margin-inline-start: 16px;
  padding-inline-end: 8px;
  text-align: start;
  border-inline-start: 2px solid blue;
  float: inline-start;
}
```

Property mapping:

| Physical            | Logical                |
| ------------------- | ---------------------- |
| `margin-left`       | `margin-inline-start`  |
| `margin-right`      | `margin-inline-end`    |
| `padding-left`      | `padding-inline-start` |
| `padding-right`     | `padding-inline-end`   |
| `border-left`       | `border-inline-start`  |
| `border-right`      | `border-inline-end`    |
| `left`              | `inset-inline-start`   |
| `right`             | `inset-inline-end`     |
| `text-align: left`  | `text-align: start`    |
| `text-align: right` | `text-align: end`      |
| `width`             | `inline-size`          |
| `height`            | `block-size`           |

### RTL-Aware Icons

Icons with directional meaning (arrows, navigation) must be flipped:

```css
[dir='rtl'] .icon-arrow {
  transform: scaleX(-1);
}
```

## Locale Negotiation and Detection

### Strategy Priority Order

1. **URL path** (`/de/about`) -- most explicit, SEO-friendly, shareable
2. **Cookie** (`locale=de`) -- persists user preference across sessions
3. **`Accept-Language` header** -- browser preference, good default
4. **Geolocation** -- least reliable, use as last resort only

### Server-Side Detection

```ts
function negotiateLocale(
  request: Request,
  supportedLocales: string[],
  defaultLocale: string,
): string {
  const cookieLocale = parseCookieLocale(request);
  if (cookieLocale && supportedLocales.includes(cookieLocale)) {
    return cookieLocale;
  }

  const acceptHeader = request.headers.get('Accept-Language');
  if (acceptHeader) {
    const preferred = parseAcceptLanguage(acceptHeader);
    for (const lang of preferred) {
      const match = supportedLocales.find(
        (l) => l === lang || l.startsWith(lang.split('-')[0]),
      );
      if (match) return match;
    }
  }

  return defaultLocale;
}

function parseAcceptLanguage(header: string): string[] {
  return header
    .split(',')
    .map((part) => {
      const [lang, q] = part.trim().split(';q=');
      return { lang: lang.trim(), q: q ? parseFloat(q) : 1 };
    })
    .sort((a, b) => b.q - a.q)
    .map(({ lang }) => lang);
}
```

### Setting Locale Cookie

```ts
function setLocaleCookie(response: Response, locale: string): void {
  const maxAge = 60 * 60 * 24 * 365;
  response.headers.append(
    'Set-Cookie',
    `locale=${locale}; Path=/; Max-Age=${maxAge}; SameSite=Lax`,
  );
}
```

## Hreflang SEO Tags

Every page with multiple locale variants needs hreflang link tags:

```html
<head>
  <link rel="alternate" hreflang="en" href="https://example.com/en/about" />
  <link rel="alternate" hreflang="de" href="https://example.com/de/about" />
  <link rel="alternate" hreflang="fr" href="https://example.com/fr/about" />
  <link rel="alternate" hreflang="x-default" href="https://example.com/about" />
</head>
```

### Generating Hreflang Tags

```ts
type LocaleUrl = { locale: string; url: string };

function generateHreflangTags(
  currentPath: string,
  supportedLocales: string[],
  baseUrl: string,
  defaultLocale: string,
): LocaleUrl[] {
  const tags: LocaleUrl[] = supportedLocales.map((locale) => ({
    locale,
    url: `${baseUrl}/${locale}${currentPath}`,
  }));

  tags.push({
    locale: 'x-default',
    url: `${baseUrl}/${defaultLocale}${currentPath}`,
  });

  return tags;
}
```

### Sitemap Integration

```xml
<url>
  <loc>https://example.com/en/about</loc>
  <xhtml:link rel="alternate" hreflang="en" href="https://example.com/en/about"/>
  <xhtml:link rel="alternate" hreflang="de" href="https://example.com/de/about"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/about"/>
</url>
```

## Translation Workflow Management

### File Organization

```sh
locales/
  en/
    common.json
    dashboard.json
    settings.json
  de/
    common.json
    dashboard.json
    settings.json
```

### Key Naming Conventions

- Use dot-separated namespaces: `dashboard.chart.title`
- Group by feature, not by UI component
- Keep keys descriptive: `order_confirmation_email_subject` not `oc_email_sub`
- Avoid positional keys: `error_message` not `error_1`

### Translation Completeness Check

```ts
function findMissingKeys(
  reference: Record<string, unknown>,
  target: Record<string, unknown>,
  prefix = '',
): string[] {
  const missing: string[] = [];

  for (const key of Object.keys(reference)) {
    const fullKey = prefix ? `${prefix}.${key}` : key;
    if (!(key in target)) {
      missing.push(fullKey);
    } else if (
      typeof reference[key] === 'object' &&
      reference[key] !== null &&
      typeof target[key] === 'object' &&
      target[key] !== null
    ) {
      missing.push(
        ...findMissingKeys(
          reference[key] as Record<string, unknown>,
          target[key] as Record<string, unknown>,
          fullKey,
        ),
      );
    }
  }

  return missing;
}
```

### Pseudolocalization for Testing

Generate pseudo-translations to catch layout issues before real translations arrive:

```ts
function pseudolocalize(text: string): string {
  const map: Record<string, string> = {
    a: '\u00e0',
    e: '\u00e9',
    i: '\u00ee',
    o: '\u00f6',
    u: '\u00fc',
    A: '\u00c0',
    E: '\u00c9',
    I: '\u00ce',
    O: '\u00d6',
    U: '\u00dc',
  };

  const converted = text.replace(/[aeiouAEIOU]/g, (c) => map[c] ?? c);
  return `[!! ${converted} !!]`;
}
```

Pseudolocalization helps catch:

- Text overflow and truncation
- Hardcoded strings missed by extraction
- Layout issues with longer text (German/Finnish translations are typically 30-40% longer than English)
- RTL layout problems when combined with mirrored pseudo-direction
