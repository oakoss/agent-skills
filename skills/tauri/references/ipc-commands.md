---
title: IPC Commands
description: Defining Rust commands, invoking from frontend, events, channels, and error handling across the IPC boundary
tags: [command, invoke, emit, listen, channel, ipc, events, error-handling]
---

# IPC Commands

## Defining Commands

Commands are Rust functions annotated with `#[tauri::command]`:

```rust
#[tauri::command]
fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}
```

Register all commands in a single `generate_handler!` call:

```rust
tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![greet, another_command])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

## Invoking from Frontend

```ts
import { invoke } from '@tauri-apps/api/core';

const greeting = await invoke<string>('greet', { name: 'World' });
```

Arguments are passed as a camelCase JSON object. Rust parameter names in snake_case are automatically mapped from camelCase.

## Async Commands

Async commands run on a separate Tokio task, keeping the main thread free:

```rust
#[tauri::command]
async fn fetch_data(url: String) -> Result<String, String> {
    let response = reqwest::get(&url)
        .await
        .map_err(|e| e.to_string())?;
    response.text().await.map_err(|e| e.to_string())
}
```

Borrowed types like `&str` and `State<'_, T>` require owned types in async commands. Use `String` instead of `&str`.

## Error Handling

Return `Result<T, E>` where `E` implements `serde::Serialize`:

```rust
use serde::Serialize;

#[derive(Debug, Serialize)]
enum AppError {
    NotFound(String),
    DatabaseError(String),
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AppError::NotFound(msg) => write!(f, "Not found: {msg}"),
            AppError::DatabaseError(msg) => write!(f, "Database error: {msg}"),
        }
    }
}

#[tauri::command]
fn read_file(path: String) -> Result<String, AppError> {
    std::fs::read_to_string(&path)
        .map_err(|e| AppError::NotFound(e.to_string()))
}
```

Frontend receives errors as rejected Promises:

```ts
try {
  const content = await invoke<string>('read_file', { path: '/missing' });
} catch (error) {
  console.error(error);
}
```

## Accessing Special Types in Commands

```rust
#[tauri::command]
fn with_context(
    app: tauri::AppHandle,
    window: tauri::WebviewWindow,
    state: tauri::State<'_, AppState>,
) -> String {
    let label = window.label();
    format!("Called from window: {label}")
}
```

Tauri injects `AppHandle`, `WebviewWindow`, and `State` automatically; they are not passed from the frontend.

## Channels (Streaming Data)

Channels enable streaming data from Rust to the frontend:

```rust
use tauri::ipc::Channel;

#[tauri::command]
fn stream_progress(on_progress: Channel<u32>) {
    for i in 0..=100 {
        on_progress.send(i).unwrap();
        std::thread::sleep(std::time::Duration::from_millis(50));
    }
}
```

```ts
import { invoke, Channel } from '@tauri-apps/api/core';

const onProgress = new Channel<number>();
onProgress.onmessage = (progress) => {
  console.log(`Progress: ${progress}%`);
};

await invoke('stream_progress', { onProgress });
```

## Events

Events provide pub/sub communication between frontend and backend.

### Frontend to Frontend

```ts
import { emit, listen } from '@tauri-apps/api/event';

const unlisten = await listen<string>('user-logged-in', (event) => {
  console.log(event.payload);
});

await emit('user-logged-in', 'alice');

unlisten();
```

### Rust to Frontend

```rust
use tauri::Emitter;

app.emit("backend-event", "payload data").unwrap();
```

### Frontend to Rust

```rust
use tauri::Listener;

app.listen("frontend-event", |event| {
    println!("Received: {:?}", event.payload());
});
```

### Window-Scoped Events

Target events to specific windows:

```ts
import { Window } from '@tauri-apps/api/window';

const mainWindow = new Window('main');
await mainWindow.emit('window-specific-event', { data: 'value' });

const unlisten = await mainWindow.listen('response-event', (event) => {
  console.log(event.payload);
});
```

```rust
use tauri::Emitter;

window.emit("window-specific-event", "data").unwrap();
```

## Raw IPC Request

Access the full request object for advanced use cases:

```rust
use tauri::ipc::Request;

#[tauri::command]
fn raw_handler(request: Request) -> String {
    let headers = request.headers();
    format!("Content-Type: {:?}", headers.get("content-type"))
}
```
