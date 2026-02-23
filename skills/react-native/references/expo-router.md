---
title: Expo Router Navigation
description: File-based routing with Expo Router including stack, tabs, drawer navigators, typed routes, deep linking, and layout patterns
tags:
  [
    expo-router,
    Stack,
    Tabs,
    Drawer,
    navigation,
    deep-linking,
    typed-routes,
    layout,
  ]
---

# Expo Router Navigation

Expo Router provides file-based routing for React Native, mapping filesystem paths directly to navigation routes. It wraps React Navigation and adds automatic deep linking, typed routes, and universal links.

## File System Structure

```sh
app/
  _layout.tsx           # Root layout (Stack, Tabs, etc.)
  index.tsx             # / route
  about.tsx             # /about route
  settings/
    _layout.tsx         # Nested layout for /settings/*
    index.tsx           # /settings route
    profile.tsx         # /settings/profile route
  [id].tsx              # Dynamic route: /123, /abc
  [...rest].tsx         # Catch-all: /any/nested/path
  +not-found.tsx        # 404 handler
```

## Root Stack Layout

```tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      <Stack.Screen name="+not-found" />
    </Stack>
  );
}
```

## Tab Navigation

Create a `(tabs)` directory group with its own `_layout.tsx`:

```sh
app/
  (tabs)/
    _layout.tsx         # Tab navigator
    index.tsx           # First tab (Home)
    explore.tsx         # Second tab (Explore)
    profile.tsx         # Third tab (Profile)
```

```tsx
import { Tabs } from 'expo-router';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => (
            <MaterialIcons name="home" size={28} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarIcon: ({ color }) => (
            <MaterialIcons name="search" size={28} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color }) => (
            <MaterialIcons name="person" size={28} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
```

## Drawer Navigation

Requires `@react-navigation/drawer` and `react-native-gesture-handler`:

```tsx
import { Drawer } from 'expo-router/drawer';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

export default function DrawerLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <Drawer>
        <Drawer.Screen name="index" options={{ drawerLabel: 'Home' }} />
        <Drawer.Screen name="settings" options={{ drawerLabel: 'Settings' }} />
      </Drawer>
    </GestureHandlerRootView>
  );
}
```

## Navigation Patterns

### Programmatic Navigation

```tsx
import { router } from 'expo-router';

router.push('/profile/123');
router.replace('/login');
router.back();
router.canGoBack();
router.dismiss();
router.dismissAll();
```

### Link Component

```tsx
import { Link } from 'expo-router';

function NavLink() {
  return (
    <Link href="/profile/123" asChild>
      <Pressable>
        <Text>View Profile</Text>
      </Pressable>
    </Link>
  );
}
```

### Dynamic Routes

File: `app/user/[id].tsx`

```tsx
import { useLocalSearchParams } from 'expo-router';

export default function UserScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <Text>User: {id}</Text>;
}
```

## Route Groups

Parenthesized directories create logical groups without affecting URL paths:

```sh
app/
  (auth)/
    _layout.tsx         # Auth-specific layout
    login.tsx           # /login
    register.tsx        # /register
  (app)/
    _layout.tsx         # Authenticated layout
    index.tsx           # /
    profile.tsx         # /profile
```

## Typed Routes

Enable in `app.json`:

```json
{
  "expo": {
    "experiments": {
      "typedRoutes": true
    }
  }
}
```

Provides compile-time route validation:

```tsx
import { router } from 'expo-router';

router.push('/profile/123');
router.push('/nonexistent');
```

## Modal Screens

```tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen
        name="modal"
        options={{
          presentation: 'modal',
          headerTitle: 'Details',
        }}
      />
    </Stack>
  );
}
```

Present modals with `router.push('/modal')`. Use `router.dismiss()` to close.

## Deep Linking

Expo Router generates deep link handling automatically. Configure the `scheme` in `app.json`:

```json
{
  "expo": {
    "scheme": "myapp"
  }
}
```

Links like `myapp://profile/123` automatically resolve to `app/profile/[id].tsx`.

## Screen Options from Route

Set header options dynamically within a route file:

```tsx
import { Stack } from 'expo-router';

export default function ProfileScreen() {
  return (
    <>
      <Stack.Screen options={{ title: 'My Profile' }} />
      <View>
        <Text>Profile content</Text>
      </View>
    </>
  );
}
```

## Error Boundaries

```tsx
import { ErrorBoundary } from 'expo-router';

export { ErrorBoundary };

export default function Screen() {
  return <RiskyComponent />;
}
```

Export `ErrorBoundary` from any route file to catch errors at that level.
