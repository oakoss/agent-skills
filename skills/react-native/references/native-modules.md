---
title: Native Modules
description: expo-dev-client for custom development builds and Expo Modules API for creating native Swift/Kotlin modules
tags:
  [
    expo-dev-client,
    expo-modules-api,
    native-module,
    Swift,
    Kotlin,
    turbo-module,
    config-plugin,
  ]
---

# Native Modules

## expo-dev-client

Development builds with `expo-dev-client` create a custom version of Expo Go that includes your native dependencies. This enables development with any native library while retaining Expo's developer tools.

### Setup

```bash
npx expo install expo-dev-client
eas build --profile development --platform ios
```

Start the development server for a dev client build:

```bash
npx expo start --dev-client
```

### When Dev Client Is Required

- Installing native libraries not included in Expo Go (e.g., `react-native-ble-plx`)
- Using custom native modules built with Expo Modules API
- Configuring native project settings via config plugins
- Testing push notifications on physical devices

### Development vs Production Flow

```text
Development:
  expo-dev-client → eas build --profile development → npx expo start --dev-client

Production:
  eas build --profile production → eas submit → app store
```

## Expo Modules API

The Expo Modules API enables building native modules in Swift and Kotlin with a declarative API, without touching Objective-C or Java.

### Create a Module

```bash
npx create-expo-module my-module
```

Generated structure:

```sh
my-module/
  src/
    index.ts                    # TypeScript API
    MyModule.ts                 # Module definition
  ios/
    MyModule.swift              # Swift implementation
  android/
    src/main/java/expo/modules/mymodule/
      MyModule.kt              # Kotlin implementation
  expo-module.config.json       # Module configuration
```

### Module Configuration

`expo-module.config.json`:

```json
{
  "platforms": ["ios", "android"],
  "ios": {
    "modules": ["MyModule"]
  },
  "android": {
    "modules": ["expo.modules.mymodule.MyModule"]
  }
}
```

### Swift Module

```swift
import ExpoModulesCore

public class MyModule: Module {
    public func definition() -> ModuleDefinition {
        Name("MyModule")

        Function("hello") { (name: String) -> String in
            return "Hello, \(name)!"
        }

        AsyncFunction("fetchData") { (url: String) -> String in
            let (data, _) = try await URLSession.shared.data(
                from: URL(string: url)!
            )
            return String(data: data, encoding: .utf8) ?? ""
        }

        Events("onStatusChange")

        Property("platform") {
            return "ios"
        }
    }
}
```

### Kotlin Module

```kotlin
package expo.modules.mymodule

import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition

class MyModule : Module() {
    override fun definition() = ModuleDefinition {
        Name("MyModule")

        Function("hello") { name: String ->
            "Hello, $name!"
        }

        AsyncFunction("fetchData") { url: String ->
            java.net.URL(url).readText()
        }

        Events("onStatusChange")

        Property("platform") {
            "android"
        }
    }
}
```

### TypeScript API

```ts
import { requireNativeModule } from 'expo-modules-core';

const MyModule = requireNativeModule('MyModule');

export function hello(name: string): string {
  return MyModule.hello(name);
}

export async function fetchData(url: string): Promise<string> {
  return MyModule.fetchData(url);
}

export const platform: string = MyModule.platform;
```

### Native Views

Expose native UI components to React:

```swift
import ExpoModulesCore

public class MyViewModule: Module {
    public func definition() -> ModuleDefinition {
        Name("MyView")

        View(MyNativeView.self) {
            Prop("color") { (view, color: UIColor) in
                view.backgroundColor = color
            }

            Events("onTap")
        }
    }
}
```

```tsx
import { requireNativeViewManager } from 'expo-modules-core';

const NativeView = requireNativeViewManager('MyView');

function MyView({ color, onTap }: { color: string; onTap: () => void }) {
  return <NativeView color={color} onTap={onTap} style={{ flex: 1 }} />;
}
```

## Config Plugins

Config plugins modify native project configuration during prebuild without ejecting:

```ts
import { type ConfigPlugin, withInfoPlist } from 'expo/config-plugins';

const withCustomConfig: ConfigPlugin = (config) => {
  return withInfoPlist(config, (modConfig) => {
    modConfig.modResults.NSLocationWhenInUseUsageDescription =
      'Required for nearby search';
    return modConfig;
  });
};

export default withCustomConfig;
```

Register in `app.json`:

```json
{
  "expo": {
    "plugins": ["./plugins/withCustomConfig"]
  }
}
```

### Common Config Plugin Use Cases

| Plugin                  | Purpose                                        |
| ----------------------- | ---------------------------------------------- |
| `expo-camera`           | Camera permissions strings                     |
| `expo-notifications`    | Push notification entitlements                 |
| `expo-location`         | Background location modes                      |
| `expo-build-properties` | Native build settings (min SDK, Swift version) |

```json
{
  "expo": {
    "plugins": [
      [
        "expo-build-properties",
        {
          "ios": {
            "deploymentTarget": "15.1"
          },
          "android": {
            "minSdkVersion": 24,
            "compileSdkVersion": 34
          }
        }
      ]
    ]
  }
}
```

## Local Modules

For project-specific native code, create modules within the project:

```sh
modules/
  my-local-module/
    src/
      index.ts
    ios/
      MyLocalModule.swift
    android/
      src/main/java/expo/modules/mylocalmodule/
        MyLocalModule.kt
    expo-module.config.json
```

Register in `package.json`:

```json
{
  "expo": {
    "autolinking": {
      "nativeModulesDir": "./modules"
    }
  }
}
```

Local modules are automatically linked during prebuild.
