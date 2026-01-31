---
name: localization-engineer
description: |
  Implements internationalization (i18n) and localization (l10n) for multilingual Next.js applications using next-intl. Covers locale routing with defineRouting, translation management with useTranslations and getTranslations, date/number/currency formatting with useFormatter, RTL layout support, ICU message syntax, and multilingual SEO with hreflang tags.

  Use when adding multi-language support, formatting dates and currencies by locale, handling RTL layouts, setting up translation workflows, configuring locale routing middleware, or implementing hreflang SEO tags.
license: MIT
metadata:
  author: oakoss
  version: '1.1'
---

# Localization Engineer

## Overview

Provides patterns for building multilingual Next.js applications with next-intl, covering locale routing, translation management, formatting, and SEO. Handles the full i18n pipeline from middleware configuration through translation rendering.

**When to use:** Adding multi-language support, locale-aware formatting (dates, numbers, currencies), RTL layouts, language switching, translation management workflows, multilingual SEO.

**When NOT to use:** Single-language apps with no internationalization plans, non-Next.js frameworks (use react-intl or i18next directly), static content that never changes locale.

## Quick Reference

| Pattern             | API                                                    | Key Points                                               |
| ------------------- | ------------------------------------------------------ | -------------------------------------------------------- |
| Define routing      | `defineRouting({ locales, defaultLocale })`            | Centralized config shared by middleware and navigation   |
| Middleware          | `createMiddleware(routing)`                            | Pass routing config, handles negotiation and rewrites    |
| Request config      | `getRequestConfig(async ({ requestLocale }))`          | Server-side config, `requestLocale` must be awaited      |
| Client translations | `useTranslations('namespace')`                         | Client Components, returns sync `t()` function           |
| Server translations | `getTranslations('namespace')`                         | Async Server Components, must be awaited                 |
| Variables           | `t('key', { name: value })`                            | ICU message syntax for interpolation                     |
| Pluralization       | `{count, plural, one {# item} other {# items}}`        | ICU plural format in message files                       |
| Rich text           | `t.rich('key', { link: (chunks) => <a>{chunks}</a> })` | Embed React components in translations                   |
| Formatting          | `useFormatter()` / `getFormatter()`                    | Date, number, currency, relative time                    |
| Locale detection    | `useLocale()`                                          | Returns current locale string                            |
| Error fallback      | `getMessageFallback` in request config                 | Uses `IntlErrorCode.MISSING_MESSAGE` for differentiation |
| SEO alternates      | `alternates.languages` in `generateMetadata`           | Generates hreflang link tags                             |

## Common Mistakes

| Mistake                                                   | Correct Pattern                                                                    |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Hardcoding user-facing strings directly in components     | Use `useTranslations` or `getTranslations` with namespaced message files           |
| Concatenating translated strings to build sentences       | Use ICU message format with variables for proper grammar across languages          |
| Using `useTranslations` in async Server Components        | Use `getTranslations` from `next-intl/server` for async contexts                   |
| Using physical CSS properties like `margin-left` with RTL | Use CSS logical properties (`margin-inline-start`) for automatic RTL handling      |
| Passing `locale` directly to `getRequestConfig` callback  | Use `requestLocale` parameter and await it (`const locale = await requestLocale`)  |
| Duplicating routing config in middleware and navigation   | Use `defineRouting` once, import in both middleware and navigation                 |
| Missing fallback configuration for untranslated keys      | Configure `getMessageFallback` with `IntlErrorCode` to handle missing translations |
| Omitting hreflang tags from multilingual pages            | Add `alternates.languages` in `generateMetadata` for multilingual SEO              |

## Delegation

- **Audit existing codebase for hardcoded strings and missing translations**: Use `Explore` agent to scan components for untranslated text and incomplete message files
- **Set up full i18n pipeline with middleware, routing, and message files**: Use `Task` agent to configure next-intl, create locale routing, and structure translation keys
- **Plan localization architecture for a new multilingual application**: Use `Plan` agent to design namespace structure, locale detection strategy, and translation management workflow

## References

- [Setup and configuration](references/setup.md) -- next-intl installation, defineRouting, middleware, request config, translation file structure
- [Translations and variables](references/translations.md) -- useTranslations, getTranslations, variables, pluralization, rich text
- [Formatting](references/formatting.md) -- Date/time, number, currency, and percentage formatting with useFormatter
- [UI patterns](references/ui-patterns.md) -- Language switcher, RTL support with CSS logical properties, locale detection
- [SEO and management](references/seo-management.md) -- Multilingual SEO, hreflang, translation service sync, missing translation handling
