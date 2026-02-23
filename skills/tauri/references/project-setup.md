---
title: Project Setup
description: Scaffolding a Tauri v2 project, directory structure, configuration files, and development workflow
tags:
  [
    setup,
    scaffold,
    tauri.conf.json,
    cargo,
    create-tauri-app,
    directory-structure,
  ]
---

# Project Setup

## Scaffolding

Create a new Tauri project with the official scaffolding tool:

```bash
pnpm create tauri-app my-app
```

Or with Cargo:

```bash
cargo create-tauri-app my-app
```

The scaffolder prompts for frontend framework (React, Svelte, Vue, Solid, vanilla) and package manager. It generates both the Rust backend and frontend project in one step.

## Directory Structure

```sh
my-app/
├── src/                   # Frontend source (framework-dependent)
│   ├── App.tsx
│   └── main.ts
├── src-tauri/             # Rust backend
│   ├── Cargo.toml         # Rust dependencies
│   ├── tauri.conf.json    # Tauri configuration
│   ├── capabilities/      # Permission capability files
│   │   └── default.json
│   ├── icons/             # App icons (generated)
│   ├── src/
│   │   ├── main.rs        # Desktop entry point
│   │   └── lib.rs         # Shared logic (desktop + mobile)
│   └── gen/               # Auto-generated code (do not edit)
├── package.json
└── vite.config.ts         # Or equivalent bundler config
```

## Entry Points

Desktop and mobile share `lib.rs` for core logic. The `main.rs` is desktop-only:

```rust
// src-tauri/src/main.rs
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    app_lib::run();
}
```

```rust
// src-tauri/src/lib.rs
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

## Configuration: tauri.conf.json

Core configuration lives in `src-tauri/tauri.conf.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-utils/schema.json",
  "productName": "my-app",
  "version": "0.1.0",
  "identifier": "com.example.my-app",
  "build": {
    "frontendDist": "../dist",
    "devUrl": "http://localhost:5173",
    "beforeDevCommand": "pnpm dev",
    "beforeBuildCommand": "pnpm build"
  },
  "app": {
    "windows": [
      {
        "title": "My App",
        "width": 800,
        "height": 600,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": "default-src 'self'; style-src 'self' 'unsafe-inline'"
    }
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ]
  }
}
```

## Cargo.toml Essentials

```toml
[dependencies]
tauri = { version = "2", features = [] }
tauri-build = { version = "2", features = [] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

Add feature flags as needed:

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon", "image-png"] }
```

## Development Workflow

```bash
# Start dev server (frontend HMR + Rust recompilation)
pnpm tauri dev

# Build production bundle
pnpm tauri build

# Generate app icons from a source image
pnpm tauri icon path/to/icon.png

# Run on Android emulator
pnpm tauri android dev

# Run on iOS simulator
pnpm tauri ios dev
```

## Mobile Setup

Initialize mobile targets after project creation:

```bash
pnpm tauri android init
pnpm tauri ios init
```

This creates `src-tauri/gen/android/` and `src-tauri/gen/apple/` directories with platform-specific project files. Mobile builds use the same `lib.rs` entry point annotated with `#[tauri::mobile_entry_point]`.

## Environment Variables

| Variable                             | Purpose                            |
| ------------------------------------ | ---------------------------------- |
| `TAURI_SIGNING_PRIVATE_KEY`          | Private key for update signing     |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | Password for signing key           |
| `APPLE_CERTIFICATE`                  | Base64-encoded signing certificate |
| `APPLE_CERTIFICATE_PASSWORD`         | Certificate password               |
| `APPLE_SIGNING_IDENTITY`             | Code signing identity              |
