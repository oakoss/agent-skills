---
title: CLI and Filtering
description: Vitest CLI commands, watch mode, test filtering by name and path, tags, sharding for CI, and lint-staged integration
tags: [cli, watch, filtering, tags, sharding, ci, vitest-run, lint-staged]
---

# CLI and Filtering

## Running Tests

Start Vitest in watch mode (default for development):

```bash
vitest
```

Single run without watch (CI, scripts):

```bash
vitest run
```

Run tests related to changed source files (dependency graph aware):

```bash
vitest related src/utils/format.ts
```

List matching test files without running them:

```bash
vitest list
vitest list src/components/
```

Run benchmarks:

```bash
vitest bench
```

## Common Flags

```bash
vitest run --changed              # Tests affected by uncommitted git changes
vitest run --changed HEAD~1       # Tests affected since last commit
vitest -t "should validate"       # Filter by test name pattern
vitest run --bail 1               # Stop after first failure
vitest run --retry 3              # Retry failed tests up to 3 times
vitest run --reporter=verbose     # Detailed output per test
vitest run --reporter=junit       # JUnit XML for CI
vitest run --project=unit         # Run specific workspace project
vitest run --shard 1/3            # Run first third of tests
vitest run --pool=forks           # Use child processes instead of threads
vitest run --no-coverage          # Skip coverage even if configured
```

## Watch Mode Keyboard Shortcuts

When Vitest is running in watch mode, press these keys:

| Key     | Action                    |
| ------- | ------------------------- |
| `a`     | Run all tests             |
| `f`     | Re-run only failed tests  |
| `p`     | Filter by filename        |
| `t`     | Filter by test name       |
| `q`     | Quit                      |
| `Enter` | Re-run current test suite |
| `h`     | Show help                 |

The `p` and `t` filters accept regex patterns. Press `Escape` to clear a filter.

## Test Filtering

### By File Path Pattern

Pass a file pattern as a positional argument:

```bash
vitest run src/components/
vitest run Button
vitest run "src/**/*.integration.test.ts"
```

### By Test Name

Use `-t` or `--testNamePattern` to match `describe` and `test` names:

```bash
vitest -t "should handle errors"
vitest -t "validation"
```

Combine file and name filters:

```bash
vitest run src/auth/ -t "login"
```

### Changed Files Only

Run tests affected by git changes:

```bash
vitest run --changed
```

Compare against a specific branch:

```bash
vitest run --changed main
```

### Dependency Graph with `vitest related`

Find and run tests that import a specific source file, directly or transitively:

```bash
vitest related src/utils/format.ts src/utils/date.ts
```

This traces the import graph to find all test files that depend on the given files.

## Tags

Annotate tests with tags for selective execution:

```ts
import { describe, test } from 'vitest';

test('connects to database', { tags: ['db'] }, () => {
  // ...
});

test('validates input', { tags: ['unit', 'fast'] }, () => {
  // ...
});

describe('payment processing', { tags: ['integration', 'slow'] }, () => {
  test('charges card', () => {
    // ...
  });
});
```

### Running by Tag

Filter tests by tag expression:

```bash
vitest run --tags-filter db
vitest run --tags-filter "unit or fast"
vitest run --tags-filter "integration and not slow"
vitest run --tags-filter "!flaky"
```

Use `and`, `or`, `not`, and `!` operators within `--tags-filter`. List all defined tags with `--list-tags`.

### Strict Tags Config

Require all tests to use pre-defined tags:

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    strictTags: true,
    tags: [
      { name: 'unit' },
      { name: 'integration' },
      { name: 'slow', timeout: 30_000 },
    ],
  },
});
```

## Sharding for CI

Split the test suite across multiple CI workers:

```bash
vitest run --shard 1/3
vitest run --shard 2/3
vitest run --shard 3/3
```

Each shard gets a deterministic subset of test files. The denominator is the total number of shards.

### GitHub Actions Matrix Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1/3, 2/3, 3/3]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: 20
      - run: npm ci
      - run: npx vitest run --shard ${{ matrix.shard }} --reporter=blob
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: blob-report-${{ strategy.job-index }}
          path: .vitest-reports/

  merge-reports:
    needs: test
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: 20
      - run: npm ci
      - uses: actions/download-artifact@v4
        with:
          pattern: blob-report-*
          path: .vitest-reports/
          merge-multiple: true
      - run: npx vitest --merge-reports
```

The `--reporter=blob` flag produces a binary report that `--merge-reports` combines into a unified result.

### Coverage with Sharding

Merge coverage reports from sharded runs:

```yaml
- run: npx vitest run --shard ${{ matrix.shard }} --coverage
- uses: actions/upload-artifact@v4
  with:
    name: coverage-${{ strategy.job-index }}
    path: coverage/
```

Then merge with your coverage tool (e.g., `istanbul-merge` or `c8 merge`).

## lint-staged Integration

Run only related tests on staged files before committing:

```json
{
  "*.{ts,tsx}": ["vitest related --run"]
}
```

The `--run` flag ensures single-run mode (no watch). `vitest related` traces the import graph from the staged files to find affected tests.

### With ESLint and Prettier

```json
{
  "*.{ts,tsx}": ["eslint --fix", "prettier --write", "vitest related --run"]
}
```

## Reporter Options

Built-in reporters for different output needs:

```bash
vitest run --reporter=default         # Grouped by file
vitest run --reporter=verbose         # Every test on its own line
vitest run --reporter=dot             # Minimal dots
vitest run --reporter=json            # JSON to stdout
vitest run --reporter=junit           # JUnit XML
vitest run --reporter=html            # Interactive HTML report
vitest run --reporter=hanging-process # Debug leaked handles
```

Use multiple reporters simultaneously:

```bash
vitest run --reporter=default --reporter=junit --outputFile.junit=results.xml
```

### Config-Based Reporters

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    reporters: ['default', 'junit'],
    outputFile: {
      junit: 'test-results/junit.xml',
    },
  },
});
```

## Project Filtering

In a monorepo with multiple test projects, run tests for specific projects:

```bash
vitest run --project=unit
vitest run --project=integration --project=e2e
```

Projects are defined in `vitest.config.ts` using the `projects` option (v3.2+):

```ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: 'unit',
          include: ['src/**/*.test.ts'],
        },
      },
      {
        test: {
          name: 'integration',
          include: ['tests/integration/**/*.test.ts'],
        },
      },
    ],
  },
});
```
