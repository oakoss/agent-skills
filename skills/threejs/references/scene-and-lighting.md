---
title: Scene, Lighting, and Model Loading
description: Scene setup, camera types, renderer configuration, lighting, environment maps, GLTF/Draco loading, raycasting, and coordinate system
tags:
  [
    scene,
    camera,
    lighting,
    gltf,
    draco,
    raycaster,
    environment,
    shadows,
    renderer,
  ]
---

# Scene, Lighting, and Model Loading

Covers the foundational Three.js vanilla API for scene graph construction, camera configuration, lighting, environment maps, model loading, and interaction via raycasting.

## Coordinate System

Three.js uses a right-handed coordinate system with Y-up:

| Axis | Direction                     |
| ---- | ----------------------------- |
| +X   | Right                         |
| +Y   | Up                            |
| +Z   | Toward camera (out of screen) |
| -Z   | Into screen                   |

Rotations follow the right-hand rule. GLTF models export in this convention by default.

## Scene Setup

```ts
import * as THREE from 'three';

const scene = new THREE.Scene();

scene.background = new THREE.Color(0x222244);

scene.fog = new THREE.Fog(0x222244, 50, 100);
```

| Property                     | Purpose                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------- |
| `scene.background`           | `Color`, `Texture`, or `CubeTexture`                                              |
| `scene.environment`          | Environment map applied to all PBR materials that lack their own `envMap`         |
| `scene.fog`                  | `Fog(color, near, far)` for linear fog, `FogExp2(color, density)` for exponential |
| `scene.backgroundBlurriness` | Blur the background texture (0-1), useful with HDR environments                   |

## Camera Types

### PerspectiveCamera

The standard camera for most 3D scenes. Mimics how the human eye perceives depth.

```ts
const camera = new THREE.PerspectiveCamera(
  45, // fov (vertical, degrees)
  window.innerWidth / window.innerHeight, // aspect ratio
  0.1, // near clipping plane
  1000, // far clipping plane
);
camera.position.set(0, 10, 30);
camera.lookAt(0, 0, 0);
```

| Parameter | Guidance                                                      |
| --------- | ------------------------------------------------------------- |
| `fov`     | 45-75 for most scenes; lower for architectural, higher for VR |
| `near`    | As large as possible to preserve depth buffer precision       |
| `far`     | As small as possible; large far/near ratio causes z-fighting  |

### OrthographicCamera

No perspective foreshortening. Used for 2D overlays, isometric views, and UI elements.

```ts
const aspect = window.innerWidth / window.innerHeight;
const frustumSize = 10;

const camera = new THREE.OrthographicCamera(
  (-frustumSize * aspect) / 2, // left
  (frustumSize * aspect) / 2, // right
  frustumSize / 2, // top
  -frustumSize / 2, // bottom
  0.1, // near
  1000, // far
);
```

Update on resize:

```ts
window.addEventListener('resize', () => {
  const aspect = window.innerWidth / window.innerHeight;
  camera.left = (-frustumSize * aspect) / 2;
  camera.right = (frustumSize * aspect) / 2;
  camera.top = frustumSize / 2;
  camera.bottom = -frustumSize / 2;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

## Renderer Configuration

```ts
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);
```

| Setting            | Options                                                                                                | Default          |
| ------------------ | ------------------------------------------------------------------------------------------------------ | ---------------- |
| `toneMapping`      | `NoToneMapping`, `LinearToneMapping`, `ReinhardToneMapping`, `ACESFilmicToneMapping`, `AgXToneMapping` | `NoToneMapping`  |
| `outputColorSpace` | `SRGBColorSpace`, `LinearSRGBColorSpace`                                                               | `SRGBColorSpace` |
| `shadowMap.type`   | `BasicShadowMap`, `PCFShadowMap`, `PCFSoftShadowMap`, `VSMShadowMap`                                   | `PCFShadowMap`   |
| `setPixelRatio`    | Clamp to `Math.min(window.devicePixelRatio, 2)` on high-DPI displays for performance                   | —                |

## Lighting Types

### AmbientLight

Uniform illumination with no direction or shadows. Prevents completely black areas.

```ts
const ambient = new THREE.AmbientLight(0x444444, 1);
scene.add(ambient);
```

**When to use:** Base fill light in every scene. Keep intensity low to avoid washed-out appearance.

### HemisphereLight

Two-color gradient light simulating sky/ground bounce. More natural than AmbientLight for outdoor scenes.

```ts
const hemi = new THREE.HemisphereLight(
  0xffffff, // sky color
  0x8d8d8d, // ground color
  3,
);
hemi.position.set(0, 20, 0);
scene.add(hemi);
```

**When to use:** Outdoor scenes where sky illumination differs from ground bounce.

### DirectionalLight

Parallel rays from an infinitely distant source. The primary shadow-casting light for most scenes.

```ts
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(3, 10, 10);
dirLight.castShadow = true;

