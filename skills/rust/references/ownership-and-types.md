---
title: Ownership and Types
description: Ownership, borrowing, lifetimes, traits, generics, and serde serialization patterns
tags:
  [
    ownership,
    borrowing,
    lifetimes,
    traits,
    generics,
    serde,
    derive,
    phantom-data,
  ]
---

# Ownership and Types

## Ownership Rules

Every value has exactly one owner. When the owner goes out of scope, the value is dropped. Assignment moves ownership for non-Copy types.

```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1; // s1 is moved to s2
    // println!("{s1}"); // compile error: value used after move

    let n1: i32 = 42;
    let n2 = n1; // i32 implements Copy, so n1 is still valid
    println!("{n1} {n2}");
}
```

## Borrowing

References borrow values without taking ownership. The borrow checker enforces: one mutable reference XOR any number of immutable references.

```rust
fn calculate_length(s: &str) -> usize {
    s.len()
}

fn append_greeting(s: &mut String) {
    s.push_str(", world!");
}

fn main() {
    let mut name = String::from("hello");
    let len = calculate_length(&name);
    append_greeting(&mut name);
    println!("{name} has original length {len}");
}
```

## Lifetimes

Lifetime annotations describe the relationship between reference lifetimes. The compiler uses them to ensure references remain valid.

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn level(&self) -> i32 {
        3
    }

    fn announce(&self, announcement: &str) -> &'a str {
        println!("Attention: {announcement}");
        self.text
    }
}
```

### Lifetime Elision Rules

The compiler infers lifetimes in three cases:

1. Each reference parameter gets its own lifetime
2. If exactly one input lifetime, it applies to all output references
3. If `&self` or `&mut self` is a parameter, its lifetime applies to output references

```rust
// Elided: fn first_word(s: &str) -> &str
// Expanded: fn first_word<'a>(s: &'a str) -> &'a str
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &byte) in bytes.iter().enumerate() {
        if byte == b' ' {
            return &s[..i];
        }
    }
    s
}
```

## Traits and Generics

Traits define shared behavior. Use trait bounds to constrain generic types.

```rust
trait Summary {
    fn summarize(&self) -> String;

    fn preview(&self) -> String {
        format!("Read more: {}", self.summarize())
    }
}

struct Article {
    title: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, &self.content[..50])
    }
}

fn notify(item: &impl Summary) {
    println!("Breaking: {}", item.summarize());
}

// Equivalent with trait bound syntax
fn notify_bounded<T: Summary>(item: &T) {
    println!("Breaking: {}", item.summarize());
}

// Multiple bounds with where clause
fn process<T>(item: &T) -> String
where
    T: Summary + std::fmt::Display,
{
    format!("{item}: {}", item.summarize())
}
```

### Common Derive Traits

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct UserId(u64);

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum Priority {
    Low,
    Medium,
    High,
}

#[derive(Default)]
struct Config {
    retries: u32,
    timeout_ms: u64,
    verbose: bool,
}
```

## Enums and Pattern Matching

```rust
enum Command {
    Quit,
    Echo(String),
    Move { x: i32, y: i32 },
    Color(u8, u8, u8),
}

fn handle(cmd: Command) {
    match cmd {
        Command::Quit => std::process::exit(0),
        Command::Echo(msg) => println!("{msg}"),
        Command::Move { x, y } => println!("Moving to ({x}, {y})"),
        Command::Color(r, g, b) => println!("#{r:02x}{g:02x}{b:02x}"),
    }
}
```

## Serde Serialization

Serde provides format-agnostic serialization. Derive `Serialize` and `Deserialize`, then use format crates like `serde_json`, `serde_yaml`, or `toml`.

```toml
[dependencies]
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    name: String,
    email: String,
    #[serde(default)]
    active: bool,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ApiResponse<T> {
    status_code: u16,
    data: T,
    #[serde(skip_serializing_if = "Option::is_none")]
    error_message: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(tag = "type", content = "payload")]
enum Event {
    UserCreated(User),
    UserDeleted { id: u64 },
    SystemMessage(String),
}

fn main() -> serde_json::Result<()> {
    let user = User {
        name: "Alice".into(),
        email: "alice@example.com".into(),
        active: true,
    };

    let json = serde_json::to_string_pretty(&user)?;
    println!("{json}");

    let parsed: User = serde_json::from_str(&json)?;
    println!("{parsed:?}");

    Ok(())
}
```

### Common Serde Attributes

| Attribute                                           | Effect                                |
| --------------------------------------------------- | ------------------------------------- |
| `#[serde(rename_all = "camelCase")]`                | Rename all fields to camelCase        |
| `#[serde(default)]`                                 | Use Default::default() if missing     |
| `#[serde(skip_serializing_if = "Option::is_none")]` | Omit None fields                      |
| `#[serde(flatten)]`                                 | Inline nested struct fields           |
| `#[serde(tag = "type")]`                            | Internally tagged enum representation |
| `#[serde(untagged)]`                                | Try each variant in order             |
| `#[serde(deny_unknown_fields)]`                     | Reject unexpected fields              |

## Cargo Workspace Management

Workspaces share a single `Cargo.lock` and output directory across multiple crates.

```toml
# Root Cargo.toml
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.package]
edition = "2021"
license = "MIT"
repository = "https://github.com/org/project"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
```

```toml
# crates/my-lib/Cargo.toml
[package]
name = "my-lib"
version = "0.1.0"
edition.workspace = true
license.workspace = true

[dependencies]
serde.workspace = true
```

## Smart Pointers

| Type                     | Use Case                                        |
| ------------------------ | ----------------------------------------------- |
| `Box<T>`                 | Heap allocation, recursive types, trait objects |
| `Rc<T>`                  | Single-threaded shared ownership                |
| `Arc<T>`                 | Thread-safe shared ownership                    |
| `Cell<T>` / `RefCell<T>` | Interior mutability (single-threaded)           |
| `Mutex<T>` / `RwLock<T>` | Interior mutability (thread-safe)               |
| `Cow<'a, T>`             | Clone-on-write, avoid unnecessary allocation    |

```rust
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Clone)]
struct AppState {
    db: Arc<DatabasePool>,
    cache: Arc<Mutex<HashMap<String, String>>>,
}
```
