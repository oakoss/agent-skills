---
title: Structlog Logging
description: Structured logging with structlog, processor pipelines, context binding, and integration with standard logging
tags: [structlog, logging, structured-logging, processors, context]
---

# Structlog Logging

## Setup

```bash
uv add structlog
```

## Basic Configuration

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

## Production Configuration (JSON Output)

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracing.DictTracer(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)
```

## Basic Usage

```python
import structlog

log = structlog.get_logger()


async def process_order(order_id: str, user_id: str) -> None:
    log.info("processing_order", order_id=order_id, user_id=user_id)

    try:
        result = await charge_payment(order_id)
        log.info("payment_charged", order_id=order_id, amount=result.amount)
    except PaymentError:
        log.error("payment_failed", order_id=order_id, exc_info=True)
        raise
```

## Context Binding

### Logger-Level Binding

```python
log = structlog.get_logger().bind(service="order-api", environment="production")

log.info("server_started", port=8000)
```

### Request-Scoped Context (contextvars)

```python
import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars


async def request_middleware(request: Request, call_next):
    clear_contextvars()
    bind_contextvars(
        request_id=request.headers.get("x-request-id", "unknown"),
        method=request.method,
        path=request.url.path,
    )

    log.info("request_started")
    response = await call_next(request)
    log.info("request_completed", status_code=response.status_code)
    return response
```

All log entries within the request automatically include `request_id`, `method`, and `path`.

## Custom Processors

```python
def add_app_context(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    event_dict["app"] = "my-api"
    event_dict["version"] = "1.0.0"
    return event_dict


structlog.configure(
    processors=[
        add_app_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
```

## Filtering Sensitive Data

```python
SENSITIVE_KEYS = {"password", "token", "secret", "authorization"}


def filter_sensitive(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    for key in SENSITIVE_KEYS:
        if key in event_dict:
            event_dict[key] = "***REDACTED***"
    return event_dict
```

## FastAPI Integration

```python
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import structlog
from fastapi import FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
    )
    log.info("app_started")
    yield
    log.info("app_stopped")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    clear_contextvars()
    bind_contextvars(request_id=request.headers.get("x-request-id", ""))
    response = await call_next(request)
    return response
```

## Exception Logging

```python
try:
    await process_payment(order_id)
except Exception:
    log.exception("payment_processing_failed", order_id=order_id)
    raise
```
