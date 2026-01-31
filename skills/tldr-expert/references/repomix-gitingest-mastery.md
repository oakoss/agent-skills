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

# Compressed mode (extracts signatures via Tree-sitter, removes function bodies)
repomix --include "src/huge-module/**" --compress

# Pack with Markdown output instead of XML
repomix --style markdown --output context.md

# Metadata only without file contents
repomix --no-files
```

### Output Modes

| Mode       | Flag         | Token Savings | Use Case                              |
| ---------- | ------------ | ------------- | ------------------------------------- |
| Full       | (default)    | None          | Small modules, full understanding     |
| Compressed | `--compress` | ~70%          | Medium-large modules, reasoning tasks |
| No files   | `--no-files` | ~95%          | Repository structure analysis only    |

### Security: Secretlint Integration

Repomix includes built-in secretlint scanning to ensure context bundles never contain:

- API keys or secrets
- PII (personally identifiable information)
- Internal IP addresses or sensitive metadata

This runs automatically on every pack operation. Disable with `--no-security-check` if needed.

## Gitingest: Repository Digest Tool

Gitingest (Python: `pip install gitingest`) transforms entire Git repositories into structured text digests optimized for LLM consumption.

### Key Use Cases

**Dependency discovery:** Point Gitingest at a library's GitHub URL to understand its API surface.

```bash
gitingest https://github.com/org/library -o library-digest.txt
```

**Architecture review:** Get a tree view and file-size breakdown for quick orientation.

```bash
gitingest . -o project-digest.txt
```

**Onboarding digest:** Create a prompt-friendly summary for new contributors or sub-agents.

```bash
gitingest . -o digest.txt
```

### Configuration Tips

- Ensure a valid `.gitignore` exists at the project root for clean output (files in `.gitignore` are skipped by default)
- Use `--include-gitignored` if you need ignored files in the digest
- Use `-o -` to pipe output to STDOUT instead of a file
- Use `--token` or `GITHUB_TOKEN` env var for private repository access
- Use remote GitHub URLs for third-party library analysis

## Tree-sitter Signature Extraction

Tree-sitter (used internally by Repomix `--compress` and llm-tldr) extracts the "shape" of code without implementation details.

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
| Context bundle too large | Too many implementation details     | Use `--compress` to extract signatures only               |
| Gitingest output messy   | Missing `.gitignore` configuration  | Ensure a valid `.gitignore` exists at the root            |
| Secretlint blocks output | Detected potential secret in source | Review flagged files and remove or rotate exposed secrets |
| XML parsing errors       | Special characters in source code   | Switch to Markdown output with `--style markdown`         |
