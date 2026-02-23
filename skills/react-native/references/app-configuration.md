---
title: App Configuration
description: app.json/app.config.ts configuration, environment variables, fonts, splash screen, and project setup
tags:
  [
    app-json,
    app-config,
    expo-config,
    fonts,
    splash-screen,
    environment,
    expo-constants,
  ]
---

# App Configuration

## app.json vs app.config.ts

`app.json` is static configuration. `app.config.ts` enables dynamic values and environment variables:

```ts
import { type ExpoConfig, type ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: 'My App',
  slug: 'my-app',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  scheme: 'myapp',
  userInterfaceStyle: 'automatic',
  newArchEnabled: true,
  splash: {
    image: './assets/splash-icon.png',
    resizeMode: 'contain',
    backgroundColor: '#ffffff',
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.example.myapp',
  },
  android: {
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#ffffff',
    },
    package: 'com.example.myapp',
  },
  web: {
    bundler: 'metro',
    favicon: './assets/favicon.png',
  },
  experiments: {
    typedRoutes: true,
  },
  plugins: [
    'expo-router',
    'expo-font',
    [
      'expo-camera',
      {
        cameraPermission: 'Allow $(PRODUCT_NAME) to access your camera.',
      },
    ],
  ],
  extra: {
    apiUrl: process.env.API_URL ?? 'https://api.example.com',
    eas: {
      projectId: 'your-project-id',
    },
  },
});
```

## Environment Variables

### Using .env Files

Expo supports `.env` files with the `EXPO_PUBLIC_` prefix:

```text
EXPO_PUBLIC_API_URL=https://api.example.com
EXPO_PUBLIC_SENTRY_DSN=https://sentry.io/123
```

Access in code:

```tsx
const apiUrl = process.env.EXPO_PUBLIC_API_URL;
```

Variables without the `EXPO_PUBLIC_` prefix are available in config files but not in app code.

### Using expo-constants

Access config values at runtime:

```tsx
import Constants from 'expo-constants';

const apiUrl = Constants.expoConfig?.extra?.apiUrl;
const appVersion = Constants.expoConfig?.version;
```

## Custom Fonts

### Setup with expo-font

```bash
npx expo install expo-font
```

Load fonts in the root layout:

```tsx
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded] = useFonts({
    'Inter-Regular': require('../assets/fonts/Inter-Regular.ttf'),
    'Inter-Bold': require('../assets/fonts/Inter-Bold.ttf'),
  });

  useEffect(() => {
    if (fontsLoaded) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return <Stack />;
}
```

Use in styles:

```tsx
const styles = StyleSheet.create({
  heading: {
    fontFamily: 'Inter-Bold',
    fontSize: 24,
  },
});
```

### Google Fonts

```bash
npx expo install @expo-google-fonts/inter expo-font
```

```tsx
import {
  useFonts,
  Inter_400Regular,
  Inter_700Bold,
} from '@expo-google-fonts/inter';
```

## Splash Screen

Configure in `app.json`:

```json
{
  "expo": {
    "splash": {
      "image": "./assets/splash-icon.png",
      "resizeMode": "contain",
      "backgroundColor": "#1a1a2e"
    },
    "ios": {
      "splash": {
        "image": "./assets/splash-ios.png",
        "resizeMode": "cover"
      }
    },
    "android": {
      "splash": {
        "image": "./assets/splash-android.png",
        "resizeMode": "cover",
        "backgroundColor": "#1a1a2e"
      }
    }
  }
}
```

Control splash visibility programmatically:

```tsx
import * as SplashScreen from 'expo-splash-screen';

SplashScreen.preventAutoHideAsync();

async function initApp() {
  await loadFonts();
  await loadInitialData();
  SplashScreen.hideAsync();
}
```

## Asset Management

### Static Assets

```tsx
import { Image } from 'expo-image';

<Image
  source={require('../assets/logo.png')}
  style={{ width: 200, height: 60 }}
/>;
```

### Asset Bundling

Pre-download assets for offline use:

```tsx
import { Asset } from 'expo-asset';

async function cacheAssets() {
  const images = [
    require('../assets/splash.png'),
    require('../assets/icon.png'),
  ];
  const cacheImages = images.map((image) =>
    Asset.fromModule(image).downloadAsync(),
  );
  await Promise.all(cacheImages);
}
```

## Metro Configuration

Custom Metro config for path aliases and additional file extensions:

```js
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

config.resolver.sourceExts = [...config.resolver.sourceExts, 'mjs', 'cjs'];

module.exports = config;
```

### Path Aliases with tsconfig

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

```tsx
import { Button } from '@/components/Button';
import { useAuth } from '@/hooks/useAuth';
```

Expo's Metro config resolves `tsconfig.json` paths automatically.
