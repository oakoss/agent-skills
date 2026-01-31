---
title: WebGPU and TSL Shader Patterns
description: WebGPU renderer initialization, TSL node-based shaders, compute shaders, and migration from WebGL/GLSL
tags: [webgpu, tsl, shaders, compute, wgsl, renderer, async-init]
---

# WebGPU and TSL Shader Patterns

WebGPU is the production standard for modern Three.js. TSL (Three Shader Language) is a node-based shader system that compiles to WGSL (WebGPU) or GLSL (WebGL fallback). Import from `three/webgpu` for the WebGPU renderer and from `three/tsl` for TSL utilities.

## Why WebGPU

| Advantage             | Detail                                       |
| --------------------- | -------------------------------------------- |
| Lower CPU overhead    | Draw calls processed faster than WebGL       |
| Compute shaders       | Move physics, particles, and flocking to GPU |
| Modern GPU features   | Bind groups, storage buffers, indirect draws |
| Multiplexed pipelines | Multiple render passes without state reset   |

## Mandatory Async Initialization

WebGPU requires asynchronous setup. Rendering before initialization produces black screens or race conditions.

```ts
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
```

In React Three Fiber, pass a custom renderer factory to `<Canvas>`:

```tsx
'use client';

import * as THREE from 'three/webgpu';
import { Canvas, extend } from '@react-three/fiber';
import { Suspense } from 'react';

extend(THREE as any);

export default function Scene() {
  return (
    <Suspense fallback={<div>Loading 3D Scene...</div>}>
      <Canvas
        shadows
        camera={{ position: [0, 0, 5], fov: 75 }}
        gl={async (props) => {
          const renderer = new THREE.WebGPURenderer({
            ...props,
            antialias: true,
          });
          await renderer.init();
          return renderer;
        }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        {/* Scene content */}
      </Canvas>
    </Suspense>
  );
}
```

## TSL Basics

TSL looks like JavaScript but describes shader operations as a node graph. It compiles to WGSL for WebGPU or GLSL for WebGL.

### Animated Color

```ts
import * as THREE from 'three/webgpu';
import { color, mix, oscSine, timerLocal } from 'three/tsl';

const material = new THREE.MeshStandardNodeMaterial();
const time = timerLocal();
const animatedColor = mix(color(0xff0000), color(0x0000ff), oscSine(time));
material.colorNode = animatedColor;
```

### Vertex Displacement (Wave Shader)

```ts
import * as THREE from 'three/webgpu';
import { positionLocal, timerLocal, sin, float, vec3 } from 'three/tsl';

const material = new THREE.MeshStandardNodeMaterial();
const time = timerLocal();
const pos = positionLocal;

const wave = sin(pos.x.add(time)).mul(0.5);
const newPos = vec3(pos.x, pos.y.add(wave), pos.z);

material.positionNode = newPos;
```

### UV-Based Texture Mixing

```ts
import * as THREE from 'three/webgpu';
import { texture, uv, mix, timerLocal, oscSine } from 'three/tsl';

const tex1 = new THREE.TextureLoader().load('/texture1.jpg');
const tex2 = new THREE.TextureLoader().load('/texture2.jpg');

const material = new THREE.MeshStandardNodeMaterial();
const t = oscSine(timerLocal());
material.colorNode = mix(texture(tex1, uv()), texture(tex2, uv()), t);
```

## Compute Shaders

Run arbitrary GPU calculations without rendering. Define compute functions with `Fn` and dispatch with `renderer.computeAsync()`:

```ts
import * as THREE from 'three/webgpu';
import {
  Fn,
  instancedArray,
  instanceIndex,
  float,
  vec3,
  hash,
} from 'three/tsl';

const count = 10000;
const positionBuffer = instancedArray(count, 'vec3');

const computeInit = Fn(() => {
  const i = float(instanceIndex);
  positionBuffer.element(instanceIndex).assign(
    vec3(hash(i), hash(i.add(1)), hash(i.add(2)))
      .mul(10)
      .sub(5),
  );
})().compute(count);

await renderer.computeAsync(computeInit);
```

Use cases: particle systems, physics simulations, flocking algorithms, procedural generation.

## WebGL Fallback Strategy

`WebGPURenderer` automatically falls back to WebGL 2 when WebGPU is not available. No separate code path is needed -- ship one renderer and Three.js handles compatibility. To force WebGL for testing:

```ts
import * as THREE from 'three/webgpu';

const renderer = new THREE.WebGPURenderer({
  canvas,
  antialias: true,
  forceWebGL: true,
});
await renderer.init();
```

TSL automatically compiles to GLSL when the renderer falls back to WebGL.

## TSL vs GLSL Comparison

| GLSL Concept         | TSL Equivalent       |
| -------------------- | -------------------- |
| `uniform float time` | `timerLocal()`       |
| `varying vec2 vUv`   | `uv()`               |
| `gl_Position`        | `positionNode`       |
| `gl_FragColor`       | `colorNode`          |
| `sin(x)`             | `sin(x)` (same name) |
| `mix(a, b, t)`       | `mix(a, b, t)`       |
| `texture2D(tex, uv)` | `texture(tex, uv())` |

TSL advantages: automatic cross-compilation, type safety through the node graph, no string-based shader code, easier debugging.
