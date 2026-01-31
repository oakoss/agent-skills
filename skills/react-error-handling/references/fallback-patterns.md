---
title: Fallback UI Patterns
description: Error state UI patterns, retry mechanisms, and graceful degradation strategies
tags:
  [
    fallback-ui,
    error-state,
    retry-button,
    graceful-degradation,
    user-experience,
  ]
---

# Fallback UI Patterns

## Minimal Fallback

```tsx
function MinimalError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="p-4 text-center">
      <p className="text-muted-foreground">Something went wrong</p>
      <button onClick={resetErrorBoundary} className="mt-2 underline">
        Try again
      </button>
    </div>
  );
}
```

Use when:

- Space is limited (sidebar, card)
- Error context is clear from UI location
- Technical details not helpful to user

## Detailed Fallback with Icon

```tsx
import { AlertCircle } from 'lucide-react';
import { type FallbackProps } from 'react-error-boundary';

function DetailedError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="flex flex-col items-center gap-4 p-8">
      <AlertCircle className="size-12 text-destructive" />
      <div className="text-center">
        <h2 className="text-lg font-semibold">Something went wrong</h2>
        <p className="text-sm text-muted-foreground">{error.message}</p>
      </div>
      <button
        onClick={resetErrorBoundary}
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
      >
        Try again
      </button>
    </div>
  );
}
```

## Card-Based Error

```tsx
import { AlertTriangle } from 'lucide-react';
import { type FallbackProps } from 'react-error-boundary';

function CardError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="mx-auto max-w-md rounded-lg border border-destructive/50 bg-card p-6">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle className="size-5 text-destructive" />
        <h2 className="text-lg font-semibold">Error</h2>
      </div>
      <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>
      <div className="flex gap-2">
        <button
          onClick={resetErrorBoundary}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Retry
        </button>
        <button
          onClick={() => (window.location.href = '/')}
          className="rounded-md border px-4 py-2 text-sm"
        >
          Go home
        </button>
      </div>
    </div>
  );
}
```

## Development vs Production Fallback

```tsx
import { type FallbackProps } from 'react-error-boundary';

function EnvironmentAwareError({ error, resetErrorBoundary }: FallbackProps) {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="p-6">
      <h2 className="mb-4 text-lg font-semibold text-destructive">
        Application Error
      </h2>
      <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>

      {isDevelopment && (
        <details className="mb-4">
          <summary className="cursor-pointer text-sm font-medium">
            Stack trace
          </summary>
          <pre className="mt-2 overflow-auto rounded bg-muted p-4 text-xs">
            {error.stack}
          </pre>
        </details>
      )}

      <button
        onClick={resetErrorBoundary}
        className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
      >
        Try again
      </button>
    </div>
  );
}
```

## Full-Page Error

```tsx
import { RefreshCw, Home } from 'lucide-react';
import { type FallbackProps } from 'react-error-boundary';

function FullPageError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="max-w-md space-y-6 text-center">
        <div className="mx-auto flex size-20 items-center justify-center rounded-full bg-destructive/10">
          <RefreshCw className="size-10 text-destructive" />
        </div>
        <div>
          <h1 className="mb-2 text-2xl font-bold">Oops! Something broke</h1>
          <p className="text-muted-foreground">
            {error.message || 'An unexpected error occurred'}
          </p>
        </div>
        <div className="flex justify-center gap-4">
          <button
            onClick={resetErrorBoundary}
            className="flex items-center gap-2 rounded-md bg-primary px-6 py-3 text-primary-foreground"
          >
            <RefreshCw className="size-4" />
            Try again
          </button>
          <button
            onClick={() => (window.location.href = '/')}
            className="flex items-center gap-2 rounded-md border px-6 py-3"
          >
            <Home className="size-4" />
            Go home
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Section-Specific Fallback

```tsx
import { type FallbackProps } from 'react-error-boundary';

function SidebarError({ resetErrorBoundary }: FallbackProps) {
  return (
    <aside className="w-64 border-r p-4">
      <div className="rounded-md border border-destructive/50 bg-destructive/5 p-3">
        <p className="mb-2 text-sm font-medium">Sidebar failed to load</p>
        <button onClick={resetErrorBoundary} className="text-xs underline">
          Retry
        </button>
      </div>
    </aside>
  );
}

function MainContentError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <main className="flex-1 p-8">
      <div className="rounded-lg border-2 border-dashed border-destructive/50 p-12 text-center">
        <h2 className="mb-2 text-lg font-semibold">
          Failed to load main content
        </h2>
        <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>
        <button
          onClick={resetErrorBoundary}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Reload content
        </button>
      </div>
    </main>
  );
}
```

## Retry with Backoff Strategy

```tsx
import { useState } from 'react';
import { type FallbackProps } from 'react-error-boundary';

function RetryableError({ error, resetErrorBoundary }: FallbackProps) {
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    setIsRetrying(true);
    setRetryCount((c) => c + 1);

    const delay = Math.min(1000 * 2 ** retryCount, 10000);
    await new Promise((resolve) => setTimeout(resolve, delay));

    setIsRetrying(false);
    resetErrorBoundary();
  };

  return (
    <div className="rounded-lg border p-6">
      <h2 className="mb-2 text-lg font-semibold text-destructive">
        Error occurred
      </h2>
      <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>
      <div className="flex items-center gap-4">
        <button
          onClick={handleRetry}
          disabled={isRetrying}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground disabled:opacity-50"
        >
          {isRetrying
            ? 'Retrying...'
            : `Retry${retryCount > 0 ? ` (${retryCount})` : ''}`}
        </button>
        {retryCount > 2 && (
          <p className="text-xs text-muted-foreground">
            If this keeps happening, try refreshing the page
          </p>
        )}
      </div>
    </div>
  );
}
```

## Contextual Error Messages

```tsx
import { type FallbackProps } from 'react-error-boundary';

