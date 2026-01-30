---
title: Command Detection and Processing Pipeline
description: How DCG parses, normalizes, and matches commands through a four-stage pipeline
tags: [detection, pipeline, parsing, pattern-matching, SIMD]
---

# Command Detection and Processing Pipeline

## Why DCG Exists

AI coding agents are powerful but fallible. They can accidentally run destructive commands:

- **"Let me clean up the build artifacts"** results in `rm -rf ./src` (typo)
- **"I'll reset to the last commit"** results in `git reset --hard` (destroys uncommitted changes)
- **"Let me fix the merge conflict"** results in `git checkout -- .` (discards all modifications)
- **"I'll clean up untracked files"** results in `git clean -fd` (permanently deletes untracked files)

DCG intercepts dangerous commands _before_ execution and blocks them with a clear explanation.

## Processing Pipeline

```text
+-------------------------------------------------------------+
|                        Claude Code                          |
|  Agent executes `rm -rf ./build`                            |
+------------------------+------------------------------------+
                         |
                         v  PreToolUse hook (stdin: JSON)
+-------------------------------------------------------------+
|                          dcg                                |
|  +------------+    +-----------+    +---------------+       |
|  |   Parse    |--->| Normalize |--->| Quick Reject  |       |
|  |   JSON     |    |  Command  |    |   Filter      |       |
|  +------------+    +-----------+    +-------+-------+       |
|                                             |               |
|                    +------------------------+               |
|                    v                                        |
|  +------------------------------------------------------+  |
|  |                Pattern Matching                       |  |
|  |  1. Check SAFE_PATTERNS (whitelist) --> Allow         |  |
|  |  2. Check DESTRUCTIVE_PATTERNS -------> Deny          |  |
|  |  3. No match -------------------------> Allow         |  |
|  +------------------------------------------------------+  |
+------------------------+------------------------------------+
                         |
                         v  stdout: JSON (deny) or empty (allow)
```

## Stage 1: JSON Parsing

- Reads hook input from stdin
- Validates Claude Code's `PreToolUse` format
- Non-Bash tools immediately allowed

## Stage 2: Command Normalization

- Strips absolute paths: `/usr/bin/git status` becomes `git status`
- Preserves argument paths

## Stage 3: Quick Rejection Filter

- SIMD-accelerated substring search for "git" or "rm"
- Commands without these bypass regex entirely (99%+ of commands)

## Stage 4: Pattern Matching

- Safe patterns checked first (short-circuit on match to allow)
- Destructive patterns checked second (match to deny)
- No match results in default allow

## Critical Design Principles

### Whitelist-First Architecture

Safe patterns are checked _before_ destructive patterns:

```bash
git checkout -b feature    # Matches SAFE "checkout-new-branch" --> ALLOW
git checkout -- file.txt   # No safe match, matches DESTRUCTIVE --> DENY
```

### Fail-Safe Defaults (Default-Allow)

Unrecognized commands are **allowed by default** to ensure the hook never breaks legitimate workflows.

### Zero False Negatives Philosophy

The pattern set prioritizes **never allowing dangerous commands** over avoiding false positives.

## Performance Optimizations

| Optimization          | Technique                                   |
| --------------------- | ------------------------------------------- |
| **Lazy Static**       | Regex patterns compiled once via `LazyLock` |
| **SIMD Quick Reject** | `memchr` crate for CPU vector instructions  |
| **Early Exit**        | Safe match returns immediately              |
| **Zero-Copy JSON**    | `serde_json` operates on input buffer       |
| **Zero-Allocation**   | `Cow<str>` for path normalization           |
| **Release Profile**   | `opt-level="z"`, LTO, single codegen unit   |

**Result:** Sub-millisecond execution for typical commands.

## Pattern Counts

| Type                             | Count |
| -------------------------------- | ----- |
| Safe patterns (whitelist)        | 34    |
| Destructive patterns (blacklist) | 16    |
