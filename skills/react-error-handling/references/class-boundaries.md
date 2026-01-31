---
title: Class-Based Error Boundaries
description: Manual ErrorBoundary implementation with getDerivedStateFromError and componentDidCatch
tags:
  [
    ErrorBoundary,
    componentDidCatch,
    getDerivedStateFromError,
    class-component,
    error-logging,
  ]
---

# Class-Based Error Boundaries

## Basic Implementation

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

type ErrorBoundaryProps = {
  children: ReactNode;
  fallback: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error caught by boundary:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}
```

## With Reset Capability

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

type ErrorBoundaryProps = {
  children: ReactNode;
  fallback: (error: Error, reset: () => void) => ReactNode;
  onReset?: () => void;
};

type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Error boundary caught:', {
      error,
      componentStack: info.componentStack,
    });
  }

  reset = () => {
    this.props.onReset?.();
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      return this.props.fallback(this.state.error, this.reset);
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

Usage:

```tsx
<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )}
  onReset={() => console.log('Error boundary reset')}
>
  <MyComponent />
</ErrorBoundary>
```

## With Error Logging Service

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

type ErrorBoundaryProps = {
  children: ReactNode;
  fallback: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state = { hasError: false };

  static getDerivedStateFromError(_error: Error): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    this.props.onError?.(error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

Usage with monitoring:

```tsx
import * as Sentry from '@sentry/react';

<ErrorBoundary
  fallback={<ErrorFallback />}
  onError={(error, info) => {
    Sentry.captureException(error, {
      contexts: { react: { componentStack: info.componentStack } },
    });
  }}
>
  <App />
</ErrorBoundary>;
```

## Development-Only Stack Traces

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

type ErrorBoundaryState = {
  hasError: boolean;
  error: Error | null;
};

class ErrorBoundary extends Component<
  { children: ReactNode },
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    if (process.env.NODE_ENV === 'development') {
      console.error('Error details:', {
        error,
        componentStack: info.componentStack,
      });
    }
  }

  render() {
    if (this.state.hasError && this.state.error) {
      return (
        <div className="error-container">
          <h2>Something went wrong</h2>
          <p>{this.state.error.message}</p>
          {process.env.NODE_ENV === 'development' && (
            <pre className="error-stack">{this.state.error.stack}</pre>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
```

## What Error Boundaries Catch

Error boundaries catch errors in:

- **Component rendering** - Errors thrown during the render phase
- **Lifecycle methods** - Errors in componentDidMount, componentDidUpdate, etc.
- **Constructors** - Errors in child component constructors
- **startTransition callbacks** - Errors thrown inside startTransition

```tsx
function BrokenComponent() {
  const [count, setCount] = useState(0);

  if (count > 5) {
    throw new Error('Count too high');
  }

  return <button onClick={() => setCount(count + 1)}>Increment</button>;
}
```

## What Error Boundaries Do NOT Catch

```tsx
function ComponentWithUncaughtErrors() {
  const handleClick = () => {
    throw new Error('Event handler error');
  };

  useEffect(() => {
    setTimeout(() => {
      throw new Error('Async error');
    }, 1000);
  }, []);

  return <button onClick={handleClick}>Click</button>;
}
```

Error boundaries do NOT catch:

- **Event handlers** - Use try/catch directly in handlers
- **Async code** - setTimeout, requestAnimationFrame, Promise callbacks
- **Server-side rendering** - Errors during SSR
- **Errors in the boundary itself** - Only child component errors

Event handler solution:

```tsx
function SafeComponent() {
  const handleClick = () => {
    try {
      riskyOperation();
    } catch (error) {
      console.error('Event handler error:', error);
      showUserErrorMessage();
    }
  };

  return <button onClick={handleClick}>Click</button>;
}
```

## Multiple Boundaries for Granular Control

```tsx
function App() {
  return (
    <ErrorBoundary fallback={<PageError />}>
      <Header />
      <ErrorBoundary fallback={<SidebarError />}>
        <Sidebar />
      </ErrorBoundary>
      <ErrorBoundary fallback={<MainContentError />}>
        <MainContent />
      </ErrorBoundary>
      <Footer />
    </ErrorBoundary>
  );
}
```

This pattern:

- Isolates errors to specific UI sections
- Prevents cascade failures
- Provides contextual error messages
- Allows partial page functionality

## Testing Error Boundaries

```tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ErrorBoundary from './ErrorBoundary';

const ThrowError = () => {
  throw new Error('Test error');
};

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary fallback={<div>Error</div>}>
        <div>Content</div>
      </ErrorBoundary>,
    );
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders fallback on error', () => {
    const consoleError = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Error occurred</div>}>
        <ThrowError />
      </ErrorBoundary>,
    );

    expect(screen.getByText('Error occurred')).toBeInTheDocument();
    consoleError.mockRestore();
  });

  it('calls onError when error caught', () => {
    const onError = vi.fn();
    const consoleError = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {});

    render(
      <ErrorBoundary fallback={<div>Error</div>} onError={onError}>
        <ThrowError />
      </ErrorBoundary>,
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({ componentStack: expect.any(String) }),
    );
    consoleError.mockRestore();
  });
});
```
