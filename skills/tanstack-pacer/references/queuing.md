---
title: Queuing and Async Queuing
description: Queuer and AsyncQueuer classes, FIFO/LIFO ordering, priority queuing, concurrency control, and retry patterns
tags:
  [queue, Queuer, AsyncQueuer, FIFO, LIFO, priority, concurrency, retry, async]
---

# Queuing and Async Queuing

## Overview

Unlike debouncing, throttling, and rate limiting which drop or delay executions, queuers ensure every item is processed. They manage the flow of operations without losing requests, making them ideal for scenarios where data loss is unacceptable.

## Queuer Class (Synchronous)

```ts
import { Queuer } from '@tanstack/pacer';

const queuer = new Queuer((item: string) => processItem(item), {
  wait: 100,
  maxSize: 50,
  started: true,
});

queuer.addItem('task-1');
queuer.addItem('task-2');
```

### Queuer Options

| Option               | Type                     | Default    | Description                               |
| -------------------- | ------------------------ | ---------- | ----------------------------------------- |
| `wait`               | `number`                 | `0`        | Delay between processing items            |
| `maxSize`            | `number`                 | `Infinity` | Maximum queue size                        |
| `started`            | `boolean`                | `true`     | Whether to start processing immediately   |
| `enabled`            | `boolean`                | `true`     | Whether the queuer accepts items          |
| `getPriority`        | `(item) => number`       | —          | Priority function (higher = first)        |
| `expirationDuration` | `number`                 | —          | Max time items can stay in queue          |
| `getIsExpired`       | `(item) => boolean`      | —          | Custom expiration check                   |
| `onReject`           | `(item, queuer) => void` | —          | Called when item is rejected (queue full) |
| `onExpire`           | `(item, queuer) => void` | —          | Called when item expires                  |

## Queue Ordering

### FIFO (Default)

First in, first out. Items are processed in the order they were added:

```ts
const queuer = new Queuer(processItem, { wait: 100 });

queuer.addItem('first');
queuer.addItem('second');
queuer.addItem('third');
```

### LIFO (Stack)

Last in, first out. Add to back, process from back:

```ts
queuer.addItem('item', 'back');
queuer.getNextItem('back');
```

### Priority Queue

Provide a `getPriority` function; higher values are processed first:

```ts
import { Queuer } from '@tanstack/pacer';

type Task = { name: string; urgency: number };

const queuer = new Queuer<Task>((task) => processTask(task), {
  wait: 100,
  getPriority: (task) => task.urgency,
});

queuer.addItem({ name: 'low', urgency: 1 });
queuer.addItem({ name: 'critical', urgency: 10 });
queuer.addItem({ name: 'medium', urgency: 5 });
```

## Queue Control

```ts
queuer.start();
queuer.stop();

queuer.peek();
queuer.getNextItem();

queuer.getAllItems();
queuer.clear();

queuer.store.state.size;
queuer.store.state.isEmpty;
queuer.store.state.isRunning;
```

## queue Function

The functional API for simpler use cases:

```ts
import { queue } from '@tanstack/pacer';

const processQueue = queue((item: string) => console.log('Processing:', item), {
  wait: 200,
  maxSize: 100,
});

processQueue('item-1');
processQueue('item-2');
```

## AsyncQueuer Class

The AsyncQueuer extends queuing with concurrency control, async error handling, and retry support. It implements a task pool / worker pool pattern:

```ts
import { AsyncQueuer } from '@tanstack/pacer';

const asyncQueuer = new AsyncQueuer<string>(
  async (item) => {
    const response = await fetch(`/api/process/${item}`);
    return response.json();
  },
  {
    concurrency: 3,
    wait: 100,
    maxSize: 100,
    started: true,
    onSuccess: (result, item, asyncQueuer) => {
      console.log('Processed:', result);
    },
    onError: (error, item, asyncQueuer) => {
      console.error('Failed:', error);
    },
  },
);

asyncQueuer.addItem('task-1');
asyncQueuer.addItem('task-2');
```

### AsyncQueuer Options

Includes all Queuer options plus:

| Option        | Type                             | Default | Description                     |
| ------------- | -------------------------------- | ------- | ------------------------------- |
| `concurrency` | `number`                         | `1`     | Max concurrent async operations |
| `onSuccess`   | `(result, item, queuer) => void` | —       | Called per successful item      |
| `onError`     | `(error, item, queuer) => void`  | —       | Called per failed item          |

### Concurrency Control

Process multiple items simultaneously while limiting how many run at once:

```ts
const uploader = new AsyncQueuer<File>(
  async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    await fetch('/api/upload', { method: 'POST', body: formData });
  },
  {
    concurrency: 3,
    onSuccess: (_result, file) => {
      console.log(`Uploaded: ${file.name}`);
    },
  },
);

files.forEach((file) => uploader.addItem(file));
```

### AsyncQueuer State

```ts
asyncQueuer.store.state.activeCount;
asyncQueuer.store.state.pendingCount;
asyncQueuer.store.state.successCount;
asyncQueuer.store.state.errorCount;
asyncQueuer.store.state.isExecuting;
asyncQueuer.store.state.isRunning;
asyncQueuer.store.state.isEmpty;
```

## asyncQueue Function

```ts
import { asyncQueue } from '@tanstack/pacer';

const processAsync = asyncQueue(
  async (item: string) => {
    await processItem(item);
  },
  { concurrency: 2, wait: 100 },
);

processAsync('item-1');
```

## Item Expiration

Remove stale items automatically:

```ts
const queuer = new Queuer(processItem, {
  expirationDuration: 30_000,
  onExpire: (item) => {
    console.log('Expired:', item);
  },
});
```

## Queue Size Limits

Reject items when the queue is full:

```ts
const queuer = new Queuer(processItem, {
  maxSize: 100,
  onReject: (item) => {
    console.warn('Queue full, rejected:', item);
  },
});
```
