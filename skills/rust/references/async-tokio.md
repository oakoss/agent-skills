---
title: Async Tokio
description: Async programming with Tokio runtime, spawning tasks, channels, select, and graceful shutdown
tags: [tokio, async, await, spawn, select, mpsc, oneshot, shutdown, signal]
---

# Async Tokio

## Runtime Setup

Tokio is the most widely used async runtime for Rust. The `#[tokio::main]` macro transforms `async fn main()` into a synchronous entry point that starts the runtime.

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

```rust
#[tokio::main]
async fn main() {
    println!("running on tokio");
}

// For libraries that need a minimal runtime
#[tokio::main(flavor = "current_thread")]
async fn main() {
    println!("single-threaded runtime");
}
```

### Feature Flags

| Feature           | Provides                           |
| ----------------- | ---------------------------------- |
| `rt`              | Core runtime                       |
| `rt-multi-thread` | Multi-threaded scheduler           |
| `macros`          | `#[tokio::main]`, `#[tokio::test]` |
| `io-util`         | `AsyncReadExt`, `AsyncWriteExt`    |
| `net`             | TCP, UDP, Unix sockets             |
| `time`            | `sleep`, `interval`, `timeout`     |
| `sync`            | Channels, `Mutex`, `RwLock`, etc.  |
| `signal`          | Ctrl+C and OS signal handling      |
| `fs`              | Async filesystem operations        |
| `full`            | All features                       |

## Spawning Tasks

`tokio::spawn` runs a future concurrently on the runtime. The future must be `Send + 'static`.

```rust
use tokio::task::JoinHandle;

async fn fetch_data(url: String) -> Result<String, reqwest::Error> {
    reqwest::get(&url).await?.text().await
}

async fn parallel_fetch() {
    let handles: Vec<JoinHandle<Result<String, reqwest::Error>>> = vec![
        tokio::spawn(fetch_data("https://api.example.com/a".into())),
        tokio::spawn(fetch_data("https://api.example.com/b".into())),
    ];

    for handle in handles {
        match handle.await {
            Ok(Ok(body)) => println!("got {} bytes", body.len()),
            Ok(Err(e)) => eprintln!("request failed: {e}"),
            Err(e) => eprintln!("task panicked: {e}"),
        }
    }
}
```

### spawn_blocking for CPU-bound Work

```rust
async fn hash_password(password: String) -> Result<String, anyhow::Error> {
    tokio::task::spawn_blocking(move || {
        bcrypt::hash(password, bcrypt::DEFAULT_COST)
            .map_err(|e| anyhow::anyhow!("hash failed: {e}"))
    })
    .await?
}
```

## Channels

### mpsc (Multi-Producer, Single-Consumer)

```rust
use tokio::sync::mpsc;

#[derive(Debug)]
enum Command {
    Get { key: String, resp: tokio::sync::oneshot::Sender<Option<String>> },
    Set { key: String, value: String },
}

async fn run_store(mut rx: mpsc::Receiver<Command>) {
    let mut store = std::collections::HashMap::new();

    while let Some(cmd) = rx.recv().await {
        match cmd {
            Command::Get { key, resp } => {
                let _ = resp.send(store.get(&key).cloned());
            }
            Command::Set { key, value } => {
                store.insert(key, value);
            }
        }
    }
}

async fn main_task() {
    let (tx, rx) = mpsc::channel(32);

    tokio::spawn(run_store(rx));

    tx.send(Command::Set {
        key: "foo".into(),
        value: "bar".into(),
    }).await.unwrap();

    let (resp_tx, resp_rx) = tokio::sync::oneshot::channel();
    tx.send(Command::Get {
        key: "foo".into(),
        resp: resp_tx,
    }).await.unwrap();

    let value = resp_rx.await.unwrap();
    println!("got: {value:?}");
}
```

### broadcast (Multi-Producer, Multi-Consumer)

