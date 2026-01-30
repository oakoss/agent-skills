---
title: Doc Coverage
description: Feature inventory, gap analysis, doc-first and code-first audit workflows, evidence capture, and red flags for outdated documentation
tags: [coverage, audit, gap-analysis, inventory, sync, exports]
---

## Feature Inventory Targets

Scan the codebase for these documentation-worthy items:

- Public exports: classes, functions, types, and module entry points
- Configuration options: `*Settings` types, default config objects, builder patterns
- Environment variables or runtime flags
- CLI commands, scripts, and example entry points
- User-facing behaviors: retry, timeouts, streaming, errors, logging, telemetry
- Deprecations, removals, or renamed settings

## Doc-First Pass

Review each documentation page and check for:

- Missing opt-in flags, env vars, or customization options the page implies
- New features that belong on that page based on user intent and navigation
- Outdated defaults or removed options still referenced

## Code-First Pass

Map features to the closest existing page based on the docs navigation:

- Prefer updating existing pages over creating new ones unless the topic is clearly new
- Use conceptual pages for cross-cutting concerns (auth, errors, streaming, tracing, tools)
- Keep quick-start flows minimal; move advanced details into deeper pages

## Doc Sync Audit

Compare current code against documentation to find drift:

```bash
# Diff current branch against main
git diff main...HEAD -- src/

# Find undocumented exports
rg "export (const|function|class)" src/ --type ts

# Compare with docs structure
ls -R docs/
```

## Evidence Capture

When documenting gaps:

- Record the file path and symbol/setting name
- Note defaults or behavior-critical details for accuracy checks
- Avoid large code dumps; a short identifier is enough

## Red Flags for Outdated Docs

| Red Flag                                      | Action                                |
| --------------------------------------------- | ------------------------------------- |
| Option names/types no longer exist in code    | Remove or update the documentation    |
| Default values do not match implementation    | Correct the documented defaults       |
| Features removed in code but still documented | Mark as removed or delete the section |
| New behaviors without corresponding docs      | Prioritize by user impact             |

## When to Propose Structural Changes

- A page mixes unrelated audiences (quick-start + deep reference) without separation
- Multiple pages duplicate the same concept without cross-links
- New feature areas have no obvious home in the navigation structure

## Diff Mode Guidance

When auditing a feature branch against main:

- Focus only on changed behavior: new exports, modified defaults, removed features, renamed settings
- Use `git diff main...HEAD` to constrain analysis
- Document removals explicitly so docs can be pruned

## Patch Guidance

- Keep edits scoped and aligned with existing tone and format
- Update cross-links when moving or renaming sections
- Leave translated docs untouched; English-only updates
