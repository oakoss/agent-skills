---
title: Device APIs
description: Camera, push notifications, haptic feedback, and other native device API integrations via Expo SDK packages
tags:
  [
    expo-camera,
    expo-notifications,
    expo-haptics,
    permissions,
    push-tokens,
    expo-location,
    expo-sensors,
  ]
---

# Device APIs

## Camera

`expo-camera` provides camera access with barcode scanning and photo capture.

### Setup

```bash
npx expo install expo-camera
```

```json
{
  "expo": {
    "plugins": [
      [
        "expo-camera",
        {
          "cameraPermission": "Allow $(PRODUCT_NAME) to access your camera for photo capture."
        }
      ]
    ]
  }
}
```

### Camera with Permissions

```tsx
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState, useRef } from 'react';
import { View, Text, Pressable } from 'react-native';

function CameraScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState<'front' | 'back'>('back');
  const cameraRef = useRef<CameraView>(null);

  if (!permission) return <View />;

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text>Camera permission is required</Text>
        <Pressable onPress={requestPermission}>
          <Text>Grant Permission</Text>
        </Pressable>
      </View>
    );
  }

  const takePicture = async () => {
    const photo = await cameraRef.current?.takePictureAsync();
    if (photo) {
      console.log(photo.uri);
    }
  };

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} facing={facing} style={styles.camera}>
        <Pressable
          onPress={() => setFacing((f) => (f === 'back' ? 'front' : 'back'))}
        >
          <Text style={styles.button}>Flip</Text>
        </Pressable>
        <Pressable onPress={takePicture}>
          <Text style={styles.button}>Capture</Text>
        </Pressable>
      </CameraView>
    </View>
  );
}
```

### Barcode Scanning

```tsx
import { CameraView } from 'expo-camera';

function BarcodeScanner() {
  const handleScan = ({ data, type }: { data: string; type: string }) => {
    console.log(`Scanned ${type}: ${data}`);
  };

  return (
    <CameraView
      barcodeScannerSettings={{
        barcodeTypes: ['qr', 'ean13', 'code128'],
      }}
      onBarcodeScanned={handleScan}
      style={{ flex: 1 }}
    />
  );
}
```

## Push Notifications

`expo-notifications` handles local and push notifications with scheduling support.

### Setup

```bash
npx expo install expo-notifications expo-device expo-constants
```

### Register for Push Notifications

```tsx
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';
import { Platform } from 'react-native';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

async function registerForPushNotifications(): Promise<string | undefined> {
  if (!Device.isDevice) {
    throw new Error('Push notifications require a physical device');
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return undefined;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
    });
  }

  const projectId = Constants.expoConfig?.extra?.eas?.projectId;
  const token = await Notifications.getExpoPushTokenAsync({ projectId });
  return token.data;
}
```

### Listen for Notifications

```tsx
import { useEffect, useRef } from 'react';
import * as Notifications from 'expo-notifications';

function useNotificationListeners() {
  const notificationListener = useRef<Notifications.EventSubscription>();
  const responseListener = useRef<Notifications.EventSubscription>();

  useEffect(() => {
    notificationListener.current =
      Notifications.addNotificationReceivedListener((notification) => {
        console.log('Received:', notification.request.content);
      });

    responseListener.current =
      Notifications.addNotificationResponseReceivedListener((response) => {
        const data = response.notification.request.content.data;
        console.log('Tapped:', data);
      });

    return () => {
      notificationListener.current?.remove();
      responseListener.current?.remove();
    };
  }, []);
}
```

### Schedule Local Notification

```tsx
import * as Notifications from 'expo-notifications';

async function scheduleReminder(title: string, body: string, seconds: number) {
  await Notifications.scheduleNotificationAsync({
    content: { title, body, sound: true },
    trigger: {
      seconds,
      type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
    },
  });
}
```

## Haptic Feedback

`expo-haptics` provides tactile feedback patterns.

```bash
npx expo install expo-haptics
```

```tsx
import * as Haptics from 'expo-haptics';

function HapticButtons() {
  return (
    <View>
      <Pressable
        onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)}
      >
        <Text>Light Impact</Text>
      </Pressable>
      <Pressable
        onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium)}
      >
        <Text>Medium Impact</Text>
      </Pressable>
      <Pressable
        onPress={() => Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy)}
      >
        <Text>Heavy Impact</Text>
      </Pressable>
      <Pressable
        onPress={() =>
          Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success)
        }
      >
        <Text>Success</Text>
      </Pressable>
      <Pressable onPress={() => Haptics.selectionAsync()}>
        <Text>Selection</Text>
      </Pressable>
    </View>
  );
}
```

| Method                    | Purpose                                    |
| ------------------------- | ------------------------------------------ |
| `impactAsync(style)`      | Physical impact (Light, Medium, Heavy)     |
| `notificationAsync(type)` | Outcome feedback (Success, Warning, Error) |
| `selectionAsync()`        | Selection change feedback                  |

## Location

```bash
npx expo install expo-location
```

```tsx
import * as Location from 'expo-location';

async function getCurrentLocation() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') return null;

  const location = await Location.getCurrentPositionAsync({
    accuracy: Location.Accuracy.High,
  });
  return location.coords;
}
```

## Secure Storage

```bash
npx expo install expo-secure-store
```

```tsx
import * as SecureStore from 'expo-secure-store';

async function saveToken(key: string, value: string) {
  await SecureStore.setItemAsync(key, value);
}

async function getToken(key: string): Promise<string | null> {
  return SecureStore.getItemAsync(key);
}
```

Uses Keychain on iOS and EncryptedSharedPreferences on Android. Suitable for auth tokens, API keys, and sensitive user data.
