---
title: Type Checking
description: Type hints, mypy and pyright configuration, common typing patterns, and strict mode setup
tags: [mypy, pyright, type-hints, typing, strict-mode, annotations]
---

# Type Checking

## Setup

```bash
uv add --dev mypy pyright
```

## mypy Configuration

```toml
[tool.mypy]
strict = true
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

```bash
uv run mypy src/
```

## pyright Configuration

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
reportMissingTypeStubs = false
```

```bash
uv run pyright src/
```

## Common Type Patterns

### Function Signatures

```python
def greet(name: str) -> str:
    return f"Hello, {name}"


def find_user(user_id: int) -> User | None:
    ...


async def fetch_users(limit: int = 10) -> list[User]:
    ...
```

### Collections

```python
from collections.abc import Mapping, Sequence


def process_items(items: Sequence[str]) -> None:
    ...


def merge_configs(base: Mapping[str, int], override: Mapping[str, int]) -> dict[str, int]:
    return {**base, **override}
```

### Callables

```python
from collections.abc import Callable, Awaitable


def retry(func: Callable[[], Awaitable[str]], times: int = 3) -> Callable[[], Awaitable[str]]:
    ...


Handler = Callable[[Request], Awaitable[Response]]
```

### TypeVar and Generics

```python
from typing import TypeVar

T = TypeVar("T")


def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### New-Style Generics (Python 3.12+)

```python
def first[T](items: list[T]) -> T | None:
    return items[0] if items else None


class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()
```

### TypedDict

```python
from typing import NotRequired, TypedDict


class UserDict(TypedDict):
    id: int
    name: str
    email: str
    bio: NotRequired[str]


def format_user(user: UserDict) -> str:
    return f"{user['name']} <{user['email']}>"
```

### Literal Types

```python
from typing import Literal


def set_log_level(level: Literal["debug", "info", "warning", "error"]) -> None:
    ...
```

### Protocol (Structural Typing)

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...


class HTMLElement:
    def render(self) -> str:
        return "<div></div>"


def display(item: Renderable) -> None:
    print(item.render())
```

### Annotated Types

```python
from typing import Annotated

from pydantic import Field

PositiveInt = Annotated[int, Field(gt=0)]
NonEmptyStr = Annotated[str, Field(min_length=1)]
```

### Type Aliases

```python
type UserID = int
type JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None

type Handler = Callable[[Request], Awaitable[Response]]
```

### Overloaded Functions

```python
from typing import overload


@overload
def parse(data: str) -> dict[str, str]: ...
@overload
def parse(data: bytes) -> dict[str, bytes]: ...


def parse(data: str | bytes) -> dict[str, str] | dict[str, bytes]:
    if isinstance(data, str):
        return {"value": data}
    return {"value": data}
```

## Running Type Checks

```bash
uv run mypy src/
uv run pyright src/

uvx mypy src/
uvx pyright src/
```

## py.typed Marker

For libraries, include a `py.typed` marker file:

```text
src/
  my_lib/
    __init__.py
    py.typed
```

```bash
uv init --lib my-lib
```

The `--lib` flag creates this automatically.
