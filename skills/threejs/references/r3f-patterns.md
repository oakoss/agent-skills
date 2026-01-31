---
title: React Three Fiber Patterns
description: R3F hooks, Canvas configuration, Suspense streaming, Next.js integration, and scene composition patterns
tags: [r3f, react-three-fiber, useFrame, canvas, suspense, nextjs, drei]
---

# React Three Fiber Patterns

React Three Fiber (R3F) provides a declarative React interface for Three.js. It uses React's component model for scene composition and hooks for frame-by-frame logic.

## Canvas Setup

The `<Canvas>` component creates a Three.js renderer, scene, and camera:

```tsx
'use client';

import { Canvas } from '@react-three/fiber';
import { Suspense } from 'react';

export default function Scene() {
  return (
    <div className="h-screen w-full">
      <Suspense fallback={<div>Loading...</div>}>
        <Canvas shadows camera={{ position: [0, 0, 5], fov: 75 }} dpr={[1, 2]}>
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} castShadow />
          {/* Scene children */}
        </Canvas>
      </Suspense>
    </div>
  );
}
```

**Required wrapper:** Always wrap `<Canvas>` in `<Suspense>` for asset loading support and streaming compatibility.

## useFrame Hook

The primary hook for per-frame updates. Receives renderer state and delta time:

```tsx
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

function RotatingMesh() {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((_state, delta) => {
    meshRef.current.rotation.y += delta;
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  );
}
```

**Rules:**

- Never call `setState` inside `useFrame` -- it triggers React re-renders at 60fps
- Mutate refs directly for position, rotation, scale, and material properties
- Pre-allocate temporary objects (Vector3, Color) outside the callback

## useThree Hook

Access the R3F state store (camera, renderer, scene, size, etc.):

```tsx
import { useThree } from '@react-three/fiber';

function CameraLogger() {
  const { camera, size } = useThree();
  console.log(camera.position, size.width, size.height);
  return null;
}
```

## drei Helpers

`@react-three/drei` provides common abstractions:

```tsx
import {
  OrbitControls,
  Environment,
  useGLTF,
  Html,
  Float,
} from '@react-three/drei';

function Scene() {
  return (
    <>
      <OrbitControls enableDamping />
      <Environment preset="city" />
      <Float speed={2} rotationIntensity={0.5}>
        <mesh>
          <sphereGeometry />
          <meshStandardMaterial color="coral" />
        </mesh>
      </Float>
      <Html position={[0, 2, 0]} center>
        <div className="rounded bg-white p-2 text-sm shadow">Label</div>
      </Html>
    </>
  );
}
```

| Helper           | Purpose                           |
| ---------------- | --------------------------------- |
| `OrbitControls`  | Camera orbit with damping         |
| `Environment`    | HDR environment maps and lighting |
| `useGLTF`        | Load and cache GLTF/GLB models    |
| `Html`           | Overlay HTML elements in 3D space |
| `Float`          | Gentle floating animation         |
| `ContactShadows` | Ground-plane soft shadows         |
| `Bounds`         | Auto-fit camera to scene bounds   |

## Next.js Integration

### Client Component Boundary

Three.js requires browser APIs. Mark scene components with `'use client'`:

```tsx
'use client';

import { Canvas } from '@react-three/fiber';

export function ThreeScene() {
  return <Canvas>{/* ... */}</Canvas>;
}
```

### Partial Prerendering (PPR)

Next.js streams the static shell immediately while the 3D scene loads:

```tsx
import { Suspense } from 'react';
import { ThreeScene } from './three-scene';

export default function Page() {
  return (
    <main>
      <h1>Product Viewer</h1>
      <Suspense fallback={<div className="h-96 animate-pulse bg-muted" />}>
        <ThreeScene />
      </Suspense>
    </main>
  );
}
```

The page shell (heading, layout) renders instantly. The 3D canvas streams in when ready.

### Dynamic Import

For pages where the 3D scene is below the fold:

```tsx
import dynamic from 'next/dynamic';

const ThreeScene = dynamic(() => import('./three-scene'), {
  ssr: false,
  loading: () => <div className="h-96 animate-pulse bg-muted" />,
});
```

## Scene Composition Pattern

Organize complex scenes into focused components:

```tsx
function ProductViewer() {
  return (
    <Canvas shadows camera={{ position: [0, 2, 5] }}>
      <Lighting />
      <Environment preset="studio" />
      <Suspense fallback={null}>
        <ProductModel url="/product.glb" />
      </Suspense>
      <Floor />
      <CameraControls />
    </Canvas>
  );
}

function Lighting() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 5, 5]} castShadow intensity={1} />
    </>
  );
}

function Floor() {
  return (
    <mesh rotation-x={-Math.PI / 2} receiveShadow>
      <planeGeometry args={[20, 20]} />
      <meshStandardMaterial color="#f0f0f0" />
    </mesh>
  );
}
```

Each component handles one concern: lighting, model loading, ground plane, camera controls.

## WebGPU with React Three Fiber

R3F v9 supports WebGPU through an async `gl` prop. You must import from `three/webgpu` and call `extend()` to register the node-based elements:

```tsx
'use client';

import * as THREE from 'three/webgpu';
import * as TSL from 'three/tsl';
import { Canvas, extend, type ThreeToJSXElements } from '@react-three/fiber';

declare module '@react-three/fiber' {
  interface ThreeElements extends ThreeToJSXElements<typeof THREE> {}
}

extend(THREE as any);

export default function Scene() {
  return (
    <Canvas
      gl={async (props) => {
        const renderer = new THREE.WebGPURenderer(props as any);
        await renderer.init();
        return renderer;
      }}
    >
      <mesh>
        <boxGeometry />
        <meshBasicNodeMaterial />
      </mesh>
    </Canvas>
  );
}
```

Note: In R3F v9, `state.gl` is renamed to `state.renderer`.

## React Compiler Considerations

The React Compiler (React 19) handles memoization automatically. Avoid manual `useMemo` for geometries and materials unless profiling reveals a specific leak. The compiler optimizes re-render paths without explicit memoization hints.
