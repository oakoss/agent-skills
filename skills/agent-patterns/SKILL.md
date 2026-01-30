---
name: agent-patterns
description: |
  Multi-agent design patterns for Claude Code and AI development systems. Covers fungible vs specialized agents, sub-agent delegation, orchestration patterns, communication protocols, context hygiene, batch workflows, and failure recovery.

  Use when: designing multi-agent systems, creating custom sub-agents, delegating bulk operations, orchestrating parallel work, choosing between fungible and specialized agents, or debugging agent coordination issues.
---

# Agent Patterns

Comprehensive guide to multi-agent design, delegation, and orchestration in Claude Code and AI-assisted development. Default to fungible agents for software dev; use specialized agents only for peer review or discourse.

## Quick Reference

| Pattern                 | Description                                     | When to Use                                  |
| ----------------------- | ----------------------------------------------- | -------------------------------------------- |
| Fungible swarm          | Identical agents pick tasks from a shared board | Large-scale software dev, resilient systems  |
| Sequential pipeline     | Each agent builds on previous output            | Multi-step workflows with clear dependencies |
| Hierarchical            | Manager decomposes, workers execute in parallel | Complex tasks with independent subtasks      |
| Peer collaboration      | Agents iterate until consensus                  | Code review, quality-critical outputs        |
| Orchestrator delegation | Spawns sub-agents via Task tool                 | Multi-phase workflows, parallel specialists  |

| Configuration         | Value                                                                                              |
| --------------------- | -------------------------------------------------------------------------------------------------- |
| Custom agent location | `.claude/agents/*.md` (project), `~/.claude/agents/*.md` (user)                                    |
| Built-in sub-agents   | Explore (Haiku, read-only), Plan (Sonnet), General (Sonnet, all tools)                             |
| Config fields         | `name`, `description` (required); `tools`, `model`, `permissionMode`, `skills`, `hooks` (optional) |
| Batch size            | 5-8 items per agent (standard tasks)                                                               |
| Parallel agents       | 2-4 simultaneously                                                                                 |
| Max nesting depth     | 2 levels (3 works but context thins)                                                               |

## Common Mistakes

| Mistake                                                     | Correct Pattern                                                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Giving Bash tool to agents that only create files           | Use Write and Edit tools only; Bash causes approval spam from heredoc usage                      |
| Spawning too many agents (5+) for a small task              | Start with 2-3 agents; coordination overhead outweighs benefit at higher counts                  |
| Burying critical instructions past line 300 of agent prompt | Put critical rules immediately after frontmatter; models deprioritize late instructions          |
| Using specialized agents for large-scale software dev       | Use fungible agents with a shared task board; specialized agents create single points of failure |
| Not including "FIX issues found" in delegation prompts      | Without explicit action directive, agents only report problems without making changes            |

## Delegation

- **Explore codebase before designing agent prompts**: Use `Explore` agent to discover file structure and conventions
- **Plan multi-agent architecture for complex projects**: Use `Plan` agent to determine batch sizes, agent count, and task decomposition
- **Execute batch operations across many files**: Use `Task` agent with identical prompts and non-overlapping item lists

## References

- [Agent types and design patterns](references/agent-types.md)
- [Delegation patterns and batch workflows](references/delegation-patterns.md)
- [Sub-agent configuration and prompt engineering](references/sub-agent-configuration.md)
- [Communication and orchestration patterns](references/orchestration.md)
- [Troubleshooting and anti-patterns](references/troubleshooting.md)
