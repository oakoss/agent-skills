---
title: Formatting
description: Date/time formatting with dateStyle options, number and currency formatting, percentage and compact notation, relative time display using useFormatter in Client Components and getFormatter in Server Components
tags:
  [
    date-formatting,
    number-formatting,
    currency,
    useFormatter,
    getFormatter,
    intl,
  ]
---

# Formatting

## Date and Time

```tsx
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

// Examples by locale:
// en: "Monday, October 22, 2025"
// es: "lunes, 22 de octubre de 2025"
// ja: "2025年10月22日月曜日"
```

## Number and Currency

```tsx
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

// Examples by locale:
// en: "1,234.56" "$1,234.56" "12%" "1.2K"
// de: "1.234,56" "1.234,56 $" "12 %" "1200"
// ja: "1,234.56" "$1,234.56" "12%" "1.2千"
```

## Server Component Formatting

Use `getFormatter` from `next-intl/server` for async Server Components:

```tsx
import { getFormatter } from 'next-intl/server';

export default async function StatsPage() {
  const format = await getFormatter();

  const revenue = 1500000;
  const lastUpdated = new Date();

  return (
    <div>
      <p>
        Revenue:{' '}
        {format.number(revenue, { style: 'currency', currency: 'USD' })}
      </p>
      <p>Updated: {format.relativeTime(lastUpdated)}</p>
    </div>
  );
}
```

## Date Range Formatting

```tsx
'use client';
import { useFormatter } from 'next-intl';

export function DateRange({ start, end }: { start: Date; end: Date }) {
  const format = useFormatter();

  return (
    <p>
      {format.dateTimeRange(start, end, {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })}
    </p>
  );
}

// en: "Jan 1 – Mar 31, 2025"
// de: "1. Jan. – 31. März 2025"
```
