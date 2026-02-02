---
title: Enriched Search
description: Usage guide for the enrich_find.js script that adds descriptions to skill search results
tags: [enrichment, script, descriptions, skills-sh, search]
---

# Enriched Search

## What It Does

The `enrich_find.js` script wraps `pnpm dlx skills find` and enriches each result with a human-readable description fetched from skills.sh. This gives users context about what each skill does without having to visit every page manually.

## How It Works

The script operates in three steps:

1. **Search** — Runs `pnpm dlx skills find <query>` and parses the output
2. **Fetch** — For each result, fetches the skills.sh page and extracts descriptive text
3. **Display** — Presents results with name, URL, and description in a formatted layout

## Usage

```bash
node scripts/enrich_find.js "<query>"
```

### Options

| Flag              | Default | Description                                |
| ----------------- | ------- | ------------------------------------------ |
| `--max N`         | 10      | Maximum number of results to enrich        |
| `--timeout N`     | 10      | Per-request timeout in seconds             |
| `--concurrency N` | 5       | Number of parallel description fetches     |
| `--no-fetch`      | false   | Show matches without fetching descriptions |

### Examples

```bash
# Basic search
node scripts/enrich_find.js "react"

# Limit to 5 results
node scripts/enrich_find.js "testing" --max 5

# Fast mode — skip description fetching
node scripts/enrich_find.js "deploy" --no-fetch

# Increase timeout for slow connections
node scripts/enrich_find.js "kubernetes" --timeout 20

# Single-threaded fetching
node scripts/enrich_find.js "auth" --concurrency 1
```

## Output Format

Each result is displayed as:

```text
owner/repo@skill
└ https://skills.sh/owner/repo/skill
description text from the skill page
```

With ANSI formatting:

- **Bold** — skill name
- **Blue** — URL
- **Gray** — description

When no results are found, outputs: `No skills found.`

## Description Sources

The script tries two sources for descriptions, in order:

1. **skills.sh** — Extracts the first `<p>` tag from the prose section, or falls back to the `<meta name="description">` tag
2. **agent-skills.md** — If skills.sh has no description, tries the equivalent page on `agent-skills.md`

If neither source provides a description, displays `[no description found]`.

## Requirements

- **Node.js** — Uses built-in `https` and `child_process` modules (no npm dependencies)
- **Network access** — Fetches from skills.sh and agent-skills.md
- **Skills CLI** — `pnpm dlx skills` must be available (installed on demand via pnpm)

## Error Handling

- Network timeouts are handled per-request without failing the entire batch
- HTTP errors (4xx, 5xx) fall through to the fallback source
- Redirect chains are followed up to 3 hops
- If the skills CLI is not available, the script exits with a non-zero status
- Invalid options produce a usage error message
