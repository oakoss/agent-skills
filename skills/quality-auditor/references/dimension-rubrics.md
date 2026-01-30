---
title: Dimension Rubrics
description: Detailed scoring criteria, evidence requirements, and rubric tables for all 12 quality audit dimensions
tags:
  [
    scoring-rubrics,
    evaluation-criteria,
    quality-dimensions,
    evidence-based-audit,
  ]
---

# Dimension Rubrics

Each of the 12 dimensions requires specific evaluation criteria, evidence, and a scoring rubric.

## 1. Code Quality (10%)

**Evaluate:** Structure, naming conventions, duplication, cyclomatic/cognitive complexity, error handling, code smells, design patterns, SOLID principles.

| Score | Criteria                                                |
| ----- | ------------------------------------------------------- |
| 10    | Perfect structure, zero duplication, excellent patterns |
| 8     | Well-structured, minimal issues, good patterns          |
| 6     | Acceptable structure, some code smells                  |
| 4     | Poor structure, significant technical debt              |
| 2     | Chaotic, unmaintainable code                            |

**Evidence required:** Specific file examples, complexity metrics, pattern identification.

## 2. Architecture (10%)

**Evaluate:** System design, modularity, separation of concerns, scalability, dependency management, API design, data flow, coupling/cohesion.

| Score | Criteria                                       |
| ----- | ---------------------------------------------- |
| 10    | Exemplary, highly scalable, perfect modularity |
| 8     | Solid separation, scalable design              |
| 6     | Adequate, some coupling issues                 |
| 4     | High coupling, not scalable                    |
| 2     | Fundamentally flawed architecture              |

**Evidence required:** Component analysis, dependency analysis, architecture diagrams (if available).

## 3. Documentation (10%)

**Evaluate:** Completeness, clarity, accuracy, organization, practical examples, API docs, troubleshooting guides, architecture docs.

| Score | Criteria                                         |
| ----- | ------------------------------------------------ |
| 10    | Comprehensive, crystal clear, excellent examples |
| 8     | Very good coverage, clear, good examples         |
| 6     | Adequate coverage, some gaps                     |
| 4     | Poor coverage, confusing, lacks examples         |
| 2     | Minimal or misleading documentation              |

**Evidence required:** Documentation inventory, missing sections, quality assessment of examples.

## 4. Usability (10%)

**Evaluate:** Learning curve, installation ease, configuration complexity, workflow efficiency, error message quality, defaults, command/API ergonomics.

| Score | Criteria                        |
| ----- | ------------------------------- |
| 10    | Zero friction, delightful UX    |
| 8     | Minimal learning curve          |
| 6     | Usable but requires learning    |
| 4     | Steep learning curve, difficult |
| 2     | Nearly unusable                 |

**Evidence required:** Time-to-first-success, pain points, user journey analysis.

## 5. Performance (8%)

**Evaluate:** Execution speed, resource usage (CPU, memory), startup time, scalability under load, optimization techniques, caching, database queries, bundle size.

| Score | Criteria                                            |
| ----- | --------------------------------------------------- |
| 10    | Blazingly fast, minimal resources, highly optimized |
| 8     | Very fast, efficient resource usage                 |
| 6     | Acceptable performance                              |
| 4     | Slow, resource-heavy                                |
| 2     | Unusably slow, resource exhaustion                  |

**Evidence required:** Benchmarks, resource measurements, bottleneck identification.

## 6. Security (10%)

**Evaluate:** Vulnerability assessment, input validation, authentication/authorization, data encryption, dependency vulnerabilities, secret management, OWASP Top 10.

| Score | Criteria                                  |
| ----- | ----------------------------------------- |
| 10    | Zero vulnerabilities, exemplary practices |
| 8     | Very secure, minor concerns               |
| 6     | Adequate, some issues                     |
| 4     | Significant vulnerabilities               |
| 2     | Critical security flaws                   |

**Evidence required:** Vulnerability scan results, security checklist, specific issues found.

## 7. Testing (8%)

**Evaluate:** Coverage (unit/integration/e2e), test quality, automation, CI integration, test organization, mocking strategies, performance tests, security tests.

