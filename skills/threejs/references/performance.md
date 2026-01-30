---
title: Performance and Asset Optimization
description: Draco compression, KTX2 textures, InstancedMesh, BatchedMesh, frame-rate independence, and on-demand rendering
tags: [draco, ktx2, instancing, draw-calls, optimization]
---

# Performance and Asset Optimization

Maintaining high frame rates requires disciplined asset management, draw call budgets, and render loop efficiency.

## Geometry Compression with Draco

Draco reduces `.glb` geometry size by up to 90%. Always compress models for production.

```bash
bun x gltf-pipeline -i scene.gltf -o scene.glb -d
```

Load Draco-compressed models in React Three Fiber using the `useDraco` option:

```tsx
import { useGLTF } from '@react-three/drei';

function Model() {
  const { scene } = useGLTF('/model.glb');
  return <primitive object={scene} />;
}

useGLTF.preload('/model.glb');
```

## InstancedMesh for Repeated Geometry

Render thousands of identical objects with a single draw call:

```tsx
import { useRef, useEffect } from 'react';
import * as THREE from 'three';

function Forest() {
  const count = 1000;
  const meshRef = useRef<THREE.InstancedMesh>(null!);
  const tempObject = new THREE.Object3D();

  useEffect(() => {
    for (let i = 0; i < count; i++) {
      tempObject.position.set(Math.random() * 100, 0, Math.random() * 100);
      tempObject.updateMatrix();
      meshRef.current.setMatrixAt(i, tempObject.matrix);
    }
    meshRef.current.instanceMatrix.needsUpdate = true;
  }, []);

  return (
    <instancedMesh ref={meshRef} args={[null!, null!, count]}>
      <coneGeometry args={[1, 5, 8]} />
      <meshStandardMaterial color="green" />
    </instancedMesh>
  );
}
```

## BatchedMesh for Diverse Geometries

Use `BatchedMesh` (r156+) when different geometries share the same material. Draws them in a single call without requiring identical geometry.

## Texture Optimization with KTX2

PNG and JPG textures decompress into raw bitmaps in VRAM. KTX2 (Basis Universal) stays compressed on the GPU.

**When to use KTX2:** Any texture larger than 512x512 pixels in production. Use `toktx` or online converters to generate KTX2 files.

**When PNG is acceptable:** Small UI textures, sprites under 256x256, textures that need transparency with sharp edges.

## Frame-Rate Independent Motion

Always multiply animation values by `delta` from `useFrame`:

```tsx
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';

function SpinningCube() {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((_state, delta) => {
    meshRef.current.rotation.x += delta * 1.0;
    meshRef.current.rotation.y += delta * 0.5;
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  );
}
```

Without `delta`, animation speed varies with frame rate (faster on 120Hz displays, slower on 30Hz).

## On-Demand Rendering

For static or infrequently changing scenes, avoid continuous rendering:

```tsx
<Canvas frameloop="demand">
  {/* Scene only renders when invalidate() is called or state changes */}
</Canvas>
```

Trigger a re-render manually when needed:

```tsx
import { useThree } from '@react-three/fiber';

function Controller() {
  const invalidate = useThree((state) => state.invalidate);

  function handleChange() {
    invalidate();
  }

  return null;
}
```

## Object Pre-Allocation

Never allocate temporary objects inside `useFrame`. Pre-allocate them at module or component scope:

```tsx
const _tempVec = new THREE.Vector3();
const _tempColor = new THREE.Color();

function Particle() {
  const ref = useRef<THREE.Mesh>(null!);

  useFrame(() => {
    _tempVec.set(0, 1, 0);
    ref.current.position.add(_tempVec);
  });

  return <mesh ref={ref}>{/* ... */}</mesh>;
}
```

Allocating inside `useFrame` creates garbage every frame, triggering GC pauses that cause visible stuttering.

## Draw Call Budget

| Scene Type          | Target Draw Calls |
| ------------------- | ----------------- |
| Mobile AR/VR        | < 50              |
| Desktop interactive | < 100             |
| Desktop cinematic   | < 200             |

Monitor with `renderer.info.render.calls` or the `stats-gl` helper.

## Resource Cleanup

Explicitly dispose of GPU resources when components unmount:

```tsx
import { useEffect } from 'react';

function DisposableScene({ geometry, material, texture }) {
  useEffect(() => {
    return () => {
      geometry.dispose();
      material.dispose();
      texture.dispose();
    };
  }, [geometry, material, texture]);

  return null;
}
```

Failing to dispose causes VRAM leaks that degrade performance over time.
