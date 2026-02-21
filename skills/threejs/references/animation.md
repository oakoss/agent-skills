---
title: Animation System
description: AnimationMixer, clips, actions, GLTF animations, skeletal animation, morph targets, procedural animation, and blending
tags:
  [
    animation,
    mixer,
    clip,
    action,
    skeletal,
    morph,
    keyframe,
    blending,
    crossfade,
  ]
---

# Animation System

Three.js provides a complete animation system built on `AnimationMixer`, `AnimationClip`, and `AnimationAction`. Supports skeletal animation from GLTF models, morph targets, procedural animation, and weight-based blending.

## Core Architecture

| Class             | Role                                                                          |
| ----------------- | ----------------------------------------------------------------------------- |
| `AnimationMixer`  | Drives playback for a specific scene object; call `.update(delta)` each frame |
| `AnimationClip`   | Reusable animation data containing keyframe tracks                            |
| `AnimationAction` | Playback controller for a single clip on a mixer (play, pause, fade, loop)    |
| `KeyframeTrack`   | Single animated property (position, rotation, scale, morph weight)            |

## AnimationMixer

Create one mixer per animated object. Update it in the render loop with `clock.getDelta()`:

```ts
import * as THREE from 'three';

const clock = new THREE.Clock();
const mixer = new THREE.AnimationMixer(model);

function animate(): void {
  const delta = clock.getDelta();
  mixer.update(delta);
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

Using `getDelta()` ensures frame-rate-independent playback. Never use a fixed timestep like `mixer.update(1/60)`.

## GLTF Animation Loading

GLTF models store animations in `gltf.animations`. Create actions from clips via the mixer:

```ts
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const loader = new GLTFLoader();
let mixer: THREE.AnimationMixer;
const actions: Map<string, THREE.AnimationAction> = new Map();

loader.load('/character.glb', (gltf) => {
  const model = gltf.scene;
  scene.add(model);

  mixer = new THREE.AnimationMixer(model);

  for (const clip of gltf.animations) {
    const action = mixer.clipAction(clip);
    actions.set(clip.name, action);
  }

  actions.get('Idle')?.play();
});
```

Find a specific clip by name:

```ts
const walkClip = THREE.AnimationClip.findByName(gltf.animations, 'Walk');
const walkAction = mixer.clipAction(walkClip);
```

## AnimationAction Controls

```ts
const action = mixer.clipAction(clip);

action.play();
action.stop();
action.paused = true;
action.paused = false;

action.timeScale = 2;
action.setLoop(THREE.LoopRepeat, Infinity);
action.setLoop(THREE.LoopOnce, 1);
action.clampWhenFinished = true;

action.setEffectiveWeight(0.5);
action.setEffectiveTimeScale(1.5);
```

| Method / Property                    | Purpose                                        |
| ------------------------------------ | ---------------------------------------------- |
| `play()`                             | Start playback from current time               |
| `stop()`                             | Stop and reset to beginning                    |
| `reset()`                            | Reset time and weight, keep in play state      |
| `fadeIn(duration)`                   | Ramp weight from 0 to 1                        |
| `fadeOut(duration)`                  | Ramp weight from current to 0                  |
| `crossFadeTo(other, duration, warp)` | Fade out this action while fading in another   |
| `setLoop(mode, count)`               | `LoopOnce`, `LoopRepeat`, `LoopPingPong`       |
| `clampWhenFinished`                  | Hold last frame when `LoopOnce` completes      |
| `timeScale`                          | Playback speed multiplier (negative = reverse) |
| `weight`                             | Blend influence (0-1)                          |

## Animation Blending

### Crossfade Between Animations

Smooth transition between two actions (e.g., walk to run):

```ts
function crossFade(
  from: THREE.AnimationAction,
  to: THREE.AnimationAction,
  duration: number,
): void {
  from.fadeOut(duration);
  to.reset().fadeIn(duration).play();
}

