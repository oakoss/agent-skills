---
title: Async Patterns
description: Async/await patterns with asyncio, task groups, semaphores, context managers, and structured concurrency
tags: [asyncio, async, await, task-group, semaphore, structured-concurrency]
---

# Async Patterns

## Basic Async Function

```python
import asyncio

import httpx


async def fetch_url(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
```

## Task Groups (Structured Concurrency)

```python
async def fetch_all(urls: list[str]) -> list[str]:
    results: list[str] = []

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_url(url)) for url in urls]

    return [task.result() for task in tasks]
```

TaskGroup raises `ExceptionGroup` if any task fails. All tasks are cancelled on first failure.

## Concurrency Limiting with Semaphore

```python
async def fetch_with_limit(urls: list[str], max_concurrent: int = 10) -> list[str]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_fetch(url: str) -> str:
        async with semaphore:
            return await fetch_url(url)

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(limited_fetch(url)) for url in urls]

    return [task.result() for task in tasks]
```

## Async Context Managers

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


@asynccontextmanager
async def db_connection(url: str) -> AsyncIterator[Connection]:
    conn = await connect(url)
    try:
        yield conn
    finally:
        await conn.close()


async def query_users() -> list[User]:
    async with db_connection("postgresql://localhost/mydb") as conn:
        return await conn.fetch("SELECT * FROM users")
```

## Async Iterators

```python
from collections.abc import AsyncIterator


async def stream_lines(path: str) -> AsyncIterator[str]:
    import aiofiles

    async with aiofiles.open(path) as f:
        async for line in f:
            yield line.strip()


async def process_file(path: str) -> None:
    async for line in stream_lines(path):
        await process_line(line)
```

## Timeouts

```python
async def fetch_with_timeout(url: str, timeout: float = 5.0) -> str:
    async with asyncio.timeout(timeout):
        return await fetch_url(url)
```

## Queue-Based Producer/Consumer

```python
async def producer(queue: asyncio.Queue[str], items: list[str]) -> None:
    for item in items:
        await queue.put(item)


async def consumer(queue: asyncio.Queue[str], name: str) -> None:
    while True:
        item = await queue.get()
        await process(item)
        queue.task_done()


async def run_pipeline(items: list[str], num_workers: int = 3) -> None:
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)

    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer(queue, items))
        for i in range(num_workers):
            tg.create_task(consumer(queue, f"worker-{i}"))

        await queue.join()
```

## Event Coordination

```python
async def waiter(event: asyncio.Event) -> None:
    await event.wait()
    print("Event received")


async def setter(event: asyncio.Event) -> None:
    await asyncio.sleep(1)
    event.set()


async def coordinate() -> None:
    event = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(waiter(event))
        tg.create_task(setter(event))
```

## Retry Pattern

```python
import asyncio
import random


async def retry_async[T](
    func,
    *args,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> T:
    for attempt in range(max_retries):
        try:
            return await func(*args)
        except Exception:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            await asyncio.sleep(delay)
    raise RuntimeError("Unreachable")
```

## Running Async Code

```python
async def main() -> None:
    result = await fetch_url("https://example.com")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```
