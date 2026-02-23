---
title: FastAPI Patterns
description: FastAPI application structure, routing, dependency injection, middleware, and error handling with uv
tags: [fastapi, uvicorn, routing, dependency-injection, middleware, lifespan]
---

# FastAPI Patterns

## Project Setup

```bash
uv init my-api
cd my-api
uv add fastapi "uvicorn[standard]"
uv add --dev pytest httpx pytest-asyncio
```

## Application Structure

```text
src/
  my_api/
    __init__.py
    main.py
    config.py
    dependencies.py
    routers/
      __init__.py
      users.py
      items.py
    models/
      __init__.py
      user.py
    schemas/
      __init__.py
      user.py
```

## Application Entry Point

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from my_api.routers import items, users


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup: initialize resources
    yield
    # Shutdown: cleanup resources


app = FastAPI(title="My API", lifespan=lifespan)
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(items.router, prefix="/items", tags=["items"])
```

## Router Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status

from my_api.dependencies import get_db
from my_api.schemas.user import UserCreate, UserResponse

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(db: Database = Depends(get_db)):
    return await db.fetch_all("SELECT * FROM users")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Database = Depends(get_db)):
    user = await db.fetch_one("SELECT * FROM users WHERE id = :id", {"id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Database = Depends(get_db)):
    user_id = await db.execute("INSERT INTO users (name, email) VALUES (:name, :email)", payload.model_dump())
    return {**payload.model_dump(), "id": user_id}
```

## Dependency Injection

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status


async def get_db() -> AsyncIterator[Database]:
    db = Database()
    try:
        yield db
    finally:
        await db.disconnect()


async def get_current_user(
    authorization: Annotated[str, Header()],
    db: Database = Depends(get_db),
) -> User:
    token = authorization.removeprefix("Bearer ")
    user = await db.fetch_one("SELECT * FROM users WHERE token = :token", {"token": token})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me")
async def get_me(user: CurrentUser) -> UserResponse:
    return user
```

## Middleware

```python
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = str(duration)
        return response


app.add_middleware(TimingMiddleware)
```

## Error Handling

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


@app.exception_handler(AppError)
async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
```

## Running the Server

```bash
uv run uvicorn my_api.main:app --reload --host 0.0.0.0 --port 8000
```

```toml
[project.scripts]
serve = "uvicorn my_api.main:app --reload"
```
