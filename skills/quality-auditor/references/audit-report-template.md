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

Use this template structure when producing quality audit reports. Every section requires evidence -- no scores without justification.

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

## Report Template

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

1. [Strength 1 with evidence -- file path, metric, or example]
2. [Strength 2 with evidence]
3. [Strength 3 with evidence]

**Critical Areas for Improvement:**

1. [Weakness 1 with specific file references]
2. [Weakness 2 with specific file references]
3. [Weakness 3 with specific file references]

**Recommendation:** [Exceptional / Excellent / Very Good / Good / Acceptable / Needs Improvement]

---

## Detailed Scores

| Dimension            | Weight | Score | Rating   | Priority          |
| -------------------- | ------ | ----- | -------- | ----------------- |
| Code Quality         | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Architecture         | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Documentation        | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Usability            | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Performance          | 8%     | X/10  | [Rating] | [High/Medium/Low] |
| Security             | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Testing              | 8%     | X/10  | [Rating] | [High/Medium/Low] |
| Maintainability      | 8%     | X/10  | [Rating] | [High/Medium/Low] |
| Developer Experience | 10%    | X/10  | [Rating] | [High/Medium/Low] |
| Accessibility        | 8%     | X/10  | [Rating] | [High/Medium/Low] |
| CI/CD                | 5%     | X/10  | [Rating] | [High/Medium/Low] |
| Innovation           | 3%     | X/10  | [Rating] | [High/Medium/Low] |

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

- [Code examples, metrics, tool output]

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

## Quality Metrics

| Metric           | Result | Target   | Status      |
| ---------------- | ------ | -------- | ----------- |
| Code Coverage    | [X]%   | 80%+     | [Pass/Fail] |
| Complexity Avg   | [X]    | <15      | [Pass/Fail] |
| Dependency Vulns | [X]    | 0 high   | [Pass/Fail] |
| Bundle Size      | [X] KB | [Budget] | [Pass/Fail] |

---

## Conclusion

[Summary of findings, overall assessment, final recommendation]

**Final Verdict:** [Detailed recommendation with next steps]
```

## Weighted Score Calculation

Calculate the overall score using dimension weights:

```text
Overall = (CodeQuality * 0.10) + (Architecture * 0.10) + (Documentation * 0.10)
        + (Usability * 0.10) + (Performance * 0.08) + (Security * 0.10)
        + (Testing * 0.08) + (Maintainability * 0.08) + (DX * 0.10)
        + (Accessibility * 0.08) + (CICD * 0.05) + (Innovation * 0.03)
```

Round to one decimal place. Apply any caps (Phase 0 failure caps at 6.0).

## Evidence Standards

Every score must include at least one of:

- **File reference** -- specific path and line number
- **Metric** -- quantitative measurement from a tool
- **Code example** -- concrete snippet demonstrating the issue
- **Tool output** -- scan results, coverage reports, benchmark data

Scores without evidence are invalid. If a dimension cannot be evaluated (e.g., no UI means accessibility is not applicable), note it as "N/A" and redistribute the weight proportionally.

## The Rejection Protocol

If the audit fails any critical check:

1. **Stop** -- do not proceed with the commit or final report
2. **Analyze** -- identify the specific deviation from standards
3. **Remediate** -- apply the fix immediately
4. **Re-audit** -- restart the checklist from Phase 0
