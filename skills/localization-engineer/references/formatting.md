---
title: Formatting
description: Date/time formatting with dateStyle options, number and currency formatting, percentage and compact notation, and relative time display using useFormatter
tags: [date-formatting, number-formatting, currency, useFormatter, intl]
---

# Formatting

## Date and Time

```ts
'use client';
import { useFormatter } from 'next-intl';

export function FormattedDate({ date }: { date: Date }) {
  const format = useFormatter();

  return (
    <div>
      {/* Full date */}
      <p>{format.dateTime(date, { dateStyle: 'full' })}</p>

      {/* Short date */}
      <p>{format.dateTime(date, { dateStyle: 'short' })}</p>

      {/* Custom format */}
      <p>
        {format.dateTime(date, {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: 'numeric',
        })}
      </p>

      {/* Relative time */}
      <p>{format.relativeTime(date)}</p>
    </div>
  );
}

// Examples:
// en: "Monday, October 22, 2025"
// es: "lunes, 22 de octubre de 2025"
// ja: "2025年10月22日月曜日"
```

## Number and Currency

```ts
'use client';
import { useFormatter } from 'next-intl';

export function FormattedNumber({ value }: { value: number }) {
  const format = useFormatter();

  return (
    <div>
      {/* Number */}
      <p>{format.number(value)}</p>

      {/* Currency */}
      <p>{format.number(value, { style: 'currency', currency: 'USD' })}</p>

      {/* Percentage */}
      <p>{format.number(value / 100, { style: 'percent' })}</p>

      {/* Compact notation */}
      <p>{format.number(value, { notation: 'compact' })}</p>
    </div>
  );
}

// Examples:
// en: "1,234.56" "$1,234.56" "12%" "1.2K"
// de: "1.234,56" "1.234,56 $" "12 %" "1200"
// ja: "1,234.56" "$1,234.56" "12%" "1.2千"
```
