---
title: Pydantic Validation
description: Pydantic v2 data models, validation, serialization, settings management, and custom types
tags: [pydantic, basemodel, validation, settings, field, serialization]
---

# Pydantic Validation

## Setup

```bash
uv add "pydantic>=2.0"
uv add pydantic-settings
```

## Basic Models

```python
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
```

## Validation

```python
from pydantic import BaseModel, field_validator, model_validator


class OrderCreate(BaseModel):
    items: list[str]
    quantity: int = Field(gt=0)
    discount_code: str | None = None

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Order must have at least one item")
        return v

    @model_validator(mode="after")
    def validate_discount(self) -> "OrderCreate":
        if self.discount_code and self.quantity < 5:
            raise ValueError("Discount requires minimum 5 items")
        return self
```

## Serialization

```python
user = UserResponse(id=1, name="Alice", email="alice@example.com")

user.model_dump()
user.model_dump(exclude={"email"})
user.model_dump(exclude_none=True)

user.model_dump_json()

UserResponse.model_validate({"id": 1, "name": "Alice", "email": "alice@example.com"})
UserResponse.model_validate_json('{"id": 1, "name": "Alice", "email": "alice@example.com"}')
```

## Nested Models

```python
from datetime import datetime


class Address(BaseModel):
    street: str
    city: str
    country: str = "US"


class UserProfile(BaseModel):
    user: UserResponse
    address: Address
    created_at: datetime
    tags: list[str] = []
```

## Generic Models

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int

    @property
    def has_next(self) -> bool:
        return self.page * self.per_page < self.total
```

## Discriminated Unions

```python
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class EmailNotification(BaseModel):
    type: Literal["email"] = "email"
    to: str
    subject: str


class SMSNotification(BaseModel):
    type: Literal["sms"] = "sms"
    phone: str
    message: str


Notification = Annotated[
    Union[EmailNotification, SMSNotification],
    Field(discriminator="type"),
]


class Event(BaseModel):
    notification: Notification
```

## Settings Management

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
    )

    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str = Field(min_length=32)
    allowed_origins: list[str] = ["http://localhost:3000"]
```

```bash
APP_DATABASE_URL=postgresql://localhost/mydb
APP_SECRET_KEY=supersecretkeythatis32charslong!!
```

```python
settings = Settings()
```

## Custom Types

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def validate_slug(v: str) -> str:
    if not v.replace("-", "").isalnum():
        raise ValueError("Slug must be alphanumeric with hyphens")
    return v.lower()


Slug = Annotated[str, AfterValidator(validate_slug)]


class Article(BaseModel):
    title: str
    slug: Slug
```

## Model Config Options

```python
from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
```
