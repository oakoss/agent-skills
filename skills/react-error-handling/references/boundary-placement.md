---
title: Error Boundary Placement Strategies
description: Where to place error boundaries for optimal granularity and user experience
tags:
  [
    boundary-placement,
    granularity,
    error-isolation,
    nested-boundaries,
    architecture,
  ]
---

# Error Boundary Placement Strategies

## Granularity Principles

Error boundaries should be placed at meaningful UI sections where an error state makes sense to the user.

**Too coarse:**

```tsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

A single error anywhere crashes the entire app.

**Too granular:**

```tsx
<ErrorBoundary>
  <Avatar />
</ErrorBoundary>
<ErrorBoundary>
  <UserName />
</ErrorBoundary>
<ErrorBoundary>
  <UserBio />
</ErrorBoundary>
```

Excessive boilerplate, confusing error states.

**Right balance:**

```tsx
<ErrorBoundary>
  <UserCard>
    <Avatar />
    <UserName />
    <UserBio />
  </UserCard>
</ErrorBoundary>
```

Logical grouping that makes sense to fail as a unit.

## Application-Level Boundary

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function RootErrorFallback({ error }: FallbackProps) {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="max-w-md text-center">
        <h1 className="mb-4 text-2xl font-bold">Something went wrong</h1>
        <p className="mb-4 text-muted-foreground">{error.message}</p>
        <button
          onClick={() => window.location.reload()}
          className="rounded-md bg-primary px-6 py-3 text-primary-foreground"
        >
          Reload application
        </button>
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary FallbackComponent={RootErrorFallback}>
      <Router />
    </ErrorBoundary>
  );
}
```

Use for:

- Catastrophic failures
- Last resort fallback
- Errors in core app logic

## Route-Level Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useLocation } from '@tanstack/react-router';

function RouteErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="container py-12">
      <h1 className="mb-4 text-2xl font-bold">Page Error</h1>
      <p className="mb-4">{error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function Router() {
  const location = useLocation();

  return (
    <ErrorBoundary
      FallbackComponent={RouteErrorFallback}
      resetKeys={[location.pathname]}
    >
      <Routes />
    </ErrorBoundary>
  );
}
```

Use for:

- Per-route error isolation
- Route-specific error messages
- Automatic reset on navigation

## Layout Section Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function Layout() {
  return (
    <div className="flex min-h-screen">
      <ErrorBoundary FallbackComponent={SidebarError}>
        <Sidebar />
      </ErrorBoundary>

      <div className="flex-1">
        <ErrorBoundary FallbackComponent={HeaderError}>
          <Header />
        </ErrorBoundary>

        <ErrorBoundary FallbackComponent={MainError}>
          <main>
            <Outlet />
          </main>
        </ErrorBoundary>
      </div>
    </div>
  );
}

function SidebarError() {
  return (
    <aside className="w-64 border-r p-4">
      <div className="rounded border border-destructive/50 p-3">
        <p className="text-sm">Navigation unavailable</p>
      </div>
    </aside>
  );
}
```

Benefits:

- Sidebar errors don't crash main content
- Header errors don't crash sidebar
- Layout structure preserved

## Component-Level Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function Dashboard() {
  return (
    <div className="grid grid-cols-3 gap-4">
      <ErrorBoundary FallbackComponent={WidgetError}>
        <StatsWidget />
      </ErrorBoundary>

      <ErrorBoundary FallbackComponent={WidgetError}>
        <ChartWidget />
      </ErrorBoundary>

      <ErrorBoundary FallbackComponent={WidgetError}>
        <ActivityWidget />
      </ErrorBoundary>
    </div>
  );
}

function WidgetError() {
  return (
    <div className="rounded border border-dashed p-4 text-center">
      <p className="text-sm text-muted-foreground">Widget failed to load</p>
    </div>
  );
}
```

Use for:

- Dashboard widgets
- Card components
- Independent UI sections

## Modal/Dialog Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { Dialog, DialogContent } from '@/components/ui/dialog';

function UserDialog({ userId, open, onClose }: UserDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <ErrorBoundary FallbackComponent={DialogError} resetKeys={[userId]}>
          <UserDetails userId={userId} />
        </ErrorBoundary>
      </DialogContent>
    </Dialog>
  );
}

function DialogError({ error }: FallbackProps) {
  return (
    <div className="p-4 text-center">
      <p className="text-destructive">Failed to load user details</p>
      <p className="text-sm text-muted-foreground">{error.message}</p>
    </div>
  );
}
```

Benefits:

- Modal errors don't crash parent page
- User can close modal to recover
- Automatic reset on user switch

