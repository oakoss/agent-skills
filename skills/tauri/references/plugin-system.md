---
title: Plugin System
description: Using official Tauri v2 plugins, adding plugins to projects, and plugin permissions configuration
tags:
  [
    plugin,
    clipboard,
    dialog,
    notification,
    updater,
    deep-link,
    fs,
    shell,
    store,
    autostart,
  ]
---

# Plugin System

## Adding a Plugin

Each Tauri plugin has a Rust crate and an optional NPM package for frontend APIs.

### Rust Side

```bash
cargo add tauri-plugin-dialog
```

Register in the builder chain:

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_dialog::init())
    .plugin(tauri_plugin_clipboard_manager::init())
    .plugin(tauri_plugin_notification::init())
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
```

### Frontend Side

```bash
pnpm add @tauri-apps/plugin-dialog
```

```ts
import { open, save } from '@tauri-apps/plugin-dialog';
```

### Permissions

Add plugin permissions in `src-tauri/capabilities/default.json`:

```json
{
  "permissions": [
    "core:default",
    "dialog:default",
    "clipboard-manager:allow-write-text",
    "clipboard-manager:allow-read-text",
    "notification:default"
  ]
}
```

## Official Plugins Reference

### Dialog

```ts
import { open, save, message, ask, confirm } from '@tauri-apps/plugin-dialog';

const selected = await open({
  multiple: true,
  filters: [{ name: 'Images', extensions: ['png', 'jpg'] }],
});

const savePath = await save({
  defaultPath: 'document.txt',
  filters: [{ name: 'Text', extensions: ['txt'] }],
});

await message('Operation complete', { title: 'Success', kind: 'info' });

const yes = await ask('Delete this file?', {
  title: 'Confirm',
  kind: 'warning',
});
```

### Clipboard

```ts
import { writeText, readText } from '@tauri-apps/plugin-clipboard-manager';

await writeText('Copied text');
const text = await readText();
```

### Notification

```ts
import {
  isPermissionGranted,
  requestPermission,
  sendNotification,
} from '@tauri-apps/plugin-notification';

let permitted = await isPermissionGranted();
if (!permitted) {
  const permission = await requestPermission();
  permitted = permission === 'granted';
}

if (permitted) {
  sendNotification({ title: 'Tauri', body: 'Hello from Tauri!' });
}
```

### File System

```bash
cargo add tauri-plugin-fs
pnpm add @tauri-apps/plugin-fs
```

```ts
import { readTextFile, writeTextFile, exists } from '@tauri-apps/plugin-fs';
import { BaseDirectory } from '@tauri-apps/api/path';

const content = await readTextFile('config.json', {
  baseDir: BaseDirectory.AppConfig,
});

await writeTextFile('config.json', JSON.stringify(config), {
  baseDir: BaseDirectory.AppConfig,
});

const fileExists = await exists('config.json', {
  baseDir: BaseDirectory.AppConfig,
});
```

File system permissions use path scopes:

```json
{
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [{ "path": "$APPCONFIG/**" }]
    },
    {
      "identifier": "fs:allow-write-text-file",
      "allow": [{ "path": "$APPCONFIG/**" }]
    }
  ]
}
```

### Store (Persistent Key-Value)

```bash
cargo add tauri-plugin-store
pnpm add @tauri-apps/plugin-store
```

```ts
import { load } from '@tauri-apps/plugin-store';

const store = await load('settings.json', { autoSave: true });

await store.set('theme', 'dark');
const theme = await store.get<string>('theme');

await store.delete('theme');
await store.save();
```

### Shell (Opener)

```bash
cargo add tauri-plugin-opener
pnpm add @tauri-apps/plugin-opener
```

```ts
import { openUrl, openPath } from '@tauri-apps/plugin-opener';

await openUrl('https://tauri.app');
await openPath('/path/to/file.pdf');
```

### Deep Link

```bash
cargo add tauri-plugin-deep-link
pnpm add @tauri-apps/plugin-deep-link
```

Register the scheme in `tauri.conf.json`:

```json
{
  "plugins": {
    "deep-link": {
      "desktop": {
        "schemes": ["myapp"]
      }
    }
  }
}
```

```ts
import { onOpenUrl } from '@tauri-apps/plugin-deep-link';

await onOpenUrl((urls) => {
  console.log('Deep link received:', urls);
});
```

### Autostart

```bash
cargo add tauri-plugin-autostart
```

```rust
use tauri_plugin_autostart::MacosLauncher;

tauri::Builder::default()
    .plugin(tauri_plugin_autostart::init(
        MacosLauncher::LaunchAgent,
        None,
    ))
```

### Global Shortcut

```bash
cargo add tauri-plugin-global-shortcut
pnpm add @tauri-apps/plugin-global-shortcut
```

```ts
import { register } from '@tauri-apps/plugin-global-shortcut';

await register('CommandOrControl+Shift+C', (event) => {
  if (event.state === 'Pressed') {
    console.log('Shortcut triggered');
  }
});
```

## Plugin Naming Convention

| Component      | Pattern                             |
| -------------- | ----------------------------------- |
| Cargo crate    | `tauri-plugin-{name}`               |
| NPM package    | `@tauri-apps/plugin-{name}`         |
| Permission ID  | `{name}:action` or `{name}:default` |
| Config section | `plugins.{name}`                    |
