# Skills Audit & Enrichment Status

Epic: `agent-skills-p37`
Plan: `.claude/plans/splendid-sparking-dragonfly.md`

## Progress

| Phase | Task ID            | Description                      | Skills | Status  | Notes                                |
| ----- | ------------------ | -------------------------------- | ------ | ------- | ------------------------------------ |
| 0     | `agent-skills-191` | Fix existing validation warnings | --     | done    | Already clean — 0 errors, 0 warnings |
| 1     | `agent-skills-d3i` | TanStack Ecosystem               | 6      | done    | All 6 skills enriched, validated     |
| 2     | `agent-skills-2rd` | React & Frontend Core            | 8      | pending | blocked by Phase 0                   |
| 3     | `agent-skills-31d` | Testing & Quality                | 5      | pending | blocked by Phase 0                   |
| 4     | `agent-skills-cm4` | Security & Auth                  | 5      | pending | blocked by Phase 0                   |
| 5     | `agent-skills-6rv` | DevOps, Git & Infra              | 8      | pending | blocked by Phase 0                   |
| 6     | `agent-skills-ays` | AI, Agents & Orchestration       | 8      | pending | blocked by Phase 0                   |
| 7     | `agent-skills-5f4` | UX, Design & Visualization       | 9      | pending | blocked by Phase 0                   |
| 8     | `agent-skills-r6d` | Content, Tools & Specialized     | 10     | pending | blocked by Phase 0                   |
| 9     | `agent-skills-jxc` | Remaining                        | 10     | pending | blocked by Phase 0                   |
| 10    | `agent-skills-5z4` | New skills recommendations       | --     | pending | blocked by Batches 1-9               |
| 11    | `agent-skills-7h2` | Final validation pass            | --     | pending | blocked by Phase 10                  |

**Total skills: 69** | **Completed: 6/69** | **Phases done: 2/12**

## Dependency Chain

```text
Phase 0 (fix warnings)
  |
  +---> Batches 1-9 (can run in parallel after Phase 0)
  |       |
  |       +---> Phase 10 (recommendations, after all batches)
  |               |
  |               +---> Phase 11 (final validation)
  |
  +---> Epic closes when Phase 11 completes
```

## Per-Skill Tracker

### Batch 1: TanStack Ecosystem (Phase 1)

| Skill                | Sources Read | Docs Validated | Enriched | Validated |
| -------------------- | ------------ | -------------- | -------- | --------- |
| tanstack-query       | done         | done           | done     | done      |
| tanstack-router      | done         | done           | done     | done      |
| tanstack-start       | done         | done           | done     | done      |
| tanstack-table       | done         | done           | done     | done      |
| tanstack-integration | done         | done           | done     | done      |
| zod-validation       | done         | done           | done     | done      |

### Batch 2: React & Frontend Core (Phase 2)

| Skill              | Sources Read | Docs Validated | Enriched | Validated |
| ------------------ | ------------ | -------------- | -------- | --------- |
| react              |              |                |          |           |
| shadcn-ui          |              |                |          |           |
| tailwind           |              |                |          |           |
| design-system      |              |                |          |           |
| zustand            |              |                |          |           |
| motion             |              |                |          |           |
| frontend-builder   |              |                |          |           |
| hydration-guardian |              |                |          |           |

### Batch 3: Testing & Quality (Phase 3)

| Skill            | Sources Read | Docs Validated | Enriched | Validated |
| ---------------- | ------------ | -------------- | -------- | --------- |
| playwright       |              |                |          |           |
| e2e-testing      |              |                |          |           |
| quality-auditor  |              |                |          |           |
| usability-tester |              |                |          |           |
| de-slopify       |              |                |          |           |

### Batch 4: Security & Auth (Phase 4)

| Skill                     | Sources Read | Docs Validated | Enriched | Validated |
| ------------------------- | ------------ | -------------- | -------- | --------- |
| better-auth               |              |                |          |           |
| security                  |              |                |          |           |
| security-audit            |              |                |          |           |
| secure-ai                 |              |                |          |           |
| destructive-command-guard |              |                |          |           |

### Batch 5: DevOps, Git & Infra (Phase 5)

| Skill           | Sources Read | Docs Validated | Enriched | Validated |
| --------------- | ------------ | -------------- | -------- | --------- |
| git-workflow    |              |                |          |           |
| github          |              |                |          |           |
| ci-cd           |              |                |          |           |
| turborepo       |              |                |          |           |
| ssh-remote      |              |                |          |           |
| postgres-tuning |              |                |          |           |
| db-enforcer     |              |                |          |           |
| repo-updater    |              |                |          |           |

### Batch 6: AI, Agents & Orchestration (Phase 6)

| Skill                | Sources Read | Docs Validated | Enriched | Validated |
| -------------------- | ------------ | -------------- | -------- | --------- |
| agent-patterns       |              |                |          |           |
| agent-session-search |              |                |          |           |
| orchestration        |              |                |          |           |
| planning             |              |                |          |           |
| mcp-expert           |              |                |          |           |
| rag-implementer      |              |                |          |           |
| prompt               |              |                |          |           |
| skill-management     |              |                |          |           |

### Batch 7: UX, Design & Visualization (Phase 7)

| Skill             | Sources Read | Docs Validated | Enriched | Validated |
| ----------------- | ------------ | -------------- | -------- | --------- |
| ux-designer       |              |                |          |           |
| ui-ux-polish      |              |                |          |           |
| brand-designer    |              |                |          |           |
| icon-design       |              |                |          |           |
| data-visualizer   |              |                |          |           |
| figma-developer   |              |                |          |           |
| responsive-images |              |                |          |           |
| threejs           |              |                |          |           |
| accessibility     |              |                |          |           |

### Batch 8: Content, Tools & Specialized (Phase 8)

| Skill                 | Sources Read | Docs Validated | Enriched | Validated |
| --------------------- | ------------ | -------------- | -------- | --------- |
| tiptap                |              |                |          |           |
| remotion              |              |                |          |           |
| chrome-devtools       |              |                |          |           |
| pdf-tools             |              |                |          |           |
| docs                  |              |                |          |           |
| tldr-expert           |              |                |          |           |
| seo-optimizer         |              |                |          |           |
| performance-optimizer |              |                |          |           |
| localization-engineer |              |                |          |           |
| scrum-conductor       |              |                |          |           |

### Batch 9: Remaining (Phase 9)

| Skill                   | Sources Read | Docs Validated | Enriched | Validated |
| ----------------------- | ------------ | -------------- | -------- | --------- |
| realtime-sync           |              |                |          |           |
| ghostty                 |              |                |          |           |
| arktype-validation      |              |                |          |           |
| asset-manager           |              |                |          |           |
| knowledge-base-manager  |              |                |          |           |
| knowledge-graph-builder |              |                |          |           |
| beads-viewer            |              |                |          |           |
| beads-workflow          |              |                |          |           |
| utility-pro             |              |                |          |           |
| expert-instruction      |              |                |          |           |

## Changelog

| Date       | Phase | Action                                                   |
| ---------- | ----- | -------------------------------------------------------- |
| 2026-01-30 | setup | Created beads issues and status tracker                  |
| 2026-01-30 | 0     | Phase 0 complete — all skills already passing validation |
| 2026-01-30 | 1     | Batch 1 complete — 6 TanStack + zod skills enriched      |
