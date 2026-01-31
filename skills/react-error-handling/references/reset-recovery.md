---
title: Reset and Recovery Patterns
description: Error recovery mechanisms, reset strategies, and retry patterns
tags: [error-recovery, reset, retry, resetKeys, onReset, error-boundary-reset]
---

# Reset and Recovery Patterns

## Manual Reset with Button

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

<ErrorBoundary FallbackComponent={ErrorFallback}>
  <MyComponent />
</ErrorBoundary>;
```

## Automatic Reset on Prop Change

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function UserDashboard() {
  const [userId, setUserId] = useState('user-123');

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} resetKeys={[userId]}>
      <Dashboard userId={userId} />
    </ErrorBoundary>
  );
}
```

When `userId` changes, the error boundary automatically resets and re-renders children. This pattern is ideal for:

- Route parameter changes (id, slug)
- Active filter changes
- User switching
- Search query changes

## Reset with State Cleanup

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function DataView() {
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState({});

  const handleReset = () => {
    setData(null);
    setFilters({});
  };

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={handleReset}>
      <DataTable data={data} filters={filters} />
    </ErrorBoundary>
  );
}
```

## Combining resetKeys and onReset

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function SearchResults() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(1);

  const handleReset = () => {
    setPage(1);
  };

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      resetKeys={[query]}
      onReset={handleReset}
    >
      <Results query={query} page={page} />
    </ErrorBoundary>
  );
}
```

When `query` changes:

1. Error boundary resets automatically
2. `onReset` runs, resetting `page` to 1

## useErrorBoundary for Manual Trigger

```tsx
import { useErrorBoundary } from 'react-error-boundary';
import { useEffect } from 'react';

function DataFetcher() {
  const { showBoundary } = useErrorBoundary();

  useEffect(() => {
    fetchData().then(processData).catch(showBoundary);
  }, [showBoundary]);

  return <div>Loading...</div>;
}
```

This pattern propagates async errors to the nearest error boundary.

## Reset with TanStack Query

```tsx
import { QueryErrorResetBoundary } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary onReset={reset} FallbackComponent={ErrorFallback}>
          <MyComponent />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}
```

Resetting the error boundary also clears TanStack Query error state, allowing failed queries to retry.

## Retry with Exponential Backoff

```tsx
import { useState, useCallback } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

function RetryBoundary({ children }: { children: React.ReactNode }) {
  const [retryCount, setRetryCount] = useState(0);

  const handleReset = useCallback(() => {
    setRetryCount((c) => c + 1);
  }, []);

  return (
    <ErrorBoundary
      onReset={handleReset}
      resetKeys={[retryCount]}
      fallbackRender={({ error, resetErrorBoundary }) => (
        <RetryFallback
          error={error}
          retryCount={retryCount}
          onRetry={resetErrorBoundary}
        />
      )}
    >
      {children}
    </ErrorBoundary>
  );
}

function RetryFallback({
  error,
  retryCount,
  onRetry,
}: {
  error: Error;
  retryCount: number;
  onRetry: () => void;
}) {
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    const delay = Math.min(1000 * 2 ** retryCount, 10000);
    await new Promise((resolve) => setTimeout(resolve, delay));
    setIsRetrying(false);
    onRetry();
  };

  return (
    <div>
      <p>Error: {error.message}</p>
      <p>Attempts: {retryCount}</p>
      <button onClick={handleRetry} disabled={isRetrying}>
        {isRetrying ? 'Retrying...' : 'Retry'}
      </button>
    </div>
  );
}
```

## Reset on Route Change

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useLocation } from '@tanstack/react-router';

function RouteErrorBoundary({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      resetKeys={[location.pathname]}
    >
      {children}
    </ErrorBoundary>
  );
}
```

Error boundary automatically resets when navigating to a different route.

## Conditional Reset Based on Error Type

```tsx
import { ErrorBoundary } from 'react-error-boundary';

