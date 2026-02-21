---
title: Storytelling and Annotation
description: Data storytelling principles, chart annotations, narrative color use, dashboard flow, small multiples, and visualization edge cases
tags:
  [
    storytelling,
    annotation,
    narrative,
    color,
    dashboard,
    small-multiples,
    empty-state,
    accessibility,
    reference-line,
    callout,
  ]
---

# Storytelling and Annotation

## Data Storytelling Principles

| Principle              | Description                                                       |
| ---------------------- | ----------------------------------------------------------------- |
| Data-ink ratio         | Maximize ink used for data, minimize decorative elements          |
| Progressive disclosure | Show summary first, let users drill into detail                   |
| Narrative arc          | Context (setup) → tension (insight) → resolution (recommendation) |
| One chart, one message | Each visualization should communicate a single clear insight      |

High data-ink ratio means removing gridlines, borders, and backgrounds that add no information. Every pixel should earn its place.

## Chart Titles That Tell the Story

Titles are the most-read element on any chart. Make them carry the insight.

| Weak (Descriptive)     | Strong (Narrative)                      |
| ---------------------- | --------------------------------------- |
| "Sales Data"           | "Sales doubled after the Q4 campaign"   |
| "Monthly Active Users" | "User growth stalled in March"          |
| "Revenue by Region"    | "APAC now drives 40% of total revenue"  |
| "Error Rate"           | "Error rate spiked 3x after deployment" |

```tsx
<LineChart data={data}>
  <text x="50%" y={20} textAnchor="middle" className="text-lg font-semibold">
    Sales doubled after the Q4 campaign
  </text>
  <text x="50%" y={40} textAnchor="middle" className="text-sm text-gray-500">
    Monthly revenue, Jan–Dec 2024
  </text>
  <Line type="monotone" dataKey="revenue" stroke="#0066CC" />
</LineChart>
```

## Reference Lines

Mark thresholds, targets, and averages to give data context.

