---
name: localization-engineer
description: 'Implements internationalization (i18n) and localization (l10n) for multilingual applications using next-intl. Use when adding multi-language support, formatting dates and currencies by locale, handling RTL layouts, setting up translation workflows, or configuring hreflang SEO tags.'
version: 1.0.0
tags: [i18n, localization, translation, multilingual, internationalization]
---

# Localization Engineer

Build multilingual applications with proper internationalization (i18n) and localization (l10n) support using next-intl.

## Capabilities

| Category             | Features                                              |
| -------------------- | ----------------------------------------------------- |
| Internationalization | Multi-language text, date/time, number/currency, RTL  |
| Localization         | Translation management, language detection, switching |
| SEO                  | hreflang tags, locale-specific metadata               |

## Quick Start (next-intl)

| Step       | File               | Purpose                            |
| ---------- | ------------------ | ---------------------------------- |
| Install    | —                  | `npm install next-intl`            |
| Config     | `i18n/request.ts`  | Load messages for requested locale |
| Middleware | `middleware.ts`    | Locale routing and detection       |
| Messages   | `messages/en.json` | Translation strings (nested JSON)  |
| Use        | Component          | `useTranslations('namespace')`     |

## Translation Key Structure

| Level     | Example Key                           | Purpose               |
| --------- | ------------------------------------- | --------------------- |
| Namespace | `common`, `auth`, `nav`               | Group by feature/page |
| Key       | `welcome`, `login`                    | Individual string     |
| Variable  | `{name}`, `{count}`                   | Dynamic interpolation |
| Plural    | `{count, plural, one {#} other {#s}}` | Pluralization         |

## Formatting

| Type     | Hook           | Example Output (en/de/ja)                           |
| -------- | -------------- | --------------------------------------------------- |
| Date     | `useFormatter` | "Oct 22, 2025" / "22. Okt. 2025" / "2025年10月22日" |
| Number   | `useFormatter` | "1,234.56" / "1.234,56" / "1,234.56"                |
| Currency | `useFormatter` | "$1,234.56" / "1.234,56 $" / "$1,234.56"            |
| Percent  | `useFormatter` | "12%" / "12 %" / "12%"                              |
| Relative | `useFormatter` | "2 days ago" / "vor 2 Tagen" / "2日前"              |

## RTL Languages

| Language | Code | Direction |
| -------- | ---- | --------- |
| Arabic   | ar   | RTL       |
| Hebrew   | he   | RTL       |
| Farsi    | fa   | RTL       |

Use CSS logical properties (`margin-inline-start`, `padding-inline-end`) instead of physical (`margin-left`, `padding-right`) for automatic RTL support.

## Anti-Patterns

| Anti-Pattern                             | Fix                                              |
| ---------------------------------------- | ------------------------------------------------ |
| Hardcoded strings in components          | Use `useTranslations` with message files         |
| Concatenating translated strings         | Use ICU message format with variables            |
| Physical CSS properties with RTL support | Use CSS logical properties                       |
| Missing hreflang tags                    | Add `alternates.languages` in metadata           |
| No fallback for missing translations     | Configure `getMessageFallback` in request config |
| Inline locale-specific content           | Use translation files for all user-facing text   |

## Translation Management

| Service  | Use Case                     |
| -------- | ---------------------------- |
| Lokalise | Team translation workflows   |
| Crowdin  | Open-source projects         |
| Phrase   | Enterprise translation       |
| Manual   | Small projects (< 5 locales) |

## Common Mistakes

| Mistake                                                           | Correct Pattern                                                                            |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Hardcoding user-facing strings directly in components             | Use `useTranslations` with namespaced message files for all visible text                   |
| Concatenating translated strings to build sentences               | Use ICU message format with variables for proper grammar across languages                  |
| Using physical CSS properties like `margin-left` with RTL support | Use CSS logical properties (`margin-inline-start`) for automatic RTL handling              |
| Missing fallback configuration for untranslated keys              | Configure `getMessageFallback` in request config to handle missing translations gracefully |
| Omitting hreflang tags from multilingual pages                    | Add `alternates.languages` in metadata for proper multilingual SEO                         |

## Delegation

- **Audit existing codebase for hardcoded strings and missing translations**: Use `Explore` agent to scan components for untranslated text and incomplete message files
- **Set up full i18n pipeline with middleware, routing, and message files**: Use `Task` agent to configure next-intl, create locale routing, and structure translation keys
- **Plan localization architecture for a new multilingual application**: Use `Plan` agent to design namespace structure, locale detection strategy, and translation management workflow

## References

- [Setup & Configuration](references/setup.md) — next-intl installation, middleware, request config, translation file structure
- [Translations & Variables](references/translations.md) — useTranslations, variables, pluralization, locale-specific content
- [Formatting](references/formatting.md) — Date/time, number, currency, and percentage formatting with useFormatter
- [UI Patterns](references/ui-patterns.md) — Language switcher, RTL support, language detection
- [SEO & Management](references/seo-management.md) — Multilingual SEO, hreflang, translation sync, missing translation handling
