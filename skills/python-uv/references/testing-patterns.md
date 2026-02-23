---
title: Testing Patterns
description: pytest setup, fixtures, async testing, parametrize, mocking, and coverage with uv
tags: [pytest, fixtures, parametrize, mock, coverage, async-testing]
---

# Testing Patterns

## Setup

```bash
uv add --dev pytest pytest-cov pytest-asyncio httpx
```

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "-ra -q"
```

## Project Structure

```text
tests/
  __init__.py
  conftest.py
  test_users.py
  test_items.py
```

## Basic Tests

```python
def test_addition():
    assert 1 + 1 == 2


def test_user_creation():
    user = User(name="Alice", email="alice@example.com")
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
```

## Fixtures

```python
import pytest


@pytest.fixture
def sample_user() -> User:
    return User(name="Alice", email="alice@example.com")


@pytest.fixture
def user_list() -> list[User]:
    return [
        User(name="Alice", email="alice@example.com"),
        User(name="Bob", email="bob@example.com"),
    ]


def test_user_name(sample_user: User):
    assert sample_user.name == "Alice"
```

### Scoped Fixtures

```python
@pytest.fixture(scope="session")
async def db() -> AsyncIterator[Database]:
    database = Database("postgresql://localhost/test")
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture(autouse=True)
async def clean_db(db: Database) -> AsyncIterator[None]:
    yield
    await db.execute("DELETE FROM users")
```

## Async Testing

```python
import pytest


@pytest.mark.asyncio
async def test_fetch_users(db: Database):
    users = await db.fetch_all("SELECT * FROM users")
    assert len(users) == 0


@pytest.mark.asyncio
async def test_create_user(db: Database):
    await db.execute("INSERT INTO users (name) VALUES (:name)", {"name": "Alice"})
    users = await db.fetch_all("SELECT * FROM users")
    assert len(users) == 1
```

## Parametrize

```python
@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("", ""),
    ],
)
def test_uppercase(input_val: str, expected: str):
    assert input_val.upper() == expected


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (1, 2, 3),
        (0, 0, 0),
        (-1, 1, 0),
    ],
    ids=["positive", "zeros", "negative"],
)
def test_add(a: int, b: int, expected: int):
    assert a + b == expected
```

## Mocking

```python
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_send_email():
    with patch("my_app.email.send", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        result = await notify_user("alice@example.com", "Hello")
        assert result is True
        mock_send.assert_called_once_with("alice@example.com", "Hello")
```

## FastAPI Testing

```python
import pytest
from httpx import ASGITransport, AsyncClient

from my_api.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    response = await client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/users/", json={"name": "Alice", "email": "alice@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

## Exception Testing

```python
def test_raises_value_error():
    with pytest.raises(ValueError, match="Invalid email"):
        validate_email("not-an-email")


@pytest.mark.asyncio
async def test_raises_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await get_user(999)
    assert exc_info.value.status_code == 404
```

## Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing

uv run pytest --cov=src --cov-report=html
```

```toml
[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## Running Tests

```bash
uv run pytest

uv run pytest tests/test_users.py

uv run pytest -k "test_create"

uv run pytest -x

uv run pytest --tb=short -q
```
