---
name: quality-auditor
description: 'Code quality gatekeeper and auditor. Enforces strict quality gates, resolves the AI verification gap, and evaluates codebases across 12 critical dimensions with evidence-based scoring. Use when auditing code quality, reviewing AI-generated code, scoring codebases against industry standards, or enforcing pre-commit quality gates.'
---

# Quality Auditor

## Overview

Evaluates tools, frameworks, systems, and codebases against the highest industry standards across 12 weighted dimensions. Produces evidence-based scores, identifies anti-patterns, and generates prioritized improvement roadmaps. Applies extra scrutiny to AI-generated code through the verification gap protocol.

**When to use:** Auditing code quality, reviewing AI-generated code, scoring codebases against industry benchmarks, enforcing pre-commit quality gates, comparing tools or frameworks.

**When NOT to use:** Quick code reviews without scoring, style-only linting (use a linter), feature implementation.

## Quick Reference

| Dimension            | Weight | What to Evaluate                                                    |
| -------------------- | ------ | ------------------------------------------------------------------- |
| Code Quality         | 10%    | Structure, patterns, SOLID, duplication, complexity, error handling |
| Architecture         | 10%    | Design, modularity, scalability, coupling/cohesion, API design      |
| Documentation        | 10%    | Completeness, clarity, accuracy, examples, troubleshooting          |
| Usability            | 10%    | Learning curve, installation ease, error messages, ergonomics       |
| Performance          | 8%     | Speed, resource usage, caching, bundle size, Core Web Vitals        |
| Security             | 10%    | OWASP Top 10, input validation, auth, secrets, dependencies         |
| Testing              | 8%     | Coverage (unit/integration/e2e), quality, automation, organization  |
| Maintainability      | 8%     | Technical debt, readability, refactorability, versioning            |
| Developer Experience | 10%    | Setup ease, debugging, tooling, hot reload, IDE integration         |
| Accessibility        | 8%     | WCAG compliance, keyboard nav, screen readers, cognitive load       |
| CI/CD                | 5%     | Automation, pipelines, deployment, rollback, monitoring             |
| Innovation           | 3%     | Novel approaches, forward-thinking design, unique value             |

## Scoring System

| Score | Rating      | Meaning                                     |
| ----- | ----------- | ------------------------------------------- |
| 10    | Exceptional | Industry-leading, sets new standards        |
| 8-9   | Excellent   | Exceeds expectations significantly          |
| 6-7   | Good        | Meets expectations with improvements needed |
| 5     | Acceptable  | Below average, significant improvements     |
| 3-4   | Poor        | Major gaps and fundamental problems         |
| 1-2   | Critical    | Barely functional or non-functional         |

## Audit Process

1. **Phase 0 -- Resource Completeness** (mandatory first step; audit fails if this fails)
2. **Phase 1 -- Discovery** (read docs, examine code, test system, review materials)
3. **Phase 2 -- Evaluation** (score each dimension with evidence, strengths, weaknesses)
4. **Phase 3 -- Synthesis** (executive summary, detailed scores, recommendations, risk assessment)

## Common Mistakes

| Mistake                                                    | Correct Pattern                                                                                          |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Giving inflated scores without evidence                    | Every score must cite specific files, metrics, or code examples as evidence                              |
| Skipping Phase 0 resource completeness check               | Always verify registry completeness first; missing resources cap the overall score at 6/10               |
| Evaluating only code quality and ignoring other dimensions | Score all 12 dimensions with appropriate weights; architecture, security, and DX matter equally          |
| Accepting superficial "LGTM" reviews                       | Perform deep semantic audits checking contract integrity, security sanitization, and performance hygiene |
| Proceeding after audit failure without re-audit            | Stop, analyze the deviation, remediate, then restart the checklist from step 1                           |
| Using 10/10 scores without exceptional justification       | Reserve 10/10 for truly industry-leading work; most quality tools score 6-7                              |

## Delegation

- **Discover codebase structure and gather audit evidence**: Use `Explore` agent to survey file organization, dependencies, test coverage, and documentation
- **Execute targeted quality checks across dimensions**: Use `Task` agent to run linters, security scanners, performance profilers, and accessibility audits
- **Design quality improvement roadmap**: Use `Plan` agent to prioritize quick wins, short-term, and long-term recommendations from audit findings

## References

- [Dimension Rubrics](references/dimension-rubrics.md) -- detailed scoring criteria, evidence requirements, and rubric tables for all 12 dimensions
- [Audit Report Template](references/audit-report-template.md) -- structured report format, executive summary, recommendations, risk assessment
- [Anti-Patterns Guide](references/anti-patterns-guide.md) -- code, architecture, security, testing, and process anti-patterns to identify during audits
