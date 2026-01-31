---
title: Validation
description: Manifest-implementation drift detection, validation dimensions, scoring criteria, and pass thresholds
tags:
  [
    validation,
    drift,
    scoring,
    manifest,
    implementation,
    precondition,
    effect,
    coverage,
  ]
---

# Validation

## Purpose

Validates that a skill's implementation matches what its manifest (SKILL.md frontmatter and body) promises. Detects drift between description and reality, missing functionality, and over-promised capabilities.

## When to Validate

- After updating skill implementations or reference files
- During quality audits
- When manifests feel outdated or incorrect
- Before releasing new versions
- When a skill has not been reviewed in over 90 days

## Validation Dimensions

| Dimension               | What It Checks                                      |
| ----------------------- | --------------------------------------------------- |
| Description Accuracy    | Implementation matches manifest description         |
| Precondition Validation | Claimed preconditions are actually checked in code  |
| Effect Verification     | Code produces all claimed effects                   |
| API Surface Analysis    | Exported functions and patterns match manifest      |
| Drift Detection         | Implementation has diverged from manifest over time |
| Coverage Scoring        | Percentage of manifest that is actually implemented |

## Validation Process

### Step 1: Load Manifest and Implementation

Read the skill's `SKILL.md` frontmatter as the manifest. Read all reference files, scripts, and assets as the implementation. If the skill is declarative only (no scripts), validate the description against reference file content.

### Step 2: Validate Description Accuracy

Compare the `description` field against actual skill content:

- Does the skill cover every topic mentioned in the description?
- Are there topics covered in references but not mentioned in the description?
- Are "Use when" scenarios actually addressed by the skill content?

Produce an accuracy score from 0.0 to 1.0.

### Step 3: Validate Preconditions

If the skill mentions prerequisites (e.g., "requires Node.js 18+", "assumes TypeScript project"):

- Are those prerequisites documented clearly?
- Do scripts check for them before executing?
- Are error messages clear when prerequisites are not met?

Produce a coverage score from 0.0 to 1.0.

### Step 4: Validate Effects

For each capability the skill claims to provide:

- Is there actual content (instructions, examples, scripts) that delivers it?
- Are there conditions where the claimed effect would not work?
- Are there undocumented capabilities the skill provides but does not describe?

Produce a coverage score from 0.0 to 1.0.

### Step 5: Validate Cross-References

- Every file referenced in SKILL.md exists on disk
- Every file on disk is referenced somewhere (no orphans)
- Reference file frontmatter (`title`, `description`, `tags`) is present and accurate
- No broken relative paths

## Scoring

```text
Overall score = average(description_accuracy, precondition_coverage, effect_coverage)

Pass criteria:
  - Overall score >= 0.8
  - Zero high-severity issues
```

### Severity Levels for Validation Issues

| Level  | Meaning                                                                     |
| ------ | --------------------------------------------------------------------------- |
| High   | Missing core functionality, unenforced preconditions, unimplemented effects |
| Medium | Incomplete features, poor error handling, undocumented capabilities         |
| Low    | Minor inconsistencies, documentation gaps, style issues                     |

## Common Drift Patterns

| Pattern                   | Detection                                         | Fix                                           |
| ------------------------- | ------------------------------------------------- | --------------------------------------------- |
| Description oversells     | Topics in description not covered in content      | Remove from description or add content        |
| Undocumented capabilities | Content exists without description mention        | Update description to include it              |
| Stale examples            | Code examples reference deprecated APIs           | Update to current API patterns                |
| Orphan references         | SKILL.md links to files that do not exist         | Create the file or remove the link            |
| Phantom files             | Files exist but nothing links to them             | Add reference in SKILL.md or remove file      |
| Precondition assumptions  | Scripts assume environment state without checking | Add explicit checks with clear error messages |

## Running Validation

### Automated Structural Validation

```bash
pnpm validate:skills skills/[skill-name]
```

This checks frontmatter, naming, line counts, required sections, and reference link integrity.

### Manual Content Validation

For semantic validation (does the content match the claims), perform these steps:

1. Read the `description` field and list every claim
2. For each claim, find the supporting content in SKILL.md or references
3. Score each claim as covered (1.0), partially covered (0.5), or missing (0.0)
4. Average the scores for the description accuracy component
5. Repeat for preconditions and effects
6. Calculate the overall score and identify any high-severity gaps

## Validation Report Format

A validation report should include:

- **Skill name and validation date**
- **Overall score** with component breakdowns
- **Issues list** with severity, description, and suggested fix
- **Pass/fail determination** based on score >= 0.8 and zero high-severity issues
- **Recommendations** for improving the score
