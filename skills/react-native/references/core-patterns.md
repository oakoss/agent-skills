---
title: Core Patterns
description: StyleSheet API, FlatList rendering, Platform-specific code, and fundamental React Native component patterns
tags:
  [StyleSheet, FlatList, Platform, View, Text, ScrollView, Pressable, FlashList]
---

# Core Patterns

## StyleSheet API

`StyleSheet.create()` validates styles at creation time and enables optimizations by sending styles over the bridge once.

```tsx
import { View, Text, StyleSheet } from 'react-native';

function ProfileCard({ name, bio }: { name: string; bio: string }) {
  return (
    <View style={styles.card}>
      <Text style={styles.name}>{name}</Text>
      <Text style={styles.bio}>{bio}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  name: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  bio: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
});
```

### Composing Styles

Pass an array to `style` for composition. Later values override earlier ones:

```tsx
<View style={[styles.card, isActive && styles.activeCard]} />
<Text style={[styles.text, { color: theme.primary }]} />
```

## FlatList

Virtualized list rendering for large datasets. Only renders visible items plus a buffer.

```tsx
import { FlatList, type ListRenderItem } from 'react-native';

type Item = { id: string; title: string };

function ItemList({ items }: { items: Item[] }) {
  const renderItem: ListRenderItem<Item> = ({ item }) => (
    <View style={styles.row}>
      <Text>{item.title}</Text>
    </View>
  );

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
      ItemSeparatorComponent={() => <View style={styles.separator} />}
      ListEmptyComponent={<Text>No items found</Text>}
      contentContainerStyle={styles.listContent}
    />
  );
}
```

### SectionList

Grouped data with section headers:

```tsx
import { SectionList } from 'react-native';

type Section = { title: string; data: Item[] };

function GroupedList({ sections }: { sections: Section[] }) {
  return (
    <SectionList
      sections={sections}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <ItemRow item={item} />}
      renderSectionHeader={({ section }) => (
        <Text style={styles.sectionHeader}>{section.title}</Text>
      )}
      stickySectionHeadersEnabled
    />
  );
}
```

### FlashList (High Performance)

Drop-in replacement for FlatList from Shopify with recycling architecture:

```tsx
import { FlashList } from '@shopify/flash-list';

function FastList({ items }: { items: Item[] }) {
  return (
    <FlashList
      data={items}
      renderItem={({ item }) => <ItemRow item={item} />}
      estimatedItemSize={72}
      keyExtractor={(item) => item.id}
    />
  );
}
```

`estimatedItemSize` is required. Measure average item height for optimal recycling.

## Platform-Specific Code

### Platform.select and Platform.OS

```tsx
import { Platform, StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 3,
    },
    default: {
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    },
  }),
});

function PlatformMessage() {
  return <Text>{Platform.OS === 'ios' ? 'iPhone' : 'Android'} app</Text>;
}
```

### Platform-Specific File Extensions

Create files with platform extensions for entirely different implementations:

```sh
components/
  Button.tsx          # Shared/default
  Button.ios.tsx      # iOS-specific
  Button.android.tsx  # Android-specific
  Button.web.tsx      # Web-specific
```

Import without the extension -- the bundler resolves the correct file:

```tsx
import { Button } from './components/Button';
```

## Pressable

The current recommended touchable component, replacing `TouchableOpacity`:

```tsx
import { Pressable, type PressableProps } from 'react-native';

function Button({ children, onPress, disabled }: PressableProps) {
  return (
    <Pressable
      disabled={disabled}
      style={({ pressed }) => [
        styles.button,
        pressed && styles.pressed,
        disabled && styles.disabled,
      ]}
      onPress={onPress}
    >
      {children}
    </Pressable>
  );
}
```

## SafeAreaView

Handles device notches, status bars, and home indicators:

```tsx
import { SafeAreaView } from 'react-native-safe-area-context';

function Screen({ children }: { children: React.ReactNode }) {
  return (
    <SafeAreaView style={styles.screen} edges={['top', 'bottom']}>
      {children}
    </SafeAreaView>
  );
}
```

Use `react-native-safe-area-context` (not the built-in `SafeAreaView` from `react-native`) for cross-platform consistency and granular edge control.

## KeyboardAvoidingView

Prevents the keyboard from covering input fields:

```tsx
import { KeyboardAvoidingView, Platform } from 'react-native';

function FormScreen() {
  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <TextInput placeholder="Email" />
      <TextInput placeholder="Password" secureTextEntry />
    </KeyboardAvoidingView>
  );
}
```

## Image Handling

```tsx
import { Image } from 'expo-image';

function Avatar({ uri }: { uri: string }) {
  return (
    <Image
      source={{ uri }}
      style={styles.avatar}
      contentFit="cover"
      placeholder={{ blurhash: 'LKN]Rv%2Tw=w]~RBVZRi};RPxuwH' }}
      transition={200}
    />
  );
}
```

Prefer `expo-image` over `react-native`'s `Image` for caching, blurhash placeholders, and animated image support.
