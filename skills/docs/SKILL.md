---
name: docs
description: |
  Technical documentation patterns for software projects. Covers API documentation, README structure, architecture decision records (ADRs), code comments, changelogs, onboarding guides, and documentation-as-code workflows.

  Use when writing API docs, structuring READMEs, creating ADRs, documenting architecture decisions, writing migration guides, or setting up documentation pipelines.
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Technical Documentation

## Overview

Technical documentation translates complex systems into actionable knowledge for developers. Good docs reduce onboarding time, prevent repeated questions, and serve as a single source of truth for architecture decisions and API contracts.

**When to use:** Writing API references, structuring project READMEs, recording architecture decisions, creating migration guides, building onboarding materials, writing runbooks, or establishing documentation standards.

**When NOT to use:** Marketing copy, end-user product documentation (use a CMS), auto-generated API docs without curation (use the generator directly), or documentation that duplicates what types and tests already communicate.

## Quick Reference

| Pattern          | Format                                     | Key Points                                      |
| ---------------- | ------------------------------------------ | ----------------------------------------------- |
| README           | Badges, description, quick start, API link | First thing users see; keep under 200 lines     |
| API docs         | Method, path, params, request/response     | Include error codes and real examples           |
| ADR              | Status, context, decision, consequences    | Numbered, immutable once accepted               |
| Changelog        | Keep a Changelog + semver                  | Auto-generate from conventional commits         |
| Migration guide  | Version-to-version, before/after code      | Highlight breaking changes prominently          |
| Inline docs      | JSDoc/TSDoc for public API only            | Document WHY, not WHAT; skip obvious signatures |
| Runbook          | Step-by-step with escalation paths         | Written for 3 AM incidents; no ambiguity        |
| Onboarding guide | Setup, concepts, first contribution        | Test with a new hire; update when it breaks     |

## Common Mistakes

| Mistake                                | Correct Pattern                                                 |
| -------------------------------------- | --------------------------------------------------------------- |
| No documentation at all                | Start with README + ADRs; iterate from there                    |
| Stale docs that contradict the code    | Automate what you can; review docs in PRs alongside code        |
| Documenting implementation, not intent | Explain WHY a decision was made, not HOW the code works         |
| No code examples in API docs           | Every endpoint and public function needs a usage example        |
| Monolithic docs in a single file       | Split by audience: quick start, reference, guides, tutorials    |
| Copy-pasting without adapting          | Tailor examples to the project's actual stack and patterns      |
| Documenting every function with JSDoc  | Only document public API and non-obvious behavior               |
| ADRs without status or date tracking   | Always include status (proposed/accepted/deprecated/superseded) |
| Changelogs written after release       | Write changelog entries alongside the code change               |
| Missing error scenarios in API docs    | Document every error code with cause and resolution             |

## Delegation

- **Documentation discovery**: Use `Explore` agent to find existing docs and gaps
- **Documentation review**: Use `Task` agent for comprehensive doc audits
- **Code review**: Delegate to `code-reviewer` agent for inline doc quality

> If the `tldr-expert` skill is available, delegate summary and brief generation to it.

## References

- [Project documentation: READMEs, ADRs, changelogs, migration and onboarding guides](references/project-documentation.md)
- [API and code documentation: endpoint refs, JSDoc, runbooks, doc testing](references/api-and-code-docs.md)
