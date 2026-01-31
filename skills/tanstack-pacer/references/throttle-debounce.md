---
title: Throttle and Debounce
description: Throttler and Debouncer classes, functional APIs, options, leading/trailing edge control, and async variants
tags:
  [
    throttle,
    debounce,
    Throttler,
    Debouncer,
    leading,
    trailing,
    wait,
    async,
    maybeExecute,
  ]
---

# Throttle and Debounce

## When to Use Which

- **Debounce**: Collapse rapid calls into one execution after activity stops. Best for search input, form validation, window resize end.
- **Throttle**: Guarantee evenly spaced executions regardless of call frequency. Best for scroll handlers, live updates, polling-like behavior.

## Debouncer Class

```ts
import { Debouncer } from '@tanstack/pacer';

const debouncer = new Debouncer((query: string) => fetchSearchResults(query), {
  wait: 500,
  enabled: true,
});

debouncer.maybeExecute('search term');
debouncer.cancel();
debouncer.flush();
```

### Debouncer Options

| Option      | Type                  | Default  | Description                          |
| ----------- | --------------------- | -------- | ------------------------------------ |
| `wait`      | `number`              | required | Milliseconds to wait after last call |
| `enabled`   | `boolean`             | `true`   | Whether the debouncer accepts calls  |
| `onExecute` | `(debouncer) => void` | —        | Called after function executes       |

### Debouncer State

Access state via `debouncer.store.state`:

```ts
debouncer.store.state.isPending;
debouncer.store.state.executionCount;
debouncer.store.state.status;
debouncer.store.state.lastArgs;
```

### No maxWait by Design

The Debouncer intentionally omits `maxWait`. If you need executions to run at regular intervals even during continuous activity, use the Throttler instead.

## debounce Function

The functional API creates a Debouncer instance with a simpler interface:

```ts
import { debounce } from '@tanstack/pacer';

const debouncedSearch = debounce((query: string) => fetchSearchResults(query), {
  wait: 300,
});

debouncedSearch('term');
```

## Throttler Class

```ts
import { Throttler } from '@tanstack/pacer';

const throttler = new Throttler((value: number) => updatePosition(value), {
  wait: 200,
  leading: true,
  trailing: true,
  enabled: true,
});

throttler.maybeExecute(42);
throttler.cancel();
throttler.flush();
```

### Throttler Options

| Option      | Type                  | Default  | Description                                         |
| ----------- | --------------------- | -------- | --------------------------------------------------- |
| `wait`      | `number`              | required | Minimum interval between executions                 |
| `leading`   | `boolean`             | `true`   | Execute immediately on first call                   |
| `trailing`  | `boolean`             | `true`   | Execute after wait period if called during throttle |
| `enabled`   | `boolean`             | `true`   | Whether the throttler accepts calls                 |
| `onExecute` | `(throttler) => void` | —        | Called after function executes                      |

### Leading and Trailing Edge Behavior

```text
Calls:    --|--|----|--------|--
leading:  X                  X      (immediate on first call)
trailing:       X       X       X   (after wait period ends)
both:     X     X       X   X    X  (both edges)
neither:                            (no executions - not useful)
```

- `leading: true, trailing: true` (default): Executes on both edges, most responsive
- `leading: true, trailing: false`: Only the first call in each window executes
- `leading: false, trailing: true`: Only executes after the wait period

### Throttler State

Access state via `throttler.store.state`:

```ts
throttler.store.state.isPending;
throttler.store.state.executionCount;
throttler.store.state.status;
throttler.store.state.lastArgs;
```

## throttle Function

```ts
import { throttle } from '@tanstack/pacer';

const throttledScroll = throttle((position: number) => updateUI(position), {
  wait: 100,
  leading: true,
  trailing: true,
});

window.addEventListener('scroll', () => throttledScroll(window.scrollY));
```

## Async Variants

Both utilities have async counterparts that handle Promises:

```ts
import { AsyncDebouncer, AsyncThrottler } from '@tanstack/pacer';

const asyncDebouncer = new AsyncDebouncer(
  async (query: string) => {
    const results = await fetch(`/api/search?q=${query}`);
    return results.json();
  },
  {
    wait: 500,
    onSuccess: (result, asyncDebouncer) => {
      console.log('Search complete:', result);
    },
    onError: (error, asyncDebouncer) => {
      console.error('Search failed:', error);
    },
  },
);

await asyncDebouncer.maybeExecute('query');
```

### Async-Specific Options

| Option          | Type                         | Description                        |
| --------------- | ---------------------------- | ---------------------------------- |
| `onSuccess`     | `(result, instance) => void` | Called on successful execution     |
| `onError`       | `(error, instance) => void`  | Called on failed execution         |
| `abortPrevious` | `boolean`                    | Cancel previous pending async call |

## Dynamic Option Updates

All classes support runtime option changes:

```ts
const throttler = new Throttler(handler, { wait: 200 });

throttler.setOptions({ wait: 500 });
```

## Cancel and Flush

Both Debouncer and Throttler support cancel and flush:

```ts
debouncer.cancel();

debouncer.flush();
```

- `cancel()`: Cancels any pending execution without running the function
- `flush()`: Immediately executes the pending call (if any) and resets the timer

## Reset

Reset all internal state and counters:

```ts
throttler.reset();
```
