---
title: Task Runner
description: Defining tasks in mise.toml with dependencies, scripts, arguments, watch mode, and incremental builds
tags: [tasks, run, depends, watch, scripts, arguments, sources, outputs, shell]
---

# Task Runner

## Inline Tasks

Simple tasks can be defined as key-value pairs:

```toml
[tasks]
build = "cargo build --release"
test = "cargo test"
lint = "eslint src/"
hello = "echo 'Hello World'"
```

Run with:

```bash
mise run build
mise run test
```

## Task Configuration

Full task configuration supports descriptions, aliases, environment overrides, and working directories:

```toml
[tasks.build]
description = "Build the project for production"
alias = "b"
run = "cargo build --release"
dir = "{{cwd}}"
env = { RUST_BACKTRACE = "1" }
```

## Dependencies Between Tasks

Tasks can depend on other tasks that run first:

```toml
[tasks.build]
run = "cargo build --release"

[tasks.test]
run = "cargo test"
depends = ["build"]

[tasks.ci]
description = "Run full CI pipeline"
depends = ["lint", "test", "build"]
```

The `depends` array ensures prerequisite tasks complete before the current task starts. When a task has only dependencies and no `run`, it acts as a task group.

## Multi-line Scripts

Use triple-quoted strings for multi-line scripts:

```toml
[tasks.deploy]
description = "Deploy to production"
run = """
#!/usr/bin/env bash
set -euo pipefail
echo "Building..."
cargo build --release
echo "Deploying..."
./scripts/deploy.sh
"""
```

## Multiple Commands

Run multiple commands sequentially with an array:

```toml
[tasks.setup]
run = [
    "mise install",
    "npm install",
    "npm run db:migrate"
]
```

## Different Interpreters

Specify a shebang or shell override to use non-bash interpreters:

```toml
[tasks.analyze]
run = """
#!/usr/bin/env python3
import json
with open("data.json") as f:
    data = json.load(f)
print(f"Records: {len(data)}")
"""

[tasks.script]
shell = "node -e"
run = "console.log('Hello from Node!')"
```

## Task Arguments

Pass arguments to tasks after `--`:

```bash
mise run test -- --watch --verbose
```

For structured arguments, use the `usage` field:

```toml
[tasks.greet]
usage = '''
arg "<name>" help="Name to greet" default="World"
flag "-l --loud" help="Shout the greeting"
'''
run = """
#!/usr/bin/env bash
if [ "$usage_loud" = "true" ]; then
    echo "HELLO ${usage_name^^}!"
else
    echo "Hello $usage_name!"
fi
"""
```

## Watch Mode

Re-run tasks automatically when source files change:

```bash
mise watch build
mise watch test
```

Watch mode uses the `sources` field to determine which files to monitor. Define sources on the task:

```toml
[tasks.build]
run = "tsc"
sources = ["src/**/*.ts", "tsconfig.json"]
```

## Incremental Builds (Sources and Outputs)

Skip tasks when source files have not changed since the last run:

```toml
[tasks.compile]
description = "Compile TypeScript"
run = "tsc"
sources = ["src/**/*.ts", "tsconfig.json"]
outputs = ["dist/**/*.js"]
```

If all `outputs` are newer than all `sources`, the task is skipped. Use `--force` to override:

```bash
mise run compile --force
```

## External Script Files

Reference standalone scripts instead of inline commands:

```toml
[tasks.release]
file = "scripts/release.sh"
description = "Cut a new release"
```

## Confirmation Prompts

Require confirmation before running destructive tasks:

```toml
[tasks.deploy]
run = "./scripts/deploy.sh"
confirm = "Are you sure you want to deploy to production?"
```

## Task Output Modes

Control how task output is displayed:

```bash
# Default: prefix each line with task name
mise run ci

# Interleave output from parallel tasks
mise run ci --output interleave

# Silent mode (errors only)
mise run ci --output silent

# Quiet mode (minimal output)
mise run ci --quiet
```

## Parallel Task Execution

Independent tasks in a dependency graph run in parallel by default. Control parallelism with `--jobs`:

```bash
mise run ci --jobs 4
```

## Listing Tasks

```bash
# Show all available tasks
mise tasks

# Show tasks with descriptions
mise tasks --extended

# Dry run (show execution plan without running)
mise run ci --dry-run
```

## File-based Tasks

Tasks can be defined as executable files in a `.mise/tasks/` directory:

```bash
# .mise/tasks/build
#!/usr/bin/env bash
set -euo pipefail
cargo build --release
```

```bash
# .mise/tasks/test
#!/usr/bin/env python3
import subprocess
subprocess.run(["pytest", "-v"], check=True)
```

File-based tasks are discovered automatically. The filename becomes the task name.
