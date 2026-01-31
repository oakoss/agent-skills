---
title: Audit Rubric
description: Multi-dimension audit rubric with pass/warn/fail criteria, weighted scoring methodology, automated vs manual checklists, and audit report format
tags:
  [
    audit-rubric,
    pass-warn-fail,
    weighted-scoring,
    automated-checks,
    manual-review,
    scoring-methodology,
  ]
---

# Audit Rubric

A structured rubric for executing quality audits with clear pass/warn/fail thresholds, weighted scoring, and a distinction between automated and manual audit items.

## Pass / Warn / Fail Thresholds

Each dimension receives a 1-10 score, then maps to a threshold:

| Threshold | Score Range | Meaning                                         | Action Required           |
| --------- | ----------- | ----------------------------------------------- | ------------------------- |
| Pass      | 7-10        | Meets or exceeds standards                      | No action                 |
| Warn      | 5-6         | Below standard but functional                   | Improvement plan required |
| Fail      | 1-4         | Critical gaps, blocks release or further work   | Immediate remediation     |
| N/A       | --          | Dimension does not apply (e.g., no UI for a11y) | Redistribute weight       |

**Hard fail conditions (override any score):**

- Phase 0 resource completeness fails -- cap overall at 6.0
- Any security dimension score of 3 or below -- flag as release blocker
- Any critical anti-pattern found without a mitigation plan -- fail the audit

## Dimension Rubric Summary

Each dimension uses consistent criteria across three levels. See `dimension-rubrics.md` for full per-dimension detail.

### Code Quality (10%)

| Level | Criteria                                                      |
| ----- | ------------------------------------------------------------- |
| Pass  | Consistent patterns, low duplication, complexity under limits |
| Warn  | Some code smells, moderate duplication, complexity hotspots   |
| Fail  | No patterns, widespread duplication, god objects              |

### Architecture (10%)

| Level | Criteria                                                        |
| ----- | --------------------------------------------------------------- |
| Pass  | Clear module boundaries, low coupling, scalable design          |
| Warn  | Some coupling, unclear boundaries in non-critical areas         |
| Fail  | Circular dependencies, tight coupling, no separation of concern |

### Documentation (10%)

| Level | Criteria                                                   |
| ----- | ---------------------------------------------------------- |
| Pass  | All features documented, examples work, accurate to code   |
| Warn  | Major features documented, some gaps, some stale examples  |
| Fail  | Missing docs for critical paths, misleading or no examples |

### Usability (10%)

| Level | Criteria                                                      |
| ----- | ------------------------------------------------------------- |
| Pass  | Under 10 minutes to first success, clear error messages       |
| Warn  | 10-30 minutes to first success, some confusing error messages |
| Fail  | Over 30 minutes to first success, cryptic errors, no defaults |

### Performance (8%)

| Level | Criteria                                                              |
| ----- | --------------------------------------------------------------------- |
| Pass  | Within performance budget, no N+1 queries, acceptable Core Web Vitals |
| Warn  | Occasional slow paths, minor budget overruns, no profiling            |
| Fail  | Unusable latency, resource exhaustion, no optimization                |

### Security (10%)

| Level | Criteria                                                       |
| ----- | -------------------------------------------------------------- |
| Pass  | OWASP Top 10 addressed, inputs validated, no hardcoded secrets |
| Warn  | Most inputs validated, minor dependency vulnerabilities        |
| Fail  | Hardcoded secrets, SQL injection, missing auth on endpoints    |

### Testing (8%)

| Level | Criteria                                                           |
| ----- | ------------------------------------------------------------------ |
| Pass  | 80%+ coverage, unit/integration/e2e present, tests verify behavior |
| Warn  | 60-79% coverage, mostly unit tests, some flaky tests               |
| Fail  | Under 40% coverage, no integration tests, tests verify mocks       |

### Maintainability (8%)

| Level | Criteria                                                     |
| ----- | ------------------------------------------------------------ |
| Pass  | Low tech debt, clear contribution path, semver compliance    |
| Warn  | Moderate debt, some outdated deps, unclear contribution path |
| Fail  | High debt, abandoned dependencies, no versioning strategy    |

### Developer Experience (10%)

| Level | Criteria                                                    |
| ----- | ----------------------------------------------------------- |
| Pass  | Under 5 minutes setup, fast feedback loop, good error DX    |
| Warn  | 5-15 minutes setup, some friction, basic error messages     |
| Fail  | Over 15 minutes setup, broken tooling, no debugging support |

### Accessibility (8%)

| Level | Criteria                                                    |
| ----- | ----------------------------------------------------------- |
| Pass  | WCAG 2.1 AA compliant, keyboard navigable, screen reader OK |
| Warn  | Partial WCAG compliance, keyboard works for main flows      |
| Fail  | No WCAG compliance, keyboard traps, inaccessible content    |

### CI/CD (5%)

| Level | Criteria                                             |
| ----- | ---------------------------------------------------- |
| Pass  | Automated build, test, deploy pipeline with rollback |
| Warn  | Automated build and test, manual deploy              |
| Fail  | No automation, manual build and deploy               |

### Innovation (3%)

| Level | Criteria                                           |
| ----- | -------------------------------------------------- |
| Pass  | Novel approach or unique value proposition         |
| Warn  | Conventional but competent implementation          |
| Fail  | Derivative with no differentiation (rarely blocks) |

## Weighted Scoring Methodology

### Calculating the Overall Score

Multiply each dimension score by its weight, then sum:

