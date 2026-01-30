# Skills Status Tracking

## Session Recovery

After compaction or new session, read these files to recover context:

1. **This file** — current progress, what's done, what's next
2. `skills/skills_guidelines.md` — authoring rules, validation checklist, source locations
3. `skills/tanstack-query/SKILL.md` — template to follow for restructuring

## Overview

- **Total skills**: 69 (was 68; added zod-validation and arktype-validation, deleted react-tanstack-senior)
- **Restructured** (SKILL.md + references/): 62
- **Single-file** (no references/ needed): 7
- **Validation**: All 69 skills pass, 0 warnings
- **Doc accuracy**: tanstack-start and zod-validation verified against current official docs

## Restructured Skills

| Skill                     | SKILL.md Lines | References | Status |
| ------------------------- | -------------- | ---------- | ------ |
| tanstack-query            | 102            | 13 files   | Done   |
| tanstack-table            | 92             | 10 files   | Done   |
| tanstack-start            | 102            | 10 files   | Done   |
| playwright                | 85             | 10 files   | Done   |
| agent-session-search      | 92             | 9 files    | Done   |
| prompt                    | 60             | 9 files    | Done   |
| tanstack-router           | 81             | 8 files    | Done   |
| git-workflow              | 85             | 8 files    | Done   |
| design-system             | 102            | 7 files    | Done   |
| security-audit            | 80             | 7 files    | Done   |
| accessibility             | 130            | 6 files    | Done   |
| data-visualizer           | 71             | 6 files    | Done   |
| figma-developer           | 74             | 6 files    | Done   |
| asset-manager             | 87             | 6 files    | Done   |
| tiptap                    | 97             | 6 files    | Done   |
| knowledge-base-manager    | 87             | 6 files    | Done   |
| performance-optimizer     | 92             | 6 files    | Done   |
| brand-designer            | 109            | 6 files    | Done   |
| frontend-builder          | 106            | 6 files    | Done   |
| better-auth               | 122            | 6 files    | Done   |
| security                  | 118            | 6 files    | Done   |
| motion                    | 110            | 6 files    | Done   |
| knowledge-graph-builder   | 114            | 6 files    | Done   |
| orchestration             | 93             | 6 files    | Done   |
| tanstack-integration      | 75             | 6 files    | Done   |
| remotion                  | 60             | 6 files    | Done   |
| turborepo                 | 96             | 6 files    | Done   |
| localization-engineer     | 101            | 5 files    | Done   |
| github                    | 55             | 5 files    | Done   |
| tailwind                  | 110            | 5 files    | Done   |
| usability-tester          | 105            | 5 files    | Done   |
| repo-updater              | 110            | 5 files    | Done   |
| icon-design               | 92             | 5 files    | Done   |
| agent-patterns            | 54             | 5 files    | Done   |
| chrome-devtools           | 62             | 5 files    | Done   |
| destructive-command-guard | 60             | 5 files    | Done   |
| docs                      | 54             | 5 files    | Done   |
| planning                  | 71             | 5 files    | Done   |
| rag-implementer           | 70             | 5 files    | Done   |
| react                     | 71             | 5 files    | Done   |
| responsive-images         | 81             | 5 files    | Done   |
| seo-optimizer             | 56             | 5 files    | Done   |
| zustand                   | 73             | 5 files    | Done   |
| db-enforcer               | 66             | 4 files    | Done   |
| e2e-testing               | 64             | 4 files    | Done   |
| expert-instruction        | 68             | 4 files    | Done   |
| mcp-expert                | 64             | 4 files    | Done   |
| pdf-tools                 | 54             | 4 files    | Done   |
| realtime-sync             | 56             | 4 files    | Done   |
| scrum-conductor           | 59             | 4 files    | Done   |
| secure-ai                 | 64             | 4 files    | Done   |
| arktype-validation        | 52             | 3 files    | Done   |
| hydration-guardian        | 59             | 3 files    | Done   |
| postgres-tuning           | 55             | 3 files    | Done   |
| quality-auditor           | 72             | 3 files    | Done   |
| shadcn-ui                 | 55             | 3 files    | Done   |
| threejs                   | 55             | 3 files    | Done   |
| tldr-expert               | 61             | 3 files    | Done   |
| ui-ux-polish              | 54             | 3 files    | Done   |
| utility-pro               | 54             | 3 files    | Done   |
| ux-designer               | 64             | 3 files    | Done   |
| zod-validation            | 59             | 3 files    | Done   |

## Single-File Skills (no references/ needed)

beads-viewer, beads-workflow, ci-cd, de-slopify, ghostty, skill-management, ssh-remote

## Known Decisions

Decisions made during sessions that should carry forward:

1. **SKILL.md depth**: Lean index (100-150 lines, no code) — user chose this over "working document" (200-350 lines with some code)
2. **Reference style**: Topic-scoped files (e.g., `mutations.md`) not atomic rules (e.g., `mut-optimistic-updates.md`) — Vercel uses atomic rules but our approach groups related patterns for better coherence
3. **Cross-skill content**: When content belongs to an integration skill (e.g., Form+Query → `tanstack-integration`), move it there rather than duplicating
4. **Gap-filling**: When restructuring, check `.agents/skills/[name]*/` and `.claude/skills/[name]/` for content not in the consolidated `skills/` version
5. **No code in SKILL.md**: Tables can reference API names and one-liners but no fenced code blocks
6. **Vercel reference**: Reviewed `github.com/vercel-labs/agent-skills` for structure inspiration — their SKILL.md is navigational, rules are atomic, AGENTS.md is a compiled build artifact. We took the navigational index idea but kept topic-scoped references
7. **Doc accuracy**: Skills for active libraries should be verified against current official docs (Context7 MCP). The `.agents/skills/` and `.claude/skills/` sources may contain outdated APIs
8. **Dispersal over deletion**: When removing a skill, disperse its unique content into relevant existing skills rather than deleting — compare content before merging
9. **Zod env validation**: Environment variable validation with Zod belongs in the zod-validation skill, not framework-specific skills like tanstack-start

## Consolidation History

These 69 skills were consolidated from ~124 source skills. The merges already happened — this is recorded so you don't redo them or wonder where content came from.

| Final Skill          | Merged From                                                                                                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| better-auth          | better-auth + better-auth-best-practices                                                                                                                                                                 |
| tanstack-query       | tanstack-query + tanstack-query-best-practices + tanstack-query-expert                                                                                                                                   |
| tanstack-router      | tanstack-router + tanstack-router-best-practices                                                                                                                                                         |
| tanstack-start       | tanstack-start + tanstack-start-best-practices                                                                                                                                                           |
| tanstack-integration | tanstack-integration + tanstack-integration-best-practices                                                                                                                                               |
| react                | react + react-expert + vercel-react-best-practices                                                                                                                                                       |
| zustand              | zustand-expert + zustand-state-management                                                                                                                                                                |
| tailwind             | tailwind4-expert + tailwind-v4-shadcn + tailwind-patterns + tailwind-design-system + tailwindcss-advanced-design-systems                                                                                 |
| design-system        | design-system-architect + design-system-patterns + design-system-pro + design-systems + frontend-design-system + ux-design-systems + ui-ux-pro + ui-ux-pro-max + visual-designer + web-design-guidelines |
| accessibility        | accessibility + accessibility-engineer + ui-ux-specialist                                                                                                                                                |
| security             | security-architect + security-engineer                                                                                                                                                                   |
| git-workflow         | git-automation + git-flow                                                                                                                                                                                |
| ci-cd                | github-actions-pro + deployment-advisor                                                                                                                                                                  |
| agent-patterns       | agent-fungibility + multi-agent-architect + sub-agent-patterns + subagent-orchestrator                                                                                                                   |
| motion               | motion + animation-designer                                                                                                                                                                              |
| de-slopify           | de-slopify + humanizer-pro                                                                                                                                                                               |
| docs                 | docs-pro + mermaid-diagram-pro                                                                                                                                                                           |
| turborepo            | monorepo-master + turborepo                                                                                                                                                                              |
| skill-management     | skill-creator + skill-review + skill-validator                                                                                                                                                           |
| quality-auditor      | quality-auditor + strict-auditor                                                                                                                                                                         |
| planning             | planning-workflow + project-planning + project-session-management                                                                                                                                        |
| orchestration        | orchestration-planner + framework-orchestrator                                                                                                                                                           |

Renames (no merge, just dropped suffixes): security-audit-pro → security-audit, e2e-testing-expert → e2e-testing, shadcn-ui-expert → shadcn-ui, playwright-local → playwright, threejs-expert → threejs, remotion-best-practices → remotion, seo-pro → seo-optimizer, realtime-sync-pro → realtime-sync, prompt-pro → prompt

## Pitfalls Encountered