crossFade(actions.get('Walk')!, actions.get('Run')!, 0.5);
```

### Weight-Based Blending

Blend multiple animations simultaneously using weights:

```ts
const idleAction = mixer.clipAction(idleClip);
const walkAction = mixer.clipAction(walkClip);
const runAction = mixer.clipAction(runClip);

idleAction.play();
walkAction.play();
runAction.play();

function setMovementBlend(speed: number): void {
  const idleWeight = Math.max(0, 1 - speed * 2);
  const walkWeight = speed < 0.5 ? speed * 2 : 2 - speed * 2;
  const runWeight = Math.max(0, speed * 2 - 1);

  idleAction.setEffectiveWeight(idleWeight);
  walkAction.setEffectiveWeight(walkWeight);
  runAction.setEffectiveWeight(runWeight);
}

setMovementBlend(0.0);
setMovementBlend(0.5);
setMovementBlend(1.0);
```

### Additive Animation

Layer animations on top of a base pose (e.g., breathing on top of idle):

```ts
THREE.AnimationUtils.makeClipAdditive(breathingClip);

const breathingAction = mixer.clipAction(breathingClip);
breathingAction.setEffectiveWeight(0.5);
breathingAction.play();
```

For pose clips (single-frame), extract a sub-clip:

```ts
const poseClip = THREE.AnimationUtils.subclip(clip, clip.name, 2, 3, 30);
THREE.AnimationUtils.makeClipAdditive(poseClip);
```

## KeyframeTrack Types

Build custom animations programmatically:

```ts
const positionTrack = new THREE.VectorKeyframeTrack(
  '.position',
  [0, 1, 2], // times (seconds)
  [0, 0, 0, 2, 3, 0, 0, 0, 0], // values (x,y,z per keyframe)
);

const rotationTrack = new THREE.QuaternionKeyframeTrack(
  '.quaternion',
  [0, 1, 2],
  [0, 0, 0, 1, 0, 0.707, 0, 0.707, 0, 0, 0, 1],
);

const scaleTrack = new THREE.VectorKeyframeTrack(
  '.scale',
  [0, 1, 2],
  [1, 1, 1, 2, 2, 2, 1, 1, 1],
);

const opacityTrack = new THREE.NumberKeyframeTrack(
  '.material.opacity',
  [0, 1],
  [1, 0],
);

const clip = new THREE.AnimationClip('BounceAndFade', 2, [
  positionTrack,
  rotationTrack,
  scaleTrack,
  opacityTrack,
]);

