---
title: Writing Style
description: Voice and tone guidelines, structural standards, formatting rules, error message patterns, and inclusive language for technical documentation
tags: [style-guide, voice, tone, formatting, error-messages, inclusive-language]
---

## Voice and Tone

### Active Voice

Always prefer active voice:

- Bad: "The function is called by the agent."
- Good: "The agent calls the function."

### Direct and Concise

Avoid fluff. Start with the most important information. Use simple words for complex concepts.

### Inclusive Language

Use gender-neutral pronouns (they/them) or avoid pronouns entirely. Use "users" or "developers" instead of "the user." Avoid obscure jargon unless defined.

## Structural Standards

### The Rule of Three

Limit heading hierarchies to H1, H2, and H3. If you need H4, consider splitting the page.

### Executive Summary

Every page longer than 500 words must start with a brief summary or table of contents.

### Contextual Links

Use descriptive link text:

- Bad: "Click [this link](link) to read more."
- Good: "See the [Authentication Guide](link) for details."

## Formatting Rules

| Element     | Rule                                            |
| ----------- | ----------------------------------------------- |
| Code blocks | Always specify the language                     |
| Bold        | Use for UI elements ("Click **Submit**")        |
| Italics     | Use for technical terms on first use            |
| Lists       | Bulleted for unordered, numbered for sequential |
| Variables   | Meaningful names in code examples               |

## Error Message Guidelines

Model error messages as "Problem, Cause, Solution":

| Component | Example                                    |
| --------- | ------------------------------------------ |
| Problem   | "401 Unauthorized"                         |
| Cause     | "Invalid API Key"                          |
| Solution  | "Check your `.env` file for `AUTH_SECRET`" |

## Documentation Quality Standards

- **Clarity**: Active voice, present tense, direct address
- **Accuracy**: Code examples must be tested and valid
- **Discoverability**: Every page listed in nav config with a descriptive title

## Feature Release Doc Checklist

Every new feature needs these four sections:

1. **Overview**: What it does and why it exists
2. **Configuration**: All env vars, settings, and defaults
3. **Examples**: Quick-start and advanced code blocks
4. **Troubleshooting**: Common errors and fixes

## API Reference Update Flow

1. Update JSDoc/TSDoc in source code
2. Run doc generator (e.g., `make build-docs`)
3. Verify output matches Markdown standards
