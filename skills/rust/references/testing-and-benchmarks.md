---
title: Testing and Benchmarks
description: Unit tests, integration tests, test organization, mocking patterns, and criterion benchmarking
tags:
  [test, criterion, benchmark, mock, assert, tokio-test, integration, property]
---

# Testing and Benchmarks

## Unit Tests

Unit tests live in the same file as the code they test, inside a `#[cfg(test)]` module.

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        return Err("division by zero".into());
    }
    Ok(a / b)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn test_add_negative() {
        assert_eq!(add(-1, 1), 0);
    }

    #[test]
    fn test_divide() {
        let result = divide(10.0, 3.0).unwrap();
        assert!((result - 3.333).abs() < 0.01);
    }

    #[test]
    fn test_divide_by_zero() {
        let result = divide(10.0, 0.0);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "division by zero");
    }

    #[test]
    #[should_panic(expected = "index out of bounds")]
    fn test_panics() {
        let v: Vec<i32> = vec![];
        let _ = v[0];
    }
}
```

## Async Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_async_fetch() {
        let result = fetch_data("https://example.com").await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_with_timeout() {
        let result = tokio::time::timeout(
            std::time::Duration::from_secs(5),
            slow_operation(),
        )
        .await;
        assert!(result.is_ok());
    }
}
```

## Integration Tests

Integration tests live in the `tests/` directory at the project root. Each file is compiled as a separate crate.

```text
project/
├── src/
│   └── lib.rs
├── tests/
│   ├── api_tests.rs
│   └── common/
│       └── mod.rs
```

```rust
// tests/common/mod.rs
use myapp::AppState;

pub async fn setup() -> AppState {
    let db = sqlx::PgPool::connect("postgres://localhost/test_db")
        .await
        .expect("failed to connect to test database");

    sqlx::migrate!().run(&db).await.expect("migration failed");

    AppState { db }
}

pub async fn cleanup(state: &AppState) {
    sqlx::query("TRUNCATE users CASCADE")
        .execute(&state.db)
        .await
        .expect("cleanup failed");
}
```

```rust
// tests/api_tests.rs
mod common;

use axum::{body::Body, http::{Request, StatusCode}};
use tower::ServiceExt;

#[tokio::test]
async fn test_create_user() {
    let state = common::setup().await;
    let app = myapp::build_router(state.clone());

    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/api/v1/users")
                .header("Content-Type", "application/json")
                .body(Body::from(r#"{"name": "Alice", "email": "alice@test.com"}"#))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::CREATED);

    common::cleanup(&state).await;
}

#[tokio::test]
async fn test_get_nonexistent_user() {
    let state = common::setup().await;
    let app = myapp::build_router(state.clone());

    let response = app
        .oneshot(
            Request::builder()
                .uri("/api/v1/users/99999")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::NOT_FOUND);

    common::cleanup(&state).await;
}
```

## Test Patterns

### Test Fixtures with Builder

```rust
#[cfg(test)]
mod tests {
    struct UserBuilder {
        name: String,
        email: String,
        active: bool,
    }

    impl Default for UserBuilder {
        fn default() -> Self {
            Self {
                name: "Test User".into(),
                email: "test@example.com".into(),
                active: true,
            }
        }
    }

    impl UserBuilder {
        fn name(mut self, name: &str) -> Self {
            self.name = name.into();
            self
        }

        fn inactive(mut self) -> Self {
            self.active = false;
            self
        }

        fn build(self) -> User {
            User {
                id: 0,
                name: self.name,
                email: self.email,
                active: self.active,
            }
        }
    }

    #[test]
    fn test_inactive_user() {
        let user = UserBuilder::default().inactive().build();
        assert!(!user.active);
    }
}
```

### Testing with Traits (Dependency Injection)

```rust
#[async_trait::async_trait]
pub trait UserRepository: Send + Sync {
    async fn find(&self, id: i64) -> Result<Option<User>, anyhow::Error>;
    async fn create(&self, name: &str, email: &str) -> Result<User, anyhow::Error>;
}

pub struct UserService<R: UserRepository> {
    repo: R,
}

impl<R: UserRepository> UserService<R> {
    pub fn new(repo: R) -> Self {
        Self { repo }
    }

    pub async fn get_user(&self, id: i64) -> Result<User, anyhow::Error> {
        self.repo
            .find(id)
            .await?
            .ok_or_else(|| anyhow::anyhow!("user not found"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    struct MockRepo {
        users: Vec<User>,
    }

    #[async_trait::async_trait]
    impl UserRepository for MockRepo {
        async fn find(&self, id: i64) -> Result<Option<User>, anyhow::Error> {
            Ok(self.users.iter().find(|u| u.id == id).cloned())
        }

        async fn create(&self, name: &str, email: &str) -> Result<User, anyhow::Error> {
            Ok(User { id: 1, name: name.into(), email: email.into(), active: true })
        }
    }

    #[tokio::test]
    async fn test_get_existing_user() {
        let repo = MockRepo {
            users: vec![User { id: 1, name: "Alice".into(), email: "a@b.com".into(), active: true }],
        };
        let service = UserService::new(repo);
        let user = service.get_user(1).await.unwrap();
        assert_eq!(user.name, "Alice");
    }

    #[tokio::test]
    async fn test_get_missing_user() {
        let repo = MockRepo { users: vec![] };
        let service = UserService::new(repo);
        let result = service.get_user(1).await;
        assert!(result.is_err());
    }
}
```

## Criterion Benchmarking

```toml
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }

[[bench]]
name = "my_benchmark"
harness = false
```

```rust
// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};

fn fibonacci(n: u64) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

fn bench_fibonacci(c: &mut Criterion) {
    c.bench_function("fib 20", |b| b.iter(|| fibonacci(black_box(20))));
}

fn bench_fibonacci_group(c: &mut Criterion) {
    let mut group = c.benchmark_group("fibonacci");

    for size in [10, 15, 20, 25] {
        group.bench_with_input(
            BenchmarkId::from_parameter(size),
            &size,
            |b, &size| {
                b.iter(|| fibonacci(black_box(size)));
            },
        );
    }

    group.finish();
}

fn bench_throughput(c: &mut Criterion) {
    use criterion::Throughput;

    let data: Vec<u8> = (0..1024).map(|i| (i % 256) as u8).collect();

    let mut group = c.benchmark_group("processing");
    group.throughput(Throughput::Bytes(data.len() as u64));

    group.bench_function("process_data", |b| {
        b.iter(|| process(black_box(&data)));
    });

    group.finish();
}

criterion_group!(benches, bench_fibonacci, bench_fibonacci_group, bench_throughput);
criterion_main!(benches);
```

```bash
# Run benchmarks
cargo bench

# Run specific benchmark
cargo bench -- fibonacci

# HTML reports generated in target/criterion/
```

### Async Benchmarks with Criterion

```rust
use criterion::{criterion_group, criterion_main, Criterion};
use tokio::runtime::Runtime;

fn bench_async_operation(c: &mut Criterion) {
    let rt = Runtime::new().unwrap();

    c.bench_function("async fetch", |b| {
        b.to_async(&rt).iter(|| async {
            let _ = reqwest::get("http://localhost:3000/health").await;
        });
    });
}

criterion_group!(benches, bench_async_operation);
criterion_main!(benches);
```

## Cargo Test Commands

```bash
# Run all tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test
cargo test test_name

# Run tests in specific module
cargo test module_name::

# Run only integration tests
cargo test --test api_tests

# Run tests with specific features
cargo test --features "feature_name"

# Run doc tests only
cargo test --doc
```
