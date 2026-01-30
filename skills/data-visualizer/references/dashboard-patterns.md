---
title: Dashboard Patterns
description: Dashboard implementation patterns including KPI cards, real-time SSE monitoring, interactive filters, and drill-down navigation
tags:
  [
    dashboard,
    KPI,
    real-time,
    SSE,
    EventSource,
    filter,
    drill-down,
    interactive,
    responsive,
  ]
---

# Dashboard Patterns

## KPI Dashboard

Executive dashboard with key metrics and trend indicators:

```tsx
interface KPICardProps {
  title: string;
  value: string | number;
  change: number;
  trend: 'up' | 'down';
}

function KPICard({ title, value, change, trend }: KPICardProps) {
  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';
  const trendIcon = trend === 'up' ? '\u2191' : '\u2193';

  return (
    <Card className="p-6">
      <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-3xl font-semibold">{value}</p>
        <span className={`ml-2 text-sm ${trendColor}`}>
          {trendIcon} {Math.abs(change)}%
        </span>
      </div>
    </Card>
  );
}

export default function Dashboard() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <KPICard title="Total Revenue" value="$45,231" change={12.5} trend="up" />
      <KPICard title="Active Users" value="2,350" change={-5.2} trend="down" />
      <KPICard title="Conversion Rate" value="3.24%" change={8.1} trend="up" />
      <KPICard title="Avg Order Value" value="$158" change={2.3} trend="up" />
    </div>
  );
}
```

## Real-Time Dashboard with SSE

Live data monitoring using Server-Sent Events:

```tsx
'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface DataPoint {
  time: string;
  value: number;
}

export default function RealtimeDashboard() {
  const [data, setData] = useState<DataPoint[]>([]);

  useEffect(() => {
    fetch('/api/metrics/realtime')
      .then((res) => res.json())
      .then(setData);

    const eventSource = new EventSource('/api/metrics/stream');

    eventSource.onmessage = (event) => {
      const newDataPoint = JSON.parse(event.data);
      setData((prev) => {
        const updated = [...prev, newDataPoint];
        return updated.slice(-20);
      });
    };

    return () => eventSource.close();
  }, []);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#8884d8"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

SSE API route:

```ts
export async function GET(req: Request) {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const interval = setInterval(async () => {
        const value = Math.floor(Math.random() * 100);
        const time = new Date().toLocaleTimeString();
        const data = `data: ${JSON.stringify({ time, value })}\n\n`;
        controller.enqueue(encoder.encode(data));
      }, 1000);

      req.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}
```

## Interactive Filters

Dashboard with period and region filtering:

```tsx
'use client';

import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

type Period = '7d' | '30d' | '90d';
type Region = 'all' | 'us' | 'eu' | 'asia';

export default function SalesDashboard() {
  const [period, setPeriod] = useState<Period>('30d');
  const [region, setRegion] = useState<Region>('all');
  const { data, loading } = useSalesData({ period, region });

  return (
    <div className="space-y-6">
      <div className="flex gap-4">
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value as Period)}
          className="px-4 py-2 border rounded"
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
        </select>
        <select
          value={region}
          onChange={(e) => setRegion(e.target.value as Region)}
          className="px-4 py-2 border rounded"
        >
          <option value="all">All Regions</option>
          <option value="us">United States</option>
          <option value="eu">Europe</option>
          <option value="asia">Asia</option>
        </select>
      </div>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data}>
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="sales" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
```

## Drill-Down Chart

Click bars to zoom from year → month → day:

```tsx
'use client';

import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

export default function DrillDownChart() {
  const [level, setLevel] = useState<'year' | 'month' | 'day'>('year');
  const [selectedYear, setSelectedYear] = useState<number | null>(null);

  const handleBarClick = (data: any) => {
    if (level === 'year') {
      setSelectedYear(data.year);
      setLevel('month');
    } else if (level === 'month') {
      setLevel('day');
    }
  };

  const goBack = () => {
    if (level === 'day') setLevel('month');
    else if (level === 'month') {
      setLevel('year');
      setSelectedYear(null);
    }
  };

  return (
    <div>
      {level !== 'year' && (
        <button onClick={goBack} className="mb-4">
          Back
        </button>
      )}
      <BarChart data={getData(level, selectedYear)} width={600} height={300}>
        <Bar dataKey="value" fill="#8884d8" onClick={handleBarClick} />
        <XAxis dataKey="name" />
        <YAxis />
      </BarChart>
    </div>
  );
}
```
