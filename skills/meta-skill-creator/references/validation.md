---
title: Validation
description: Validation checklist, common issues, testing your skill, and distribution readiness
tags: [validation, checklist, testing, lint, distribution, errors]
---

# Validation

Always validate skills before committing or distributing. Validation catches structural issues, missing fields, and common authoring mistakes.

## Validation Tools

### Agent Skills Reference Library

The official validation tool from the open standard:

```bash
skills-ref validate ./my-skill
```

### Project Validators

Many skill repositories include their own validators with stricter rules:

```bash
pnpm validate:skills skills/my-skill
```

## Pre-Commit Checklist

Run through this checklist before committing a new or modified skill:

### Frontmatter

- [ ] YAML block starts on line 1 (no blank lines before `---`)
- [ ] `name` field present and matches directory name
- [ ] `name` is lowercase, hyphens only, 4-64 characters
- [ ] `name` does not start/end with `-` or contain `--`
- [ ] `description` field present, 1-1024 characters
- [ ] `description` uses third-person voice
- [ ] `description` includes "Use when..." or "Use for..." trigger phrase
- [ ] `description` is keyword-rich (not vague like "helps with files")

### SKILL.md Structure

- [ ] Contains Overview section (2-3 sentences)
- [ ] Contains Quick Reference table
- [ ] Contains Common Mistakes table
- [ ] Contains Delegation section
- [ ] Contains References list (if reference files exist)
- [ ] No code examples in SKILL.md (all code in reference files)
- [ ] Under 500 lines (target 100-150)

### Reference Files

- [ ] Located in `references/` directory
- [ ] Kebab-case filenames
- [ ] Each file has `title`, `description`, and `tags` frontmatter
- [ ] Each file under 500 lines
- [ ] Self-contained (no cross-references between reference files)
- [ ] All linked from SKILL.md References section

### Code Blocks

- [ ] Every fenced code block has a language specifier
- [ ] Language specifiers match content (e.g., `yaml` for YAML, `tsx` for React)

### Naming

- [ ] Directory name is kebab-case, min 4 characters
- [ ] No abbreviations in directory name
- [ ] No excluded filenames (`README.md`, `metadata.json`, `_*`)

### Scripts (if present)

- [ ] Scripts are executable (`chmod +x`)
- [ ] Scripts handle errors explicitly
- [ ] Scripts are self-contained or document dependencies
- [ ] SKILL.md instructs agent to run (not read) scripts

## Common Validation Errors

| Error                       | Cause                                     | Fix                                          |
| --------------------------- | ----------------------------------------- | -------------------------------------------- |
| Missing frontmatter         | File does not start with `---`            | Add YAML frontmatter as first line           |
| Name mismatch               | `name` field differs from directory       | Make `name` match directory name exactly     |
| Invalid name characters     | Uppercase, spaces, or special characters  | Use only lowercase letters, numbers, hyphens |
| Missing trigger phrase      | No "Use when" or "Use for" in description | Add trigger phrase to description            |
| Description too vague       | Generic terms like "helps with"           | Use specific keywords and action verbs       |
| Code block without language | Fenced block opened with bare backticks   | Add language after opening backticks         |
| SKILL.md too long           | Over 500 lines                            | Move detailed content to reference files     |
| Reference not linked        | File exists but not referenced            | Add link in SKILL.md References section      |
| Broken reference link       | Link points to nonexistent file           | Fix path or create the missing file          |
| Excluded filename used      | `README.md` or `metadata.json` in skill   | Rename to allowed filename                   |

## Testing Your Skill

### Manual Testing

After creating a skill, verify it works end-to-end:

1. **Check discovery**: Ask the agent "What skills are available?" -- your skill should appear
2. **Check activation**: Ask a question matching your trigger phrases -- the skill should activate
3. **Check references**: Ask a question that requires reference content -- the agent should load the right file
4. **Check completeness**: Verify the agent produces correct output using the skill

### Description Testing

Test that your description triggers correctly:

1. List 5-10 queries a user might type that should activate your skill
2. List 3-5 queries that should NOT activate your skill
3. Verify trigger phrases cover the activation queries
4. Verify the description does not accidentally match non-activation queries

### Size Verification

Check line counts to ensure files are within thresholds:

```bash
wc -l skills/my-skill/SKILL.md
wc -l skills/my-skill/references/*.md
```

## Distribution Readiness

Before distributing a skill publicly, verify:

- [ ] Skill passes all validation checks
- [ ] No excluded filenames in the skill directory
- [ ] No hardcoded paths or environment-specific values
- [ ] Description is agent-agnostic (works across compatible agents)
- [ ] Reference files do not assume specific agent capabilities
- [ ] Scripts document any required system dependencies
- [ ] License field is set (if distributing publicly)

## Iterating on Skills

Skills improve over time. Common iteration patterns:

| Signal                             | Action                                         |
| ---------------------------------- | ---------------------------------------------- |
| Skill not activating               | Enrich description with more trigger keywords  |
| Agent loads wrong reference        | Improve reference file titles and descriptions |
| Agent output has errors            | Add to Common Mistakes table                   |
| Users ask same follow-up questions | Add content to reference files                 |
| Reference file too large           | Split into multiple topic-scoped files         |