1. **Parallel agents write to wrong paths**: When launching parallel sub-agents to write reference files, some wrote to `.claude/skills/` instead of `skills/`. Always specify the full absolute path in the agent prompt and verify output locations after.
2. **Content silently dropped during extraction**: When splitting a large file into references, sections between topic boundaries can fall through the cracks. Compare original section headers against reference file headers to catch gaps.
3. **Merge quality varies**: The original consolidation merged skills by concatenating and deduplicating, but quality is uneven. Some merged skills may have redundant sections, inconsistent voice, or content that contradicts itself. Restructuring is a good time to clean this up.
4. **`.agents/skills/` has content `skills/` doesn't**: The consolidation didn't capture everything from the source skills. Always check `.agents/skills/[name]*/` for gap-fill content (rules/, references/ subdirs) before finalizing a restructure.
5. **macOS grep lacks `-P` flag**: Use the Grep tool or `grep -oE` instead of `grep -oP` for regex extraction.
6. **Multi-line YAML tags**: Batch agents created reference files with expanded multi-line YAML tag arrays. The validator only parses single-line `tags: [a, b, c]`. Use Python `re.sub()` to collapse — shell-based perl approaches failed on macOS.
7. **Source skills may have outdated APIs**: `.agents/skills/` and `.claude/skills/` sources contained outdated TanStack Start APIs (`.validator()` instead of `.inputValidator()`, Vinxi-era file conventions, legacy deployment presets). Always verify against current docs before trusting source content.

## Changelog