```rust
use tokio::sync::broadcast;

async fn event_system() {
    let (tx, _) = broadcast::channel::<String>(16);

    let mut rx1 = tx.subscribe();
    let mut rx2 = tx.subscribe();

    tokio::spawn(async move {
        while let Ok(msg) = rx1.recv().await {
            println!("subscriber 1: {msg}");
        }
    });

    tokio::spawn(async move {
        while let Ok(msg) = rx2.recv().await {
            println!("subscriber 2: {msg}");
        }
    });

    tx.send("event happened".into()).unwrap();
}
```

### watch (Single-Producer, Multi-Consumer, Latest Value)

```rust
use tokio::sync::watch;

async fn config_reload() {
    let (tx, mut rx) = watch::channel(AppConfig::default());

    tokio::spawn(async move {
        while rx.changed().await.is_ok() {
            let config = rx.borrow().clone();
            println!("config updated: {config:?}");
        }
    });

    tx.send(AppConfig { port: 8080, ..Default::default() }).unwrap();
}
```

## select! Macro

`tokio::select!` waits on multiple async expressions and executes the branch that completes first.

```rust
use tokio::sync::mpsc;
use tokio::time::{sleep, Duration};

async fn process_with_timeout(mut rx: mpsc::Receiver<String>) {
    loop {
        tokio::select! {
            Some(msg) = rx.recv() => {
                println!("received: {msg}");
            }
            _ = sleep(Duration::from_secs(30)) => {
                println!("no message for 30s, shutting down");
                break;
            }
        }
    }
}
```

## Graceful Shutdown

```rust
use tokio::signal;
use tokio::sync::watch;

async fn run_server() -> anyhow::Result<()> {
    let (shutdown_tx, mut shutdown_rx) = watch::channel(false);

    let server = tokio::spawn(async move {
        let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

        loop {
            tokio::select! {
                Ok((stream, addr)) = listener.accept() => {
                    let mut rx = shutdown_rx.clone();
                    tokio::spawn(async move {
                        tokio::select! {
                            _ = handle_connection(stream, addr) => {}
                            _ = rx.changed() => {
                                println!("connection handler shutting down");
                            }
                        }
                    });
                }
                _ = shutdown_rx.changed() => {
                    println!("server shutting down");
                    break;
                }
            }
        }
    });

    signal::ctrl_c().await?;
    println!("shutdown signal received");
    let _ = shutdown_tx.send(true);

    server.await?;
    Ok(())
}
```

## Timeouts and Intervals

```rust
use tokio::time::{timeout, interval, sleep, Duration};

async fn with_timeout() -> anyhow::Result<String> {
    let result = timeout(Duration::from_secs(5), fetch_data())
        .await
        .map_err(|_| anyhow::anyhow!("operation timed out"))??;
    Ok(result)
}

async fn periodic_task() {
    let mut ticker = interval(Duration::from_secs(60));

    loop {
        ticker.tick().await;
        println!("running periodic cleanup");
    }
}
```

## Synchronization Primitives

| Primitive                | Use Case                        |
| ------------------------ | ------------------------------- |
| `tokio::sync::Mutex`     | Async-aware mutual exclusion    |
| `tokio::sync::RwLock`    | Multiple readers, single writer |
| `tokio::sync::Semaphore` | Limit concurrent access         |
| `tokio::sync::Notify`    | Wake one or all waiters         |
| `tokio::sync::Barrier`   | Synchronize multiple tasks      |

```rust
use std::sync::Arc;
use tokio::sync::Semaphore;

async fn rate_limited_fetch(urls: Vec<String>) {
    let semaphore = Arc::new(Semaphore::new(10));
    let mut handles = vec![];

    for url in urls {
        let permit = semaphore.clone().acquire_owned().await.unwrap();
        handles.push(tokio::spawn(async move {
            let result = reqwest::get(&url).await;
            drop(permit);
            result
        }));
    }

    for handle in handles {
        let _ = handle.await;
    }
}
```