class NetworkError extends Error {
  name = 'NetworkError';
}

class ValidationError extends Error {
  name = 'ValidationError';
}

function SmartErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  const canRetry = error instanceof NetworkError;

  return (
    <div>
      <h2>{error.name}</h2>
      <p>{error.message}</p>
      {canRetry ? (
        <button onClick={resetErrorBoundary}>Retry</button>
      ) : (
        <button onClick={() => (window.location.href = '/')}>Go home</button>
      )}
    </div>
  );
}

<ErrorBoundary FallbackComponent={SmartErrorFallback}>
  <MyComponent />
</ErrorBoundary>;
```

## Reset with Form State

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function FormWithErrorBoundary() {
  const [formData, setFormData] = useState({ name: '', email: '' });

  const handleReset = () => {
    setFormData({ name: '', email: '' });
  };

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={handleReset}>
      <Form data={formData} onChange={setFormData} />
    </ErrorBoundary>
  );
}
```

## Global Reset Boundary

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  const handleReset = () => {
    window.location.href = '/';
  };

  return (
    <ErrorBoundary
      fallbackRender={({ error }) => (
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h1>Application Error</h1>
            <p>{error.message}</p>
            <button onClick={handleReset}>Restart Application</button>
          </div>
        </div>
      )}
    >
      <Router />
    </ErrorBoundary>
  );
}
```

## Nested Reset Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function App() {
  const [sidebarKey, setSidebarKey] = useState(0);
  const [contentKey, setContentKey] = useState(0);

  return (
    <div className="flex">
      <ErrorBoundary
        FallbackComponent={SidebarError}
        resetKeys={[sidebarKey]}
        onReset={() => setSidebarKey((k) => k + 1)}
      >
        <Sidebar />
      </ErrorBoundary>

      <ErrorBoundary
        FallbackComponent={ContentError}
        resetKeys={[contentKey]}
        onReset={() => setContentKey((k) => k + 1)}
      >
        <MainContent />
      </ErrorBoundary>
    </div>
  );
}
```

Each section can fail and recover independently.

## Reset with Data Refresh

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useQueryClient } from '@tanstack/react-query';

function DataView() {
  const queryClient = useQueryClient();

  const handleReset = () => {
    queryClient.invalidateQueries({ queryKey: ['data'] });
  };

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} onReset={handleReset}>
      <DataTable />
    </ErrorBoundary>
  );
}
```

## Reset with Loading State

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState, useTransition } from 'react';

function App() {
  const [isPending, startTransition] = useTransition();

  const handleReset = () => {
    startTransition(() => {
      window.location.reload();
    });
  };

  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <div>
          <p>Error: {error.message}</p>
          <button onClick={handleReset} disabled={isPending}>
            {isPending ? 'Reloading...' : 'Reload'}
          </button>
        </div>
      )}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## Preventing Error Loops

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function SafeErrorBoundary({ children }: { children: React.ReactNode }) {
  const [errorCount, setErrorCount] = useState(0);

  const handleReset = () => {
    setErrorCount((c) => c + 1);
  };

  if (errorCount > 3) {
    return (
      <div>
        <h2>Too many errors</h2>
        <p>Please refresh the page or contact support.</p>
        <button onClick={() => window.location.reload()}>Refresh page</button>
      </div>
    );
  }

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      resetKeys={[errorCount]}
      onReset={handleReset}
    >
      {children}
    </ErrorBoundary>
  );
}
```

After 3 errors, stop allowing resets to prevent infinite error loops.

## Reset with Analytics

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { trackEvent } from './analytics';

function App() {
  const handleReset = () => {
    trackEvent('error_boundary_reset', {
      timestamp: Date.now(),
    });
  };

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={handleReset}
      onError={(error) => {
        trackEvent('error_boundary_triggered', {
          error: error.message,
          timestamp: Date.now(),
        });
      }}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```
