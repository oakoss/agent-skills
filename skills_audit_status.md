# Skills Audit & Enrichment Status

Epic: `agent-skills-p37`
Plan: `.claude/plans/splendid-sparking-dragonfly.md`

## Progress

| Phase | Task ID            | Description                      | Skills | Status  | Notes                                |
| ----- | ------------------ | -------------------------------- | ------ | ------- | ------------------------------------ |
| 0     | `agent-skills-191` | Fix existing validation warnings | --     | done    | Already clean — 0 errors, 0 warnings |
| 1     | `agent-skills-d3i` | TanStack Ecosystem               | 6      | done    | All 6 skills enriched, validated     |
| 2     | `agent-skills-2rd` | React & Frontend Core            | 8      | done    | All 8 skills enriched, validated     |
| 3     | `agent-skills-31d` | Testing & Quality                | 5      | done    | All 5 skills enriched, validated     |
| 4     | `agent-skills-cm4` | Security & Auth                  | 5      | done    | All 5 skills enriched, validated     |
| 5     | `agent-skills-6rv` | DevOps, Git & Infra              | 8      | done    | All 8 skills enriched, validated     |
| 6     | `agent-skills-ays` | AI, Agents & Orchestration       | 8      | done    | All 8 skills enriched, validated     |
| 7     | `agent-skills-5f4` | UX, Design & Visualization       | 9      | done    | All 9 skills enriched, validated     |
| 8     | `agent-skills-r6d` | Content, Tools & Specialized     | 10     | done    | All 10 skills enriched, validated    |
| 9     | `agent-skills-jxc` | Remaining                        | 10     | done    | All 10 skills enriched, validated    |
| 10    | `agent-skills-5z4` | New skills recommendations       | --     | done    | 14 skills recommended across 3 tiers |
| 11    | `agent-skills-7h2` | Final validation pass            | --     | pending | blocked by Phase 10                  |

**Total skills: 69** | **Completed: 69/69** | **Phases done: 11/12**

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
| react              | done         | done           | done     | done      |
| shadcn-ui          | done         | done           | done     | done      |
| tailwind           | done         | done           | done     | done      |
| design-system      | done         | done           | done     | done      |
| zustand            | done         | done           | done     | done      |
| motion             | done         | done           | done     | done      |
| frontend-builder   | done         | done           | done     | done      |
| hydration-guardian | done         | done           | done     | done      |

### Batch 3: Testing & Quality (Phase 3)

| Skill            | Sources Read | Docs Validated | Enriched | Validated |
| ---------------- | ------------ | -------------- | -------- | --------- |
| playwright       | done         | done           | done     | done      |
| e2e-testing      | done         | done           | done     | done      |
| quality-auditor  | done         | done           | done     | done      |
| usability-tester | done         | done           | done     | done      |
| de-slopify       | done         | done           | done     | done      |

### Batch 4: Security & Auth (Phase 4)

| Skill                     | Sources Read | Docs Validated | Enriched | Validated |
| ------------------------- | ------------ | -------------- | -------- | --------- |
| better-auth               | done         | done           | done     | done      |
| security                  | done         | done           | done     | done      |
| security-audit            | done         | done           | done     | done      |
| secure-ai                 | done         | done           | done     | done      |
| destructive-command-guard | done         | done           | done     | done      |

### Batch 5: DevOps, Git & Infra (Phase 5)

| Skill           | Sources Read | Docs Validated | Enriched | Validated |
| --------------- | ------------ | -------------- | -------- | --------- |
| git-workflow    | done         | done           | done     | done      |
| github          | done         | done           | done     | done      |
| ci-cd           | done         | done           | done     | done      |
| turborepo       | done         | done           | done     | done      |
| ssh-remote      | done         | done           | done     | done      |
| postgres-tuning | done         | done           | done     | done      |
| db-enforcer     | done         | done           | done     | done      |
| repo-updater    | done         | done           | done     | done      |

### Batch 6: AI, Agents & Orchestration (Phase 6)

| Skill                | Sources Read | Docs Validated | Enriched | Validated |
| -------------------- | ------------ | -------------- | -------- | --------- |
| agent-patterns       | done         | done           | done     | done      |
| agent-session-search | done         | done           | done     | done      |
| orchestration        | done         | done           | done     | done      |
| planning             | done         | done           | done     | done      |
| mcp-expert           | done         | done           | done     | done      |
| rag-implementer      | done         | done           | done     | done      |
| prompt               | done         | done           | done     | done      |
| skill-management     | done         | done           | done     | done      |

