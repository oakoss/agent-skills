---
title: CLI Applications
description: CLI tools with clap argument parsing, config crate, tracing for logging, signal handling, and FFI/WASM
tags: [clap, cli, config, tracing, signal, ffi, wasm, graceful-shutdown]
---

# CLI Applications

## Clap Argument Parsing

Clap provides derive-based and builder-based APIs for parsing command-line arguments. The derive API is recommended for most use cases.

```toml
[dependencies]
clap = { version = "4", features = ["derive", "env"] }
```

```rust
use clap::{Parser, Subcommand, Args, ValueEnum};

#[derive(Parser)]
#[command(name = "myapp", version, about = "A sample CLI application")]
struct Cli {
    /// Enable verbose output
    #[arg(short, long, global = true)]
    verbose: bool,

    /// Config file path
    #[arg(short, long, default_value = "config.toml", env = "MYAPP_CONFIG")]
    config: String,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Start the server
    Serve(ServeArgs),
    /// Run database migrations
    Migrate {
        /// Migration direction
        #[arg(value_enum, default_value_t = Direction::Up)]
        direction: Direction,
    },
    /// Generate shell completions
    Completions {
        /// Shell to generate for
        #[arg(value_enum)]
        shell: clap_complete::Shell,
    },
}

#[derive(Args)]
struct ServeArgs {
    /// Port to listen on
    #[arg(short, long, default_value_t = 3000, env = "PORT")]
    port: u16,

    /// Host to bind to
    #[arg(long, default_value = "0.0.0.0")]
    host: String,
}

#[derive(Clone, ValueEnum)]
enum Direction {
    Up,
    Down,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Serve(args) => {
            println!("Starting server on {}:{}", args.host, args.port);
        }
        Commands::Migrate { direction } => {
            println!("Running migrations");
        }
        Commands::Completions { shell } => {
            clap_complete::generate(
                shell,
                &mut Cli::command(),
                "myapp",
                &mut std::io::stdout(),
            );
        }
    }
}
```

### Common Clap Attributes

| Attribute                        | Effect                         |
| -------------------------------- | ------------------------------ |
| `#[arg(short, long)]`            | Enable `-v` and `--verbose`    |
| `#[arg(default_value_t = 8080)]` | Default value with Display     |
| `#[arg(env = "PORT")]`           | Read from environment variable |
| `#[arg(value_enum)]`             | Parse from predefined values   |
| `#[arg(num_args = 1..)]`         | Accept multiple values         |
| `#[arg(required = true)]`        | Mandatory argument             |
| `#[arg(hide = true)]`            | Hide from help output          |
| `#[command(subcommand)]`         | Nested subcommands             |

## Configuration with config Crate

```toml
[dependencies]
config = "0.14"
serde = { version = "1", features = ["derive"] }
```

```rust
use config::{Config, Environment, File};
use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub log_level: String,
}

#[derive(Debug, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
}

#[derive(Debug, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
}

impl AppConfig {
    pub fn load(config_path: &str) -> Result<Self, config::ConfigError> {
        Config::builder()
            .set_default("server.host", "0.0.0.0")?
            .set_default("server.port", 3000)?
            .set_default("database.max_connections", 10)?
            .set_default("log_level", "info")?
            .add_source(File::with_name(config_path).required(false))
            .add_source(Environment::with_prefix("APP").separator("__"))
            .build()?
            .try_deserialize()
    }
}
```

## Logging with tracing

```toml
[dependencies]
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter", "json"] }
```

```rust
use tracing::{info, warn, error, debug, instrument, Level};
use tracing_subscriber::{fmt, layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

fn init_logging(json: bool) {
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("info"));

    let registry = tracing_subscriber::registry().with(env_filter);

    if json {
        registry.with(fmt::layer().json()).init();
    } else {
        registry.with(fmt::layer().pretty()).init();
    }
}

#[instrument(skip(password))]
fn authenticate(username: &str, password: &str) -> Result<User, AuthError> {
    info!(username, "attempting authentication");

    let user = find_user(username).map_err(|e| {
        warn!(username, error = %e, "user lookup failed");
        AuthError::NotFound
    })?;

    debug!(user_id = user.id, "user found, verifying password");
    Ok(user)
}
```

## Signal Handling

```rust
use tokio::signal;

async fn wait_for_shutdown() {
    let ctrl_c = async {
        signal::ctrl_c().await.expect("failed to listen for ctrl+c");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => println!("received SIGINT"),
        _ = terminate => println!("received SIGTERM"),
    }
}
```

## FFI (Foreign Function Interface)

```rust
// Exposing Rust to C
#[no_mangle]
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[no_mangle]
pub extern "C" fn free_string(ptr: *mut std::ffi::c_char) {
    if ptr.is_null() {
        return;
    }
    unsafe {
        let _ = std::ffi::CString::from_raw(ptr);
    }
}
```

```toml
# Cargo.toml for cdylib output
[lib]
crate-type = ["cdylib"]
```

## WASM Compilation

```toml
[dependencies]
wasm-bindgen = "0.2"

[lib]
crate-type = ["cdylib"]
```

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {name}!")
}

#[wasm_bindgen]
pub struct Counter {
    value: u32,
}

#[wasm_bindgen]
impl Counter {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { value: 0 }
    }

    pub fn increment(&mut self) {
        self.value += 1;
    }

    pub fn get(&self) -> u32 {
        self.value
    }
}
```

```bash
# Build for WASM
rustup target add wasm32-unknown-unknown
cargo install wasm-pack
wasm-pack build --target web
```

## Application Bootstrap Pattern

```rust
use anyhow::Result;
use clap::Parser;

#[derive(Parser)]
struct Cli {
    #[arg(short, long, default_value = "config.toml")]
    config: String,
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let config = AppConfig::load(&cli.config)?;

    init_logging(false);

    tracing::info!("starting application");

    let db = setup_database(&config.database).await?;
    let state = AppState { db, config };

    let app = build_router(state);

    let listener = tokio::net::TcpListener::bind(
        format!("{}:{}", config.server.host, config.server.port)
    ).await?;

    tracing::info!(
        host = %config.server.host,
        port = config.server.port,
        "server listening"
    );

    axum::serve(listener, app)
        .with_graceful_shutdown(wait_for_shutdown())
        .await?;

    tracing::info!("server shut down gracefully");
    Ok(())
}
```
