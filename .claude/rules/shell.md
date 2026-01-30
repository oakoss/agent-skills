# Shell Commands

## Avoid Interactive Prompts

Always use non-interactive flags to prevent commands from blocking on user input.

| Command            | Interactive     | Non-Interactive       |
| ------------------ | --------------- | --------------------- |
| Remove files       | `rm file`       | `rm -f file`          |
| Remove directories | `rm -r dir`     | `rm -rf dir`          |
| Copy overwrite     | `cp file dest`  | `cp -f file dest`     |
| Move overwrite     | `mv file dest`  | `mv -f file dest`     |
| Git rebase         | `git rebase -i` | Avoid - not supported |
| Git add            | `git add -i`    | `git add file`        |

## Why This Matters

Interactive prompts cause background tasks to hang indefinitely waiting for input that never comes. The task will be killed after timeout, leaving work incomplete.

```sh
# Bad - prompts "remove file?"
rm important-file.txt

# Good - removes without prompting
rm -f important-file.txt

# Bad - prompts for each file
rm -r directory/

# Good - removes recursively without prompting
rm -rf directory/
```

## General Principles

- Prefer flags that assume "yes" (`-f`, `-y`, `--yes`, `--force`)
- Avoid interactive modes (`-i`, `--interactive`)
- Use `echo "y" | command` as last resort if no flag exists
- Test destructive commands on specific paths, not wildcards

## Monorepo Commands

Use Turborepo for running commands across packages:

```sh
# Run in all packages
pnpm turbo run build

# Run in specific package
pnpm turbo run build --filter=@oakoss/ui

# Run in web app only
pnpm turbo run dev --filter=web

# Run dev in parallel
pnpm dev
```

## Common Scripts

```sh
# Development
pnpm dev              # Start all dev servers
pnpm build            # Build all packages
pnpm typecheck        # Type check all packages
pnpm lint             # Lint all packages
pnpm lint:fix         # Lint and fix
pnpm format           # Format with Prettier

# Database
pnpm db:generate      # Generate Drizzle migrations
pnpm db:migrate       # Run migrations
pnpm db:push          # Push schema to DB

# Testing
pnpm test             # Run tests

# Cleanup
pnpm clean            # Remove all build artifacts
```