type ContextualErrorProps = FallbackProps & {
  context: 'sidebar' | 'content' | 'modal' | 'page';
};

const ERROR_CONTEXT = {
  sidebar: {
    title: 'Sidebar Error',
    description: 'Navigation failed to load',
    action: 'Reload sidebar',
  },
  content: {
    title: 'Content Error',
    description: 'Main content failed to load',
    action: 'Reload content',
  },
  modal: {
    title: 'Modal Error',
    description: 'This dialog encountered an error',
    action: 'Close and retry',
  },
  page: {
    title: 'Page Error',
    description: 'This page failed to load',
    action: 'Reload page',
  },
} as const;

function ContextualError({
  error,
  resetErrorBoundary,
  context,
}: ContextualErrorProps) {
  const { title, description, action } = ERROR_CONTEXT[context];

  return (
    <div className="rounded-md border border-destructive/50 bg-destructive/5 p-4">
      <h3 className="mb-1 font-semibold text-destructive">{title}</h3>
      <p className="mb-2 text-sm text-muted-foreground">{description}</p>
      <p className="mb-3 text-xs text-muted-foreground/80">{error.message}</p>
      <button
        onClick={resetErrorBoundary}
        className="rounded-md bg-destructive px-3 py-1.5 text-sm text-destructive-foreground"
      >
        {action}
      </button>
    </div>
  );
}

export default ContextualError;
```

## Toast Notification Pattern

```tsx
import { useEffect } from 'react';
import { toast } from 'sonner';
import { type FallbackProps } from 'react-error-boundary';

function ToastError({ error, resetErrorBoundary }: FallbackProps) {
  useEffect(() => {
    toast.error('An error occurred', {
      description: error.message,
      action: {
        label: 'Retry',
        onClick: resetErrorBoundary,
      },
    });
  }, [error.message, resetErrorBoundary]);

  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <p className="mb-2 text-sm text-muted-foreground">
          Something went wrong
        </p>
        <button onClick={resetErrorBoundary} className="text-sm underline">
          Try again
        </button>
      </div>
    </div>
  );
}
```

## Graceful Degradation Fallback

```tsx
import { type FallbackProps } from 'react-error-boundary';

function GracefulFallback({ resetErrorBoundary }: FallbackProps) {
  return (
    <div className="rounded-md border border-dashed p-6 text-center">
      <p className="mb-2 text-sm text-muted-foreground">
        This feature is temporarily unavailable
      </p>
      <button onClick={resetErrorBoundary} className="text-xs underline">
        Reload
      </button>
    </div>
  );
}
```

Use for:

- Non-critical UI sections
- Optional features
- Progressive enhancement scenarios

## Multiple Action Buttons

```tsx
import { type FallbackProps } from 'react-error-boundary';

function MultiActionError({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="rounded-lg border p-6">
      <h2 className="mb-2 text-lg font-semibold">Error Loading Data</h2>
      <p className="mb-4 text-sm text-muted-foreground">{error.message}</p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={resetErrorBoundary}
          className="rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Try again
        </button>
        <button
          onClick={() => window.location.reload()}
          className="rounded-md border px-4 py-2 text-sm"
        >
          Reload page
        </button>
        <button
          onClick={() => (window.location.href = '/')}
          className="rounded-md border px-4 py-2 text-sm"
        >
          Go home
        </button>
        <a href="/support" className="rounded-md border px-4 py-2 text-sm">
          Contact support
        </a>
      </div>
    </div>
  );
}
```

## Empty State Fallback

```tsx
import { FileQuestion } from 'lucide-react';
import { type FallbackProps } from 'react-error-boundary';

function EmptyStateError({ resetErrorBoundary }: FallbackProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <FileQuestion className="mb-4 size-16 text-muted-foreground/50" />
      <h3 className="mb-2 text-lg font-medium">Unable to load content</h3>
      <p className="mb-4 text-sm text-muted-foreground">
        We couldn't load this section. Please try again.
      </p>
      <button
        onClick={resetErrorBoundary}
        className="rounded-md bg-primary px-6 py-2 text-sm text-primary-foreground"
      >
        Reload
      </button>
    </div>
  );
}
```

## Loading Skeleton Fallback

```tsx
import { type FallbackProps } from 'react-error-boundary';

function SkeletonFallback({ resetErrorBoundary }: FallbackProps) {
  return (
    <div className="space-y-3">
      <div className="h-4 animate-pulse rounded bg-muted" />
      <div className="h-4 w-3/4 animate-pulse rounded bg-muted" />
      <div className="h-4 w-1/2 animate-pulse rounded bg-muted" />
      <button
        onClick={resetErrorBoundary}
        className="mt-4 rounded-md border px-4 py-2 text-sm"
      >
        Retry loading
      </button>
    </div>
  );
}
```

Maintains layout shape while providing retry option.
