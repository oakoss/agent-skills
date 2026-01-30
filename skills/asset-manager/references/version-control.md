---
title: Version Control
description: Git LFS setup for large design files, hash-based asset versioning system, and change tracking
tags: [git-lfs, versioning, hashing, change-tracking, assets]
---

# Version Control

## Git LFS Setup

Track large design files with Git LFS:

```bash
brew install git-lfs
git lfs install

git lfs track "*.psd"
git lfs track "*.ai"
git lfs track "*.sketch"
git lfs track "*.fig"
git lfs track "*.mp4"
git lfs track "*.mov"
git lfs track "assets/images/**/*.jpg"
git lfs track "assets/images/**/*.png"

git add .gitattributes
git commit -m "Configure Git LFS"
```

## Asset Versioning System

Track asset changes with SHA-256 hashing:

```ts
import fs from 'fs/promises';
import path from 'path';
import crypto from 'crypto';

interface AssetVersion {
  path: string;
  hash: string;
  size: number;
  modified: string;
  version: number;
}

class AssetVersionManager {
  private versionFile = 'asset-versions.json';
  private versions: Map<string, AssetVersion[]> = new Map();

  async load() {
    try {
      const data = await fs.readFile(this.versionFile, 'utf-8');
      const parsed = JSON.parse(data);

      for (const [path, versions] of Object.entries(parsed)) {
        this.versions.set(path, versions as AssetVersion[]);
      }
    } catch {
      // File doesn't exist yet
    }
  }

  async save() {
    const data = Object.fromEntries(this.versions);
    await fs.writeFile(this.versionFile, JSON.stringify(data, null, 2));
  }

  async trackAsset(filePath: string) {
    const buffer = await fs.readFile(filePath);
    const hash = crypto.createHash('sha256').update(buffer).digest('hex');
    const stat = await fs.stat(filePath);

    const versions = this.versions.get(filePath) || [];
    const lastVersion = versions[versions.length - 1];

    if (lastVersion && lastVersion.hash === hash) {
      return;
    }

    versions.push({
      path: filePath,
      hash,
      size: stat.size,
      modified: stat.mtime.toISOString(),
      version: versions.length + 1,
    });

    this.versions.set(filePath, versions);
  }

  async trackDirectory(dirPath: string) {
    const files = await fs.readdir(dirPath, { recursive: true });

    for (const file of files) {
      const filePath = path.join(dirPath, file.toString());
      const stat = await fs.stat(filePath);

      if (stat.isDirectory()) continue;

      await this.trackAsset(filePath);
    }
  }
}
```

Usage:

```ts
const manager = new AssetVersionManager();
await manager.load();
await manager.trackDirectory('./assets');
await manager.save();
```
