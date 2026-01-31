---
title: Templates
description: Ready-to-use command templates for common patterns including commits, reviews, deployments, and multi-phase workflows
tags: [templates, commit, review, deploy, guardrails, multi-phase, debug]
---

# Command Templates

## Basic Command

Minimal command with description and numbered steps.

```markdown
---
description: What this command does
---

# Command Name

Brief explanation of purpose.

## Steps

1. First action
2. Second action
3. Final action

## Reference

- Use `cli-command` for specific purpose
```

## Command with Arguments

Accept dynamic input with `$ARGUMENTS` and `argument-hint`.

```markdown
---
description: Review a pull request by number
argument-hint: [PR number]
allowed-tools: Bash(gh:*), Read, Grep, Glob
---

Review pull request #$ARGUMENTS

## Steps

1. Fetch PR details with `gh pr view $ARGUMENTS`
2. Review changed files
3. Check for issues against project conventions
4. Provide structured feedback

## Output Format

Provide:

- Summary of changes
- List of issues found
- Verdict: APPROVE or REQUEST CHANGES
```

Usage: `/review-pr 123`

## Guardrailed Command

For commands that modify state. Includes safety constraints and explicit boundaries.

```markdown
---
description: Deploy application to environment
disable-model-invocation: true
argument-hint: [environment]
allowed-tools: Bash(git:*), Bash(pnpm:*), Read
---

Deploy to $ARGUMENTS environment.

## Guardrails

- Do NOT deploy if tests fail
- Do NOT force-push or skip CI checks
- Do NOT modify environment variables without confirmation
- Only deploy from the main branch

## Steps

1. Verify current branch is main
2. Run full test suite
3. Build the application
4. Execute deployment to $ARGUMENTS
5. Verify deployment succeeded

## Rollback

If deployment fails:

1. Revert to previous deployment
2. Report the failure with error details
```

Usage: `/deploy staging`

## Git Commit Command

Uses bash injection for dynamic context.

```markdown
---
description: Create a conventional git commit
disable-model-invocation: true
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
2. Stage appropriate files (not unrelated changes)
3. Create commit with conventional format: type(scope): description
4. If $ARGUMENTS provided, use it as the commit message basis

## Format

Use conventional commit types: feat, fix, docs, style, refactor, perf, test, chore
```

## Multi-Phase Command

Complex workflows with distinct phases. Consider using `context: fork` for isolation.

```markdown
---
description: Complete feature development workflow
disable-model-invocation: true
argument-hint: [feature name]
---

# Feature Development: $ARGUMENTS

## Phase 1: Planning

1. Understand the requirement for $ARGUMENTS
2. Identify affected files and components
3. Create implementation plan

## Phase 2: Implementation

1. Create or modify necessary files
2. Follow project conventions
3. Add appropriate tests

## Phase 3: Verification

1. Run type checking
2. Run linting
3. Run tests
4. Verify no regressions

## Phase 4: Documentation

1. Update relevant documentation
2. Add inline comments only where non-obvious

## Output

Provide a summary of all changes made across phases.
```

## Code Review Command

Combines bash injection with structured output.

```markdown
---
description: Review staged changes before commit
allowed-tools: Bash(git:*), Read, Grep, Glob
---

## Context

- Staged changes: !`git diff --cached`
- Modified files: !`git diff --cached --name-only`

## Steps

1. Review each changed file for correctness
2. Check against project conventions
3. Look for common issues: missing error handling, type safety, edge cases
4. Provide structured feedback

## Output

For each file, report:

- Status: OK or NEEDS CHANGES
- Issues found (if any)
- Overall verdict: READY TO COMMIT or NEEDS CHANGES
```

## Debug Helper Command

Accepts error context and provides structured analysis.

```markdown
---
description: Help debug an error message or failing code
argument-hint: [error message or file:line]
---

Debug: $ARGUMENTS

## Steps

1. Parse the error location from the arguments
2. Read the relevant file and surrounding context
3. Search for related code patterns
4. Identify potential root causes
5. Suggest specific fixes

## Output

Provide:

- Parsed error details
- Root cause analysis
- Specific code fix with explanation
```

## Read-Only Explorer

Restricts tools to prevent modifications.

```markdown
---
description: Explore and explain code without making changes
allowed-tools: Read, Grep, Glob
argument-hint: [file or pattern]
---

Explore $ARGUMENTS without making any changes.

## Steps

1. Find relevant files matching $ARGUMENTS
2. Read and analyze the code
3. Trace data flow and dependencies
4. Explain the architecture

## Output

Provide:

- File structure overview
- Key components and their responsibilities
- Data flow diagram (ASCII)
- Notable patterns or concerns
```

## Forked Research Command

Runs in an isolated subagent for focused exploration.

```markdown
---
description: Research a topic in the codebase
context: fork
agent: Explore
argument-hint: [topic]
---

Research $ARGUMENTS thoroughly in this codebase.

## Steps

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Trace usage patterns and dependencies
4. Map the architecture

## Output

Summarize findings with specific file references:

- Where the feature lives
- How it works
- Key dependencies
- Potential improvements
```

## Component Generator

Uses file references for pattern consistency.

```markdown
---
description: Generate a new component following project patterns
disable-model-invocation: true
argument-hint: [component-name]
---

Create a new component named $ARGUMENTS.

## Reference Pattern

Use the existing component structure from the project.

## Steps

1. Determine the appropriate directory for the new component
2. Create the component file with proper TypeScript types
3. Create a test file following existing test patterns
4. Export from the nearest index file
5. Verify types and lint pass

## Conventions

- PascalCase for component names and files
- Props interface named `${ComponentName}Props`
- Colocate tests as `component-name.test.tsx`
```

## Checklist for New Commands

When creating a command, verify:

1. File location matches intended scope (project vs personal)
2. `description` frontmatter is present
3. Steps are numbered and actionable
4. `$ARGUMENTS` handled for empty case (if used)
5. `allowed-tools` included when using `` !`bash` `` injection
6. All code blocks have language specifiers
7. Guardrails section included for state-changing commands
8. `disable-model-invocation: true` set for side-effect commands
9. Output format specified when structured output is expected
