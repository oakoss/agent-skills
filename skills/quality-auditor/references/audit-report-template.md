---
title: Audit Report Template
description: Structured report format for quality audits including executive summary, detailed scores, recommendations, risk assessment, and comparative analysis
tags:
  [
    audit-report,
    executive-summary,
    recommendations,
    risk-assessment,
    quality-scoring,
  ]
---

# Audit Report Template

Use this template structure when producing quality audit reports.

## Report Structure

```markdown
# Quality Audit Report: [Tool/System Name]

**Date:** [Date]
**Version Audited:** [Version]
**Auditor:** [Agent/Skill name]

---

## Executive Summary

**Overall Score:** [X.X]/10 - [Rating]

**Rating Scale:**

- 9.0-10.0: Exceptional
- 8.0-8.9: Excellent
- 7.0-7.9: Very Good
- 6.0-6.9: Good
- 5.0-5.9: Acceptable
- Below 5.0: Needs Improvement

**Key Strengths:**

1. [Strength 1 with evidence]
2. [Strength 2 with evidence]
3. [Strength 3 with evidence]

**Critical Areas for Improvement:**

1. [Weakness 1 with specific file references]
2. [Weakness 2 with specific file references]
3. [Weakness 3 with specific file references]

**Recommendation:** [Exceptional / Excellent / Very Good / Good / Acceptable / Needs Improvement]

---

## Detailed Scores

| Dimension            | Score | Rating   | Priority          |
| -------------------- | ----- | -------- | ----------------- |
| Code Quality         | X/10  | [Rating] | [High/Medium/Low] |
| Architecture         | X/10  | [Rating] | [High/Medium/Low] |
| Documentation        | X/10  | [Rating] | [High/Medium/Low] |
| Usability            | X/10  | [Rating] | [High/Medium/Low] |
| Performance          | X/10  | [Rating] | [High/Medium/Low] |
| Security             | X/10  | [Rating] | [High/Medium/Low] |
| Testing              | X/10  | [Rating] | [High/Medium/Low] |
| Maintainability      | X/10  | [Rating] | [High/Medium/Low] |
| Developer Experience | X/10  | [Rating] | [High/Medium/Low] |
| Accessibility        | X/10  | [Rating] | [High/Medium/Low] |
| CI/CD                | X/10  | [Rating] | [High/Medium/Low] |
| Innovation           | X/10  | [Rating] | [High/Medium/Low] |

**Overall Score:** [Weighted Average]/10

---

## Dimension Analysis

### [N]. [Dimension Name]: [Score]/10

**Rating:** [Excellent/Good/Acceptable/Poor]

**Strengths:**

- [Specific strength with file reference]

**Weaknesses:**

- [Specific weakness with file reference]

**Evidence:**

- [Code examples, metrics]

**Improvements:**

1. [Specific actionable improvement]

[Repeat for all 12 dimensions]

---

## Recommendations

### Immediate Actions (Quick Wins) -- 1-2 weeks

1. **[Action]**
   - Impact: High
   - Effort: Low
   - Timeline: [X] days

### Short-term Improvements -- 1-3 months

1. **[Improvement]**
   - Impact: Medium-High
   - Effort: Medium
   - Timeline: [X] weeks

### Long-term Strategic -- 3-12 months

1. **[Strategic improvement]**
   - Impact: High
   - Effort: High
   - Timeline: [X] months

---

## Risk Assessment

### High-Risk Issues

**[Issue]:**

- Risk Level: Critical/High
- Impact: [Description]
- Mitigation: [Specific steps]

### Medium-Risk Issues

[List with same format]

### Low-Risk Issues

[List with same format]

---

## Comparative Analysis

| Feature/Aspect | [This Tool] | [Leader 1] | [Leader 2] |
| -------------- | ----------- | ---------- | ---------- |
| [Aspect]       | [Score]     | [Score]    | [Score]    |

---

## Conclusion

[Summary of findings, overall assessment, final recommendation]
```

## Phase 0: Resource Completeness Check

This check is mandatory before scoring. The audit must fail if resources are incomplete.

**Verification steps:**

1. Count resources in directories vs registry entries (must match)
2. Verify all resources in filesystem are discoverable through the registry
3. Check cross-references point to existing entries
4. Verify CLI reads from registry (not hardcoded data)

**Critical failure conditions (cap overall score at 6/10):**

- Registry missing >10% of resources from directories
- README documents resources not in registry
- CLI uses mock/hardcoded data instead of registry
- Cross-references point to non-existent resources

## The Verification Gap Protocol

AI-generated code requires extra scrutiny:

- **Critic agents** -- use high-reasoning models to audit faster outputs
- **Verifiable goals** -- every PR must produce a signal of success (test pass, lint pass, build pass)
- **Human oversight** -- mandatory human sign-off for critical business logic
- **Excellence over mimicry** -- do not repeat bad local patterns; use idiomatic standards
- **No black boxes** -- every complex function must explain its reasoning
- **Metadata** -- tag generated files for future auditing

## The Rejection Protocol

If the audit fails:

1. **Stop** -- do not proceed with the commit or report
2. **Analyze** -- identify the specific deviation
3. **Remediate** -- apply the fix immediately
4. **Re-audit** -- restart the checklist from step 1
