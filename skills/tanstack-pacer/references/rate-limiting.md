---
title: Rate Limiting
description: RateLimiter class, fixed and sliding window strategies, rejection handling, and async rate limiting
tags:
  [
    rate-limit,
    RateLimiter,
    fixed-window,
    sliding-window,
    token-bucket,
    limit,
    rejection,
    async,
  ]
---

# Rate Limiting

## Overview

Rate limiting restricts how many times a function can execute within a time window. Unlike throttling (even spacing) or debouncing (waiting for inactivity), rate limiting allows bursts up to the limit then blocks until the window resets.

## RateLimiter Class

```ts
import { RateLimiter } from '@tanstack/pacer';

const limiter = new RateLimiter((id: string) => fetchUserData(id), {
  limit: 5,
  window: 60_000,
  onExecute: (rateLimiter) => {
    console.log('Executed:', rateLimiter.store.state.executionCount);
  },
  onReject: (rateLimiter) => {
    console.log(
      `Rate limit exceeded. Retry in ${rateLimiter.getMsUntilNextWindow()}ms`,
    );
  },
});

limiter.maybeExecute('user-1');
```

## RateLimiter Options

| Option       | Type                   | Default   | Description                       |
| ------------ | ---------------------- | --------- | --------------------------------- |
| `limit`      | `number`               | required  | Maximum executions per window     |
| `window`     | `number`               | required  | Window duration in milliseconds   |
| `windowType` | `'fixed' \| 'sliding'` | `'fixed'` | Window strategy                   |
| `enabled`    | `boolean`              | `true`    | Whether the limiter accepts calls |
| `onExecute`  | `(limiter) => void`    | —         | Called after successful execution |
| `onReject`   | `(limiter) => void`    | —         | Called when execution is rejected |

## Window Types

### Fixed Window

All executions within the window count toward the limit. The window resets completely after the period:

```text
Window 1 (0-60s):     [X X X X X] [blocked] [blocked]
Window 2 (60-120s):   [X X X X X] [blocked]
```

Allows bursts at window boundaries (up to `2 * limit` calls in a short period spanning two windows).

```ts
const limiter = new RateLimiter(handler, {
  limit: 10,
  window: 60_000,
  windowType: 'fixed',
});
```

### Sliding Window

A rolling window that allows executions as old ones expire, providing a smoother rate:

```text
Time:  0s  10s  20s  30s  40s  50s  60s  70s
Calls: X    X    X    X    X    -    X    X
                                     ^ first call expired, slot opens
```

```ts
const limiter = new RateLimiter(handler, {
  limit: 5,
  window: 60_000,
  windowType: 'sliding',
});
```

Use sliding windows when you need consistent rate enforcement without boundary bursts.

## RateLimiter State and Methods

```ts
limiter.getRemainingInWindow();

limiter.getMsUntilNextWindow();

limiter.store.state.executionCount;
limiter.store.state.rejectionCount;

limiter.setOptions({ limit: 10 });

limiter.reset();
```

## rateLimit Function

The functional API for simpler use cases:

```ts
import { rateLimit } from '@tanstack/pacer';

const rateLimitedFetch = rateLimit((url: string) => fetch(url), {
  limit: 10,
  window: 60_000,
});

rateLimitedFetch('/api/data');
```

## Async Rate Limiting

For async operations with success/error handling:

```ts
import { AsyncRateLimiter } from '@tanstack/pacer';

const asyncLimiter = new AsyncRateLimiter(
  async (id: string) => {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  },
  {
    limit: 5,
    window: 60_000,
    onSuccess: (result, limiter) => {
      console.log('Fetched:', result);
    },
    onError: (error, limiter) => {
      console.error('Failed:', error);
    },
    onReject: (limiter) => {
      console.warn('Rate limited');
    },
  },
);

await asyncLimiter.maybeExecute('user-123');
```

## Choosing: Rate Limit vs Throttle vs Debounce

| Technique  | Behavior                               | Best For                                 |
| ---------- | -------------------------------------- | ---------------------------------------- |
| Rate limit | Allows bursts up to limit, then blocks | API call quotas, external service limits |
| Throttle   | Even spacing between executions        | Scroll handlers, UI updates              |
| Debounce   | Waits for inactivity to stop           | Search input, form validation            |

```text
Input:       --X-X-XX---X-X-X-XX-X---

Rate limit   --X-X-XX---------XX-X---   (limit: 5, blocks after 5)
(limit=5):

Throttle     --X---X----X---X----X---   (evenly spaced)
(200ms):

Debounce     ----------X---------X---   (after inactivity)
(200ms):
```

## Handling Rejections

Always provide user feedback when calls are rejected:

```ts
const limiter = new RateLimiter(submitForm, {
  limit: 3,
  window: 60_000,
  onReject: (limiter) => {
    const waitMs = limiter.getMsUntilNextWindow();
    showToast(`Too many attempts. Try again in ${Math.ceil(waitMs / 1000)}s`);
  },
});
```