- **2026-01-29**: Restructured `tanstack-query` (1670 → 102 lines + 13 references). Added Form+Query integration to `tanstack-integration`. Created `skills_guidelines.md` and `skills_status_tracking.md` for cross-session continuity.
- **2026-01-29**: Created `scripts/validate-skills.ts` validation script (lefthook pre-commit hook). Added reference file frontmatter requirements (title, tags, description). Translated Indonesian content in `skills/react-tanstack-senior/` and `.agents/skills/react-tanstack-senior/` (10 files).
- **2026-01-29**: Restructured `tanstack-table` (1498 → 92 lines + 10 references). Included v7→v8 migration guide from `.agents/skills/tanstack-table/rules/` as gap content.
- **2026-01-29**: Restructured `playwright` (1417 → 85 lines + 10 references). Integrated gap content from `.agents/skills/playwright-local/references/` (stealth techniques, selector strategies, site-specific blocking).
- **2026-01-29**: Restructured `agent-session-search` (formerly `cass`) (970 → 93 lines + 9 references). CLI tool structure organized around usage patterns: commands, robot mode, query language, search/ranking, remote sources, TUI, error handling, internals, configuration.
- **2026-01-29**: Restructured `tanstack-start` (893 → 100 lines + 9 references). Integrated gap content from `.agents/skills/tanstack-start-best-practices/rules/` (deployment adapter configs for 8 platforms, ISR/cache-control patterns, file separation conventions).
- **2026-01-29**: Restructured `data-visualizer` (862 → 69 lines + 6 references). Cleaned up informal tone. No gap content in `.agents/`.
- **2026-01-29**: Restructured `tanstack-router` (839 → 82 lines + 8 references). All agent-skills source content already consolidated.
- **2026-01-29**: Restructured `figma-developer` (769 → 74 lines + 6 references). Tutorial-style content reorganized into pattern references. No gap content in `.agents/`.
- **2026-01-29**: Restructured `asset-manager` (751 → 87 lines + 6 references). No gap content in `.agents/`.
- **2026-01-29**: Restructured `tiptap` (742 → 97 lines + 6 references). Integrated gap content from `.agents/skills/tiptap/references/` (extension catalog, common errors, docs links).
- **2026-01-29**: Restructured `knowledge-base-manager` (732 → 78 lines + 6 references). Process/methodology skill reorganized around 6-phase implementation. No gap content in `.agents/`.
- **2026-01-29**: Restructured `design-system` (731 → 85 lines + 7 references). Merged from 10 sources. Integrated gap content from `.agents/skills/design-system-pro/` (TW4 monorepo) and `.agents/skills/design-system-patterns/references/` (theming architecture, component architecture).
- **2026-01-29**: Restructured `performance-optimizer` (697 → 82 lines + 6 references). 6-phase optimization approach (profile → database → cache → frontend → backend → monitor). No gap content in `.agents/`.
- **2026-01-29**: Restructured `brand-designer` (672 → 99 lines + 6 references). Brand identity skill covering logos, colors, typography, guidelines, templates, and asset management. No gap content in `.agents/`.
- **2026-01-29**: Restructured `frontend-builder` (650 → 107 lines + 6 references). React/Next.js frontend patterns organized by concern (components, state, data, forms, styling, performance). No gap content in `.agents/`.
- **2026-01-29**: Restructured `better-auth` (650 → 112 lines + 6 references). Auth framework skill organized by adapters, sessions, plugins, config, frameworks, and troubleshooting. Gap content in `.agents/` (rules, commands) already consolidated.
- **2026-01-29**: Restructured `accessibility` (596 → 120 lines + 6 references). WCAG 2.2 AA patterns organized by semantic HTML, focus, ARIA, forms, color/media, and testing. Gap content in `.agents/` (6 reference files, 3600+ lines) already consolidated.
- **2026-01-29**: Restructured `security` (579 → 110 lines + 6 references). OWASP Top 10, STRIDE threat modeling, auth, input validation, data protection, secure config, monitoring/compliance. No gap content in `.agents/`.
- **2026-01-29**: Restructured `motion` (576 → 94 lines + 6 references). Integrated gap content from `.agents/skills/motion/` (2609 lines: naming migration framer-motion→motion, AutoAnimate comparison guide, deep Next.js integration patterns, performance optimization).
- **2026-01-29**: Restructured `knowledge-graph-builder` (558 → 98 lines + 6 references). 6-phase KG implementation (ontology → database → extraction → hybrid → queries → AI integration). No gap content in `.agents/`.
- **2026-01-29**: Restructured `localization-engineer` (549 → 85 lines + 5 references). next-intl i18n skill organized by setup, translations, formatting, UI patterns, SEO/management. No gap content in `.agents/`.
- **2026-01-29**: Restructured `github` (546 → 39 lines + 5 references). CLI command reference organized by repos/auth, issues, pull requests, actions, releases/more. No gap content in `.agents/`.
- **2026-01-29**: Restructured `tailwind` (544 → 91 lines + 5 references). Tailwind v4 CSS-first config, design tokens, shadcn/ui integration, component patterns, troubleshooting. All `.agents/` source content already consolidated.
- **2026-01-29**: Restructured `usability-tester` (518 → 89 lines + 5 references). UX testing methodology organized by test planning, conducting tests, metrics/severity, reporting, remote testing/tools. No gap content in `.agents/`.
- **2026-01-29**: Restructured `repo-updater` (formerly `ru`) (509 → 94 lines + 5 references). Bash CLI for multi-repo sync organized by commands, review system, agent sweep, configuration, troubleshooting. No gap content in `.agents/`.
- **2026-01-29**: All 25 skills over 500 lines restructured. 0 remaining.
- **2026-01-29**: Renamed abbreviated skills for Vercel skills CLI discoverability: `bv` → `beads-viewer`, `cass` → `agent-session-search`, `dcg` → `destructive-command-guard`, `ru` → `repo-updater`. Added min name length (4 chars) and CLI-excluded filename validation to `scripts/validate-skills.ts`. Updated CLAUDE.md with full skill standards and distribution info.
- **2026-01-29**: Quality audit of all 68 skills. Fixed 24 validator failures: 16 name-field mismatches, 4 directory renames (`pdf` → `pdf-tools`, `seo` → `seo-optimizer`, `ssh` → `ssh-remote`, `claude-chrome` → `chrome-devtools`), 2 missing YAML frontmatter (tailwind, zustand), 2 content fixes (planning 4-backtick fence, react-tanstack-senior broken reference links). Added trigger phrases to 42 skills, `## Common Mistakes` tables to 55 skills, `## Delegation` sections to 47 skills. Warnings reduced from 243 to 97. All 68 skills pass validation.
- **2026-01-30**: Tier 1 enhancement — 26 single-file skills restructured into lean SKILL.md + references using content from `.agents/skills/` and `.claude/skills/` sources. Fixed 129 reference files with multi-line YAML tags collapsed to single-line.
- **2026-01-30**: Dispersed `react-tanstack-senior` into relevant skills (tanstack-integration, tanstack-start, react). Deleted skill entirely after comparing all source and destination content. 4 refs had no unique content, 2 merged, 2 created as new refs, 1 distributed. 68 → 67 skills.
- **2026-01-30**: TanStack Start doc accuracy review. Verified all 9 references against current official docs via Context7 MCP. Fixed `.validator()` → `.inputValidator()` (10 occurrences across 4 files). Rewrote api-routes.md (createFileRoute + server.handlers) and deployment.md (Vite plugins). Updated middleware.md, route-protection.md, ssr-and-streaming.md, known-issues.md. Removed time-sensitive version references and non-standard `id` frontmatter field.
- **2026-01-30**: Added missing tanstack-start content: entry points (client.tsx, server.ts, start.ts), plugin configuration (tanstackStart options), plugin ordering gotcha, SEO/head management (new references/seo.md). Added login/logout server function patterns to route-protection.md. tanstack-start now has 10 references.
- **2026-01-30**: Created `zod-validation` skill (59 lines + 3 references) from `.claude/skills/zod` source. Verified against Zod v4 docs. Added missing features: template literal types, number formats (z.int, z.float32, z.int32), z.pipe(), z.cidrv4/v6, z.base64url, v4 behavior changes (.safe() = .int(), no Infinity). Added branded types, recursive schemas, error formatting, schema composition patterns.
- **2026-01-30**: Created `arktype-validation` skill (52 lines + 3 references) from ArkType docs via Context7. Covers string syntax schemas, string keywords, morphs/transforms (pipe, to, narrow), scopes with recursive types, generics, and Zod comparison table. 69 total skills.
