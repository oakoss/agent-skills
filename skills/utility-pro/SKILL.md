---
name: utility-pro
description: 'Performs advanced CLI operations, structured data transformation, and Unix forensics with modern Rust-powered tools. Use when searching codebases with ripgrep, transforming JSON or YAML with jq, refactoring across files with sed and fd, debugging APIs with httpie, or navigating directories with zoxide.'
---

# Utility Pro

## Overview

Masters the command-line environment by turning raw text and unstructured data into actionable insights. Combines Rust-powered search tools (ripgrep, fd, bat), structured data shells (Nushell), JSON manipulation (jq/yq), and modern HTTP clients (httpie/xh) for high-performance CLI workflows.

**When to use:** Codebase-wide search and analysis, multi-file refactoring, JSON/YAML transformation pipelines, API debugging, directory navigation, log parsing.

**When NOT to use:** GUI-based tasks, complex application logic (write a script instead), tasks requiring interactive prompts.

## Quick Reference

| Pattern                 | Tool / Command                               | Key Points                                       |
| ----------------------- | -------------------------------------------- | ------------------------------------------------ |
| Text search             | `rg "pattern" -g "*.tsx"`                    | 10-100x faster than grep, respects `.gitignore`  |
| File search             | `fd -e pdf` or `fd "pattern"`                | Fast alternative to `find` with smart defaults   |
| Syntax-highlighted read | `bat file.ts`                                | Cat with syntax highlighting and git integration |
| Directory jump          | `z project-name`                             | Remembers frequently visited directories         |
| Fuzzy search            | `fzf` or `CTRL-T` / `CTRL-R`                 | Interactive selection for files and history      |
| Tree view               | `eza --tree --level=2`                       | Metadata-rich ls replacement with tree support   |
| JSON query              | `jq '.items[] \| select(.active)'`           | Full functional programming for JSON             |
| YAML query              | `yq '.config.database' file.yml`             | jq-like syntax for YAML files                    |
| HTTP request            | `xh POST api.example.com/v1/data key=value`  | Colorized, user-friendly HTTP client             |
| Multi-file refactor     | `fd -e tsx -x sed -i 's/Old/New/g' {}`       | Find files then execute transforms               |
| Structured shell        | `ls \| where size > 1mb \| sort-by size`     | Nushell tables instead of text parsing           |
| Log parsing             | `rg "ERROR" --json \| jq '.data.lines.text'` | Combine tools for structured log analysis        |

## Common Mistakes

| Mistake                                               | Correct Pattern                                                                   |
| ----------------------------------------------------- | --------------------------------------------------------------------------------- |
| Using `grep` instead of `ripgrep` for codebase search | Use `rg` which is 10-100x faster and respects `.gitignore` by default             |
| Piping `ls` output into `grep` for file filtering     | Use `fd` or `eza --filter` for structured, fast file discovery                    |
| Writing complex `awk` scripts for structured data     | Use Nushell or `jq` which natively understand JSON, CSV, and YAML                 |
| Running `rm -rf` in scripts without a dry-run step    | Always add a verification or dry-run step before destructive operations           |
| Using capturing groups in regex when not needed       | Prefer non-capturing groups `(?:...)` for better performance in large-scale scans |
| Searching `node_modules` or `.git` directories        | Use `rg` which skips these by default, or configure exclusions explicitly         |

## Delegation

- **Large-scale codebase search and analysis**: Use `Explore` agent to run ripgrep queries, trace dependencies, and map code patterns
- **Multi-file refactoring workflows**: Use `Task` agent to coordinate fd, sed, and verification steps across an entire project
- **Pipeline architecture for data transformation**: Use `Plan` agent to design structured pipelines combining jq, Nushell, and API tools

## References

- [Modern Unix Toolbox](references/modern-unix-toolbox.md) -- ripgrep, fd, bat, zoxide, fzf, eza, terminal setup
- [Advanced Regex and jq](references/advanced-regex-and-jq.md) -- named captures, lookahead/lookbehind, jq filters, integrated pipelines
- [Nushell Structured Data](references/nushell-structured-data.md) -- table paradigm, API interaction, scripting, Unix interop
