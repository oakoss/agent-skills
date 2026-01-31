---
title: Performance and Errors
description: React memoization strategies, Next.js image and font optimization, code splitting, Suspense streaming patterns, and error boundary implementation
tags:
  [
    performance,
    memoization,
    error-boundary,
    code-splitting,
    suspense,
    streaming,
    nextjs-optimization,
  ]
---

# Performance and Errors

## When to Memoize

Memoization adds complexity. Only use it when you have measured a performance problem or when a component is demonstrably expensive to re-render.

| Tool          | Purpose                            | Use When                                                |
| ------------- | ---------------------------------- | ------------------------------------------------------- |
| `useMemo`     | Cache computed values              | Expensive calculations (sorting, filtering large lists) |
| `useCallback` | Stable function reference          | Passing callbacks to memoized children                  |
| `memo()`      | Skip re-renders if props unchanged | Component renders frequently with same props            |

### useMemo for Expensive Computations

```tsx
function DataTable({ data, sortField }: { data: Row[]; sortField: string }) {
  const sortedData = useMemo(
    () => [...data].sort((a, b) => a[sortField].localeCompare(b[sortField])),
    [data, sortField],
  );

  return (
    <table>
      <tbody>
        {sortedData.map((row) => (
          <tr key={row.id}>
            <td>{row.name}</td>
            <td>{row.email}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

### memo for Expensive Children

```tsx
const ExpensiveChart = memo(function ExpensiveChart({
  data,
  onSelect,
}: {
  data: ChartData[];
  onSelect: (point: ChartData) => void;
}) {
  return <canvas>{/* expensive rendering logic */}</canvas>;
});

function Dashboard({ data }: { data: ChartData[] }) {
  const handleSelect = useCallback((point: ChartData) => {
    console.log('Selected:', point);
  }, []);

  return <ExpensiveChart data={data} onSelect={handleSelect} />;
}
```

## Code Splitting

### React.lazy (Vite/React)

```tsx
import { lazy, Suspense } from 'react';

const HeavyEditor = lazy(() => import('./heavy-editor'));

function EditorPage() {
  return (
    <Suspense fallback={<Skeleton className="h-96" />}>
      <HeavyEditor />
    </Suspense>
  );
}
```

### next/dynamic (Next.js)

```tsx
import dynamic from 'next/dynamic';

const RichTextEditor = dynamic(() => import('@/components/rich-text-editor'), {
  loading: () => <Skeleton className="h-64" />,
  ssr: false,
});

export default function EditPage() {
  return <RichTextEditor />;
}
```

### Route-Level Splitting

Next.js App Router automatically code-splits at the page level. Each `page.tsx` gets its own bundle.

## Next.js Optimization

### Image Optimization

```tsx
import Image from 'next/image';

export function ProductImage({ product }: { product: Product }) {
  return (
    <Image
      src={product.imageUrl}
      alt={product.name}
      width={600}
      height={400}
      priority={false}
      placeholder="blur"
      blurDataURL={product.blurHash}
      className="rounded-lg object-cover"
      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
    />
  );
}
```

Use `priority` only for above-the-fold images (hero images, LCP elements). Provide `sizes` to serve appropriately sized images at each breakpoint.

### Font Optimization

```tsx
// app/layout.tsx
import { Inter, JetBrains_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

## Suspense Streaming

Wrap independent data sections in `<Suspense>` boundaries. Each section streams to the client as its data resolves, avoiding waterfall loading.

```tsx
import { Suspense } from 'react';

export default function DashboardPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <RevenueChart />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />
      </Suspense>
      <Suspense fallback={<ListSkeleton />}>
        <TopCustomers />
      </Suspense>
    </div>
  );
}

async function StatsPanel() {
  const stats = await fetchStats();
  return (
    <div className="grid grid-cols-2 gap-4">
      {stats.map((stat) => (
        <div key={stat.label} className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">{stat.label}</p>
          <p className="text-2xl font-bold">{stat.value}</p>
        </div>
      ))}
    </div>
  );
}
```

### Loading UI Convention

Next.js App Router supports `loading.tsx` files for automatic Suspense wrapping at the route level.

```tsx
// app/dashboard/loading.tsx
export default function Loading() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-48" />
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-48" />
        <Skeleton className="h-48" />
      </div>
    </div>
  );
}
```

## Error Boundaries

### Custom Error Boundary Component

```tsx
'use client';

import { Component, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
            <h3 className="font-medium text-destructive">
              Something went wrong
            </h3>
            <p className="text-sm text-muted-foreground">
              {this.state.error?.message}
            </p>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
```

### Next.js Route Error Handling

```tsx
// app/dashboard/error.tsx
'use client';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-16">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground">{error.message}</p>
      <button
        onClick={reset}
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
      >
        Try again
      </button>
    </div>
  );
}
```

### Not Found Handling

```tsx
// app/users/[id]/not-found.tsx
export default function UserNotFound() {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <h2 className="text-xl font-semibold">User not found</h2>
      <p className="text-muted-foreground">
        The user you are looking for does not exist.
      </p>
    </div>
  );
}
```

```tsx
// app/users/[id]/page.tsx
import { notFound } from 'next/navigation';

export default async function UserPage({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  if (!user) notFound();

  return <UserProfile user={user} />;
}
```

## Strategic Error Boundary Placement

Wrap feature sections independently so a failure in one section does not crash the entire page.

```tsx
export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <ErrorBoundary fallback={<p>Failed to load stats</p>}>
        <Suspense fallback={<StatsSkeleton />}>
          <StatsPanel />
        </Suspense>
      </ErrorBoundary>
      <ErrorBoundary fallback={<p>Failed to load chart</p>}>
        <Suspense fallback={<ChartSkeleton />}>
          <RevenueChart />
        </Suspense>
      </ErrorBoundary>
    </div>
  );
}
```
