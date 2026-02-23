---
title: EAS Workflows
description: EAS Build, Submit, and Update configuration for CI/CD, app store deployment, and OTA updates
tags:
  [
    eas-build,
    eas-submit,
    eas-update,
    ota,
    app-store,
    eas-json,
    channels,
    profiles,
  ]
---

# EAS Workflows

Expo Application Services (EAS) provides cloud build, app store submission, and over-the-air (OTA) update services.

## EAS Build

### Default Configuration

`eas.json` at project root:

```json
{
  "cli": {
    "version": ">= 13.0.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "channel": "development"
    },
    "preview": {
      "distribution": "internal",
      "channel": "preview"
    },
    "production": {
      "channel": "production",
      "autoIncrement": true
    }
  }
}
```

### Build Commands

```bash
eas build --profile development --platform ios
eas build --profile development --platform android
eas build --profile production --platform all
eas build --profile preview --platform ios --local
```

### Build Profiles

| Profile       | Distribution      | Purpose                                    |
| ------------- | ----------------- | ------------------------------------------ |
| `development` | `internal`        | Dev client for testing with native modules |
| `preview`     | `internal`        | Internal testing builds (ad-hoc/APK)       |
| `production`  | `store` (default) | App store release builds                   |

### Platform-Specific Overrides

```json
{
  "build": {
    "production": {
      "ios": {
        "buildConfiguration": "Release",
        "image": "macos-ventura-14.2-xcode-15.3"
      },
      "android": {
        "buildType": "app-bundle",
        "image": "ubuntu-22.04-jdk-17-ndk-25"
      }
    }
  }
}
```

### Environment Variables

```json
{
  "build": {
    "production": {
      "env": {
        "API_URL": "https://api.example.com"
      }
    },
    "preview": {
      "env": {
        "API_URL": "https://staging.api.example.com"
      }
    }
  }
}
```

Access in code via `process.env.API_URL` or `expo-constants`.

## EAS Submit

Automated app store submission after build completion.

### Submit Configuration

```json
{
  "submit": {
    "production": {
      "ios": {
        "appleId": "team@example.com",
        "ascAppId": "1234567890",
        "appleTeamId": "AB12XYZ34S"
      },
      "android": {
        "track": "internal",
        "serviceAccountKeyPath": "./google-service-account.json"
      }
    }
  }
}
```

### Submit Commands

```bash
eas submit -p ios --latest
eas submit -p android --latest
eas submit -p ios --id <build-id>
eas build --profile production --platform all --auto-submit
```

The `--auto-submit` flag triggers submission immediately after a successful build.

### Android Tracks

| Track        | Purpose                              |
| ------------ | ------------------------------------ |
| `internal`   | Internal testing (up to 100 testers) |
| `alpha`      | Closed testing                       |
| `beta`       | Open testing                         |
| `production` | Public release                       |

## EAS Update (OTA)

Delivers JavaScript and asset updates without app store review. Only works for JS/asset changes -- native code changes require a new build.

### Publishing Updates

```bash
eas update --branch production --message "Fix checkout bug"
eas update --branch preview --message "New feature preview"
eas update --channel development
```

### Channel-Branch Mapping

Channels connect builds to update branches:

```text
Build Profile → Channel → Branch
production   → production → production
preview      → preview    → preview
development  → development → development
```

Map a channel to a branch:

```bash
eas channel:edit production --branch production
eas channel:edit preview --branch staging
```

### Runtime Version Policy

Configure in `app.json` to control which builds receive which updates:

```json
{
  "expo": {
    "runtimeVersion": {
      "policy": "appVersion"
    }
  }
}
```

| Policy          | Behavior                                |
| --------------- | --------------------------------------- |
| `appVersion`    | Runtime version matches `version` field |
| `nativeVersion` | Based on native build number            |
| `fingerprint`   | Auto-generated from native dependencies |

`fingerprint` is recommended -- it automatically detects native dependency changes and prevents incompatible updates.

### Checking for Updates Programmatically

```tsx
import * as Updates from 'expo-updates';

async function checkForUpdates() {
  if (__DEV__) return;

  const update = await Updates.checkForUpdateAsync();
  if (update.isAvailable) {
    await Updates.fetchUpdateAsync();
    await Updates.reloadAsync();
  }
}
```

### Rollback

```bash
eas update:rollback --branch production
```

Rollback creates a new update pointing to the previous version.

## CI/CD Integration

### GitHub Actions Example

```yaml
name: EAS Build
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - uses: expo/expo-github-action@v8
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - run: npm install
      - run: eas build --profile production --platform all --non-interactive
      - run: eas submit --platform all --latest --non-interactive
```

### EAS Metadata (Store Listings)

Manage app store metadata alongside code:

```bash
eas metadata:pull
eas metadata:push
```

Configuration in `store.config.json` at project root handles app descriptions, screenshots, and store-specific fields.