```text
Overall = (CodeQuality * 0.10) + (Architecture * 0.10) + (Documentation * 0.10)
        + (Usability * 0.10) + (Performance * 0.08) + (Security * 0.10)
        + (Testing * 0.08) + (Maintainability * 0.08) + (DX * 0.10)
        + (Accessibility * 0.08) + (CICD * 0.05) + (Innovation * 0.03)
```

Round to one decimal place.

### Handling N/A Dimensions

When a dimension does not apply, redistribute its weight proportionally:

```text
Example: CLI tool with no UI -- Accessibility (8%) is N/A

Remaining weight = 100% - 8% = 92%
Adjusted weights = each remaining dimension weight / 0.92

Code Quality: 10% / 0.92 = 10.9%
Security: 10% / 0.92 = 10.9%
...
```

### Weight Adjustments by Project Type

Customize weights based on what matters most:

| Project Type    | Increase Weight     | Decrease Weight   |
| --------------- | ------------------- | ----------------- |
| Public API      | Security, Docs, DX  | Innovation, A11y  |
| Consumer Web    | A11y, Perf, UX      | CI/CD, Innovation |
| Internal Tool   | DX, Maintainability | A11y, Innovation  |
| Library/Package | Architecture, Tests | Usability, CI/CD  |
| CLI Tool        | DX, Usability, Docs | A11y, Perf        |

Document any weight adjustments in the audit report with justification.

### Score Caps

| Condition                           | Cap |
| ----------------------------------- | --- |
| Phase 0 resource completeness fails | 6.0 |
| Any dimension scores 1-2            | 7.0 |
| Security scores 3 or below          | 5.0 |
| No tests exist                      | 6.0 |

Apply the lowest applicable cap.

## Automated vs Manual Audit Items

### Automated Checks (Run First)

These checks produce objective, repeatable results. Run them before manual review.

| Check             | Tool / Command                                         | Pass Criteria             |
| ----------------- | ------------------------------------------------------ | ------------------------- |
| Type safety       | `npx tsc --noEmit --strict`                            | Zero errors               |
| Lint              | `npx eslint . --max-warnings 0`                        | Zero errors               |
| Format            | `npx prettier --check .`                               | No formatting diffs       |
| Tests             | `npx vitest run --coverage`                            | All pass, coverage target |
| Security deps     | `npm audit --audit-level=high`                         | No high/critical vulns    |
| Bundle size       | Build output size check                                | Within budget             |
| Hardcoded secrets | `rg -i "(api.?key\|secret\|password\|token)\\s*[:=]"`  | Zero matches in source    |
| Dead code         | `rg "console\\.(log\|debug)" -g "*.ts" -g "!*.test.*"` | Zero matches              |
| Complexity        | SonarQube or custom threshold                          | Under configured limit    |

### Manual Review Items

These require human or AI judgment. Perform after automated checks pass.

| Check                      | What to Evaluate                                           |
| -------------------------- | ---------------------------------------------------------- |
| Architectural fit          | Does the code follow the system's design direction?        |
| Requirement alignment      | Does implementation match what was requested?              |
| Convention consistency     | Does code follow established team patterns?                |
| API design quality         | Are endpoints/interfaces intuitive, consistent, versioned? |
| Error handling adequacy    | Are error paths thoughtful, not just catch-and-log?        |
| Edge case coverage         | Are boundary conditions and failure modes handled?         |
| Documentation accuracy     | Does documentation match the actual implementation?        |
| Future maintainability     | Will this code be easy to modify in six months?            |
| Business logic correctness | Do calculations and rules match requirements?              |
| Integration safety         | Does the change interact correctly with existing code?     |

### Audit Execution Order

1. Run all automated checks and collect results
2. If any automated check fails, stop and remediate before manual review
3. Perform manual review items, scoring each dimension
4. Calculate weighted overall score
5. Apply score caps if any hard-fail conditions triggered
6. Generate the audit report

## Audit Report Format

Structure every audit report with these sections in order:

```markdown
# Quality Audit Report: [Subject]

**Date:** [Date]
**Version:** [Version]
**Auditor:** [Agent or person]

## Executive Summary

**Overall Score:** [X.X]/10 - [Pass/Warn/Fail]

**Top 3 Strengths:** [With evidence]
**Top 3 Weaknesses:** [With evidence]
**Recommendation:** [Exceptional / Excellent / Good / Acceptable / Needs Improvement]

## Automated Gate Results

| Gate | Result | Details |
| ---- | ------ | ------- |

## Dimension Scores

| Dimension | Weight | Score | Level | Evidence Summary |
| --------- | ------ | ----- | ----- | ---------------- |

**Weighted Overall:** [X.X]/10
**Caps Applied:** [None / list]

## Findings by Priority

### Critical (Fix Before Release)

### High (Fix This Sprint)

### Medium (Plan for Next Sprint)

### Low (Backlog)

## Recommendations

### Quick Wins (High Impact / Low Effort)

### Short-Term (1-3 Months)

### Long-Term (3-12 Months)

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
```

See `audit-report-template.md` for the full template with all subsections.

## Calibration Guidelines

To maintain consistent scoring across audits:

- **10/10 is rare** -- reserved for industry-leading implementations (Linux kernel code quality, Stripe documentation)
- **Most quality software scores 6-7** -- this is the realistic baseline
- **A score of 8+ means genuinely above average** -- requires strong evidence
- **Compare against industry leaders**, not team averages or personal standards
- **Every score needs evidence** -- file paths, metrics, tool output, or concrete examples
- **Scores without evidence are invalid** -- reject them during review
