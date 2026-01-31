# agent-skills

A curated collection of 69 [agent skills](https://agentskills.io) for Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code, GitHub Copilot, Windsurf, Goose, and [27+ other agents](https://agentskills.io). Each skill is hand-written and enriched against official documentation — not auto-generated from docs.

## Install

```sh
# Browse and select skills interactively
pnpm dlx skills add oakoss/agent-skills

# Install all skills
pnpm dlx skills add oakoss/agent-skills --all

# Install specific skills
pnpm dlx skills add oakoss/agent-skills -s react tanstack-query shadcn-ui

# Install to a specific agent
pnpm dlx skills add oakoss/agent-skills -a claude-code

# Install globally (user-level)
pnpm dlx skills add oakoss/agent-skills -g

# Preview available skills
pnpm dlx skills add oakoss/agent-skills --list
```

## Skills

### TanStack Ecosystem

| Skill                                               | Description                                                              |
| --------------------------------------------------- | ------------------------------------------------------------------------ |
| [tanstack-query](skills/tanstack-query)             | TanStack Query v5 server state management for React                      |
| [tanstack-router](skills/tanstack-router)           | Type-safe, file-based React routing with route loaders and search params |
| [tanstack-start](skills/tanstack-start)             | Full-stack React framework built on TanStack Router                      |
| [tanstack-table](skills/tanstack-table)             | TanStack Table v8 headless data tables for React                         |
| [tanstack-integration](skills/tanstack-integration) | Strategic adoption guide for TanStack libraries                          |

### React & Frontend

| Skill                                           | Description                                                          |
| ----------------------------------------------- | -------------------------------------------------------------------- |
| [react](skills/react)                           | React 19+ patterns, performance optimization, component architecture |
| [shadcn-ui](skills/shadcn-ui)                   | Accessible component libraries with shadcn/ui, Radix UI, Tailwind    |
| [tailwind](skills/tailwind)                     | Tailwind CSS v4 patterns and design systems                          |
| [zustand](skills/zustand)                       | Zustand v5 state management for React                                |
| [motion](skills/motion)                         | Web animations with Motion (Framer Motion) for React                 |
| [design-system](skills/design-system)           | Design tokens, theming, and component architecture                   |
| [frontend-builder](skills/frontend-builder)     | React and Next.js frontend development                               |
| [hydration-guardian](skills/hydration-guardian) | React/Next.js hydration mismatch debugging                           |
| [tiptap](skills/tiptap)                         | Rich text editors with Tiptap and ProseMirror                        |
| [threejs](skills/threejs)                       | 3D web experiences with Three.js, WebGPU, React Three Fiber          |
| [remotion](skills/remotion)                     | Programmatic video creation in React with Remotion                   |

### Validation & Schemas

| Skill                                           | Description                                              |
| ----------------------------------------------- | -------------------------------------------------------- |
| [zod-validation](skills/zod-validation)         | Zod v4 schema validation for TypeScript                  |
| [arktype-validation](skills/arktype-validation) | ArkType runtime validation with TypeScript-native syntax |

### Testing & Quality

| Skill                                       | Description                                              |
| ------------------------------------------- | -------------------------------------------------------- |
| [playwright](skills/playwright)             | Playwright browser automation, E2E testing, web scraping |
| [e2e-testing](skills/e2e-testing)           | End-to-end test suites with Playwright                   |
| [quality-auditor](skills/quality-auditor)   | Code quality gatekeeper and auditor                      |
| [usability-tester](skills/usability-tester) | Usability testing and UX issue identification            |
| [de-slopify](skills/de-slopify)             | Remove AI writing artifacts from documentation and code  |

### Security & Auth

| Skill                                                         | Description                                                       |
| ------------------------------------------------------------- | ----------------------------------------------------------------- |
| [better-auth](skills/better-auth)                             | Self-hosted TypeScript auth with social auth, 2FA, passkeys, RBAC |
| [security](skills/security)                                   | Application security, STRIDE threat modeling, OWASP Top 10        |
| [security-audit](skills/security-audit)                       | Row Level Security enforcement and zero-trust database access     |
| [secure-ai](skills/secure-ai)                                 | AI security, prompt injection defense, data leakage prevention    |
| [destructive-command-guard](skills/destructive-command-guard) | Rust hook that blocks dangerous commands before execution         |

### DevOps, Git & Infrastructure

| Skill                                     | Description                                                    |
| ----------------------------------------- | -------------------------------------------------------------- |
| [git-workflow](skills/git-workflow)       | Branching strategies, trunk-based development, stacked changes |
| [github](skills/github)                   | GitHub CLI for repos, issues, PRs, actions, releases           |
| [ci-cd](skills/ci-cd)                     | CI/CD pipelines, GitHub Actions, deployment strategies         |
| [turborepo](skills/turborepo)             | Monorepo build system, task pipelines, caching                 |
| [ssh-remote](skills/ssh-remote)           | SSH remote access, key management, tunnels, transfers          |
| [postgres-tuning](skills/postgres-tuning) | PostgreSQL 17/18+ performance tuning and optimization          |
| [db-enforcer](skills/db-enforcer)         | PostgreSQL and Prisma database integrity enforcement           |
| [repo-updater](skills/repo-updater)       | Multi-repo synchronization with AI-assisted review             |

### AI, Agents & Orchestration

| Skill                                               | Description                                                   |
| --------------------------------------------------- | ------------------------------------------------------------- |
| [agent-patterns](skills/agent-patterns)             | Multi-agent design patterns, delegation, orchestration        |
| [agent-session-search](skills/agent-session-search) | Index and search local coding agent history across 11+ agents |
| [orchestration](skills/orchestration)               | Coordinate skills and frameworks across project lifecycle     |
| [planning](skills/planning)                         | Planning methodology and session management                   |
| [mcp-expert](skills/mcp-expert)                     | MCP server development and multi-agent tooling                |
| [rag-implementer](skills/rag-implementer)           | Retrieval-augmented generation systems                        |
| [prompt](skills/prompt)                             | Prompt engineering and agentic orchestration patterns         |
| [skill-management](skills/skill-management)         | Create, audit, and validate agent skills                      |

### UX, Design & Visualization

| Skill                                         | Description                                               |
| --------------------------------------------- | --------------------------------------------------------- |
| [ux-designer](skills/ux-designer)             | User journeys, wireframes, prototypes                     |
| [ui-ux-polish](skills/ui-ux-polish)           | Iterative UI/UX polishing workflow                        |
| [brand-designer](skills/brand-designer)       | Brand identity, logos, color palettes, typography systems |
| [icon-design](skills/icon-design)             | Semantic icon selection with Lucide, Heroicons, Phosphor  |
| [data-visualizer](skills/data-visualizer)     | Charts and dashboards with Recharts, Chart.js, D3.js      |
| [figma-developer](skills/figma-developer)     | Convert Figma designs to React components via REST API    |
| [responsive-images](skills/responsive-images) | srcset, sizes, lazy loading, WebP/AVIF                    |
| [accessibility](skills/accessibility)         | WCAG 2.2 AA, semantic HTML, ARIA, keyboard navigation     |

### Content, SEO & Documentation

| Skill                                                 | Description                                            |
| ----------------------------------------------------- | ------------------------------------------------------ |
| [docs](skills/docs)                                   | Technical documentation writing and diagram generation |
| [seo-optimizer](skills/seo-optimizer)                 | SEO architecture and content strategy                  |
| [localization-engineer](skills/localization-engineer) | Internationalization (i18n) and localization (l10n)    |
| [pdf-tools](skills/pdf-tools)                         | PDF extraction, generation, modification, form filling |
| [tldr-expert](skills/tldr-expert)                     | Semantic code intelligence and token optimization      |

### Performance & Optimization

| Skill                                                 | Description                                              |
| ----------------------------------------------------- | -------------------------------------------------------- |
| [performance-optimizer](skills/performance-optimizer) | Application performance and scalability optimization     |
| [chrome-devtools](skills/chrome-devtools)             | Browser automation via Chrome extension and DevTools MCP |

### Workflow & Project Management

| Skill                                           | Description                                           |
| ----------------------------------------------- | ----------------------------------------------------- |
| [scrum-conductor](skills/scrum-conductor)       | AI-enhanced Scrum ceremonies and sprint coordination  |
| [expert-instruction](skills/expert-instruction) | Behavioral standards for senior AI engineering agents |
| [beads-viewer](skills/beads-viewer)             | Graph-aware triage engine for Beads projects          |
| [beads-workflow](skills/beads-workflow)         | Convert plans into tasks with dependencies            |

### Specialized Tools

| Skill                                                     | Description                                                       |
| --------------------------------------------------------- | ----------------------------------------------------------------- |
| [ghostty](skills/ghostty)                                 | Ghostty terminal emulator CLI control and configuration           |
| [realtime-sync](skills/realtime-sync)                     | WebTransport, real-time sync, CRDTs, AI stream orchestration      |
| [knowledge-base-manager](skills/knowledge-base-manager)   | RAG and graph knowledge base design                               |
| [knowledge-graph-builder](skills/knowledge-graph-builder) | Knowledge graph modeling and semantic search                      |
| [asset-manager](skills/asset-manager)                     | Design asset organization, image/font optimization                |
| [utility-pro](skills/utility-pro)                         | Advanced CLI operations and Unix forensics with modern Rust tools |

## Contributing

Each skill lives in `skills/[skill-name]/` and follows the [Agent Skills open standard](https://agentskills.io). See [AGENTS.md](AGENTS.md) for authoring guidelines.

```sh
# Validate a skill
pnpm validate:skills skills/[skill-name]

# Validate all skills
pnpm validate:skills
```

## License

MIT
