---
title: Project Patterns
description: Pattern A/B/C classification, phase sequences, skill coordination by phase, parallelization opportunities, and deliverables
tags: [patterns, classification, phases, skill-coordination, parallelization]
---

# Project Patterns

Classify every project before selecting frameworks or skills.

## Pattern A: Simple Feature/Enhancement

- Adding to existing system, well-understood requirements
- Low risk, single-team, 1-5 days
- Examples: search filter, dashboard widget, form field, styling update

**Sequence:** feature framework -> code quality -> testing -> deployment

## Pattern B: New Product/System

- Building from scratch or major module, user validation needed
- Security/compliance important, multiple considerations, 4-12 weeks
- Examples: SaaS product, customer portal, internal tool, API platform

**Phases:**

1. **Discovery** -- Validation frameworks, product-market fit analysis, user research
2. **Architecture and Design** -- System design, prototyping, UX design, security architecture, API design
3. **Development** -- Full-stack development, frontend/backend build, API implementation, quality assurance
4. **Testing** -- Test validation, QA, usability testing, security review
5. **Deployment** -- DevOps setup, deployment, go-to-market planning

## Pattern C: AI-Native/Complex System

All Pattern B phases, plus:

- **Phase 2b (AI Architecture)** -- Multi-agent architecture, RAG implementation, knowledge graph design, agentic workflow orchestration
- **Phase 3b (AI Development)** -- Context engineering, multi-agent orchestration implementation
- **Phase 4b (AI Testing)** -- Agent behavior tests, RAG retrieval quality, LLM benchmarks

Characteristics: AI agents, RAG, knowledge graphs, complex orchestration, 8-20 weeks.

## Phase Gates

Do not advance without meeting gate criteria.

| Gate              | Entry Criteria                                                                                 |
| ----------------- | ---------------------------------------------------------------------------------------------- |
| Design (Phase 2)  | PRP complete, problem validated, success metrics defined, user stories documented              |
| Development (3)   | Architecture documented, data model designed, security threats identified, mitigations planned |
| Testing (Phase 4) | Features complete, unit tests over 80%, code review passed, SAST scans clean                   |
| Deployment (5)    | All tests passing, UAT completed, security testing done, coverage over 90%                     |

## Skill Coordination by Phase

Limit to 1-3 skills per phase. Each skill has a specific deliverable and clear handoff.

| Phase       | Skills                                                             |
| ----------- | ------------------------------------------------------------------ |
| Discovery   | user-researcher, product-strategist, product-analyst               |
| Design      | ux-designer, design-system-architect, security-architect           |
| Development | frontend-builder, api-designer, mvp-builder, multi-agent-architect |
| Testing     | quality-assurance, usability-tester, security-architect            |
| Deployment  | deployment-advisor, go-to-market-planner, performance-optimizer    |
| Post-Launch | product-analyst, customer-feedback-analyzer, performance-optimizer |

## Parallelization Opportunities

- UX design + Architecture design (Phase 2)
- Frontend + Backend development (Phase 3)
- Test writing + Feature development (Phase 3)
- Independent capability steps with no shared dependencies (HTN parallel steps)

## Troubleshooting

**Wrong pattern identified mid-project:**
Adapt orchestration. Pattern A to B: add discovery and design phases. Pattern B to C: add AI architecture and testing. Scope reduction: simplify orchestration.

**Phase gate not met:**
Do not skip. Identify specific unmet criteria, address them, then re-validate. Partial advancement leads to compounding rework.

## Deliverables

When orchestrating, produce:

1. **Pattern classification** with rationale and timeline estimate
2. **Orchestration plan** with phase breakdown, framework sequence, skill activation points, and gate criteria
3. **Phase status** showing current position, completion percentage, gate readiness, and next steps
4. **Decision log** capturing selected capabilities, alternatives considered, scores, and reasoning
