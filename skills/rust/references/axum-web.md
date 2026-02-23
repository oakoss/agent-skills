---
title: Axum Web
description: Web APIs and backends with axum routing, extractors, state, tower middleware, sqlx database access, and tracing
tags:
  [axum, router, extractor, middleware, tower, sqlx, tracing, state, json, rest]
---

# Axum Web

## Project Setup

```toml
[dependencies]
axum = "0.8"
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tower = "0.5"
tower-http = { version = "0.6", features = ["cors", "trace", "compression-gzip"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
```

## Router and Handlers

```rust
use axum::{
    extract::{Json, Path, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post, put, delete},
    Router,
};
use serde::{Deserialize, Serialize};

#[derive(Clone)]
struct AppState {
    db: sqlx::PgPool,
}

#[tokio::main]
async fn main() {
    tracing_subscriber::init();

    let pool = sqlx::PgPool::connect("postgres://localhost/mydb")
        .await
        .expect("failed to connect to database");

    let state = AppState { db: pool };

    let app = Router::new()
        .route("/health", get(health))
        .nest("/api/v1", api_routes())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();

    axum::serve(listener, app).await.unwrap();
}

fn api_routes() -> Router<AppState> {
    Router::new()
        .route("/users", get(list_users).post(create_user))
        .route("/users/{id}", get(get_user).put(update_user).delete(delete_user))
}

async fn health() -> &'static str {
    "ok"
}
```

## Extractors

Extractors parse request data into typed values. Order matters: body-consuming extractors must be last.

```rust
#[derive(Deserialize)]
struct Pagination {
    #[serde(default = "default_page")]
    page: u32,
    #[serde(default = "default_per_page")]
    per_page: u32,
}

fn default_page() -> u32 { 1 }
fn default_per_page() -> u32 { 20 }

async fn list_users(
    State(state): State<AppState>,
    Query(pagination): Query<Pagination>,
) -> Result<Json<Vec<User>>, ApiError> {
    let offset = (pagination.page - 1) * pagination.per_page;
    let users = sqlx::query_as!(
        User,
        "SELECT id, name, email FROM users LIMIT $1 OFFSET $2",
        pagination.per_page as i64,
        offset as i64
    )
    .fetch_all(&state.db)
    .await?;

    Ok(Json(users))
}

#[derive(Deserialize)]
struct CreateUser {
    name: String,
    email: String,
}

async fn create_user(
    State(state): State<AppState>,
    Json(payload): Json<CreateUser>,
) -> Result<(StatusCode, Json<User>), ApiError> {
    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, name, email",
        payload.name,
        payload.email
    )
    .fetch_one(&state.db)
    .await?;

    Ok((StatusCode::CREATED, Json(user)))
}

async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<i64>,
) -> Result<Json<User>, ApiError> {
    let user = sqlx::query_as!(User, "SELECT id, name, email FROM users WHERE id = $1", id)
        .fetch_optional(&state.db)
        .await?
        .ok_or(ApiError::NotFound)?;

    Ok(Json(user))
}
```

## Middleware with Tower

### Layer-Based Middleware

```rust
use axum::Router;
use tower::ServiceBuilder;
use tower_http::{
    cors::{Any, CorsLayer},
    compression::CompressionLayer,
    trace::TraceLayer,
};
use std::time::Duration;

fn app() -> Router<AppState> {
    Router::new()
        .nest("/api", api_routes())
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CompressionLayer::new())
                .layer(
                    CorsLayer::new()
                        .allow_origin(Any)
                        .allow_methods(Any)
                        .allow_headers(Any)
                        .max_age(Duration::from_secs(3600)),
                ),
        )
}
```

### Custom Middleware with from_fn

```rust
use axum::{
    extract::Request,
    http::{header, StatusCode},
    middleware::{self, Next},
    response::Response,
};

async fn auth_middleware(
    request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let auth_header = request
        .headers()
        .get(header::AUTHORIZATION)
        .and_then(|v| v.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;

    if !auth_header.starts_with("Bearer ") {
        return Err(StatusCode::UNAUTHORIZED);
    }

    let token = &auth_header[7..];
    validate_token(token)
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    Ok(next.run(request).await)
}

fn protected_routes() -> Router<AppState> {
    Router::new()
        .route("/profile", get(profile))
        .route("/settings", get(settings).put(update_settings))
        .layer(middleware::from_fn(auth_middleware))
}
```

## sqlx Database Access

```toml
[dependencies]
sqlx = { version = "0.8", features = ["runtime-tokio", "postgres", "migrate"] }
```

```rust
use sqlx::PgPool;

#[derive(Debug, sqlx::FromRow, Serialize)]
struct User {
    id: i64,
    name: String,
    email: String,
}

async fn setup_pool() -> PgPool {
    PgPool::connect_lazy("postgres://localhost/mydb")
        .expect("invalid database URL")
}
```

### Migrations

```bash
# Install sqlx-cli
cargo install sqlx-cli --no-default-features --features postgres

# Create and run migrations
sqlx migrate add create_users
sqlx migrate run

# Verify queries at compile time
cargo sqlx prepare
```

```sql
-- migrations/001_create_users.sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Tracing and Observability

```rust
use tracing::{info, warn, error, instrument};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

fn init_tracing() {
    tracing_subscriber::registry()
        .with(EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .with(tracing_subscriber::fmt::layer())
        .init();
}

#[instrument(skip(state))]
async fn create_user(
    State(state): State<AppState>,
    Json(payload): Json<CreateUser>,
) -> Result<Json<User>, ApiError> {
    info!(name = %payload.name, "creating user");

    let user = sqlx::query_as!(
        User,
        "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id, name, email",
        payload.name,
        payload.email
    )
    .fetch_one(&state.db)
    .await
    .map_err(|e| {
        error!(error = %e, "failed to create user");
        ApiError::Internal(e.into())
    })?;

    info!(user_id = user.id, "user created");
    Ok(Json(user))
}
```

## Graceful Shutdown with Axum

```rust
use tokio::signal;

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(|| async { "hello" }));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000")
        .await
        .unwrap();

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .unwrap();
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c().await.expect("failed to listen for ctrl+c");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
}
```
