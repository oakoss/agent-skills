---
title: react-error-boundary Library
description: Using the react-error-boundary package for function component error boundaries
tags:
  [
    react-error-boundary,
    ErrorBoundary,
    useErrorBoundary,
    withErrorBoundary,
    resetKeys,
    FallbackComponent,
  ]
---

# react-error-boundary Library

## Installation

```bash
pnpm add react-error-boundary
```

## Basic Usage

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary fallback={<div>Something went wrong</div>}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## FallbackComponent Pattern

```tsx
import { ErrorBoundary, type FallbackProps } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <pre style={{ color: 'red' }}>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

## fallbackRender Pattern

```tsx
import { ErrorBoundary } from 'react-error-boundary';

<ErrorBoundary
  fallbackRender={({ error, resetErrorBoundary }) => (
    <div role="alert">
      <p>Error: {error.message}</p>
      <button onClick={resetErrorBoundary}>Reset</button>
    </div>
  )}
>
  <MyComponent />
</ErrorBoundary>;
```

## Error Logging with onError

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function logErrorToService(error: Error, info: { componentStack: string }) {
  console.error('Logging error:', error, info.componentStack);
}

<ErrorBoundary FallbackComponent={ErrorFallback} onError={logErrorToService}>
  <MyComponent />
</ErrorBoundary>;
```

## Automatic Reset with resetKeys

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function UserProfile() {
  const [userId, setUserId] = useState('123');

  return (
    <ErrorBoundary FallbackComponent={ErrorFallback} resetKeys={[userId]}>
      <Profile userId={userId} />
    </ErrorBoundary>
  );
}
```

When `userId` changes, the error boundary automatically resets. This pattern is ideal for:

- Route parameter changes
- User switching
- Filter/search state changes
- Any dependency that should trigger a fresh render attempt

## Manual Reset with onReset

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);

  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => setCount(0)}
      resetKeys={[count]}
    >
      <Counter count={count} setCount={setCount} />
    </ErrorBoundary>
  );
}
```

## useErrorBoundary Hook

Manually trigger the error boundary from inside a component:

```tsx
import { useErrorBoundary } from 'react-error-boundary';

function Greeting() {
  const { showBoundary } = useErrorBoundary();

  useEffect(() => {
    fetch('/api/user')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch user');
        return res.json();
      })
      .catch(showBoundary);
  }, [showBoundary]);

  return <div>Hello</div>;
}
```

Reset from inside component:

```tsx
import { useErrorBoundary } from 'react-error-boundary';

function ErrorComponent() {
  const { resetBoundary } = useErrorBoundary();

  return (
    <div>
      <p>An error occurred</p>
      <button onClick={resetBoundary}>Try again</button>
    </div>
  );
}
```

## withErrorBoundary HOC

```tsx
import { withErrorBoundary } from 'react-error-boundary';

function MyComponent() {
  return <div>Content</div>;
}

export default withErrorBoundary(MyComponent, {
  FallbackComponent: ErrorFallback,
  onError: (error, info) => {
    console.error('Error:', error, info.componentStack);
  },
});
```

## Nested Error Boundaries

```tsx
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary FallbackComponent={PageError}>
      <Header />
      <main>
        <ErrorBoundary FallbackComponent={SidebarError}>
          <Sidebar />
        </ErrorBoundary>
        <ErrorBoundary FallbackComponent={ContentError}>
          <MainContent />
        </ErrorBoundary>
      </main>
      <Footer />
    </ErrorBoundary>
  );
}
```

## Next.js App Router Integration

```tsx
'use client';

import { ErrorBoundary } from 'react-error-boundary';

export default function ErrorBoundaryWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary
      fallbackRender={({ error }) => (
        <div>
          <h2>Something went wrong</h2>
          <p>{error.message}</p>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  );
}
```

In layout.tsx:

```tsx
import ErrorBoundaryWrapper from '@/components/error-boundary-wrapper';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ErrorBoundaryWrapper>{children}</ErrorBoundaryWrapper>
      </body>
    </html>
  );
}
```

## Combining with TanStack Query

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { QueryErrorResetBoundary } from '@tanstack/react-query';

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

This pattern:

- Resets both error boundary and query cache
- Allows failed queries to retry on reset
- Prevents stale error states in cache

## TypeScript Types

```tsx
import { type FallbackProps } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div>
      <p>{error.message}</p>
      <button onClick={resetErrorBoundary}>Reset</button>
    </div>
  );
}
```

FallbackProps type:

```tsx
type FallbackProps = {
  error: Error;
  resetErrorBoundary: () => void;
};
```

## Production Error Reporting

```tsx
import { ErrorBoundary } from 'react-error-boundary';
import * as Sentry from '@sentry/react';

<ErrorBoundary
  FallbackComponent={ErrorFallback}
  onError={(error, info) => {
    if (process.env.NODE_ENV === 'production') {
      Sentry.captureException(error, {
        contexts: {
          react: {
            componentStack: info.componentStack,
          },
        },
      });
    }
  }}
>
  <App />
</ErrorBoundary>;
```

## Testing with react-error-boundary

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ErrorBoundary } from 'react-error-boundary';
import { describe, it, expect, vi } from 'vitest';

const ThrowError = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary', () => {
  it('renders fallback on error', () => {
    const consoleError = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Error boundary</div>}>
        <ThrowError />
      </ErrorBoundary>,
    );

    expect(screen.getByText('Error boundary')).toBeInTheDocument();
    consoleError.mockRestore();
  });

  it('resets on button click', async () => {
    const user = userEvent.setup();
    let shouldThrow = true;

    const Throws = () => {
      if (shouldThrow) throw new Error('Error');
      return <div>Success</div>;
    };

    const consoleError = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    render(
      <ErrorBoundary
        fallbackRender={({ resetErrorBoundary }) => (
          <div>
            <p>Error occurred</p>
            <button
              onClick={() => {
                shouldThrow = false;
                resetErrorBoundary();
              }}
            >
              Reset
            </button>
          </div>
        )}
      >
        <Throws />
      </ErrorBoundary>,
    );

    expect(screen.getByText('Error occurred')).toBeInTheDocument();
    await user.click(screen.getByText('Reset'));
    expect(screen.getByText('Success')).toBeInTheDocument();

    consoleError.mockRestore();
  });
});
```
