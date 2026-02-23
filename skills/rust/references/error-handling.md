---
title: Error Handling
description: Error handling with Result, Option, the ? operator, thiserror for libraries, and anyhow for applications
tags: [Result, Option, thiserror, anyhow, error, From, context, unwrap]
---

# Error Handling

## Result and Option

`Result<T, E>` represents success or failure. `Option<T>` represents presence or absence. Both support the `?` operator for early return.

```rust
use std::fs;
use std::num::ParseIntError;

fn read_age(path: &str) -> Result<u32, Box<dyn std::error::Error>> {
    let contents = fs::read_to_string(path)?;
    let age: u32 = contents.trim().parse()?;
    Ok(age)
}

fn find_user(users: &[&str], name: &str) -> Option<usize> {
    users.iter().position(|&u| u == name)
}
```

### Combinators

```rust
fn process() {
    let port: u16 = std::env::var("PORT")
        .ok()                    // Result -> Option
        .and_then(|v| v.parse().ok())
        .unwrap_or(3000);

    let result: Result<i32, String> = Ok(5);
    let mapped = result
        .map(|v| v * 2)         // Transform success value
        .map_err(|e| format!("failed: {e}")); // Transform error

    let fallback = "42"
        .parse::<i32>()
        .or_else(|_| "0".parse::<i32>());
}
```

## thiserror for Library Errors

`thiserror` generates `Display` and `Error` implementations via derive macros. Use for libraries where callers need to match on error variants.

```toml
[dependencies]
thiserror = "2"
```

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),

    #[error("validation failed: {field}")]
    Validation { field: String },

    #[error("resource {id} not found")]
    NotFound { id: String },

    #[error("authentication required")]
    Unauthorized,

    #[error(transparent)]
    Unexpected(#[from] anyhow::Error),
}
```

### Composing Error Types

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("failed to read config file")]
    Io(#[from] std::io::Error),

    #[error("failed to parse config")]
    Parse(#[from] toml::de::Error),

    #[error("missing required field: {0}")]
    MissingField(String),
}

pub fn load_config(path: &str) -> Result<Config, ConfigError> {
    let contents = std::fs::read_to_string(path)?;
    let config: Config = toml::from_str(&contents)?;
    if config.database_url.is_empty() {
        return Err(ConfigError::MissingField("database_url".into()));
    }
    Ok(config)
}
```

## anyhow for Application Errors

`anyhow` provides a single error type with context chaining. Use in application code (binaries, CLI tools) where error matching is not needed.

```toml
[dependencies]
anyhow = "1"
```

```rust
use anyhow::{bail, ensure, Context, Result};

fn connect_database(url: &str) -> Result<Database> {
    ensure!(!url.is_empty(), "database URL must not be empty");

    let db = Database::connect(url)
        .context("failed to connect to database")?;

    if !db.is_healthy() {
        bail!("database health check failed");
    }

    Ok(db)
}

fn load_and_validate(path: &str) -> Result<Config> {
    let config = std::fs::read_to_string(path)
        .with_context(|| format!("failed to read config from {path}"))?;

    let parsed: Config = toml::from_str(&config)
        .context("invalid TOML in config file")?;

    Ok(parsed)
}
```

### anyhow vs thiserror Decision

| Scenario                      | Use                               |
| ----------------------------- | --------------------------------- |
| Library crate (published API) | `thiserror` with typed error enum |
| Binary / application          | `anyhow::Result` with context     |
| Internal modules in a binary  | `anyhow::Result`                  |
| FFI boundary                  | Custom error codes, not Result    |

## Axum Error Integration

Convert application errors to HTTP responses using `IntoResponse`.

```rust
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;

#[derive(Debug, thiserror::Error)]
pub enum ApiError {
    #[error("not found: {0}")]
    NotFound(String),

    #[error("validation: {0}")]
    Validation(String),

    #[error(transparent)]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let (status, message) = match &self {
            ApiError::NotFound(msg) => (StatusCode::NOT_FOUND, msg.clone()),
            ApiError::Validation(msg) => (StatusCode::BAD_REQUEST, msg.clone()),
            ApiError::Internal(_) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                "internal server error".into(),
            ),
        };

        (status, Json(json!({ "error": message }))).into_response()
    }
}

async fn get_user(
    axum::extract::Path(id): axum::extract::Path<String>,
) -> Result<Json<User>, ApiError> {
    let user = find_user(&id)
        .ok_or_else(|| ApiError::NotFound(format!("user {id}")))?;
    Ok(Json(user))
}
```

## Pattern: Converting Between Error Types

```rust
use std::num::ParseIntError;

#[derive(Debug, thiserror::Error)]
enum MyError {
    #[error("parse error: {0}")]
    Parse(#[from] ParseIntError),

    #[error("out of range: {value} (max {max})")]
    OutOfRange { value: i64, max: i64 },
}

fn parse_bounded(s: &str, max: i64) -> Result<i64, MyError> {
    let value: i64 = s.parse()?; // ParseIntError auto-converts via From
    if value > max {
        return Err(MyError::OutOfRange { value, max });
    }
    Ok(value)
}
```

## Unwrap Guidelines

| Method                     | Use When                                            |
| -------------------------- | --------------------------------------------------- |
| `unwrap()`                 | Tests, prototypes, or provably safe cases           |
| `expect("reason")`         | Invariants with documentation of why it cannot fail |
| `unwrap_or(default)`       | Sensible default exists                             |
| `unwrap_or_else(\|\| ...)` | Default requires computation                        |
| `?` operator               | Propagating errors to the caller                    |