| Score | Criteria                                |
| ----- | --------------------------------------- |
| 10    | Comprehensive, automated, >90% coverage |
| 8     | Very good, automated, >80% coverage     |
| 6     | Adequate, >60% coverage                 |
| 4     | Poor, <40% coverage                     |
| 2     | Minimal or no tests                     |

**Evidence required:** Coverage reports, test inventory, quality assessment.

## 8. Maintainability (8%)

**Evaluate:** Technical debt, code readability, refactorability, modularity, developer documentation, contribution guidelines, code review process, versioning strategy.

| Score | Criteria                                             |
| ----- | ---------------------------------------------------- |
| 10    | Zero debt, highly maintainable, excellent guidelines |
| 8     | Low debt, easy to maintain                           |
| 6     | Moderate debt, maintainable                          |
| 4     | High debt, difficult to maintain                     |
| 2     | Unmaintainable                                       |

**Evidence required:** Debt analysis, maintainability metrics, contribution difficulty assessment.

## 9. Developer Experience (10%)

**Evaluate:** Setup ease, debugging experience, error messages, tooling support, hot reload/fast feedback, CLI ergonomics, IDE integration.

| Score | Criteria                |
| ----- | ----------------------- |
| 10    | Delightful to work with |
| 8     | Very productive         |
| 6     | Some friction           |
| 4     | Frustrating             |
| 2     | Actively hostile        |

**Evidence required:** Setup time measurement, developer pain points, tooling assessment.

## 10. Accessibility (8%)

**Evaluate:** WCAG compliance, keyboard navigation, screen reader support, color contrast, cognitive load, inclusive design.

| Score | Criteria                      |
| ----- | ----------------------------- |
| 10    | Universally accessible        |
| 8     | Highly accessible, inclusive  |
| 6     | Meets accessibility standards |
| 4     | Poor accessibility            |
| 2     | Inaccessible to many users    |

**Evidence required:** WCAG audit results, usability assessment for diverse users.

## 11. CI/CD (5%)

**Evaluate:** Automation level, build pipeline, testing automation, deployment automation, release process, monitoring/alerts, rollback capabilities.

| Score | Criteria                                |
| ----- | --------------------------------------- |
| 10    | Fully automated, zero-touch deployments |
| 8     | Highly automated, minimal manual steps  |
| 6     | Partially automated                     |
| 4     | Mostly manual                           |
| 2     | No automation                           |

**Evidence required:** Pipeline configuration, deployment frequency, failure rate.

## 12. Innovation (3%)

**Evaluate:** Novel approaches, creative solutions, forward-thinking design, industry leadership, unique value proposition.

| Score | Criteria                           |
| ----- | ---------------------------------- |
| 10    | Groundbreaking, sets new standards |
| 8     | Pushes boundaries                  |
| 6     | Some innovation                    |
| 4     | Mostly conventional                |
| 2     | No innovation                      |

**Evidence required:** Novel features, comparison with alternatives, industry impact.

## Special Evaluation Criteria

**For developer tools:** Setup time (<5 min = 10/10), error message quality, debugging experience, community support.

**For frameworks/libraries:** Bundle size, tree-shaking support, TypeScript support, browser compatibility, migration path.

**For ADHD-friendly tools:** One-command simplicity, automatic everything, clear visual feedback, minimal decisions, forgiving design (easy undo/backups), low cognitive load.

## Industry Benchmarks

| Dimension            | Industry Leader      |
| -------------------- | -------------------- |
| Code Quality         | Linux kernel, SQLite |
| Documentation        | Stripe, Tailwind CSS |
| Usability            | Vercel, Netlify      |
| Developer Experience | Next.js, Vite        |
| Testing              | Jest, Playwright     |

## Standards Referenced

- **Code:** Clean Code (Martin), Code Complete (McConnell), SonarQube quality gates
- **Architecture:** Clean Architecture (Martin), Domain-Driven Design (Evans)
- **Security:** OWASP Top 10, SANS Top 25, CWE/SANS
- **Accessibility:** WCAG 2.1 (AA/AAA), inclusive design guidelines
- **Testing:** Test Pyramid (Cohn), 80% minimum coverage target
- **Performance:** Core Web Vitals, RAIL model (Google), performance budgets
