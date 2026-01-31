---
title: Configuration
description: Vitest configuration with vitest.config.ts, workspace setup, coverage configuration, reporters, browser mode, and environment settings
tags:
  [
    vitest.config,
    workspace,
    coverage,
    reporters,
    environment,
    globals,
    setupFiles,
    browser-mode,
  ]
---

# Configuration

## Basic Configuration

Create `vitest.config.ts` in your project root:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./vitest.setup.ts'],
  },
});
```

## Shared Config with Vite

Vitest reads your `vite.config.ts` by default. Add test-specific config:

```ts
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
  },
});
```

## Separate Test Config

Use conditional config or separate files:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'node',
  },
});
```

Or merge configs:

```ts
import viteConfig from './vite.config';
import { mergeConfig, defineConfig } from 'vitest/config';

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
    },
  }),
);
```

## Test Environment

Choose the runtime environment:

```ts
export default defineConfig({
  test: {
    environment: 'node',
  },
});
```

Available environments:

- `node` — default, Node.js environment (no DOM)
- `jsdom` — JSDOM, simulated browser environment
- `happy-dom` — Happy DOM, faster alternative to JSDOM
- `edge-runtime` — Edge runtime environment

Per-file environment:

```ts
/**
 * @vitest-environment jsdom
 */

import { render } from '@testing-library/react';
```

## Global Test APIs

Enable global test APIs (no imports needed):

```ts
export default defineConfig({
  test: {
    globals: true,
  },
});
```

Add TypeScript types in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

Now use `describe`, `it`, `expect` without imports.

## Setup Files

Run code before tests:

```ts
export default defineConfig({
  test: {
    setupFiles: ['./vitest.setup.ts'],
  },
});
```

Example `vitest.setup.ts`:

```ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});
```

## Coverage Configuration

Configure code coverage:

```ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.config.{ts,js}',
        '**/*.test.{ts,tsx}',
        '**/types.ts',
      ],
      thresholds: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80,
      },
    },
  },
});
```

Coverage providers:

- `v8` — fast, native V8 coverage (default)
- `istanbul` — more detailed reports, slower

Run coverage:

```bash
vitest --coverage
```

## Workspace Configuration

Test multiple projects in one workspace:

```ts
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  {
    test: {
      name: 'unit',
      environment: 'node',
      include: ['src/**/*.test.ts'],
    },
  },
  {
    test: {
      name: 'browser',
      environment: 'jsdom',
      include: ['src/**/*.test.tsx'],
    },
  },
]);
```

Or use glob patterns:

```ts
export default defineWorkspace(['packages/*']);
```

Run specific project:

```bash
vitest --project unit
```

## Browser Mode

Run tests in real browsers:

```ts
export default defineConfig({
  test: {
    browser: {
      enabled: true,
      name: 'chromium',
      provider: 'playwright',
      headless: true,
    },
  },
});
```

Available browsers:

- `chromium`, `firefox`, `webkit` (Playwright)
- `chrome`, `edge`, `firefox`, `safari` (WebdriverIO)

## Reporters

Configure test output:

```ts
export default defineConfig({
  test: {
    reporters: ['default', 'html', 'json'],
    outputFile: {
      html: './test-results/index.html',
      json: './test-results/results.json',
    },
  },
});
```

Built-in reporters:

- `default` — default CLI output
- `verbose` — detailed output
- `dot` — minimal dot output
- `json` — JSON output
- `html` — HTML report
- `junit` — JUnit XML
- `tap` — TAP format
- `github-actions` — GitHub Actions annotations
- `hanging-process` — detect hanging processes

## Test Timeout

Set global timeout:

```ts
export default defineConfig({
  test: {
    testTimeout: 10000,
    hookTimeout: 10000,
  },
});
```

Per-test timeout:

```ts
test('slow operation', async () => {
  await slowOperation();
}, 30000);
```

## Include and Exclude Patterns

Control which files are tested:

```ts
export default defineConfig({
  test: {
    include: ['**/*.{test,spec}.{ts,tsx}'],
    exclude: [
      'node_modules',
      'dist',
      '.next',
      'e2e/**',
      '**/*.e2e.{test,spec}.{ts,tsx}',
    ],
  },
});
```

## Watch Mode Settings

Configure watch behavior:

```ts
export default defineConfig({
  test: {
    watch: true,
    watchExclude: ['**/node_modules/**', '**/dist/**'],
  },
});
```

## Sequence and Pool

Control test execution order:

```ts
export default defineConfig({
  test: {
    sequence: {
      shuffle: true,
      concurrent: true,
    },
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true,
      },
    },
  },
});
```

Pool options:

- `threads` — worker threads (default)
- `forks` — child processes
- `vmThreads` — VM context in worker threads

## Mock Configuration

Configure module mocking:

```ts
export default defineConfig({
  test: {
    mockReset: true,
    restoreMocks: true,
    clearMocks: true,
  },
});
```

- `mockReset` — reset mocks after each test
- `restoreMocks` — restore spies after each test
- `clearMocks` — clear call history after each test

## Snapshot Settings

Configure snapshot behavior:

```ts
export default defineConfig({
  test: {
    snapshotFormat: {
      printBasicPrototype: false,
    },
    resolveSnapshotPath: (testPath, snapExtension) => {
      return testPath.replace(/\.test\.([tj]sx?)/, `${snapExtension}.$1`);
    },
  },
});
```

## In-Source Testing

Enable tests in source files:

```ts
export default defineConfig({
  test: {
    includeSource: ['src/**/*.ts'],
  },
  define: {
    'import.meta.vitest': 'undefined',
  },
});
```

Write tests in source files:

```ts
export function add(a: number, b: number) {
  return a + b;
}

if (import.meta.vitest) {
  const { it, expect } = import.meta.vitest;

  it('adds numbers', () => {
    expect(add(1, 2)).toBe(3);
  });
}
```

## TypeScript Configuration

Add triple-slash directive for types:

```ts
/// <reference types="vitest/config" />
import { defineConfig } from 'vite';

export default defineConfig({
  test: {},
});
```

Or in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
```

## Alias Configuration

Share aliases with Vite:

```ts
import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

## Conditional Config

Different config for CI:

```ts
export default defineConfig({
  test: {
    coverage: { enabled: process.env.CI === 'true' },
    reporters: process.env.CI ? ['github-actions'] : ['default'],
  },
});
```
