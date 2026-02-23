---
title: State Management
description: Application state with Tauri's managed state, thread-safe patterns, and accessing state across commands and event handlers
tags: [state, manage, mutex, tokio, apphandle, manager]
---

# State Management

## Basic Setup

Register state during app setup with `app.manage()`:

```rust
use std::sync::Mutex;

struct AppData {
    welcome_message: String,
}

struct Counter {
    value: u32,
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            app.manage(AppData {
                welcome_message: "Welcome to Tauri!".into(),
            });
            app.manage(Mutex::new(Counter { value: 0 }));
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_welcome, increment])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Accessing State in Commands

Tauri injects state via the `State` extractor:

```rust
use tauri::State;

#[tauri::command]
fn get_welcome(data: State<'_, AppData>) -> String {
    data.welcome_message.clone()
}
```

## Mutable State with Mutex

Wrap mutable state in `std::sync::Mutex`:

```rust
use std::sync::Mutex;
use tauri::State;

#[tauri::command]
fn increment(counter: State<'_, Mutex<Counter>>) -> u32 {
    let mut counter = counter.lock().unwrap();
    counter.value += 1;
    counter.value
}
```

## Async Commands with Tokio Mutex

When holding a lock across `.await` points, use `tokio::sync::Mutex`:

```rust
use tokio::sync::Mutex;
use tauri::State;

struct AsyncDb {
    connection: String,
}

#[tauri::command]
async fn query_db(db: State<'_, Mutex<AsyncDb>>) -> Result<String, String> {
    let db = db.lock().await;
    Ok(format!("Connected to: {}", db.connection))
}
```

Standard `std::sync::Mutex` should be preferred unless the lock must be held across await points, because Tokio's mutex has slightly higher overhead.

## Accessing State Outside Commands

Use the `Manager` trait through `AppHandle`:

```rust
use std::sync::Mutex;
use tauri::Manager;

fn setup_event_handlers(app: &tauri::AppHandle) {
    let app_handle = app.clone();
    app.listen("some-event", move |_event| {
        let state = app_handle.state::<Mutex<Counter>>();
        let mut counter = state.lock().unwrap();
        counter.value += 1;
    });
}
```

## State in Plugin Setup

Plugins manage their own state through the plugin builder:

```rust
pub fn init<R: tauri::Runtime>() -> tauri::plugin::TauriPlugin<R> {
    tauri::plugin::Builder::new("my-plugin")
        .setup(|app, _api| {
            app.manage(PluginState::default());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![plugin_command])
        .build()
}
```

## Key Rules

| Rule                       | Explanation                                              |
| -------------------------- | -------------------------------------------------------- |
| No `Arc` wrapper needed    | Tauri's `State` handles reference counting internally    |
| One type per `manage` call | Each unique type can only be managed once                |
| Type must match exactly    | Wrong type in `State<'_, T>` causes a runtime panic      |
| Mutex for mutability       | Shared state across threads requires interior mutability |
| `State` is read-only ref   | The `State` wrapper provides `&T`, not `&mut T`          |
