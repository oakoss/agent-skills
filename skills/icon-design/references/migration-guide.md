---
title: Migration Guide
description: Mapping tables for migrating from Font Awesome, Material Icons, Feather Icons, and emoji to modern icon libraries
tags: [migration, font-awesome, material, feather, emoji, mapping]
---

# Migration Guide

Migrate from legacy icon libraries to modern alternatives.

## Font Awesome to Lucide/Phosphor

| Font Awesome               | Lucide         | Phosphor          |
| -------------------------- | -------------- | ----------------- |
| `fa-home`                  | `Home`         | `House`           |
| `fa-user`                  | `User`         | `User`            |
| `fa-users`                 | `Users`        | `Users`           |
| `fa-cog` / `fa-gear`       | `Settings`     | `Gear`            |
| `fa-search`                | `Search`       | `MagnifyingGlass` |
| `fa-envelope`              | `Mail`         | `Envelope`        |
| `fa-phone`                 | `Phone`        | `Phone`           |
| `fa-map-marker`            | `MapPin`       | `MapPin`          |
| `fa-check`                 | `Check`        | `Check`           |
| `fa-times` / `fa-close`    | `X`            | `X`               |
| `fa-plus`                  | `Plus`         | `Plus`            |
| `fa-trash`                 | `Trash2`       | `Trash`           |
| `fa-edit` / `fa-pencil`    | `Pencil`       | `Pencil`          |
| `fa-star`                  | `Star`         | `Star`            |
| `fa-heart`                 | `Heart`        | `Heart`           |
| `fa-bell`                  | `Bell`         | `Bell`            |
| `fa-calendar`              | `Calendar`     | `Calendar`        |
| `fa-clock`                 | `Clock`        | `Clock`           |
| `fa-download`              | `Download`     | `Download`        |
| `fa-upload`                | `Upload`       | `Upload`          |
| `fa-share`                 | `Share2`       | `Share`           |
| `fa-link`                  | `Link`         | `Link`            |
| `fa-lock`                  | `Lock`         | `Lock`            |
| `fa-eye`                   | `Eye`          | `Eye`             |
| `fa-eye-slash`             | `EyeOff`       | `EyeSlash`        |
| `fa-bars`                  | `Menu`         | `List`            |
| `fa-chevron-down`          | `ChevronDown`  | `CaretDown`       |
| `fa-external-link`         | `ExternalLink` | `ArrowSquareOut`  |
| `fa-shopping-cart`         | `ShoppingCart` | `ShoppingCart`    |
| `fa-credit-card`           | `CreditCard`   | `CreditCard`      |
| `fa-tag`                   | `Tag`          | `Tag`             |
| `fa-trophy`                | `Trophy`       | `Trophy`          |
| `fa-shield`                | `Shield`       | `Shield`          |
| `fa-bolt` / `fa-lightning` | `Zap`          | `Lightning`       |
| `fa-spinner`               | `Loader2`      | `CircleNotch`     |

### Font Awesome Style Mapping

| FA Style               | Lucide  | Heroicons     | Phosphor           |
| ---------------------- | ------- | ------------- | ------------------ |
| `fa-regular` (outline) | Default | `/24/outline` | `weight="regular"` |
| `fa-solid`             | N/A     | `/24/solid`   | `weight="fill"`    |
| `fa-light`             | N/A     | N/A           | `weight="light"`   |
| `fa-thin`              | N/A     | N/A           | `weight="thin"`    |
| `fa-duotone`           | N/A     | N/A           | `weight="duotone"` |

## Material Icons to Lucide/Phosphor

| Material Icon              | Lucide         | Phosphor          |
| -------------------------- | -------------- | ----------------- |
| `home`                     | `Home`         | `House`           |
| `person`                   | `User`         | `User`            |
| `people` / `group`         | `Users`        | `Users`           |
| `settings`                 | `Settings`     | `Gear`            |
| `search`                   | `Search`       | `MagnifyingGlass` |
| `mail` / `email`           | `Mail`         | `Envelope`        |
| `phone`                    | `Phone`        | `Phone`           |
| `place` / `location_on`    | `MapPin`       | `MapPin`          |
| `check`                    | `Check`        | `Check`           |
| `close`                    | `X`            | `X`               |
| `delete`                   | `Trash2`       | `Trash`           |
| `edit`                     | `Pencil`       | `Pencil`          |
| `star`                     | `Star`         | `Star`            |
| `favorite`                 | `Heart`        | `Heart`           |
| `notifications`            | `Bell`         | `Bell`            |
| `event` / `calendar_today` | `Calendar`     | `Calendar`        |
| `schedule` / `access_time` | `Clock`        | `Clock`           |
| `description`              | `FileText`     | `FileText`        |
| `visibility`               | `Eye`          | `Eye`             |
| `visibility_off`           | `EyeOff`       | `EyeSlash`        |
| `menu`                     | `Menu`         | `List`            |
| `open_in_new`              | `ExternalLink` | `ArrowSquareOut`  |
| `shopping_cart`            | `ShoppingCart` | `ShoppingCart`    |
| `security`                 | `Shield`       | `Shield`          |
| `flash_on` / `bolt`        | `Zap`          | `Lightning`       |
| `autorenew` / `sync`       | `RefreshCw`    | `ArrowsClockwise` |

## Feather Icons to Lucide

Lucide is a direct fork of Feather Icons with the same naming:

```tsx
import { Home, User, Settings } from 'feather-icons-react';

import { Home, User, Settings } from 'lucide-react';
```

Migration is a package swap -- icon names are identical in PascalCase.

## Emoji to Icon Components

Never use emoji for UI icons. Replace with proper icon components:

| Emoji | Lucide          | Heroicons              | Phosphor          |
| ----- | --------------- | ---------------------- | ----------------- |
| check | `Check`         | `check`                | `Check`           |
| cross | `X`             | `x-mark`               | `X`               |
| warn  | `AlertTriangle` | `exclamation-triangle` | `Warning`         |
| info  | `Info`          | `information-circle`   | `Info`            |
| phone | `Phone`         | `phone`                | `Phone`           |
| mail  | `Mail`          | `envelope`             | `Envelope`        |
| pin   | `MapPin`        | `map-pin`              | `MapPin`          |
| lock  | `Lock`          | `lock-closed`          | `Lock`            |
| bolt  | `Zap`           | `bolt`                 | `Lightning`       |
| star  | `Star`          | `star`                 | `Star`            |
| heart | `Heart`         | `heart`                | `Heart`           |
| award | `Trophy`        | `trophy`               | `Trophy`          |
| bell  | `Bell`          | `bell`                 | `Bell`            |
| clock | `Clock`         | `clock`                | `Clock`           |
| lens  | `Search`        | `magnifying-glass`     | `MagnifyingGlass` |
| user  | `User`          | `user`                 | `User`            |
| house | `Home`          | `home`                 | `House`           |
| gear  | `Settings`      | `cog-6-tooth`          | `Gear`            |

Why icons over emoji: consistent styling across platforms, accessible to screen readers, themeable with CSS, tree-shakeable for performance.
