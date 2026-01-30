---
paths:
  - '**/*.md'
---

# Markdown Rules

## Fenced Code Blocks (MD040)

**ALWAYS specify a language** for fenced code blocks:

```markdown
<!-- WRONG - will fail markdownlint -->

` ` `const x = 1;` ` `

<!-- CORRECT -->

` ` `tsx
const x = 1;
` ` `
```

## Language Reference

| Content              | Language   |
| -------------------- | ---------- |
| TypeScript/React     | `tsx`      |
| TypeScript (no JSX)  | `ts`       |
| JavaScript           | `js`       |
| Shell commands       | `bash`     |
| Directory trees      | `sh`       |
| JSON                 | `json`     |
| YAML                 | `yaml`     |
| Markdown (templates) | `markdown` |
| Plain text/output    | `text`     |
| SQL                  | `sql`      |
| HTML                 | `html`     |
| CSS                  | `css`      |
| Diff output          | `diff`     |

## Markdownlint Rules

Enabled rules with overrides:

| Rule  | Setting         | Description                 |
| ----- | --------------- | --------------------------- |
| MD007 | `indent: 2`     | 2-space list indentation    |
| MD040 | enabled         | Fenced blocks need language |
| MD046 | `style: fenced` | Use fenced code blocks      |

Disabled rules:

- MD001 - Heading level increments
- MD012 - Multiple blank lines
- MD013 - Line length
- MD024 - Duplicate heading content
- MD025 - Multiple top-level headings
- MD026 - Trailing punctuation in headings
- MD029 - Ordered list prefix style
- MD033 - Inline HTML
- MD036 - Emphasis as heading
- MD037 - Spaces in emphasis
- MD041 - First line must be heading
- MD060 - Table column alignment

Uses `.gitignore` patterns automatically.

## Running Markdownlint

```sh
# Correct - uses configured glob pattern
pnpm lint:md

# Correct - specific markdown files
pnpm lint:md .claude/rules/react.md

# Wrong - directory path overrides glob, may lint non-md files
pnpm lint:md .claude/
```
