---
title: Distribution
description: App signing, bundling, platform-specific distribution, and auto-update configuration for Tauri v2 apps
tags: [build, bundle, signing, updater, distribution, dmg, msi, appimage, nsis]
---

# App Signing, Distribution, and Auto-Updates

## Building for Production

```bash
pnpm tauri build
```

Output appears in `src-tauri/target/release/bundle/`:

| Platform | Formats                     |
| -------- | --------------------------- |
| macOS    | `.app`, `.dmg`              |
| Windows  | `.msi`, `.exe` (NSIS)       |
| Linux    | `.AppImage`, `.deb`, `.rpm` |

## Bundle Configuration

```json
{
  "bundle": {
    "active": true,
    "targets": "all",
    "identifier": "com.example.myapp",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": ""
    },
    "macOS": {
      "frameworks": [],
      "minimumSystemVersion": "",
      "signingIdentity": null,
      "entitlements": null
    },
    "linux": {
      "deb": {
        "depends": []
      }
    }
  }
}
```

## macOS Code Signing

Set environment variables for CI:

```bash
export APPLE_CERTIFICATE="base64-encoded-p12-certificate"
export APPLE_CERTIFICATE_PASSWORD="certificate-password"
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAM_ID)"
```

For notarization:

```bash
export APPLE_API_ISSUER="issuer-uuid"
export APPLE_API_KEY="key-id"
export APPLE_API_KEY_PATH="/path/to/AuthKey.p8"
```

## Windows Code Signing

For EV certificates, configure in `tauri.conf.json`:

```json
{
  "bundle": {
    "windows": {
      "certificateThumbprint": "YOUR_CERT_THUMBPRINT",
      "digestAlgorithm": "sha256",
      "timestampUrl": "http://timestamp.digicert.com"
    }
  }
}
```

## Auto-Updater

### Setup

```bash
cargo add tauri-plugin-updater
pnpm add @tauri-apps/plugin-updater
```

```rust
tauri::Builder::default()
    .plugin(tauri_plugin_updater::Builder::new().build())
```

### Generate Signing Keys

```bash
pnpm tauri signer generate -w ~/.tauri/myapp.key
```

Set environment variables:

```bash
export TAURI_SIGNING_PRIVATE_KEY="content-of-private-key"
export TAURI_SIGNING_PRIVATE_KEY_PASSWORD="key-password"
```

### Updater Configuration

```json
{
  "plugins": {
    "updater": {
      "pubkey": "YOUR_PUBLIC_KEY",
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

### Update Endpoint Response

The endpoint must return JSON matching this structure:

```json
{
  "version": "1.0.1",
  "notes": "Bug fixes and performance improvements",
  "pub_date": "2025-01-15T00:00:00Z",
  "platforms": {
    "darwin-aarch64": {
      "signature": "SIGNATURE_STRING",
      "url": "https://releases.myapp.com/myapp-1.0.1-aarch64.app.tar.gz"
    },
    "darwin-x86_64": {
      "signature": "SIGNATURE_STRING",
      "url": "https://releases.myapp.com/myapp-1.0.1-x86_64.app.tar.gz"
    },
    "linux-x86_64": {
      "signature": "SIGNATURE_STRING",
      "url": "https://releases.myapp.com/myapp-1.0.1-x86_64.AppImage.tar.gz"
    },
    "windows-x86_64": {
      "signature": "SIGNATURE_STRING",
      "url": "https://releases.myapp.com/myapp-1.0.1-x86_64-setup.nsis.zip"
    }
  }
}
```

### Check and Install Updates (Frontend)

```ts
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

const update = await check();

if (update) {
  console.log(`Update available: ${update.version}`);

  let downloaded = 0;
  let contentLength = 0;

  await update.downloadAndInstall((event) => {
    switch (event.event) {
      case 'Started':
        contentLength = event.data.contentLength ?? 0;
        break;
      case 'Progress':
        downloaded += event.data.chunkLength;
        console.log(`Downloaded ${downloaded}/${contentLength}`);
        break;
      case 'Finished':
        console.log('Download complete');
        break;
    }
  });

  await relaunch();
}
```

### Check and Install Updates (Rust)

```rust
use tauri_plugin_updater::UpdaterExt;

#[tauri::command]
async fn check_for_updates(app: tauri::AppHandle) -> Result<bool, String> {
    let update = app
        .updater()
        .check()
        .await
        .map_err(|e| e.to_string())?;

    if let Some(update) = update {
        update
            .download_and_install(|_, _| {}, || {})
            .await
            .map_err(|e| e.to_string())?;
        Ok(true)
    } else {
        Ok(false)
    }
}
```

### Updater Permissions

```json
{
  "permissions": ["updater:default", "process:allow-restart"]
}
```

## GitHub Releases as Update Endpoint

Use the CrabNebula or Tauri GitHub Action to publish releases:

```yaml
- uses: tauri-apps/tauri-action@v0
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
    TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
  with:
    tagName: v__VERSION__
    releaseName: 'v__VERSION__'
    releaseBody: 'See the assets for download links.'
    releaseDraft: true
    prerelease: false
```

Configure the updater endpoint to point to GitHub releases:

```json
{
  "plugins": {
    "updater": {
      "endpoints": [
        "https://github.com/owner/repo/releases/latest/download/latest.json"
      ]
    }
  }
}
```