### Batch 7: UX, Design & Visualization (Phase 7)

| Skill             | Sources Read | Docs Validated | Enriched | Validated |
| ----------------- | ------------ | -------------- | -------- | --------- |
| ux-designer       | done         | done           | done     | done      |
| ui-ux-polish      | done         | done           | done     | done      |
| brand-designer    | done         | done           | done     | done      |
| icon-design       | done         | done           | done     | done      |
| data-visualizer   | done         | done           | done     | done      |
| figma-developer   | done         | done           | done     | done      |
| responsive-images | done         | done           | done     | done      |
| threejs           | done         | done           | done     | done      |
| accessibility     | done         | done           | done     | done      |

### Batch 8: Content, Tools & Specialized (Phase 8)

| Skill                 | Sources Read | Docs Validated | Enriched | Validated |
| --------------------- | ------------ | -------------- | -------- | --------- |
| tiptap                | done         | done           | done     | done      |
| remotion              | done         | done           | done     | done      |
| chrome-devtools       | done         | done           | done     | done      |
| pdf-tools             | done         | done           | done     | done      |
| docs                  | done         | done           | done     | done      |
| tldr-expert           | done         | done           | done     | done      |
| seo-optimizer         | done         | done           | done     | done      |
| performance-optimizer | done         | done           | done     | done      |
| localization-engineer | done         | done           | done     | done      |
| scrum-conductor       | done         | done           | done     | done      |

### Batch 9: Remaining (Phase 9)

| Skill                   | Sources Read | Docs Validated | Enriched | Validated |
| ----------------------- | ------------ | -------------- | -------- | --------- |
| realtime-sync           | done         | done           | done     | done      |
| ghostty                 | done         | done           | done     | done      |
| arktype-validation      | done         | done           | done     | done      |
| asset-manager           | done         | done           | done     | done      |
| knowledge-base-manager  | done         | done           | done     | done      |
| knowledge-graph-builder | done         | done           | done     | done      |
| beads-viewer            | done         | done           | done     | done      |
| beads-workflow          | done         | done           | done     | done      |
| utility-pro             | done         | done           | done     | done      |
| expert-instruction      | done         | done           | done     | done      |

## New Skills Recommendations

