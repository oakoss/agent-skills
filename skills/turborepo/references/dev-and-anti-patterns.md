---
title: Watch Mode and Anti-Patterns
description: Watch mode configuration, dev server patterns, interruptible tasks, boundaries, and common anti-patterns
tags:
  [watch, dev, persistent, interruptible, boundaries, anti-patterns, parallel]
---

# Watch Mode and Anti-Patterns

## Watch Mode

Re-run tasks on file changes:

```bash
turbo watch dev
```

### Dev Task Configuration

```json
{
  "tasks": {
    "dev": {
      "dependsOn": ["^dev"],
      "cache": false,
      "persistent": false
    }
  }
}
```

Apps override with persistent:

```json
{
  "extends": ["//"],
  "tasks": {
    "dev": { "persistent": true }
  }
}
```

### with Key for Runtime Dependencies

Run tasks alongside (concurrent, not sequential):

```json
{
  "tasks": {
    "dev": {
      "with": ["api#dev"],
      "persistent": true,
      "cache": false
    }
  }
}
```

### interruptible Tasks

Allow `turbo watch` to restart tasks on dependency changes:

```json
{
  "tasks": {
    "dev": {
      "persistent": true,
      "interruptible": true,
      "cache": false
    }
  }
}
```

## Troubleshooting

### Tasks Running Sequentially

1. Check `dependsOn` -- `^build` forces sequential execution
2. For lint/typecheck, use Transit Nodes pattern instead
3. Remove unnecessary `dependsOn` entries

### Build Order Wrong

1. Verify `workspace:*` dependency is declared in `package.json`
2. Confirm `dependsOn: ["^build"]` is set in turbo.json
3. `^build` only triggers for declared dependencies

### Dev Server Not Picking Up Changes

1. Use `turbo watch dev` instead of `turbo run dev`
2. Set `interruptible: true` on dev tasks that should restart
3. Ensure dependency packages have a `dev` script

### Environment Variables Missing

1. Check if strict mode is filtering them (default behavior)
2. Add to `env`, `globalEnv`, or `globalPassThroughEnv`
3. Framework-specific vars are auto-included via inference

### Monorepo Structure Validation

- Use `turbo boundaries` to enforce package isolation
- Run `turbo run build --dry-run` to verify task graph
- Use `--filter` to test specific packages in isolation

## Anti-Patterns

### Using --parallel Flag

Bypasses dependency graph. Configure `dependsOn` correctly or use transit nodes instead.

### ../ in inputs

```json
// Bad
{ "inputs": ["$TURBO_DEFAULT$", "../shared-config.json"] }

// Good
{ "inputs": ["$TURBO_DEFAULT$", "$TURBO_ROOT$/shared-config.json"] }
```

### Too Many Root Dependencies

Root `package.json` should only have repo tooling (`turbo`, `prettier`, etc.). App dependencies belong in each package.
