---
title: Repomix and Gitingest Mastery
description: Detailed usage of Repomix for context packing and Gitingest for repository digests including configuration, output modes, and Tree-sitter extraction
tags: [repomix, gitingest, tree-sitter, context-packing, code-signatures]
---

# Repomix and Gitingest Mastery

## Repomix: Context Snapshot Tool

Repomix packages codebases into single, AI-optimized XML or Markdown files. It is the primary tool for creating context bundles.

### Recommended Configuration

```json
{
  "output": {
    "filePath": "repomix-output.xml",
    "style": "xml",
    "removeComments": true,
    "removeEmptyLines": true,
    "showLineNumbers": true
  },
  "include": ["src/**/*"],
  "ignore": {
    "customPatterns": ["**/*.test.ts", "**/dist/**", "**/docs/**"]
  }
}
```

Save as `repomix.config.json` in the project root.

### Common Commands

```bash
# Full project pack (respects config)
repomix

# Pack specific subdirectory with compression
repomix --include "src/features/auth/**" --output auth-context.md --compress

# Signatures only (understand a module without hitting token limits)
repomix --include "src/huge-module/**" --no-code-bodies

# Top-level exports only
repomix --include "src/**" --top-level-only

# Pack with Markdown output instead of XML
repomix --style markdown --output context.md
```

### Output Modes

| Mode            | Flag               | Token Savings | Use Case                             |
| --------------- | ------------------ | ------------- | ------------------------------------ |
| Full            | (default)          | None          | Small modules, full understanding    |
| Compressed      | `--compress`       | ~40%          | Medium modules, reasoning tasks      |
| Signatures only | `--no-code-bodies` | ~85%          | Large modules, architectural mapping |
| Top-level only  | `--top-level-only` | ~90%          | Very large modules, export discovery |

### Security: Secretlint Integration

Repomix includes built-in secretlint scanning to ensure context bundles never contain:

- API keys or secrets
- PII (personally identifiable information)
- Internal IP addresses or sensitive metadata

This runs automatically on every pack operation.

## Gitingest: Repository Digest Tool

Gitingest transforms entire Git repositories into structured text digests optimized for LLM consumption.

### Key Use Cases

**Dependency discovery:** Point Gitingest at a library's GitHub URL to understand its API surface.

```bash
gitingest https://github.com/org/library --output library-digest.txt
```

**Architecture review:** Get a tree view and file-size breakdown for quick orientation.

```bash
gitingest . --output project-digest.txt
```

**Onboarding digest:** Create a prompt-friendly summary for new contributors or sub-agents.

```bash
gitingest . --exclude "node_modules,dist,build" --max-size 1mb --output digest.txt
```

### Configuration Tips

- Always exclude `node_modules`, `dist`, `build`, and `.git` directories
- Set `--max-size` to prevent oversized outputs
- Ensure a valid `.gitignore` exists at the project root for clean output
- Use remote URLs for third-party library analysis

## Tree-sitter Signature Extraction

Tree-sitter (used internally by llm-tldr) extracts the "shape" of code without implementation details.

```ts
// Tree-sitter extraction produces signatures like:
export function calculateTax(amount: number): number;
export class TaxEngine {
  constructor(config: Config);
  process(item: Item): Result;
}
```

This gives the AI the "what" without the "how," saving thousands of tokens while preserving structural understanding.

## Troubleshooting

| Issue                    | Likely Cause                        | Corrective Action                                         |
| ------------------------ | ----------------------------------- | --------------------------------------------------------- |
| Context bundle too large | Too many implementation details     | Use `--top-level-only` or `--no-code-bodies`              |
| Gitingest output messy   | Missing `.gitignore` configuration  | Ensure a valid `.gitignore` exists at the root            |
| Secretlint blocks output | Detected potential secret in source | Review flagged files and remove or rotate exposed secrets |
| XML parsing errors       | Special characters in source code   | Switch to Markdown output with `--style markdown`         |
