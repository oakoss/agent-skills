---
title: Window Management
description: Creating, configuring, and managing windows and webviews in Tauri v2 multi-window applications
tags: [window, webview, multi-window, WebviewWindowBuilder, label, navigation]
---

# Window Management

## Static Windows in Config

Define windows in `tauri.conf.json`:

```json
{
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "My App",
        "width": 800,
        "height": 600,
        "resizable": true,
        "decorations": true,
        "transparent": false,
        "url": "/"
      },
      {
        "label": "settings",
        "title": "Settings",
        "width": 400,
        "height": 300,
        "url": "/settings"
      }
    ]
  }
}
```

## Creating Windows at Runtime (Rust)

```rust
use tauri::WebviewWindowBuilder;
use tauri::WebviewUrl;

#[tauri::command]
async fn open_settings(app: tauri::AppHandle) -> Result<(), String> {
    let _window = WebviewWindowBuilder::new(
        &app,
        "settings",
        WebviewUrl::App("/settings".into()),
    )
    .title("Settings")
    .inner_size(400.0, 300.0)
    .resizable(false)
    .build()
    .map_err(|e| e.to_string())?;

    Ok(())
}
```

## Creating Windows at Runtime (Frontend)

```ts
import { WebviewWindow } from '@tauri-apps/api/webviewWindow';

const settingsWindow = new WebviewWindow('settings', {
  url: '/settings',
  title: 'Settings',
  width: 400,
  height: 300,
  resizable: false,
  center: true,
});

settingsWindow.once('tauri://created', () => {
  console.log('Window created');
});

settingsWindow.once('tauri://error', (e) => {
  console.error('Window creation failed', e);
});
```

## Window Operations

```ts
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';

const appWindow = getCurrentWebviewWindow();

await appWindow.setTitle('New Title');
await appWindow.setSize({ type: 'Logical', width: 800, height: 600 });
await appWindow.setPosition({ type: 'Logical', x: 100, y: 100 });
await appWindow.center();
await appWindow.setFullscreen(true);
await appWindow.minimize();
await appWindow.maximize();
await appWindow.unmaximize();
await appWindow.setAlwaysOnTop(true);
await appWindow.setDecorations(false);
await appWindow.hide();
await appWindow.show();
await appWindow.close();
```

## Window Events

```ts
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';

const appWindow = getCurrentWebviewWindow();

const unlisten = await appWindow.onCloseRequested(async (event) => {
  const confirmed = await confirm('Are you sure you want to close?');
  if (!confirmed) {
    event.preventDefault();
  }
});

await appWindow.onResized(({ payload: size }) => {
  console.log(`Resized to ${size.width}x${size.height}`);
});

await appWindow.onMoved(({ payload: position }) => {
  console.log(`Moved to ${position.x}, ${position.y}`);
});

await appWindow.onFocusChanged(({ payload: focused }) => {
  console.log(`Window ${focused ? 'focused' : 'unfocused'}`);
});
```

## Inter-Window Communication

Windows communicate through the event system. Events can target specific windows or broadcast globally:

```ts
import { emit, listen } from '@tauri-apps/api/event';

await emit('theme-changed', { theme: 'dark' });

const unlisten = await listen<{ theme: string }>('theme-changed', (event) => {
  applyTheme(event.payload.theme);
});
```

From Rust, emit to a specific window:

```rust
use tauri::{Emitter, Manager};

#[tauri::command]
fn notify_window(app: tauri::AppHandle, label: String, message: String) {
    if let Some(window) = app.get_webview_window(&label) {
        window.emit("notification", message).unwrap();
    }
}
```

## Window Builder Options

| Option              | Type      | Description                           |
| ------------------- | --------- | ------------------------------------- |
| `title`             | `String`  | Window title bar text                 |
| `inner_size`        | `f64,f64` | Content area dimensions               |
| `min_inner_size`    | `f64,f64` | Minimum resize dimensions             |
| `max_inner_size`    | `f64,f64` | Maximum resize dimensions             |
| `resizable`         | `bool`    | Allow user resizing                   |
| `fullscreen`        | `bool`    | Start in fullscreen                   |
| `decorations`       | `bool`    | Show native title bar and borders     |
| `transparent`       | `bool`    | Transparent window background         |
| `always_on_top`     | `bool`    | Float above other windows             |
| `visible`           | `bool`    | Show window immediately               |
| `center`            | `()`      | Center window on screen               |
| `focused`           | `bool`    | Focus window on creation              |
| `content_protected` | `bool`    | Prevent screenshots of window content |

## Permissions Required

Add window permissions in capabilities:

```json
{
  "permissions": [
    "core:window:allow-create",
    "core:window:allow-close",
    "core:window:allow-set-title",
    "core:window:allow-set-size",
    "core:window:allow-center"
  ]
}
```
