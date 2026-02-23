---
title: Performance Patterns
description: React Native performance optimization including list rendering, memoization, animations, bundle size, and profiling
tags:
  [
    performance,
    FlatList,
    memoization,
    Reanimated,
    bundle-size,
    hermes,
    FlashList,
    lazy-loading,
  ]
---

# Performance Patterns

## List Optimization

### FlatList Tuning

```tsx
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(item) => item.id}
  removeClippedSubviews
  maxToRenderPerBatch={10}
  windowSize={5}
  initialNumToRender={10}
  getItemLayout={(_data, index) => ({
    length: ITEM_HEIGHT,
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>
```

| Prop                    | Effect                                     |
| ----------------------- | ------------------------------------------ |
| `removeClippedSubviews` | Unmounts offscreen views (Android benefit) |
| `maxToRenderPerBatch`   | Items rendered per scroll batch            |
| `windowSize`            | Viewport multiplier for render window      |
| `initialNumToRender`    | Items in first render pass                 |
| `getItemLayout`         | Skips measurement for fixed-height items   |

### FlashList for Large Lists

```tsx
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={items}
  renderItem={renderItem}
  estimatedItemSize={80}
  keyExtractor={(item) => item.id}
/>;
```

FlashList uses cell recycling instead of unmounting/remounting, providing better performance for lists over 100 items.

## Memoization

### React.memo for List Items

```tsx
import { memo } from 'react';

const ListItem = memo(function ListItem({ item, onPress }: ListItemProps) {
  return (
    <Pressable onPress={() => onPress(item.id)}>
      <Text>{item.title}</Text>
    </Pressable>
  );
});
```

### useCallback for Stable References

```tsx
function ItemList({ items }: { items: Item[] }) {
  const handlePress = useCallback((id: string) => {
    router.push(`/item/${id}`);
  }, []);

  const renderItem: ListRenderItem<Item> = useCallback(
    ({ item }) => <ListItem item={item} onPress={handlePress} />,
    [handlePress],
  );

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
    />
  );
}
```

## Animations

### Reanimated Worklets

```tsx
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

function AnimatedCard() {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  const handlePressIn = () => {
    scale.value = withSpring(0.95);
  };

  const handlePressOut = () => {
    scale.value = withSpring(1);
  };

  return (
    <Pressable onPressIn={handlePressIn} onPressOut={handlePressOut}>
      <Animated.View style={[styles.card, animatedStyle]}>
        <Text>Animated Card</Text>
      </Animated.View>
    </Pressable>
  );
}
```

### Layout Animations

```tsx
import Animated, {
  FadeIn,
  FadeOut,
  LinearTransition,
} from 'react-native-reanimated';

function AnimatedList({ items }: { items: Item[] }) {
  return (
    <Animated.FlatList
      data={items}
      itemLayoutAnimation={LinearTransition}
      renderItem={({ item }) => (
        <Animated.View entering={FadeIn} exiting={FadeOut}>
          <Text>{item.title}</Text>
        </Animated.View>
      )}
      keyExtractor={(item) => item.id}
    />
  );
}
```

### Gesture Handler + Reanimated

```tsx
import { Gesture, GestureDetector } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
} from 'react-native-reanimated';

function DraggableBox() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const pan = Gesture.Pan()
    .onUpdate((event) => {
      translateX.value = event.translationX;
      translateY.value = event.translationY;
    })
    .onEnd(() => {
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
    });

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: translateX.value },
      { translateY: translateY.value },
    ],
  }));

  return (
    <GestureDetector gesture={pan}>
      <Animated.View style={[styles.box, animatedStyle]} />
    </GestureDetector>
  );
}
```

## Image Optimization

```tsx
import { Image } from 'expo-image';

<Image
  source={{ uri: imageUrl }}
  style={{ width: 300, height: 200 }}
  contentFit="cover"
  placeholder={{ blurhash: 'LGF5]+Yk^6#M@-5c,1J5@[or[Q6.' }}
  cachePolicy="memory-disk"
  transition={200}
  recyclingKey={imageUrl}
/>;
```

| Prop           | Purpose                                 |
| -------------- | --------------------------------------- |
| `cachePolicy`  | `memory`, `disk`, `memory-disk`, `none` |
| `placeholder`  | Blurhash/thumbhash while loading        |
| `recyclingKey` | Prevents flash when recycled in lists   |
| `transition`   | Fade-in duration in milliseconds        |

## Bundle Size

### Tree Shaking with Expo

Import only what you use from large packages:

```tsx
import MaterialIcons from '@expo/vector-icons/MaterialIcons';

import Ionicons from '@expo/vector-icons/Ionicons';
```

### Lazy Loading Screens

Expo Router supports lazy loading by default. Heavy screens load on navigation:

```tsx
import { Stack } from 'expo-router';

<Stack>
  <Stack.Screen name="heavy-screen" options={{ lazy: true }} />
</Stack>;
```

## Hermes Engine

Hermes is enabled by default in Expo. It provides faster startup, lower memory usage, and smaller bundle size compared to JSC.

Verify Hermes is active:

```tsx
const isHermes = () => !!global.HermesInternal;
```

## Profiling

### React DevTools Profiler

```bash
npx react-devtools
```

Connect to the dev client for component render profiling.

### Flipper Integration

For development builds, Flipper provides network inspection, layout inspection, and performance monitoring. Install via `expo-dev-client`.

### Performance Monitoring Checklist

| Area          | Target   | Tool                                 |
| ------------- | -------- | ------------------------------------ |
| JS thread FPS | 60 fps   | React DevTools                       |
| UI thread FPS | 60 fps   | Systrace/Instruments                 |
| Bundle size   | Minimize | `npx expo export`                    |
| Memory        | No leaks | Xcode Instruments / Android Profiler |
| Startup time  | < 2s     | Hermes + lazy loading                |
