---
title: Test Setup
description: Setup files for Vitest including jest-dom matchers, React Testing Library cleanup, custom render utilities, MSW server lifecycle, DOM polyfills, and multi-file setup strategies
tags:
  [
    setupFiles,
    jest-dom,
    cleanup,
    custom-render,
    msw,
    polyfills,
    matchMedia,
    ResizeObserver,
  ]
---

# Test Setup

Setup files run before your tests via the `setupFiles` config option. They configure the test environment — extending matchers, registering cleanup, stubbing browser APIs, and bootstrapping mock servers.

## jest-dom Matchers

Extend `expect` with DOM-specific matchers via `@testing-library/jest-dom`:

```ts
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
```

The `/vitest` entrypoint auto-extends Vitest's `expect`. Using the bare `@testing-library/jest-dom` import targets Jest and won't wire up correctly.

Add the types in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```

Available matchers after setup:

```tsx
expect(element).toBeInTheDocument();
expect(element).toBeVisible();
expect(element).toHaveTextContent('text');
expect(element).toHaveTextContent(/regex/);
expect(element).toHaveClass('active');
expect(element).toHaveAttribute('aria-label', 'Close');
expect(element).toHaveFocus();
expect(element).toBeDisabled();
expect(element).toBeEnabled();
expect(element).toBeRequired();
expect(element).toBeValid();
expect(element).toBeInvalid();
expect(element).toHaveValue('input value');
expect(element).toBeChecked();
expect(element).toHaveStyle({ color: 'red' });
expect(element).toHaveAccessibleName('Submit form');
expect(element).toHaveAccessibleDescription('Submits the contact form');
expect(element).toHaveRole('button');
expect(element).toBeEmptyDOMElement();
expect(element).toContainElement(child);
expect(form).toHaveFormValues({ email: 'a@b.com', terms: true });
```

## React Testing Library Cleanup

React Testing Library auto-cleans up after each test in most frameworks. For Vitest, register cleanup explicitly:

```ts
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

Without cleanup, rendered components leak between tests, causing stale queries and memory issues.

## Custom Render with Providers

Create a reusable render function that wraps components with common providers:

```tsx
// test/utils.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, type RenderOptions } from '@testing-library/react';
import { type ReactElement } from 'react';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

interface ProviderOptions {
  queryClient?: QueryClient;
}

function AllProviders({
  children,
  queryClient = createTestQueryClient(),
}: ProviderOptions & { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

export function renderWithProviders(
  ui: ReactElement,
  { queryClient, ...renderOptions }: ProviderOptions & RenderOptions = {},
) {
  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders queryClient={queryClient}>{children}</AllProviders>
    ),
    ...renderOptions,
  });
}

export { createTestQueryClient };
```

Use in tests:

```tsx
import { renderWithProviders } from '../test/utils';

it('renders user list', async () => {
  renderWithProviders(<UserList />);
  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

### Multiple Providers

Stack additional providers as your app requires:

```tsx
import { MemoryRouter } from 'react-router-dom';

interface ProviderOptions {
  queryClient?: QueryClient;
  initialRoute?: string;
}

function AllProviders({
  children,
  queryClient = createTestQueryClient(),
  initialRoute = '/',
}: ProviderOptions & { children: React.ReactNode }) {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </MemoryRouter>
  );
}
```

## MSW Server Setup

Configure Mock Service Worker for API mocking across tests:

```ts
// test/server.ts
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () => {
    return HttpResponse.json([
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
    ]);
  }),
];

export const server = setupServer(...handlers);
```

Register the server lifecycle in the setup file:

```ts
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { server } from './test/server';

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
});

afterAll(() => {
  server.close();
});
```

`onUnhandledRequest: 'error'` catches unhandled API calls — preventing silent network requests in tests.

Override handlers per test:

```tsx
import { http, HttpResponse } from 'msw';
import { server } from '../test/server';

it('handles server error', async () => {
  server.use(
    http.get('/api/users', () => {
      return HttpResponse.json({ error: 'Internal error' }, { status: 500 });
    }),
  );

  renderWithProviders(<UserList />);
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});
```

## Global Mock Resets

Configure automatic mock cleanup in the setup file instead of per-test `afterEach`:

```ts
// vitest.setup.ts
import { afterEach } from 'vitest';
import { vi } from 'vitest';

afterEach(() => {
  vi.restoreAllMocks();
});
```

Or configure globally in `vitest.config.ts`:

```ts
export default defineConfig({
  test: {
    restoreMocks: true,
  },
});
```

The config approach is preferred — it covers all tests without a setup file import. `restoreMocks` restores spies and clears `vi.fn()` implementations after each test.

## DOM Polyfills

Browser APIs missing from jsdom/happy-dom need stubs in the setup file:

```ts
// vitest.setup.ts

// matchMedia — required by responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

```ts
// ResizeObserver — required by virtualized lists, charts, auto-sizing
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.stubGlobal('ResizeObserver', ResizeObserverStub);
```

```ts
// IntersectionObserver — required by lazy loading, infinite scroll
class IntersectionObserverStub {
  readonly root = null;
  readonly rootMargin = '';
  readonly thresholds: readonly number[] = [];
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
}

vi.stubGlobal('IntersectionObserver', IntersectionObserverStub);
```

```ts
// scrollTo — jsdom doesn't implement scroll methods
Element.prototype.scrollTo = vi.fn();
window.scrollTo = vi.fn() as unknown as typeof window.scrollTo;
```

## jsdom vs happy-dom

Both provide a DOM environment for testing, but with different tradeoffs:

| Feature          | jsdom                      | happy-dom        |
| ---------------- | -------------------------- | ---------------- |
| Speed            | Slower                     | 2-3x faster      |
| Spec compliance  | Higher                     | Lower            |
| `canvas` support | Via `canvas` package       | Built-in (basic) |
| `fetch` support  | Node 18+ built-in          | Built-in         |
| CSS parsing      | Limited                    | Limited          |
| Community        | Larger, more battle-tested | Growing          |

Use `jsdom` when spec compliance matters (accessibility testing, complex DOM manipulation). Use `happy-dom` when test speed is the priority and you don't hit edge cases.

Switch per-file when needed:

```ts
/**
 * @vitest-environment happy-dom
 */
```

## Multiple Setup Files

Split setup files by concern when different test types need different environments:

```ts
export default defineConfig({
  test: {
    setupFiles: ['./vitest.setup.ts', './vitest.setup.msw.ts'],
  },
});
```

Files execute in order. Common pattern:

- `vitest.setup.ts` — jest-dom, cleanup, polyfills (always needed)
- `vitest.setup.msw.ts` — MSW server lifecycle (API tests only)

For project-scoped setup, use the `projects` config:

```ts
export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          include: ['src/**/*.test.ts'],
          setupFiles: ['./vitest.setup.ts'],
        },
      },
      {
        test: {
          name: 'integration',
          include: ['src/**/*.integration.test.ts'],
          setupFiles: ['./vitest.setup.ts', './vitest.setup.msw.ts'],
        },
      },
    ],
  },
});
```

## Complete Setup File

A typical setup file combining the common patterns:

```ts
// vitest.setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll, vi } from 'vitest';
import { server } from './test/server';

beforeAll(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  vi.restoreAllMocks();
});

afterAll(() => {
  server.close();
});

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```
