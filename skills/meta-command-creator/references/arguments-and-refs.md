---
title: Arguments and References
description: $ARGUMENTS placeholder, positional arguments, bash injection with ! prefix, file references with @ prefix, and session variables
tags:
  [
    arguments,
    positional,
    bash-injection,
    file-reference,
    session-id,
    dynamic-context,
  ]
---

# Arguments and References

## $ARGUMENTS Placeholder

When a user invokes `/command some text here`, the string `some text here` is available as `$ARGUMENTS`. If the command content does not include `$ARGUMENTS`, Claude Code appends `ARGUMENTS: <value>` to the end of the content.

### Basic usage

```markdown
---
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

## Steps

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

Invocation: `/fix-issue 123` replaces `$ARGUMENTS` with `123`.

### Handling empty arguments

Always account for the case where no arguments are provided:

```markdown
---
description: Build the project
argument-hint: [target]
---

Build target: $ARGUMENTS

## Steps

1. If no arguments provided, run the default build
2. Otherwise, build the specified target
3. Report results
```

## Positional Arguments

Access individual arguments by zero-based index using `$ARGUMENTS[N]` or the shorthand `$N`.

### $ARGUMENTS[N] syntax

```markdown
---
description: Migrate a component between frameworks
argument-hint: [component] [from] [to]
---

Migrate the $ARGUMENTS[0] component from $ARGUMENTS[1] to $ARGUMENTS[2].
Preserve all existing behavior and tests.
```

Invocation: `/migrate-component SearchBar React Vue`

- `$ARGUMENTS[0]` = `SearchBar`
- `$ARGUMENTS[1]` = `React`
- `$ARGUMENTS[2]` = `Vue`

### $N shorthand

The same command using shorthand notation:

```markdown
---
description: Migrate a component between frameworks
argument-hint: [component] [from] [to]
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

### Two-argument pattern

```markdown
---
description: Create a new file from template
argument-hint: [type] [name]
---

Create a $0 named $1

## Steps

1. Determine template based on type $0
2. Create file named $1
3. Apply project conventions
```

Invocation: `/create component UserProfile`

## Bash Injection (! Prefix)

The `` !`command` `` syntax runs shell commands before the skill content is sent to Claude. The command output replaces the placeholder. This is preprocessing, not something Claude executes.

### Requirements

- The `allowed-tools` frontmatter MUST include `Bash(...)` when using `!` prefix
- Commands run in the project root directory
- Output is inserted inline where the placeholder appears

### Git context example

```markdown
---
description: Create a conventional git commit
allowed-tools: Bash(git add:*), Bash(git commit:*), Bash(git status:*), Bash(git diff:*)
argument-hint: [optional message]
---

## Context

- Current status: !`git status`
- Current diff: !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`

## Steps

1. Analyze the changes shown above
2. Stage appropriate files
3. Create commit with conventional format: type(scope): description

## Format

Use these types: feat, fix, docs, style, refactor, perf, test, chore
```

### PR review example

```markdown
---
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context

- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task

Summarize this pull request. Focus on:

1. What changed and why
2. Potential risks
3. Testing recommendations
```

### Multiple dynamic sources

```markdown
---
description: Review staged changes before commit
allowed-tools: Bash(git:*), Read, Grep, Glob
---

## Context

- Staged changes: !`git diff --cached`
- Modified files: !`git diff --cached --name-only`
- Current branch: !`git branch --show-current`

## Steps

1. Review each changed file
2. Check against project conventions
3. Look for common issues
4. Provide structured feedback
```

## File References (@ Prefix)

The `@` prefix inlines file contents into the command prompt. Use it to give Claude direct access to specific files without requiring tool calls.

### Basic usage

```markdown
---
description: Review configuration files
---

Review the following configuration for issues:

- Package config: @package.json
- TypeScript config: @tsconfig.json
- ESLint config: @eslint.config.js
```

### Comparing files

```markdown
---
description: Compare two implementations
argument-hint: [file1] [file2]
---

Compare @$0 with @$1 and summarize the differences.

Focus on:

1. Behavioral changes
2. Performance implications
3. Missing edge cases
```

### Referencing project context

```markdown
---
description: Create a component following project patterns
argument-hint: [component-name]
---

Create a new component named $ARGUMENTS following the patterns in:

- Example component: @src/components/Button.tsx
- Shared types: @src/types/components.d.ts

## Steps

1. Follow the structure of the example component
2. Use shared types from the types file
3. Add appropriate props interface
```

## Session Variables

### ${CLAUDE_SESSION_ID}

The current session identifier. Useful for logging, session-specific files, or correlating output.

```markdown
---
description: Log activity for this session
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

$ARGUMENTS
```

## Extended Thinking

Include the word "ultrathink" in skill content to trigger extended thinking mode for deeper reasoning:

```markdown
---
description: Analyze architecture implications
disable-model-invocation: true
---

ultrathink

Analyze the architecture implications of $ARGUMENTS.

## Steps

1. Map current dependencies
2. Identify affected components
3. Evaluate trade-offs
4. Recommend approach
```

## Combining Patterns

Commands can combine multiple features for powerful workflows:

```markdown
---
description: Debug a failing test
allowed-tools: Bash(pnpm test:*), Read, Grep, Glob
argument-hint: [test file or pattern]
---

## Context

- Test output: !`pnpm test $ARGUMENTS 2>&1 | tail -50`
- Test file: @$ARGUMENTS

## Steps

1. Analyze the test failure output above
2. Read the test file and implementation
3. Identify the root cause
4. Suggest a fix

## Output

Provide the root cause and a specific code fix.
```
