---
title: AI Collaboration
description: AI-human documentation workflow, role definitions, AI-first drafting process, documentation-as-code practices, and handling AI hallucinations
tags:
  [AI, collaboration, drafting, workflow, documentation-as-code, hallucinations]
---

## Role of the AI Agent

| Capability      | Description                                                      |
| --------------- | ---------------------------------------------------------------- |
| Drafting        | Generate initial drafts from code comments or PR descriptions    |
| Verification    | Automated checking of links, code snippets, and style compliance |
| Refactoring     | Restyle entire directories to match a new standard               |
| Synchronization | Identify gaps between implementation and documentation           |

## Role of the Human Editor

| Responsibility      | Description                                       |
| ------------------- | ------------------------------------------------- |
| Accuracy            | Verify technical correctness (AI can hallucinate) |
| Tone check          | Ensure appropriate voice for the target audience  |
| Strategic direction | Decide what needs documenting and at what depth   |
| Ethics and safety   | Ensure docs do not expose vulnerabilities or bias |

## The AI-First Workflow

1. **Code commit**: Developer pushes code with docstrings
2. **Sync audit**: Docs skill identifies new features lacking documentation
3. **AI drafting**: AI generates a draft page based on code analysis
4. **Human review**: Expert reviews, edits, and approves the draft
5. **Merge**: Documentation integrates into the main branch

## Documentation as Code (DaC)

- Docs live in the same repository as the code
- CI/CD pipelines lint documentation alongside code
- Use bundled code context when asking AI to write documentation
- Version-control documentation changes with the same rigor as code

## Handling Hallucinations

When AI generates incorrect documentation:

### Trace the Source

Determine whether the AI misinterpreted a comment, guessed a default value, or fabricated a feature.

### Fix the Source

Update the code docstrings to be more explicit. Ambiguous comments produce ambiguous documentation.

### Update the Instructions

Provide more context in the documentation skill instructions to prevent recurrence.

## Quality Verification

Before merging AI-generated documentation:

| Check                 | Method                                           |
| --------------------- | ------------------------------------------------ |
| Code examples compile | Run or lint all snippets                         |
| Links resolve         | Run a link-checker script                        |
| Defaults match code   | Compare documented values against implementation |
| Style compliance      | Run markdownlint and style guide checks          |
| Technical accuracy    | Human review of all factual claims               |
