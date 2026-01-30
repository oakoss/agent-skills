---
title: Markdown Standards
description: YAML frontmatter conventions, heading hierarchy, code block language tagging, table formatting, callouts, link conventions, and AI indexing optimization
tags: [markdown, frontmatter, headings, code-blocks, tables, callouts, links]
---

## Document Metadata (Frontmatter)

All major documentation files should include YAML frontmatter:

```yaml
---
title: Page Title
description: Concise description for SEO and AI indexing.
tags: [tag1, tag2]
---
```

## Headings

- **H1**: Only one per page, used for the main title
- **H2**: Major sections
- **H3**: Sub-sections
- **No skipping**: Never skip a level (do not go from H1 to H3)

## Code Blocks

Always specify the language for fenced code blocks:

| Content             | Language Tag |
| ------------------- | ------------ |
| TypeScript/React    | `tsx`        |
| TypeScript (no JSX) | `ts`         |
| JavaScript          | `js`         |
| Shell commands      | `bash`       |
| JSON                | `json`       |
| YAML                | `yaml`       |
| SQL                 | `sql`        |
| HTML                | `html`       |
| CSS                 | `css`        |
| Diff output         | `diff`       |
| Plain text          | `text`       |

Use meaningful variable names in examples. Add comments within code blocks to explain complex logic.

### Showing Changes

Use diff syntax for before/after comparisons:

```diff
- const oldWay = true;
+ const newWay = 2026;
```

## Tables

Use tables for data comparison, configuration options, and anti-pattern lists:

```markdown
| Option     | Type     | Default | Description          |
| :--------- | :------- | :------ | :------------------- |
| `maxDepth` | `number` | `3`     | Maximum crawl depth. |
```

## Callouts

Use standard blockquote syntax for callouts:

- `> [!NOTE]` -- Additional context
- `> [!WARNING]` -- Potential issues
- `> [!IMPORTANT]` -- Critical information

Use callouts sparingly to avoid diluting their impact.

## Links and Paths

- **Internal links**: Always use relative paths (`./other-page.md`)
- **External links**: Use absolute URLs
- **Descriptive text**: Never use "click here"; describe the destination
- **Validation**: Periodically run a link-checker to prevent broken links

## Task Lists

Use `[x]` and `[ ]` for progress tracking:

```markdown
- [x] Write overview section
- [ ] Add code examples
- [ ] Review for accuracy
```

## AI Indexing Optimization

To make docs discoverable by AI agents:

- Use semantic keywords in headings
- State the subject of the page in the first paragraph
- Include a glossary or definitions section for custom terminology
