---
title: Sidecar Binaries and Custom Protocols
description: Bundling external binaries as sidecars and registering custom URI scheme protocols in Tauri v2
tags: [sidecar, external-bin, custom-protocol, uri-scheme, shell, binary]
---

# Sidecar Binaries and Custom Protocols

## Sidecar Binaries

Sidecars are external executables bundled with the app. They run as child processes managed by Tauri.

### Configuration

Register sidecar binaries in `tauri.conf.json`:

```json
{
  "bundle": {
    "externalBin": ["binaries/my-sidecar"]
  }
}
```

### Binary Naming

Sidecar binaries must include the target triple in their filename:

```sh
binaries/
├── my-sidecar-x86_64-pc-windows-msvc.exe
├── my-sidecar-x86_64-unknown-linux-gnu
├── my-sidecar-aarch64-apple-darwin
└── my-sidecar-x86_64-apple-darwin
```

The config references the base name without the triple. Tauri resolves the correct binary at runtime.

Find the target triple:

```bash
rustc -Vv | grep host
```

### Running a Sidecar (Rust)

```rust
use tauri_plugin_shell::ShellExt;

#[tauri::command]
async fn run_sidecar(app: tauri::AppHandle) -> Result<String, String> {
    let output = app
        .shell()
        .sidecar("my-sidecar")
        .unwrap()
        .args(["--input", "data.json"])
        .output()
        .await
        .map_err(|e| e.to_string())?;

    if output.status.success() {
        String::from_utf8(output.stdout).map_err(|e| e.to_string())
    } else {
        Err(String::from_utf8(output.stderr).unwrap_or_default())
    }
}
```

### Running a Sidecar (Frontend)

```ts
import { Command } from '@tauri-apps/plugin-shell';

const command = Command.sidecar('binaries/my-sidecar', [
  '--input',
  'data.json',
]);

const output = await command.execute();
console.log('stdout:', output.stdout);
console.log('stderr:', output.stderr);
console.log('exit code:', output.code);
```

### Streaming Sidecar Output

```ts
import { Command } from '@tauri-apps/plugin-shell';

const command = Command.sidecar('binaries/my-sidecar');

command.on('close', (data) => {
  console.log(`Exited with code ${data.code}`);
});

command.stdout.on('data', (line) => {
  console.log(`stdout: ${line}`);
});

command.stderr.on('data', (line) => {
  console.error(`stderr: ${line}`);
});

const child = await command.spawn();
await child.kill();
```

### Sidecar Permissions

```json
{
  "permissions": [
    {
      "identifier": "shell:allow-execute",
      "allow": [{ "name": "binaries/my-sidecar", "sidecar": true }]
    }
  ]
}
```

## Custom Protocols

Register custom URI schemes to serve content from Rust:

```rust
tauri::Builder::default()
    .register_uri_scheme_protocol("myapp", |_ctx, request| {
        let path = request.uri().path();

        let content = match path {
            "/data" => b"Hello from custom protocol".to_vec(),
            _ => b"Not found".to_vec(),
        };

        tauri::http::Response::builder()
            .status(if path == "/data" { 200 } else { 404 })
            .header("content-type", "text/plain")
            .body(content)
            .unwrap()
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

Access from the frontend:

```ts
const response = await fetch('myapp://localhost/data');
const text = await response.text();
```

### Asset Protocol

Tauri includes a built-in `asset` protocol for serving files from the file system:

```html
<img src="asset://localhost/path/to/image.png" />
```

Configure asset protocol scope in capabilities:

```json
{
  "permissions": [
    {
      "identifier": "core:asset:default",
      "allow": [{ "path": "$APPDATA/**" }]
    }
  ]
}
```

### Custom Protocol Use Cases

| Use Case                | Pattern                                              |
| ----------------------- | ---------------------------------------------------- |
| Serve local images      | Asset protocol with scoped paths                     |
| Stream binary data      | Custom protocol returning `application/octet-stream` |
| Dynamic HTML generation | Custom protocol returning `text/html`                |
| Proxy external APIs     | Custom protocol forwarding to HTTP endpoints         |
| Serve from database     | Custom protocol querying embedded DB                 |

## Shell Plugin Setup

Both sidecar and shell commands require the shell plugin:

```bash
cargo add tauri-plugin-shell
pnpm add @tauri-apps/plugin-shell
```

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
```