Based on gaps discovered during the enrichment of all 69 skills, cross-referencing delegation sections, `.claude/skills/`, `.agents/skills/`, and the [skills.sh](https://skills.sh) ecosystem for naming conventions.

**Naming convention**: Ecosystem skills use specific, descriptive names — `vitest-testing`, `drizzle-orm`, `storybook-stories`, `stripe-integration` — not generic terms like `testing` or `database`. Names should identify the tool/library or the specific pattern.

### Tier 1: High Priority (Source material exists in `.claude/skills/`)

These have existing installed skill sources and fill critical catalog gaps.

| #   | Skill Name                  | Description                                           | Source                            | Rationale                                                                                                                       |
| --- | --------------------------- | ----------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `tanstack-form`             | TanStack Form + React Aria Components                 | `.claude/skills/tanstack-form`    | Completes TanStack ecosystem (query, router, start, table all exist). Referenced by frontend-builder, shadcn-ui, zod-validation |
| 2   | `typescript-patterns`       | Advanced generics, type guards, utility types         | `.claude/skills/typescript`       | Foundation skill — referenced across nearly every skill. Covers strict mode, discriminated unions, inference                    |
| 3   | `react-error-handling`      | Error boundaries, fallback UIs, recovery patterns     | `.claude/skills/error-boundaries` | Referenced by react, frontend-builder, tanstack-router. Covers ErrorBoundary, errorComponent, reset                             |
| 4   | `storybook-stories`         | Stories, interaction tests, play functions, Chromatic | `.claude/skills/storybook`        | Referenced by design-system. Component documentation, visual testing, a11y addon                                                |
| 5   | `drizzle-orm`               | Drizzle ORM schemas, queries, migrations              | `.claude/skills/database`         | Fills gap between db-enforcer (integrity rules) and postgres-tuning (performance). Schema design, relations, migrations         |
| 6   | `tanstack-server-functions` | createServerFn, validators, middleware chains         | `.claude/skills/server-functions` | Complements tanstack-start. RPC-style server functions with type safety                                                         |
| 7   | `vitest-testing`            | Vitest + Testing Library patterns                     | `.claude/skills/testing`          | Fills unit/component testing gap (playwright and e2e-testing cover integration/E2E only)                                        |

### Tier 2: Medium Priority (Source material exists in `.agents/skills/`)

Additional sources available but need more curation.

| #   | Skill Name               | Description                                             | Source                              | Rationale                                                                               |
| --- | ------------------------ | ------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------- |
| 8   | `css-animation-patterns` | CSS animations, keyframes, AutoAnimate, reduced motion  | `.agents/skills/animation-designer` | Broader than motion skill (which is Framer Motion specific). General animation patterns |
| 9   | `github-actions`         | Workflow design, matrix testing, reusable workflows     | `.agents/skills/github-actions-pro` | ci-cd covers general CI/CD but GitHub Actions has enough depth for a dedicated skill    |
| 10  | `vercel-deployment`      | Vercel deployment, edge functions, preview environments | `.agents/skills/deployment-advisor` | No dedicated deployment skill exists. Referenced in ci-cd and turborepo contexts        |

### Tier 3: Lower Priority (No source material, gap-driven)

Identified purely from cross-reference analysis.

| #   | Skill Name           | Description                                              | Rationale                                                                                                    |
| --- | -------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 11  | `nextjs-app-router`  | Next.js App Router, middleware, Server Actions, metadata | Referenced in frontend-builder, motion, ci-cd. Major framework with no dedicated skill                       |
| 12  | `pnpm-workspace`     | pnpm workspace patterns, shared configs, dependency mgmt | Turborepo skill is build-tool-specific. General workspace architecture patterns                              |
| 13  | `react-email`        | React Email + Resend, transactional email templates      | Referenced in better-auth (email OTP). Resend has official skills; we can cover the React Email side         |
| 14  | `stripe-integration` | Stripe Checkout, subscriptions, webhook handling         | Referenced in better-auth (Stripe plugin). Stripe has official skills; ours would cover integration patterns |

### Summary

| Tier      | Count  | Source Material                    | Action                                                          |
| --------- | ------ | ---------------------------------- | --------------------------------------------------------------- |
| 1         | 7      | `.claude/skills/` (ready)          | Create skills using existing sources + official docs validation |
| 2         | 3      | `.agents/skills/` (needs curation) | Create skills with heavier doc validation                       |
| 3         | 4      | None (gap-driven)                  | Create from scratch using official docs                         |
| **Total** | **14** |                                    |                                                                 |

### Notes

- **zod** — Already covered by `zod-validation`. No new skill needed.
- **integration-patterns** — Already covered by `tanstack-integration`. No new skill needed.
- **meta-\*** skills (meta-skill-creator, meta-agent-creator, etc.) — These are tooling/internal skills, not candidates for public distribution.
- Tier 1 skills have the highest ROI: source material already exists and they fill gaps referenced by multiple existing skills.
- **Naming review**: Names follow ecosystem conventions observed on [skills.sh](https://skills.sh) — tool-specific (`drizzle-orm`, `vitest-testing`) or pattern-specific (`typescript-patterns`, `react-error-handling`) rather than generic categories.

## Changelog

| Date       | Phase | Action                                                      |
| ---------- | ----- | ----------------------------------------------------------- |
| 2026-01-30 | setup | Created beads issues and status tracker                     |
| 2026-01-30 | 0     | Phase 0 complete — all skills already passing validation    |
| 2026-01-30 | 1     | Batch 1 complete — 6 TanStack + zod skills enriched         |
| 2026-01-30 | 2     | Batch 2 complete — 8 React & Frontend Core skills enriched  |
| 2026-01-30 | 3     | Batch 3 complete — 5 Testing & Quality skills enriched      |
| 2026-01-30 | 4     | Batch 4 complete — 5 Security & Auth skills enriched        |
| 2026-01-30 | 5     | Batch 5 complete — 8 DevOps, Git & Infra skills enriched    |
| 2026-01-30 | 6     | Batch 6 complete — 8 AI, Agents & Orchestration enriched    |
| 2026-01-30 | 7     | Batch 7 complete — 9 UX, Design & Visualization enriched    |
| 2026-01-31 | 8     | Batch 8 complete — 10 Content, Tools & Specialized enriched |
| 2026-01-31 | 9     | Batch 9 complete — 10 Remaining skills enriched             |
| 2026-01-31 | 10    | Phase 10 complete — 14 new skills recommended (7/3/4 tiers) |
