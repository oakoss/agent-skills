---
title: Configuration
description: Vitest configuration with vitest.config.ts, workspace setup, coverage configuration, reporters, browser mode, and environment settings
tags:
  [
    vitest.config,
    projects,
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

Files execute in order. See the test-setup reference for setup file contents — jest-dom matchers, cleanup, MSW server lifecycle, and DOM polyfills.

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

### Coverage Enhancements

V8 coverage is faster but Istanbul handles edge cases like decorators better. Ignore specific lines with `/* v8 ignore next */` or `/* istanbul ignore next */`. Set `thresholds.autoUpdate: true` to auto-update coverage thresholds as coverage improves:

```ts
export default defineConfig({
  test: {
    coverage: {
      thresholds: { autoUpdate: true },
    },
  },
});
```

## Projects Configuration (v3.2+)

Define multiple test projects in a single config. The `projects` option replaces the deprecated `workspace` and removed `vitest.workspace` file:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: [
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
    ],
  },
});
```

Or use glob patterns:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: ['packages/*'],
  },
});
```

Run specific project:

```bash
vitest --project unit
```

### Legacy Workspace Migration

If migrating from `vitest.workspace.js`, move config into `vitest.config.ts`:

```ts
// Legacy (deprecated in v3.2, removed in v4)
// import { defineWorkspace } from 'vitest/config';
// export default defineWorkspace([...])

// Current approach
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: ['./packages/*', { test: { name: 'unit' } }],
  },
});
```

## Browser Mode

Run tests in real browsers. Use `projects` to run browser and unit tests together:

```ts
import { defineConfig } from 'vitest/config';
import { playwright } from '@vitest/browser-playwright';

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          environment: 'node',
          include: ['tests/unit/**/*.test.ts'],
        },
      },
      {
        test: {
          name: 'browser',
          browser: {
            enabled: true,
            provider: playwright(),
            instances: [{ browser: 'chromium' }],
          },
          include: ['tests/browser/**/*.test.ts'],
        },
      },
    ],
  },
});
```

Initialize browser mode quickly:

```bash
npx vitest init browser
```

Available browser providers:

- `@vitest/browser-playwright` — Chromium, Firefox, WebKit
- `@vitest/browser-webdriverio` — Chrome, Edge, Firefox, Safari

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

For in-source testing patterns, see the advanced-patterns reference.

## Provide / Inject

Share values from config to tests:

```ts
export default defineConfig({
  test: {
    provide: {
      apiUrl: 'http://localhost:3000',
    },
  },
});
```

Access in tests with `inject('apiUrl')`. See the fixtures-and-context reference for full patterns.

## TypeScript Configuration

Add types in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals", "@testing-library/jest-dom"]
  }
}
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
