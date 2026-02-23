---
title: NativeWind Integration
description: NativeWind v4 setup and patterns for using Tailwind CSS utility classes in React Native
tags:
  [
    nativewind,
    tailwind,
    className,
    styling,
    dark-mode,
    responsive,
    react-native-css,
  ]
---

# NativeWind Integration

NativeWind v4 brings Tailwind CSS to React Native, enabling `className` prop styling with the full Tailwind utility set. It compiles Tailwind classes to React Native styles at build time.

## Setup

```bash
npx expo install nativewind tailwindcss react-native-reanimated
```

### tailwind.config.ts

```ts
import { type Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;
```

### global.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### babel.config.js

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }]],
    plugins: ['nativewind/babel'],
  };
};
```

### metro.config.js

```js
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

### Import Global Styles

In `app/_layout.tsx`:

```tsx
import '../global.css';

export default function RootLayout() {
  return <Stack />;
}
```

## Basic Usage

```tsx
import { View, Text, Pressable } from 'react-native';

function Card({ title, description }: { title: string; description: string }) {
  return (
    <View className="rounded-xl bg-white p-4 shadow-md dark:bg-gray-800">
      <Text className="text-lg font-semibold text-gray-900 dark:text-white">
        {title}
      </Text>
      <Text className="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {description}
      </Text>
    </View>
  );
}

function PrimaryButton({
  title,
  onPress,
}: {
  title: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      className="items-center rounded-lg bg-blue-600 px-4 py-3 active:bg-blue-700"
      onPress={onPress}
    >
      <Text className="text-base font-medium text-white">{title}</Text>
    </Pressable>
  );
}
```

## Platform-Specific Classes

NativeWind supports platform variants:

```tsx
<View className="p-4 ios:pb-8 android:pb-4 web:max-w-lg web:mx-auto" />
<Text className="text-base ios:font-semibold android:font-bold" />
```

## Dark Mode

NativeWind supports the `dark:` variant using the device color scheme:

```tsx
import { useColorScheme } from 'nativewind';

function ThemeToggle() {
  const { colorScheme, toggleColorScheme } = useColorScheme();

  return (
    <Pressable
      className="rounded-lg bg-gray-200 p-3 dark:bg-gray-700"
      onPress={toggleColorScheme}
    >
      <Text className="text-gray-900 dark:text-white">
        {colorScheme === 'dark' ? 'Light Mode' : 'Dark Mode'}
      </Text>
    </Pressable>
  );
}
```

## State Variants

```tsx
<Pressable className="bg-blue-500 active:bg-blue-700 disabled:opacity-50">
  <Text className="text-white">Press Me</Text>
</Pressable>

<TextInput
  className="rounded border border-gray-300 p-3 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
  placeholder="Enter text"
/>
```

## Custom Components with className

Use `cssInterop` to enable `className` on third-party components:

```tsx
import { cssInterop } from 'nativewind';
import { Image } from 'expo-image';
import Svg from 'react-native-svg';

cssInterop(Image, { className: 'style' });
cssInterop(Svg, { className: 'style' });
```

After wrapping, use `className` directly:

```tsx
<Image className="h-12 w-12 rounded-full" source={{ uri: avatarUrl }} />
```

## Responsive Design

NativeWind supports breakpoint prefixes based on screen width:

```tsx
<View className="flex-col sm:flex-row">
  <View className="w-full sm:w-1/2">
    <Text>Left column</Text>
  </View>
  <View className="w-full sm:w-1/2">
    <Text>Right column</Text>
  </View>
</View>
```

| Prefix | Min Width |
| ------ | --------- |
| `sm:`  | 640px     |
| `md:`  | 768px     |
| `lg:`  | 1024px    |
| `xl:`  | 1280px    |

## Combining with StyleSheet

When NativeWind classes are insufficient, combine with inline styles:

```tsx
import { type ViewStyle } from 'react-native';

function AnimatedBox({ translateY }: { translateY: ViewStyle['transform'] }) {
  return (
    <View
      className="rounded-lg bg-blue-500 p-4"
      style={{ transform: translateY }}
    />
  );
}
```

`style` prop values override NativeWind-generated styles.

## TypeScript Support

Add type declarations for `className` support in `nativewind-env.d.ts`:

```ts
/// <reference types="nativewind/types" />
```

This extends React Native core components to accept the `className` prop.
