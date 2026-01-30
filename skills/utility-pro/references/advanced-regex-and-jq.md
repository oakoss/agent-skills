---
title: Advanced Regex and jq
description: Advanced regular expression techniques and jq JSON manipulation including named captures, lookahead/lookbehind, filters, and integrated CLI pipelines
tags: [regex, jq, json, named-captures, lookahead, pipelines, log-parsing]
---

# Advanced Regex and jq

## Regular Expressions

### Key Features for CLI Usage

| Feature         | Syntax          | Use Case                               |
| --------------- | --------------- | -------------------------------------- |
| Named groups    | `(?P<name>...)` | Extracting structured fields from logs |
| Lookahead       | `(?=...)`       | Matching X only if followed by Y       |
| Lookbehind      | `(?<=...)`      | Matching X only if preceded by Y       |
| Non-greedy      | `*?` or `+?`    | Matching the smallest possible string  |
| Non-capturing   | `(?:...)`       | Grouping without capture (performance) |
| Atomic grouping | `(?>...)`       | Prevent catastrophic backtracking      |

### Log Parsing Pattern

Parse structured log lines into named fields:

```bash
# Pattern for: "2026-01-30 14:30:45 ERROR [auth] Login failed for user@example.com"
rg -P '^(?P<timestamp>[\d-]{10} [\d:]{8}) (?P<level>INFO|WARN|ERROR) \[(?P<module>[^\]]+)\] (?P<message>.*)$' app.log
```

### Practical Regex Examples

```bash
# Find all import statements for a specific module
rg "import .+ from ['\"]@/lib/auth"

# Match function declarations (TypeScript)
rg -P "(?:export\s+)?(?:async\s+)?function\s+\w+"

# Find all TODO comments with ticket references
rg -P "TODO\((?P<ticket>[A-Z]+-\d+)\)"

# Extract all URLs from a file
rg -oP "https?://[^\s\"'<>]+"

# Find duplicate consecutive words
rg -P "\b(\w+)\s+\1\b"
```

### Performance Tips

- Prefer non-capturing groups `(?:...)` over capturing `(...)` when you do not need the match
- Use `rg -P` for PCRE2 when you need lookahead/lookbehind
- Use `--only-matching` to reduce output noise in pipelines
- Avoid `.*` at the start of patterns; anchor with `^` when possible

## jq: JSON Manipulation

`jq` is a full functional programming language for JSON data.

### Essential Filters

```bash
# Create array of IDs from nested objects
jq '[.items[].id]' data.json

# Filter objects by field value
jq '.[] | select(.status == "active")' data.json

# Update a specific field in-place
jq '(.user.role) |= "admin"' data.json

# Sum an array of numbers
jq '[.[].amount] | add' data.json

# Group by field and count
jq 'group_by(.module) | map({module: .[0].module, count: length})' logs.json

# Flatten nested arrays
jq '[.categories[].items[]]' data.json

# Conditional transformation
jq '.[] | if .price > 100 then .category = "premium" else . end' data.json
```

### Common Patterns

```bash
# Extract IDs from nested array where status is active
jq '.projects[] | select(.status == "active") | .id' data.json

# Get error count per module from JSON logs
jq -r 'group_by(.module) | .[] | {module: .[0].module, count: length}' logs.json

# Merge two JSON files
jq -s '.[0] * .[1]' base.json overrides.json

# Convert JSON to CSV
jq -r '.[] | [.name, .email, .role] | @csv' users.json

# Pretty-print with sorted keys
jq -S '.' messy.json
```

### yq for YAML

`yq` uses jq-like syntax for YAML files:

```bash
# Read a nested value
yq '.config.database.host' config.yml

# Update a value
yq -i '.config.port = 8080' config.yml

# Convert YAML to JSON
yq -o json config.yml
```

## Integrated Pipelines

The real power comes from combining tools in pipelines.

```bash
# Find all API endpoints in the codebase and list unique URLs
rg -oP "fetch\(['\"]([^'\"]+)['\"]" --no-filename | \
  sed "s/fetch(['\"//" | sed "s/['\"])//" | \
  sort | uniq -c | sort -rn

# Find all exported functions and count by file
rg -c "^export " -g "*.ts" | sort -t: -k2 -rn

# Extract all environment variable references
rg -oP "process\.env\.(\w+)" --no-filename | sort -u

# Audit disk usage of source directories as JSON
du -sk src/*/ | jq -Rs 'split("\n") | map(select(. != "") | split("\t") | {size: .[0] | tonumber, path: .[1]}) | sort_by(.size) | reverse'
```