```tsx
import {
  LineChart,
  Line,
  ReferenceLine,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export function RevenueWithTarget({
  data,
}: {
  data: { month: string; revenue: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip />
        <ReferenceLine
          y={50000}
          stroke="#D32F2F"
          strokeDasharray="5 5"
          label="Target"
        />
        <ReferenceLine
          x="Jun"
          stroke="#999"
          strokeDasharray="3 3"
          label="Campaign Launch"
        />
        <Line
          type="monotone"
          dataKey="revenue"
          stroke="#0066CC"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## Highlight Regions with ReferenceArea

Draw attention to specific time periods or value ranges.

```tsx
import {
  AreaChart,
  Area,
  ReferenceArea,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export function HighlightedPeriod({
  data,
}: {
  data: { date: string; value: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <AreaChart data={data}>
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <ReferenceArea
          x1="2024-03-01"
          x2="2024-03-31"
          fill="#FF000020"
          label="Outage Window"
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#0066CC"
          fill="#0066CC20"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
```

## Custom Callout Labels

Use Recharts `customizedLabel` to annotate specific data points.

```tsx
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  type LabelProps,
} from 'recharts';

function PeakLabel({ x, y, value }: LabelProps) {
  if (typeof x !== 'number' || typeof y !== 'number') return null;
  if (Number(value) < 100000) return null;

  return (
    <g>
      <circle cx={x} cy={y} r={6} fill="#D32F2F" />
      <text
        x={x}
        y={y - 15}
        textAnchor="middle"
        fill="#D32F2F"
        fontSize={12}
        fontWeight="bold"
      >
        Peak: {Number(value).toLocaleString()}
      </text>
    </g>
  );
}

export function AnnotatedChart({
  data,
}: {
  data: { month: string; users: number }[];
}) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <XAxis dataKey="month" />
        <YAxis />
        <Line
          type="monotone"
          dataKey="users"
          stroke="#0066CC"
          strokeWidth={2}
          label={<PeakLabel />}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## Color as Narrative

Use color intentionally to direct attention, not just differentiate series.

| Strategy           | When to Use                       | Implementation                         |
| ------------------ | --------------------------------- | -------------------------------------- |
| Highlight vs mute  | One series matters most           | Bold color for focus, gray for context |
| Sequential palette | Ordered data (low → high)         | Single hue, varying lightness          |
| Diverging palette  | Data with a meaningful center     | Two hues from a neutral midpoint       |
| Categorical        | Unrelated groups (max 5-7 colors) | Distinct, accessible hues              |
| Semantic           | Status or sentiment (good vs bad) | Green/red with accessible alternatives |

```tsx
const HIGHLIGHT_COLOR = '#0066CC';
const MUTED_COLOR = '#C0C0C0';

export function FocusedComparison({
  data,
  focusSeries,
}: {
  data: Record<string, unknown>[];
  focusSeries: string;
}) {
  const allSeries = ['productA', 'productB', 'productC'];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        {allSeries.map((key) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={key === focusSeries ? HIGHLIGHT_COLOR : MUTED_COLOR}
            strokeWidth={key === focusSeries ? 3 : 1}
            dot={key === focusSeries}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
```

## Dashboard Narrative Flow

| Principle          | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| Z-pattern reading  | Place most important content top-left, call-to-action bottom |
| Information funnel | KPIs at top → trends in middle → detail tables at bottom     |
| Consistent time    | All charts on a dashboard should share the same time range   |
| Visual grouping    | Related metrics share a row or card group                    |

```text
┌──────────────────────────────────────────────┐
│  KPI Cards (revenue, users, conversion, NPS) │  ← Scan first
├────────────────────┬─────────────────────────┤
│  Trend Line Chart  │  Breakdown Bar Chart    │  ← Understand trends
├────────────────────┴─────────────────────────┤
│  Detail Table with Filters                   │  ← Drill into specifics
└──────────────────────────────────────────────┘
```

KPI card pattern with trend indicator:

```tsx
type KPIProps = {
  label: string;
  value: string;
  change: number;
};

export function KPICard({ label, value, change }: KPIProps) {
  const isPositive = change >= 0;

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
      <p className={isPositive ? 'text-green-600' : 'text-red-600'}>
        {isPositive ? '↑' : '↓'} {Math.abs(change)}%
        <span className="text-gray-400"> vs last period</span>
      </p>
    </div>
  );
}
```

## Small Multiples

Compare the same chart across categories or time periods. Shared axes make comparison immediate.

```tsx
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer } from 'recharts';

type RegionData = {
  region: string;
  data: { month: string; revenue: number }[];
};

export function SmallMultiples({ regions }: { regions: RegionData[] }) {
  const globalMax = Math.max(
    ...regions.flatMap((r) => r.data.map((d) => d.revenue)),
  );

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {regions.map((region) => (
        <div key={region.region}>
          <h3 className="mb-2 text-sm font-semibold">{region.region}</h3>
          <ResponsiveContainer width="100%" height={150}>
            <LineChart data={region.data}>
              <XAxis dataKey="month" tick={false} />
              <YAxis domain={[0, globalMax]} hide />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#0066CC"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
}
```

Shared Y-axis domain (`globalMax`) ensures each panel uses the same scale for honest comparison.

## Edge Cases in Visualizations

### Empty State

```tsx
export function ChartEmptyState({
  message = 'No data available',
}: {
  message?: string;
}) {
  return (
    <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-dashed">
      <svg
        className="mb-2 h-12 w-12 text-gray-300"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" />
      </svg>
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  );
}
```

### Loading State

```tsx
export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div
      className="animate-pulse rounded-lg bg-gray-100"
      style={{ height }}
      role="status"
    >
      <span className="sr-only">Loading chart...</span>
    </div>
  );
}
```

### Error State

```tsx
export function ChartError({
  error,
  onRetry,
}: {
  error: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex h-64 flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50">
      <p className="text-sm text-red-600">{error}</p>
      {onRetry ? (
        <button
          onClick={onRetry}
          className="mt-2 text-sm text-red-600 underline"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}
```

### Conditional Rendering Pattern

```tsx
type ChartWrapperProps = {
  data: unknown[] | undefined;
  isLoading: boolean;
  error: string | null;
  onRetry?: () => void;
  children: React.ReactNode;
};

export function ChartWrapper({
  data,
  isLoading,
  error,
  onRetry,
  children,
}: ChartWrapperProps) {
  if (isLoading) return <ChartSkeleton />;
  if (error) return <ChartError error={error} onRetry={onRetry} />;
  if (!data?.length) return <ChartEmptyState />;
  return <>{children}</>;
}
```

## Accessibility in Storytelling

Charts must convey their narrative through text and structure, not just visuals.

| Technique                  | Implementation                                              |
| -------------------------- | ----------------------------------------------------------- |
| Descriptive title          | Chart title states the insight, not just the metric         |
| Text summary               | Add a sentence below the chart summarizing the key takeaway |
| Accessible label on SVG    | `<svg role="img" aria-label="...">`                         |
| Data table fallback        | Provide a hidden or expandable table with the raw data      |
| Pattern fills              | Supplement color with patterns for colorblind users         |
| Keyboard-navigable tooltip | Recharts `Tooltip` supports `cursor` for keyboard focus     |

```tsx
export function AccessibleChart({
  data,
  title,
  summary,
}: {
  data: { month: string; value: number }[];
  title: string;
  summary: string;
}) {
  return (
    <figure role="group" aria-label={title}>
      <figcaption>
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-gray-500">{summary}</p>
      </figcaption>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} role="img" aria-label={summary}>
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke="#0066CC" />
        </LineChart>
      </ResponsiveContainer>
      <details className="mt-2">
        <summary className="cursor-pointer text-sm text-blue-600">
          View data table
        </summary>
        <table className="mt-1 w-full text-sm">
          <thead>
            <tr>
              <th className="text-left">Month</th>
              <th className="text-right">Value</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.month}>
                <td>{row.month}</td>
                <td className="text-right">{row.value.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}
```
