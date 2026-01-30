---
title: Delegation Patterns and Batch Workflows
description: How to delegate work to agents including batch sizing, prompt templates, and workflow steps
tags: [delegation, batch, workflow, prompt-template, parallel]
---

# Delegation Patterns and Batch Workflows

## The Sweet Spot

Tasks that are **repetitive but require judgment**:

- Audit 70 skills checking versions against docs
- Update 50 files deciding what needs changing
- Research 10 frameworks evaluating trade-offs

Not a good fit: simple find-replace (no judgment), single complex tasks (not repetitive), tasks with cross-item dependencies (agents work independently).

## Core Prompt Template

```markdown
For each [item]:

1. Read [source file/data]
2. Verify with [external check]
3. Check [authoritative source]
4. Evaluate/score
5. FIX issues found

Items: [explicit list]
Working directory: [absolute path]
```

"FIX issues found" is critical -- without it agents only report, with it they act.

## Batch Sizing

| Batch Size | Use When                                        |
| ---------- | ----------------------------------------------- |
| 3-5 items  | Complex tasks (deep research, multi-step fixes) |
| 5-8 items  | Standard tasks (audits, updates, validations)   |
| 8-12 items | Simple tasks (version checks, format fixes)     |

Launch 2-4 agents in parallel, each with their own batch.

## Workflow

```text
1. PLAN:   Identify items, divide into batches
2. LAUNCH: Parallel Task calls with identical templates, different item lists
3. WAIT:   Agents work in parallel (read -> verify -> check -> edit -> report)
4. REVIEW: Check agent reports, git status, spot-check diffs
5. COMMIT: Batch changes with meaningful changelog (one commit per category)
```

## Context Hygiene

The primary value of sub-agents is keeping the main context clean.

**Without agents**: A deploy workflow runs ~10 tool calls, consuming 500+ lines in main context. Over a session, this compounds.

**With agents**: The same workflow returns a 30-line summary. All verbose tool outputs and intermediate reasoning are discarded after the agent returns.

**When this matters most**:

- Repeatable workflows (deploy, migrate, audit, review)
- Verbose tool outputs (build logs, test results, API responses)
- Multi-step operations where only the final result matters
- Long sessions where context pressure builds up
