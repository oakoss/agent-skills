---
title: Auditing Skills
description: 9-phase skill audit process, severity classification, fix decisions, version bumps, and common review findings
tags: [audit, review, severity, fix, version-bump, quality, staleness]
---

# Auditing Skills

## 9-Phase Audit Process

| Phase | Name                   | What to Check                                                        |
| ----- | ---------------------- | -------------------------------------------------------------------- |
| 1     | Pre-Review             | Read skill files, check line counts, test discovery                  |
| 2     | Standards              | YAML validity, keywords, third-person style, directory structure     |
| 3     | Official Docs          | Verify APIs against current docs, check GitHub updates, npm versions |
| 4     | Code Examples          | Imports exist, API signatures match, templates work                  |
| 5     | Cross-File Consistency | SKILL.md vs references, bundled resources match actual files         |
| 6     | Dependencies           | Package versions current, breaking changes, staleness > 90 days      |
| 7     | Categorize             | Assign severity with evidence (GitHub/docs/npm links)                |
| 8     | Fix                    | Auto-fix unambiguous issues, ask user for architectural ones         |
| 9     | Verify                 | Run validator, test discovery, no contradictions, commit             |

## Phase Details

### Phase 1: Pre-Review

- Read all skill files (SKILL.md, references, scripts, assets)
- Check line counts against thresholds (SKILL.md: 100-150 target, 500 max)
- Test skill discovery by searching with natural language queries

### Phase 2: Standards Compliance

- YAML frontmatter parses correctly
- `name` matches directory, follows naming rules (lowercase, hyphens, 1-64 chars)
- `description` includes "Use when" or "Use for" triggers
- Third-person active voice throughout
- No excluded files (`README.md`, `metadata.json`, `_*` files)
- Reference files have required frontmatter (`title`, `description`, `tags`)

### Phase 3: Official Documentation Verification

- Use web search to verify API patterns against current official docs
- Check GitHub repository for recent updates, breaking changes, deprecations
- Verify npm package versions are current
- Compare skill patterns against production repositories

### Phase 4: Code Example Accuracy

- All imports reference real packages and real exports
- API signatures match current library versions
- Configuration examples use valid options
- Templates produce working code when applied

### Phase 5: Cross-File Consistency

- SKILL.md references match actual files in the directory
- Reference file content aligns with SKILL.md claims
- No orphan files (files that exist but are not referenced)
- No orphan links (references to files that do not exist)

### Phase 6: Dependency Check

- Package versions referenced in examples are current
- Check for breaking changes between referenced and current versions
- Flag dependencies not updated in over 90 days

### Phase 7: Severity Classification

| Level    | Meaning                                    | Examples                                           |
| -------- | ------------------------------------------ | -------------------------------------------------- |
| Critical | Code will fail if followed                 | Non-existent imports, invalid config, missing deps |
| High     | Code produces wrong results or confusion   | Contradictory examples, outdated major versions    |
| Medium   | Code works but is suboptimal or incomplete | Stale minors (> 90 days), missing doc sections     |
| Low      | Cosmetic or minor quality issues           | Typos, formatting, missing optional metadata       |

Every finding must include evidence: a link to official docs, GitHub issue, npm page, or specific code reference.

### Phase 8: Fix Decisions

**Auto-fix** when all conditions are met:

- The correct answer is unambiguous (e.g., import path from official docs)
- Clear evidence supports the fix
- No architectural impact

**Ask the user** when:

- Multiple valid approaches exist
- The fix involves breaking changes
- Architectural choices are required

### Phase 9: Verification

- Run `pnpm validate:skills skills/[skill-name]`
- Test discovery with natural language queries
- Confirm no contradictions between files
- Verify all referenced files exist

## Version Bumps

| Type  | When                                  | Example          |
| ----- | ------------------------------------- | ---------------- |
| Major | API patterns change, breaking changes | v1 to v2         |
| Minor | New features, backward compatible     | v1.0 to v1.1     |
| Patch | Bug fixes, typos, formatting only     | v1.0.0 to v1.0.1 |

## Common Review Findings

| Issue                  | Frequency  | Fix Approach                            |
| ---------------------- | ---------- | --------------------------------------- |
| Fake API adapters      | Common     | Verify imports exist in actual packages |
| Stale API methods      | Common     | Check signatures against current docs   |
| Schema inconsistency   | Moderate   | Align table/field names across files    |
| Version drift (> 90d)  | Frequent   | Update versions in code examples        |
| Contradictory examples | Moderate   | Pick one canonical pattern per concept  |
| Broken links           | Occasional | Verify all URLs resolve                 |
| Orphan file references | Occasional | Remove references or create the files   |

## Automated vs Manual Checks

**Automated** (via `pnpm validate:skills`):

- YAML syntax and frontmatter validation
- Name/description constraints
- Line count thresholds
- Code block language specifiers
- Required sections
- Reference link integrity

**Manual** (requires human or AI review):

- API methods vs current official documentation
- GitHub issues affecting skill patterns
- Code correctness and production readiness
- Schema consistency across examples
- Whether content duplicates agent knowledge

## Quality Checklist

Before committing a skill:

- Name is lowercase-hyphen-case, 1-64 chars, matches directory
- Description is 1-1024 chars with "Use when" or "Use for" trigger phrases
- SKILL.md under 500 lines with required sections
- All code examples tested against current library versions
- Package versions verified current
- Known issues documented with sources
- Cross-file consistency verified
- No high-severity issues remaining
- `pnpm validate:skills` passes
