---
title: Module Patterns
description: Inline type imports, declaration files, module augmentation, and ambient types
tags: [modules, type-imports, declarations, augmentation, ambient-types, d.ts]
---

# Module Patterns

TypeScript module patterns for organizing types, augmenting third-party libraries, and managing ambient declarations.

## Inline Type Imports

Import types explicitly with `type` keyword:

```ts
import { type User, createUser } from './user';
import { type Config } from './config';

function processUser(user: User) {
  console.log(user.name);
}

import { type FC } from 'react';

const Button: FC<{ label: string }> = ({ label }) => {
  return <button>{label}</button>;
};
```

Inline type imports are removed from compiled JavaScript, reducing bundle size.

## Type-Only Imports

Import only types:

```ts
import type { User, Post, Comment } from './types';

function renderUser(user: User) {
  console.log(user.name);
}

import type * as Types from './types';

function renderPost(post: Types.Post) {
  console.log(post.title);
}
```

`import type` ensures the import is only used for types, never values.

## Type-Only Exports

Export types explicitly:

```ts
export type { User, Post } from './types';

export type { Config as AppConfig } from './config';

type User = { id: string; name: string };
export type { User };

export { createUser };
export type { User };
```

Type-only exports clarify which exports are types vs values.

## Declaration Files

Define types without implementation:

```ts
declare module 'my-library' {
  export function doSomething(input: string): string;
  export class MyClass {
    constructor(name: string);
    getName(): string;
  }
  export const VERSION: string;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module '*.css' {
  const classes: Record<string, string>;
  export default classes;
}
```

Declaration files (`.d.ts`) contain only type information.

## Module Augmentation

Extend third-party module types:

```ts
import 'express';

declare module 'express' {
  interface Request {
    user?: {
      id: string;
      name: string;
    };
  }
}

import 'fastify';

declare module 'fastify' {
  interface FastifyRequest {
    user: User;
  }
}

import '@tanstack/react-query';

declare module '@tanstack/react-query' {
  interface Register {
    defaultError: AxiosError;
  }
}
```

Module augmentation adds properties to existing types from external libraries.

## Global Augmentation

Add types to the global scope:

```ts
declare global {
  interface Window {
    ENV: {
      API_URL: string;
      VERSION: string;
    };
  }

  const API_URL: string;

  namespace NodeJS {
    interface ProcessEnv {
      DATABASE_URL: string;
      API_KEY: string;
    }
  }
}

export {};

declare global {
  type UUID = string;
  type Timestamp = number;
}

export {};
```

Use `declare global` to add types to the global scope. The `export {}` makes the file a module.

## Ambient Declarations

Declare types for untyped libraries:

```ts
declare const VERSION: string;
declare const BUILD_TIME: number;

declare function gtag(
  command: 'config' | 'event',
  targetId: string,
  config?: Record<string, unknown>,
): void;

declare class Analytics {
  constructor(apiKey: string);
  track(event: string, properties?: Record<string, unknown>): void;
  identify(userId: string, traits?: Record<string, unknown>): void;
}

declare namespace Stripe {
  interface StripeStatic {
    (key: string): StripeInstance;
  }
  interface StripeInstance {
    createToken(element: Element): Promise<TokenResponse>;
  }
}
```

Ambient declarations describe the shape of external code without providing implementation.

## Triple-Slash Directives

Reference other declaration files:

```ts
/// <reference types="node" />
/// <reference path="./custom.d.ts" />

/// <reference lib="es2020" />
/// <reference lib="dom" />

export function readFile(path: string): Buffer;
```

Triple-slash directives are legacy syntax. Prefer `import` statements.

## UMD Modules

Declare types for UMD libraries:

```ts
export as namespace MyLibrary;

export function doSomething(input: string): string;

export class MyClass {
  constructor(name: string);
}

declare global {
  interface Window {
    MyLibrary: typeof import('./index');
  }
}
```

UMD modules work in both module and global contexts.

## Namespace Augmentation

Extend namespaces:

```ts
declare namespace MyNamespace {
  interface Config {
    apiUrl: string;
  }
}

declare namespace MyNamespace {
  interface Config {
    timeout: number;
  }

  function init(config: Config): void;
}

const config: MyNamespace.Config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
};
```

Multiple `declare namespace` declarations merge into a single namespace.

## Exporting from Declaration Files

Export types from `.d.ts` files:

```ts
export type User = {
  id: string;
  name: string;
};

export interface Post {
  id: string;
  title: string;
  authorId: string;
}

export declare function createUser(name: string): User;

export declare class Database {
  constructor(url: string);
  query(sql: string): Promise<unknown[]>;
}
```

Declaration files can export types, interfaces, and declare functions/classes.

## Module Resolution

Configure module resolution:

```json
{
  "compilerOptions": {
    "moduleResolution": "bundler",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "~/*": ["app/*"]
    }
  }
}
```

Use path mapping for cleaner imports:

```ts
import { User } from '@/types/user';
import { config } from '~/config';
```

## CommonJS Interop

Import CommonJS modules:

```ts
import express from 'express';
import * as express from 'express';

const express = require('express');

export = MyClass;

import MyClass = require('./my-class');
```

Use `esModuleInterop` for better CommonJS/ESM compatibility:

```json
{
  "compilerOptions": {
    "esModuleInterop": true
  }
}
```

## Real-World Example: Typed Environment Variables

```ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NODE_ENV: 'development' | 'production' | 'test';
      DATABASE_URL: string;
      API_KEY: string;
      PORT?: string;
    }
  }
}

export {};

const dbUrl: string = process.env.DATABASE_URL;
const port: number = Number.parseInt(process.env.PORT ?? '3000');
const isDev: boolean = process.env.NODE_ENV === 'development';
```

Type-safe environment variables prevent runtime errors.

## Package Exports Field

Define package entry points:

```json
{
  "name": "my-library",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./utils": {
      "types": "./dist/utils.d.ts",
      "import": "./dist/utils.mjs"
    }
  }
}
```

The `exports` field defines how your package can be imported.

## Type-Only Packages

Publish types separately:

```json
{
  "name": "@types/my-library",
  "version": "1.0.0",
  "types": "index.d.ts",
  "files": ["*.d.ts"]
}
```

Create type-only packages for untyped JavaScript libraries.

## Declaration Maps

Generate source maps for types:

```json
{
  "compilerOptions": {
    "declaration": true,
    "declarationMap": true
  }
}
```

Declaration maps enable "Go to Definition" for compiled libraries.

## Composite Projects

Split large codebases into projects:

```json
{
  "compilerOptions": {
    "composite": true,
    "rootDir": ".",
    "outDir": "dist"
  },
  "references": [{ "path": "../shared" }]
}
```

Use project references for incremental builds:

```ts
import { User } from '@shared/types';

export function processUser(user: User) {
  console.log(user.name);
}
```

## Module Wildcards

Handle dynamic imports:

```ts
declare module 'virtual:*' {
  const content: string;
  export default content;
}

declare module '*.svg?component' {
  import { type FC } from 'react';
  const Component: FC;
  export default Component;
}

declare module '*.module.css' {
  const classes: Record<string, string>;
  export default classes;
}

declare module 'data:*' {
  const content: string;
  export default content;
}
```

Module wildcards handle build tool-specific imports.
