---
title: Security Model
description: Capability-based permissions, access control lists, window scoping, and security boundaries in Tauri v2
tags: [security, capabilities, permissions, acl, scope, csp, window-label]
---

# Security Model

## Architecture

Tauri v2 uses a **capability-based permission system** that replaced the v1 allowlist. Every IPC command is inaccessible by default. Access must be explicitly granted through capabilities that scope permissions to specific windows and webviews.

```text
Capability
├── Windows/Webviews (which UI contexts have access)
├── Permissions (which commands are allowed/denied)
│   └── Scopes (restrictions on command arguments)
└── Platforms (optional platform filtering)
```

## Capability Files

Capabilities live in `src-tauri/capabilities/` as JSON or TOML files. All files in this directory are automatically included at build time.

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "main-capability",
  "description": "Main window permissions",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "dialog:default",
    "fs:allow-read-text-file",
    {
      "identifier": "fs:allow-write-text-file",
      "allow": [{ "path": "$APPDATA/**" }]
    }
  ]
}
```

## Permission Identifiers

Permissions follow the pattern `{plugin}:{action}`:

| Pattern                   | Meaning                              |
| ------------------------- | ------------------------------------ |
| `core:default`            | Core default permissions set         |
| `dialog:default`          | All default dialog permissions       |
| `fs:allow-read-text-file` | Allow reading text files             |
| `fs:deny-read-text-file`  | Explicitly deny reading text files   |
| `shell:allow-open`        | Allow opening URLs/paths             |
| `notification:default`    | All default notification permissions |

Deny permissions always take precedence over allow permissions.

## Scoped Permissions

Restrict command arguments with scopes:

```json
{
  "identifier": "fs:allow-read-text-file",
  "allow": [{ "path": "$APPCONFIG/**" }, { "path": "$APPDATA/**" }]
}
```

```json
{
  "identifier": "fs:allow-read-text-file",
  "deny": [{ "path": "$HOME/.ssh/**" }]
}
```

## Path Variables

| Variable        | Description                   |
| --------------- | ----------------------------- |
| `$APPCONFIG`    | App-specific config directory |
| `$APPDATA`      | App-specific data directory   |
| `$APPLOCALDATA` | App-specific local data       |
| `$APPCACHE`     | App-specific cache directory  |
| `$APPLOG`       | App-specific log directory    |
| `$HOME`         | User home directory           |
| `$DESKTOP`      | User desktop directory        |
| `$DOCUMENT`     | User documents directory      |
| `$DOWNLOAD`     | User downloads directory      |
| `$RESOURCE`     | App resource directory        |
| `$TEMP`         | System temp directory         |

## Window Scoping

Capabilities target specific windows by label:

```json
{
  "identifier": "settings-capability",
  "windows": ["settings"],
  "permissions": ["store:default"]
}
```

Use `"windows": ["*"]` to grant to all windows (use sparingly).

## Platform-Specific Capabilities

```json
{
  "identifier": "desktop-only",
  "windows": ["main"],
  "platforms": ["linux", "macOS", "windows"],
  "permissions": ["shell:allow-open"]
}
```

```json
{
  "identifier": "mobile-only",
  "windows": ["main"],
  "platforms": ["iOS", "android"],
  "permissions": ["haptics:default", "biometric:default"]
}
```

## Remote Domain Access

Grant capabilities to remote domains loaded in webviews:

```json
{
  "identifier": "remote-api",
  "windows": ["main"],
  "remote": {
    "urls": ["https://*.myapp.com"]
  },
  "permissions": ["core:event:default"]
}
```

## Content Security Policy

Configure CSP in `tauri.conf.json`:

```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' asset: https://asset.localhost; connect-src ipc: http://ipc.localhost"
    }
  }
}
```

## Custom Command Permissions

For custom commands, create permission files in `src-tauri/permissions/`:

```json
{
  "identifier": "allow-greet",
  "description": "Allows calling the greet command",
  "commands": {
    "allow": ["greet"]
  }
}
```

Then reference in capabilities:

```json
{
  "permissions": ["allow-greet"]
}
```

## Security Boundaries

**What the capability system protects against:**

- Frontend code accessing unauthorized system APIs
- Compromised frontend escalating to full system access
- One window accessing another window's capabilities

**What it does NOT protect against:**

- Malicious Rust backend code (full system access by design)
- Overly permissive scope configurations
- WebView zero-day vulnerabilities
- Compromised build environment

## Key Rules

| Rule                                   | Explanation                                             |
| -------------------------------------- | ------------------------------------------------------- |
| Labels for security, not titles        | Window labels (not display titles) determine access     |
| Deny overrides allow                   | A deny permission always wins over allow                |
| Capabilities merge                     | Multiple capabilities for a window merge permissions    |
| No iframe distinction on Linux/Android | Requests from iframes and windows are indistinguishable |
| Scopes are AND-combined                | Multiple allow scopes are combined (any match works)    |