## List Item Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function MessageList({ messages }: { messages: Message[] }) {
  return (
    <div className="space-y-2">
      {messages.map((message) => (
        <ErrorBoundary
          key={message.id}
          fallback={
            <div className="rounded border border-dashed p-2 text-xs text-muted-foreground">
              Message failed to render
            </div>
          }
        >
          <MessageItem message={message} />
        </ErrorBoundary>
      ))}
    </div>
  );
}
```

Use for:

- Long lists where one item shouldn't crash all
- Messaging apps
- Feed items
- Comment threads

## Data Table Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function DataTable({ data }: { data: RowData[] }) {
  return (
    <ErrorBoundary FallbackComponent={TableError}>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <ErrorBoundary
              key={row.id}
              fallback={
                <tr>
                  <td
                    colSpan={3}
                    className="text-center text-xs text-muted-foreground"
                  >
                    Failed to render row
                  </td>
                </tr>
              }
            >
              <TableRow data={row} />
            </ErrorBoundary>
          ))}
        </tbody>
      </table>
    </ErrorBoundary>
  );
}

function TableError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="rounded border p-8 text-center">
      <p className="mb-2 font-medium">Table failed to load</p>
      <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>
      <button onClick={resetErrorBoundary}>Reload table</button>
    </div>
  );
}
```

Two-level strategy:

- Table-level boundary for structural errors
- Row-level boundaries for data errors

## Form Section Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function CheckoutForm() {
  return (
    <form className="space-y-6">
      <ErrorBoundary FallbackComponent={SectionError}>
        <ShippingSection />
      </ErrorBoundary>
      <ErrorBoundary FallbackComponent={SectionError}>
        <PaymentSection />
      </ErrorBoundary>
      <button type="submit">Complete order</button>
    </form>
  );
}
```

Allows partial form failures without losing all progress.

## Lazy-Loaded Component Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { lazy, Suspense } from 'react';

const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  return (
    <ErrorBoundary
      fallbackRender={({ resetErrorBoundary }) => (
        <div className="rounded border p-4">
          <p>Chart failed to load</p>
          <button onClick={resetErrorBoundary}>Retry</button>
        </div>
      )}
    >
      <Suspense fallback={<div>Loading chart...</div>}>
        <HeavyChart />
      </Suspense>
    </ErrorBoundary>
  );
}
```

Catches both:

- Code-splitting errors (network failures)
- Runtime errors in lazy component

## Nested Boundaries with Context

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { createContext, useContext } from 'react';

const ErrorLevelContext = createContext<'page' | 'section'>('page');

function Page() {
  return (
    <ErrorLevelContext.Provider value="page">
      <ErrorBoundary FallbackComponent={PageError}>
        <PageContent />
      </ErrorBoundary>
    </ErrorLevelContext.Provider>
  );
}
```

Track error context for better debugging and logging.

## Reusable Boundary Wrapper

```tsx
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary';

type BoundaryLevel = 'page' | 'section' | 'widget';

const BOUNDARY_CONFIG: Record<
  BoundaryLevel,
  { Fallback: React.ComponentType<FallbackProps> }
> = {
  page: { Fallback: PageError },
  section: { Fallback: SectionError },
  widget: { Fallback: WidgetError },
};

function BoundaryWrapper({
  level,
  children,
}: {
  level: BoundaryLevel;
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary FallbackComponent={BOUNDARY_CONFIG[level].Fallback}>
      {children}
    </ErrorBoundary>
  );
}
```

## Decision Matrix

| UI Element       | Boundary Level | Fallback Type        | Reset Strategy      |
| ---------------- | -------------- | -------------------- | ------------------- |
| Entire app       | Root           | Full-page            | Reload app          |
| Route/page       | Route          | Page-level message   | Reset on navigation |
| Layout section   | Section        | Section placeholder  | Manual retry        |
| Dashboard widget | Component      | Empty state          | Manual retry        |
| List item        | Item           | Minimal placeholder  | Continue rendering  |
| Modal/dialog     | Component      | Dialog error message | Close to recover    |
| Form section     | Section        | Section error        | Allow partial use   |
| Lazy component   | Component      | Loading skeleton     | Retry load          |
| Data table       | Table + Row    | Two-level fallback   | Retry or skip row   |

## Testing Boundary Placement

```tsx
import { render, screen } from '@testing-library/react';

const ThrowError = () => {
  throw new Error('Test error');
};

it('isolates sidebar errors', () => {
  render(
    <div>
      <ErrorBoundary fallback={<div>Sidebar error</div>}>
        <ThrowError />
      </ErrorBoundary>
      <div>Main content</div>
    </div>,
  );

  expect(screen.getByText('Sidebar error')).toBeInTheDocument();
  expect(screen.getByText('Main content')).toBeInTheDocument();
});
```
