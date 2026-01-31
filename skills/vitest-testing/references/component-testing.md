---
title: Component Testing
description: React component testing with React Testing Library, accessible queries, user-event interactions, async utilities, and testing context providers
tags:
  [
    react-testing-library,
    render,
    screen,
    queries,
    user-event,
    waitFor,
    findBy,
    getByRole,
    accessibility,
  ]
---

# Component Testing

## Basic Component Test

Render and query components:

```tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);

    expect(
      screen.getByRole('button', { name: /click me/i }),
    ).toBeInTheDocument();
  });
});
```

## Query Priority

Use queries in this order for better accessibility and test maintainability:

1. **getByRole** — queries by ARIA role (most accessible)
2. **getByLabelText** — queries form inputs by their label
3. **getByPlaceholderText** — queries inputs by placeholder
4. **getByText** — queries by text content
5. **getByDisplayValue** — queries inputs by current value
6. **getByAltText** — queries images by alt text
7. **getByTitle** — queries by title attribute
8. **getByTestId** — last resort, use only when semantic queries are not possible

```tsx
screen.getByRole('button', { name: /submit/i });

screen.getByLabelText(/email/i);

screen.getByText(/welcome/i);

screen.getByTestId('custom-element');
```

## Query Variants

Three query variants for different scenarios:

```tsx
screen.getByRole('button');

screen.queryByRole('button');

await screen.findByRole('button');
```

Query types:

- `getBy*` — returns element or throws (use for elements that should exist)
- `queryBy*` — returns element or null (use for elements that should not exist)
- `findBy*` — returns promise, waits for element (use for async elements)

Multiple elements:

- `getAllBy*` — returns array or throws
- `queryAllBy*` — returns array (empty if none found)
- `findAllBy*` — returns promise with array

## User Interactions with user-event

Simulate user behavior:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it } from 'vitest';

it('handles click', async () => {
  const user = userEvent.setup();
  const handleClick = vi.fn();

  render(<Button onPress={handleClick}>Click</Button>);

  await user.click(screen.getByRole('button'));

  expect(handleClick).toHaveBeenCalledTimes(1);
});
```

Always call `userEvent.setup()` before rendering. All user-event methods are async.

## Common User Events

```tsx
const user = userEvent.setup();

await user.click(element);
await user.dblClick(element);
await user.tripleClick(element);

await user.type(input, 'Hello world');
await user.clear(input);

await user.selectOptions(select, ['option1', 'option2']);
await user.deselectOptions(select, ['option1']);

await user.upload(fileInput, file);

await user.hover(element);
await user.unhover(element);

await user.tab();
await user.tab({ shift: true });

await user.keyboard('{Enter}');
await user.keyboard('{Escape}');
await user.keyboard('{ArrowDown}');
```

## Testing Form Interactions

```tsx
it('submits form with valid data', async () => {
  const user = userEvent.setup();
  const handleSubmit = vi.fn();

  render(<LoginForm onSubmit={handleSubmit} />);

  await user.type(screen.getByLabelText(/email/i), 'user@example.com');
  await user.type(screen.getByLabelText(/password/i), 'password123');
  await user.click(screen.getByRole('button', { name: /submit/i }));

  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'user@example.com',
    password: 'password123',
  });
});
```

## Async Testing with waitFor

Wait for async changes:

```tsx
import { render, screen, waitFor } from '@testing-library/react';

