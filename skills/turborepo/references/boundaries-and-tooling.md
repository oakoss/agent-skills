---
title: Boundaries, Query, and Code Generation
description: Package boundary enforcement, GraphQL repository queries, code generation, and developer tooling
tags: [boundaries, tags, query, graphql, generate, generators, ls, devtools]
---

# Boundaries, Query, and Code Generation

## Boundaries

Enforce package isolation rules to catch import violations and undeclared dependencies.

### Enable Boundaries

Add to root `turbo.json`:

```json
{
  "boundaries": {}
}
```

Run the check:

```bash
turbo boundaries
```

Catches two types of violations:

- Importing a file outside the package's directory
- Importing a package not declared in the package's `package.json`

### Boundary Tags

Tags allow custom rules for package dependency relationships. Define tags in each package's `turbo.json`:

```json
{
  "tags": ["internal"],
  "extends": ["//"],
  "tasks": {}
}
```

Define tag rules in root `turbo.json`:

```json
{
  "boundaries": {
    "tags": {
      "public": {
        "dependencies": {
          "allow": ["public"]
        }
      },
      "internal": {
        "dependents": {
          "deny": ["public"]
        }
      }
    }
  }
}
```

### Tag Rule Options

| Rule                 | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `dependencies.allow` | Tags/packages this tagged package can depend on            |
| `dependencies.deny`  | Tags/packages this tagged package cannot depend on         |
| `dependents.allow`   | Tags/packages allowed to depend on this tagged package     |
| `dependents.deny`    | Tags/packages denied from depending on this tagged package |

Rules apply transitively -- violations are caught even through intermediate dependencies.

### Common Boundary Patterns

Separate public and internal packages:

```json
{
  "boundaries": {
    "tags": {
      "public": {
        "dependencies": {
          "deny": ["internal"]
        }
      }
    }
  }
}
```

Isolate feature domains:

```json
{
  "boundaries": {
    "tags": {
      "auth": {
        "dependencies": {
          "allow": ["auth", "shared"]
        }
      },
      "billing": {
        "dependencies": {
          "allow": ["billing", "shared"]
        }
      }
    }
  }
}
```

## turbo query

Run GraphQL queries against the repository's package and task graphs:

```bash
turbo query
```

Opens a GraphiQL playground when run without arguments.

### Query Examples

Find all packages that depend on a specific package:

```bash
turbo query "{ packages(filter: { dependents: { name: { equal: \"@repo/ui\" } } }) { items { name } } }"
```

Query from a file:

```bash
turbo query path/to/query.gql
```

Machine-readable output:

```bash
turbo query --output=json "{ packages { items { name path } } }"
```

### Use Cases

- Discover dependency relationships between packages
- Find changed packages and their dependents
- Audit task configurations across the monorepo
- Build custom CI pipelines based on graph data

## turbo generate

Scaffold new packages and run custom generators.

### Create a New Package

```bash
turbo generate workspace
turbo generate workspace --name @repo/new-lib --copy @repo/ui
```

Options:

| Flag      | Description                   |
| --------- | ----------------------------- |
| `--name`  | Name for the new package      |
| `--copy`  | Source package to copy from   |
| `--empty` | Create an empty workspace     |
| `--type`  | Package type (app or package) |

### Custom Generators

Define generators in `turbo/generators/config.ts`:

```ts
import type { PlopTypes } from '@turbo/gen';

export default function generator(plop: PlopTypes.NodePlopAPI): void {
  plop.setGenerator('component', {
    description: 'Create a new React component',
    prompts: [
      {
        type: 'input',
        name: 'name',
        message: 'Component name?',
      },
    ],
    actions: [
      {
        type: 'add',
        path: 'packages/ui/src/{{kebabCase name}}.tsx',
        templateFile: 'turbo/generators/templates/component.hbs',
      },
    ],
  });
}
```

Run a custom generator:

```bash
turbo generate run component
turbo gen component --args "Button"
```

Install the generator dependency:

```bash
pnpm add -D @turbo/gen
```

## turbo ls

List all packages in the monorepo:

```bash
turbo ls
```

Shows package names and their directories.

### Filter Package List

```bash
turbo ls --filter=./packages/*
turbo ls --affected
```

## turbo devtools

Visual explorer for Package Graph and Task Graph:

```bash
turbo devtools
```

Hot-reloads as you make changes to `turbo.json` or package structure. Useful for debugging dependency relationships and task ordering.
