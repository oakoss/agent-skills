---
title: Decision Tracking and Conditional Documents
description: When to generate additional planning documents and tracking architectural decisions
tags: [decisions, documents, conditional, architecture, tracking]
---

# Decision Tracking and Conditional Documents

## Always Generate

- IMPLEMENTATION_PHASES.md
- SESSION.md

## Generate Conditionally

| Document                 | When                                           |
| ------------------------ | ---------------------------------------------- |
| DATABASE_SCHEMA.md       | 3+ tables                                      |
| API_ENDPOINTS.md         | 5+ endpoints                                   |
| ARCHITECTURE.md          | Multiple services                              |
| UI_COMPONENTS.md         | Component library project                      |
| CRITICAL_WORKFLOWS.md    | Complex setup steps, order-sensitive workflows |
| INSTALLATION_COMMANDS.md | Recommended for all projects                   |
| ENV_VARIABLES.md         | Needs API keys or secrets                      |
| TESTING.md               | Testing strategy needs documentation           |

## Best Practices Guides

Keep best practices guides in your project folder and reference them in AGENTS.md. Have Claude Code search the web and update them to latest versions.

## Real-World Example Plan Documents

| Project                  | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| CASS Memory System       | Full plan covering system architecture and implementation phases |
| CASS GitHub Pages Export | Plan for creating a web export application                       |

## FAQ

**Q: Should I code a skeleton first?**

You get a better result faster by creating one big detailed, granular plan. That is the only way to get models to understand the entire system at once. Once you start turning it into code, it gets too big to understand.

**Q: What about problems I did not anticipate?**

Finding the flaws and fixing them is the whole point of all the iterations and blending in feedback from all the frontier models. After implementing v1, create another plan for v2.

**Q: How do I divide tasks for agents?**

Each agent uses the task board to find the next optimal task and marks it in-progress. Distributed, fungible agents.

**Q: Do agents need specialization?**

No. Every agent is fungible and a generalist. They all use the same base model and read the same AGENTS.md.

**Q: Should design decisions be in markdown or beads?**

The beads themselves can and should contain this markdown. You can have long descriptions and comments inside the beads -- they do not need to be short bullet point entries.
