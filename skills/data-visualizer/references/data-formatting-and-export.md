---
title: Data Formatting and Export
description: Number formatting utilities for currency, percentages, and compact numbers, plus chart export as PNG and data export as CSV
tags: [format, currency, percent, number, Intl, export, CSV, PNG, html2canvas]
---

# Data Formatting and Export

## Number Formatting

```ts
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatPercent(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100);
}

export function formatNumber(value: number): string {
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toFixed(0);
}
```

Usage in Recharts:

```tsx
<YAxis tickFormatter={formatCurrency} />
```

## Export Chart as PNG

```tsx
'use client';

import html2canvas from 'html2canvas';

export function ExportableChart({ children }) {
  const chartRef = useRef<HTMLDivElement>(null);

  const exportToPNG = async () => {
    if (!chartRef.current) return;
    const canvas = await html2canvas(chartRef.current);
    const link = document.createElement('a');
    link.download = 'chart.png';
    link.href = canvas.toDataURL();
    link.click();
  };

  return (
    <div>
      <button
        onClick={exportToPNG}
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Export as PNG
      </button>
      <div ref={chartRef}>{children}</div>
    </div>
  );
}
```

## Export Data as CSV

```ts
export function exportToCSV(data: Record<string, unknown>[], filename: string) {
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map((row) => headers.map((h) => row[h]).join(',')),
  ].join('\n');

  const blob = new Blob([csv], { type: 'text/csv' });
  const link = document.createElement('a');
  link.download = `${filename}.csv`;
  link.href = URL.createObjectURL(blob);
  link.click();
}
```

Usage:

```tsx
<button onClick={() => exportToCSV(data, 'sales-data')}>Export to CSV</button>
```