const action = mixer.clipAction(clip);
action.setLoop(THREE.LoopRepeat, Infinity);
action.play();
```

| Track Type                | Property Path               | Values Per Keyframe |
| ------------------------- | --------------------------- | ------------------- |
| `VectorKeyframeTrack`     | `.position`, `.scale`       | 3 (x, y, z)         |
| `QuaternionKeyframeTrack` | `.quaternion`               | 4 (x, y, z, w)      |
| `NumberKeyframeTrack`     | `.material.opacity`, custom | 1                   |
| `BooleanKeyframeTrack`    | `.visible`                  | 1                   |
| `ColorKeyframeTrack`      | `.material.color`           | 3 (r, g, b)         |
| `StringKeyframeTrack`     | Custom properties           | 1                   |

## Skeletal Animation

GLTF models with armatures export `Bone`, `Skeleton`, and `SkinnedMesh` objects automatically. The mixer drives bone transforms through clips.

```ts
loader.load('/character.glb', (gltf) => {
  const model = gltf.scene;
  scene.add(model);

  const skeleton = new THREE.SkeletonHelper(model);
  skeleton.visible = true;
  scene.add(skeleton);

  model.traverse((child) => {
    if ((child as THREE.SkinnedMesh).isSkinnedMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  mixer = new THREE.AnimationMixer(model);
  const action = mixer.clipAction(gltf.animations[0]);
  action.play();
});
```

Access individual bones for procedural adjustments:

```ts
const head = model.getObjectByName('Head') as THREE.Bone;
if (head) {
  head.rotation.y = Math.sin(elapsedTime) * 0.3;
}
```

## Morph Targets

Morph targets (blend shapes) deform geometry between preset shapes. Common for facial animation.

```ts
loader.load('/face.glb', (gltf) => {
  const mesh = gltf.scene.getObjectByName('Face') as THREE.Mesh;

  const influences = mesh.morphTargetInfluences!;
  const dict = mesh.morphTargetDictionary!;

  influences[dict['smile']] = 0.8;
  influences[dict['blink']] = 1.0;
});
```

Animate morph targets over time:

```ts
function animate(): void {
  const t = clock.getElapsedTime();

  influences[dict['blink']] = Math.sin(t * 3) > 0.9 ? 1 : 0;
  influences[dict['smile']] = (Math.sin(t * 0.5) + 1) / 2;

  mixer.update(clock.getDelta());
  renderer.render(scene, camera);
}
```

GLTF animations can also drive morph targets via `NumberKeyframeTrack` targeting `morphTargetInfluences[index]`.

## Procedural Animation

### Spring Physics (Smooth Damp)

Smooth interpolation that avoids abrupt starts and stops:

```ts
const _current = new THREE.Vector3();
const _velocity = new THREE.Vector3();
const _temp = new THREE.Vector3();

function smoothDamp(
  current: THREE.Vector3,
  target: THREE.Vector3,
  velocity: THREE.Vector3,
  smoothTime: number,
  delta: number,
): void {
  const omega = 2 / smoothTime;
  const x = omega * delta;
  const exp = 1 / (1 + x + 0.48 * x * x + 0.235 * x * x * x);

  _temp.copy(current).sub(target);
  const change = _temp.clone();

  current.copy(target).add(change.multiplyScalar(exp));

  velocity.copy(current).sub(target).divideScalar(delta);
}
```

### Oscillation with Trigonometric Functions

```ts
const _position = new THREE.Vector3();

function animate(): void {
  const t = clock.getElapsedTime();

  mesh.position.y = Math.sin(t * 2) * 0.5 + 1;
  mesh.rotation.y = t * 0.5;
  mesh.scale.setScalar(1 + Math.sin(t * 3) * 0.1);

  renderer.render(scene, camera);
}
```

### Look-At with Damping

```ts
const _targetQuat = new THREE.Quaternion();
const _lookAtMatrix = new THREE.Matrix4();

function smoothLookAt(
  object: THREE.Object3D,
  target: THREE.Vector3,
  speed: number,
  delta: number,
): void {
  _lookAtMatrix.lookAt(object.position, target, object.up);
  _targetQuat.setFromRotationMatrix(_lookAtMatrix);
  object.quaternion.slerp(_targetQuat, 1 - Math.exp(-speed * delta));
}
```

## Performance Tips

| Practice                                                     | Reason                                             |
| ------------------------------------------------------------ | -------------------------------------------------- |
| Pre-allocate `Vector3`, `Quaternion`, `Matrix4`              | Avoids GC pressure every frame                     |
| Use `clock.getDelta()` for mixer updates                     | Frame-rate-independent playback                    |
| Share mixers per root object, not per mesh                   | One mixer drives all animations for a model        |
| Dispose unused actions with `mixer.uncacheAction(clip)`      | Frees memory for removed animations                |
| Use `LoopOnce` + `clampWhenFinished` for one-shot animations | Prevents looping after completion                  |
| Stop actions when off-screen                                 | `action.paused = true` saves CPU                   |
| Listen for `'finished'` event on mixer                       | Trigger state changes when one-shot animations end |

```ts
mixer.addEventListener('finished', (event) => {
  const finishedAction = event.action as THREE.AnimationAction;
  finishedAction.fadeOut(0.25);
  actions.get('Idle')?.reset().fadeIn(0.25).play();
});
```