it('loads and displays data', async () => {
  render(<UserProfile userId="1" />);

  expect(screen.getByText(/loading/i)).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText('Alice')).toBeInTheDocument();
  });

  expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
});
```

## Using findBy for Async Elements

`findBy` combines `getBy` + `waitFor`:

```tsx
it('displays loaded data', async () => {
  render(<UserProfile userId="1" />);

  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

Equivalent to:

```tsx
await waitFor(() => {
  expect(screen.getByText('Alice')).toBeInTheDocument();
});
```

## Testing with Context Providers

Wrap components in required providers:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

it('fetches and displays user', async () => {
  renderWithQuery(<UserProfile userId="1" />);

  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

## Reusable Test Wrapper

Create a wrapper for common providers:

```tsx
import { type ReactElement } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, type RenderOptions } from '@testing-library/react';

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });
}

interface WrapperOptions {
  queryClient?: QueryClient;
}

function createWrapper({
  queryClient = createTestQueryClient(),
}: WrapperOptions = {}) {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

function renderWithProviders(
  ui: ReactElement,
  options?: WrapperOptions & RenderOptions,
) {
  return render(ui, {
    wrapper: createWrapper(options),
    ...options,
  });
}

it('uses custom render', async () => {
  renderWithProviders(<UserList />);
  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

## Testing Error States

Verify error handling:

```tsx
it('displays error message', async () => {
  server.use(
    http.get('/api/user', () => {
      return HttpResponse.json({ message: 'User not found' }, { status: 404 });
    }),
  );

  render(<UserProfile userId="999" />);

  expect(await screen.findByText(/user not found/i)).toBeInTheDocument();
});
```

## Testing Loading States

Verify loading indicators:

```tsx
it('shows loading state', () => {
  render(<UserProfile userId="1" />);

  expect(screen.getByRole('status')).toHaveAttribute('aria-busy', 'true');
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
});
```

## Testing Conditional Rendering

Use `queryBy` to assert absence:

```tsx
it('hides premium content for free users', () => {
  render(<Dashboard user={{ tier: 'free' }} />);

  expect(screen.queryByText(/premium feature/i)).not.toBeInTheDocument();
});

it('shows premium content for premium users', () => {
  render(<Dashboard user={{ tier: 'premium' }} />);

  expect(screen.getByText(/premium feature/i)).toBeInTheDocument();
});
```

## Testing Accessibility

Verify ARIA attributes and keyboard navigation:

```tsx
it('has accessible name', () => {
  render(<Button>Submit</Button>);

  const button = screen.getByRole('button', { name: /submit/i });
  expect(button).toBeInTheDocument();
});

it('supports keyboard navigation', async () => {
  const user = userEvent.setup();
  const handleClick = vi.fn();

  render(<Button onPress={handleClick}>Click</Button>);

  await user.tab();
  expect(screen.getByRole('button')).toHaveFocus();

  await user.keyboard('{Enter}');
  expect(handleClick).toHaveBeenCalled();
});

it('announces to screen readers', () => {
  render(<Alert>Important message</Alert>);

  expect(screen.getByRole('alert')).toHaveTextContent('Important message');
});
```

## Testing with MSW (Mock Service Worker)

Mock API calls at the network level:

```tsx
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll } from 'vitest';

const server = setupServer(
  http.get('/api/user/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it('fetches user data', async () => {
  render(<UserProfile userId="1" />);

  expect(await screen.findByText('Alice')).toBeInTheDocument();
});
```

## Testing Component Variants

Test different prop combinations:

```tsx
describe('Button variants', () => {
  it.each([
    { variant: 'primary', class: 'bg-blue-500' },
    { variant: 'secondary', class: 'bg-gray-500' },
    { variant: 'destructive', class: 'bg-red-500' },
  ])('renders $variant variant', ({ variant, class: className }) => {
    render(<Button variant={variant}>Click</Button>);

    expect(screen.getByRole('button')).toHaveClass(className);
  });
});
```

## Testing Debounced Input

Wait for debounced updates:

```tsx
it('debounces search input', async () => {
  const user = userEvent.setup();
  const handleSearch = vi.fn();

  render(<SearchInput onSearch={handleSearch} debounce={300} />);

  const input = screen.getByRole('textbox');

  await user.type(input, 'query');

  expect(handleSearch).not.toHaveBeenCalled();

  await waitFor(() => expect(handleSearch).toHaveBeenCalledWith('query'), {
    timeout: 500,
  });
});
```

## Testing Focus Management

Verify focus behavior:

```tsx
it('focuses first input on mount', () => {
  render(<LoginForm />);

  expect(screen.getByLabelText(/email/i)).toHaveFocus();
});

it('moves focus on submit', async () => {
  const user = userEvent.setup();

  render(<MultiStepForm />);

  await user.type(screen.getByLabelText(/email/i), 'user@example.com');
  await user.click(screen.getByRole('button', { name: /next/i }));

  expect(screen.getByLabelText(/password/i)).toHaveFocus();
});
```

## Debugging Tests

View rendered output:

```tsx
import { screen } from '@testing-library/react';

screen.debug();

screen.debug(screen.getByRole('button'));

screen.logTestingPlaygroundURL();
```

## Custom Matchers

Common jest-dom matchers:

```tsx
expect(element).toBeInTheDocument();
expect(element).toBeVisible();
expect(element).toHaveTextContent('text');
expect(element).toHaveClass('className');
expect(element).toHaveAttribute('attr', 'value');
expect(element).toHaveFocus();
expect(element).toBeDisabled();
expect(element).toBeEnabled();
expect(element).toBeRequired();
expect(element).toBeValid();
expect(element).toBeInvalid();
expect(element).toHaveValue('value');
expect(element).toBeChecked();
```