dirLight.shadow.camera.top = 10;
dirLight.shadow.camera.bottom = -10;
dirLight.shadow.camera.left = -10;
dirLight.shadow.camera.right = 10;
dirLight.shadow.camera.near = 0.1;
dirLight.shadow.camera.far = 40;
dirLight.shadow.mapSize.width = 1024;
dirLight.shadow.mapSize.height = 1024;
dirLight.shadow.bias = -0.0005;

scene.add(dirLight);
```

**When to use:** Sun/moon simulation, primary scene illumination with shadows.

### PointLight

Emits light in all directions from a single point. Intensity decays with distance.

```ts
const point = new THREE.PointLight(0xff9900, 100, 50);
point.position.set(0, 5, 0);
point.castShadow = true;
scene.add(point);
```

**When to use:** Light bulbs, candles, torches. The second parameter is intensity; the third is `distance` (0 = infinite, no decay cutoff).

### SpotLight

Cone-shaped light with configurable angle and soft edges.

```ts
const spot = new THREE.SpotLight(0xff8888, 400);
spot.angle = Math.PI / 5;
spot.penumbra = 0.3;
spot.position.set(8, 10, 5);
spot.castShadow = true;
spot.shadow.mapSize.width = 1024;
spot.shadow.mapSize.height = 1024;
spot.shadow.camera.near = 1;
spot.shadow.camera.far = 200;
spot.shadow.bias = -0.002;
spot.shadow.radius = 4;
scene.add(spot);
```

**When to use:** Stage lighting, flashlights, focused illumination. `penumbra` (0-1) controls edge softness.

### Shadow Setup Checklist

1. `renderer.shadowMap.enabled = true`
2. `light.castShadow = true` on shadow-casting lights
3. `mesh.castShadow = true` on objects that cast shadows
4. `mesh.receiveShadow = true` on surfaces that receive shadows
5. Adjust `light.shadow.camera` bounds to tightly fit the scene (smaller = sharper shadows)

## Environment Maps

### CubeTextureLoader

Six-image cube maps for reflections and scene backgrounds:

```ts
const cubeLoader = new THREE.CubeTextureLoader();
const envMap = cubeLoader
  .setPath('/textures/cubemap/')
  .load(['px.jpg', 'nx.jpg', 'py.jpg', 'ny.jpg', 'pz.jpg', 'nz.jpg']);

scene.background = envMap;
scene.environment = envMap;
```

### HDR with RGBELoader

Higher dynamic range for physically-based reflections:

```ts
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const pmremGenerator = new THREE.PMREMGenerator(renderer);
pmremGenerator.compileEquirectangularShader();

new RGBELoader()
  .setPath('/textures/hdr/')
  .load('environment.hdr', (hdrTexture) => {
    const envMap = pmremGenerator.fromEquirectangular(hdrTexture).texture;
    scene.environment = envMap;
    scene.background = envMap;
    hdrTexture.dispose();
    pmremGenerator.dispose();
  });
