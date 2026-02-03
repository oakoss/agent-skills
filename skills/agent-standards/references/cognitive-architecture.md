---
title: Cognitive Architecture
description: EGI reasoning framework, five-layer reasoning stack, planning modes, verifiable goals, multi-agent orchestration, and cognitive load management
tags:
  [
    reasoning,
    egi-framework,
    planning,
    multi-agent,
    cognitive-load,
    orchestration,
  ]
---

# Cognitive Architecture

## The Five-Layer Reasoning Stack

The Extended General Intelligence (EGI) framework defines how an AI agent processes information and produces actions:

1. **Perception**: Ingesting raw input (text, code, traces, terminal output)
2. **Semantic Understanding**: Mapping inputs to the current project context and ubiquitous language
3. **Collaborative Reasoning**: Evaluating multiple hypotheses and simulating outcomes
4. **Orchestration**: Sequencing tool calls and sub-tasks into a coherent plan
5. **Meta-Cognition**: Self-reflection and error correction (the critic layer)

## Planning Modes

Agents operate in one of three planning modes depending on the situation:

- **Goal-Driven (Proactive)**: The agent defines a high-level objective and works backward to create steps. Best for feature implementation and architecture tasks.
- **Event-Driven (Reactive)**: The agent responds to external triggers such as a failing test or a lint error. Best for debugging and CI pipeline issues.
- **Hybrid**: The agent maintains a proactive plan but can pivot instantly based on new evidence. This is the preferred mode for production work.

## Verifiable Goals

Every task must have a Definition of Done (DoD). Never consider a task finished without a verification signal:

- Test suite passes
- Build completes successfully
- User provides explicit approval
- Linter reports zero violations

## Multi-Agent Orchestration

Complex tasks are broken down into specialized roles:

- **Architect**: Designs the system structure and interfaces
- **Engineer**: Implements the logic and writes tests
- **Security**: Audits for vulnerabilities and compliance
- **SRE**: Ensures observability, performance, and deployment safety

## Cognitive Load Management

Agents must actively manage their own context window to maintain quality:

- **Pruning**: Removing irrelevant history that no longer affects the current task
- **Summarization**: Condensing long logs into actionable facts (single-sentence failure descriptions)
- **Archiving**: Moving stable information to long-term memory so it can be retrieved later without occupying active context
