---
title: Performance
description: Performance optimization for data visualizations including lazy loading chart libraries and virtualization for large datasets
tags:
  [
    performance,
    lazy-loading,
    dynamic-import,
    virtualization,
    large-dataset,
    bundle-size,
  ]
---

# Performance

## Lazy Loading Charts

Reduce initial bundle by loading chart libraries on demand:

```tsx
import dynamic from 'next/dynamic';

const LineChart = dynamic(
  () => import('recharts').then((mod) => mod.LineChart),
  { ssr: false },
);

export default function ChartPage() {
  return <LineChart data={data} />;
}
```

## Virtualization for Large Datasets

For tables or lists with thousands of rows:

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

export function LargeDataTable({ data }: { data: any[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: data.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} className="h-96 overflow-auto">
      <div style={{ height: `${virtualizer.getTotalSize()}px` }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div key={virtualRow.index} className="py-2 border-b">
            {data[virtualRow.index].name}: {data[virtualRow.index].value}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## General Guidelines

| Technique                   | When to Use                        |
| --------------------------- | ---------------------------------- |
| Lazy loading                | Chart not visible on initial load  |
| `ssr: false`                | Canvas/SVG charts that need DOM    |
| Virtualization              | >1000 data points in tables/lists  |
| Data sampling               | >10K points in scatter/line charts |
| Canvas rendering (Chart.js) | Very large datasets (>50K points)  |
| Web Workers                 | Heavy data transformations         |