```

`PMREMGenerator` converts equirectangular HDR images into prefiltered mipmap cube maps suitable for PBR materials. Always dispose both the source texture and the generator after use.

## Model Loading

### GLTFLoader with Draco

GLTF/GLB is the standard format for 3D web content. Draco compression reduces geometry size by up to 90%.

```ts
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath(
  'https://www.gstatic.com/draco/versioned/decoders/1.5.7/',
);
dracoLoader.setDecoderConfig({ type: 'js' });

const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load(
  '/models/scene.glb',
  (gltf) => {
    const model = gltf.scene;

    model.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });

    scene.add(model);
  },
  (progress) => {
    const percent = (progress.loaded / progress.total) * 100;
    console.log(`Loading: ${percent.toFixed(0)}%`);
  },
  (error) => {
    console.error('GLTF load failed:', error);
  },
);
```

### Loading Manager Pattern

Coordinate multiple asset loads with a single progress tracker:

```ts
const manager = new THREE.LoadingManager();

manager.onProgress = (_url, loaded, total) => {
  const progress = (loaded / total) * 100;
  document.getElementById('progress')!.style.width = `${progress}%`;
};

manager.onLoad = () => {
  document.getElementById('loading-screen')!.style.display = 'none';
};

const textureLoader = new THREE.TextureLoader(manager);
const gltfLoader = new GLTFLoader(manager);
```

### Disposal Pattern

GPU resources from loaded models must be explicitly freed:

```ts
function disposeModel(model: THREE.Object3D): void {
  model.traverse((child) => {
    if ((child as THREE.Mesh).isMesh) {
      const mesh = child as THREE.Mesh;
      mesh.geometry.dispose();
      if (Array.isArray(mesh.material)) {
        mesh.material.forEach((mat) => mat.dispose());
      } else {
        mesh.material.dispose();
      }
    }
  });
}
```

## Raycasting

Raycaster tests intersections between a ray and scene objects. Used for mouse/touch picking.

```ts
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

window.addEventListener('pointermove', (event) => {
  pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
  pointer.y = -(event.clientY / window.innerHeight) * 2 + 1;
});

function checkIntersections(
  camera: THREE.Camera,
  objects: THREE.Object3D[],
): THREE.Intersection[] {
  raycaster.setFromCamera(pointer, camera);
  return raycaster.intersectObjects(objects, true);
}
```

| Property                    | Purpose                                       |
| --------------------------- | --------------------------------------------- |
| `intersections[0].object`   | The intersected mesh                          |
| `intersections[0].point`    | World-space intersection point                |
| `intersections[0].face`     | The intersected face (normal, vertex indices) |
| `intersections[0].distance` | Distance from camera to intersection          |

The second argument to `intersectObjects` (`recursive: true`) traverses children, which is required for GLTF models where meshes are nested in groups.

## Practical Example: Complete Scene

```ts
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.1,
  100,
);
camera.position.set(0, 2, 5);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 1, 0);

new RGBELoader().load('/env.hdr', (hdr) => {
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envMap = pmrem.fromEquirectangular(hdr).texture;
  scene.environment = envMap;
  scene.background = envMap;
  scene.backgroundBlurriness = 0.3;
  hdr.dispose();
  pmrem.dispose();
});

const hemi = new THREE.HemisphereLight(0xffffff, 0x8d8d8d, 1);
scene.add(hemi);

const sun = new THREE.DirectionalLight(0xffffff, 3);
sun.position.set(5, 10, 5);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 0.1;
sun.shadow.camera.far = 30;
const d = 10;
sun.shadow.camera.left = -d;
sun.shadow.camera.right = d;
sun.shadow.camera.top = d;
sun.shadow.camera.bottom = -d;
scene.add(sun);

const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(50, 50),
  new THREE.MeshStandardMaterial({ color: 0xcccccc }),
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

const draco = new DRACOLoader();
draco.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.7/');
const loader = new GLTFLoader();
loader.setDRACOLoader(draco);

loader.load('/model.glb', (gltf) => {
  gltf.scene.traverse((child) => {
    if ((child as THREE.Mesh).isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });
  scene.add(gltf.scene);
});

function animate(): void {
  controls.update();
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```
