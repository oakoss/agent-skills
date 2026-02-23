---
title: System Tray
description: System tray icons, menus, and event handling in Tauri v2 using TrayIconBuilder
tags: [tray, system-tray, TrayIconBuilder, menu, MenuItem, tray-icon]
---

# System Tray

## Setup

Enable the tray feature in `Cargo.toml`:

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "image-png"] }
```

## Basic Tray Icon

```rust
use tauri::tray::TrayIconBuilder;

tauri::Builder::default()
    .setup(|app| {
        let tray = TrayIconBuilder::new()
            .icon(app.default_window_icon().unwrap().clone())
            .tooltip("My App")
            .build(app)?;
        Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

## Tray with Menu

```rust
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem};
use tauri::tray::TrayIconBuilder;

tauri::Builder::default()
    .setup(|app| {
        let show = MenuItem::with_id(app, "show", "Show Window", true, None::<&str>)?;
        let hide = MenuItem::with_id(app, "hide", "Hide Window", true, None::<&str>)?;
        let separator = PredefinedMenuItem::separator(app)?;
        let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;

        let menu = Menu::with_items(app, &[&show, &hide, &separator, &quit])?;

        let _tray = TrayIconBuilder::new()
            .icon(app.default_window_icon().unwrap().clone())
            .menu(&menu)
            .menu_on_left_click(false)
            .on_menu_event(|app, event| match event.id.as_ref() {
                "show" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                "hide" => {
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.hide();
                    }
                }
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            })
            .build(app)?;

        Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

## Tray Icon Events

Handle click events on the tray icon itself:

```rust
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};

TrayIconBuilder::new()
    .on_tray_icon_event(|tray, event| match event {
        TrayIconEvent::Click {
            button: MouseButton::Left,
            button_state: MouseButtonState::Up,
            ..
        } => {
            let app = tray.app_handle();
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }
        TrayIconEvent::DoubleClick {
            button: MouseButton::Left,
            ..
        } => {
            let app = tray.app_handle();
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.maximize();
            }
        }
        _ => {}
    })
    .build(app)?;
```

## Submenus

```rust
use tauri::menu::{Menu, MenuItem, Submenu};

let theme_light = MenuItem::with_id(app, "theme-light", "Light", true, None::<&str>)?;
let theme_dark = MenuItem::with_id(app, "theme-dark", "Dark", true, None::<&str>)?;
let theme_menu = Submenu::with_items(app, "Theme", true, &[&theme_light, &theme_dark])?;

let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;

let menu = Menu::with_items(app, &[&theme_menu, &quit])?;
```

## Check Menu Items

```rust
use tauri::menu::CheckMenuItem;

let auto_start = CheckMenuItem::with_id(
    app,
    "auto-start",
    "Start on Login",
    true,
    false,
    None::<&str>,
)?;
```

## Dynamic Tray Updates

Update tray properties at runtime:

```rust
use tauri::Manager;

#[tauri::command]
fn update_tray_tooltip(app: tauri::AppHandle, message: String) -> Result<(), String> {
    if let Some(tray) = app.tray_by_id("main") {
        tray.set_tooltip(Some(&message)).map_err(|e| e.to_string())?;
    }
    Ok(())
}
```

## Named Tray Icons

Create tray with an explicit ID for later reference:

```rust
TrayIconBuilder::with_id("main")
    .icon(app.default_window_icon().unwrap().clone())
    .build(app)?;
```

## Permissions

Tray functionality requires capabilities:

```json
{
  "permissions": ["core:tray:default", "core:menu:default"]
}
```

## Platform Notes

| Feature            | macOS | Windows | Linux |
| ------------------ | ----- | ------- | ----- |
| Left-click event   | Yes   | Yes     | Yes   |
| Right-click menu   | Yes   | Yes     | Yes   |
| Double-click       | Yes   | Yes     | No    |
| Cursor enter/leave | Yes   | Yes     | No    |
| Animated icons     | Yes   | No      | No    |
