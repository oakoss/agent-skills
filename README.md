# agent-skills

Agent skills following the [Agent Skills open standard](https://agentskills.io) for Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code, GitHub Copilot, Windsurf, and [27+ other agents](https://agentskills.io). Installed via Vercel's [skills CLI](https://github.com/vercel-labs/skills).

## Install

```sh
# Browse and select skills interactively
pnpm dlx skills add oakoss/agent-skills

# Install all skills to all agents
pnpm dlx skills add oakoss/agent-skills --all

# Install specific skills
pnpm dlx skills add oakoss/agent-skills -s react tanstack-query

# Install to a specific agent
pnpm dlx skills add oakoss/agent-skills -a claude-code

# Install globally (user-level)
pnpm dlx skills add oakoss/agent-skills -g

# Preview available skills without installing
pnpm dlx skills add oakoss/agent-skills --list
```

## Skills

| Skill                                                         | Description                                                             |
| ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [accessibility](skills/accessibility)                         | WCAG 2.2 AA, semantic HTML, ARIA, keyboard navigation, focus management |
| [agent-patterns](skills/agent-patterns)                       | Multi-agent design patterns, delegation, orchestration                  |
| [agent-session-search](skills/agent-session-search)           | Index and search local coding agent history across 11+ agents           |
| [asset-manager](skills/asset-manager)                         | Design asset organization, image/font optimization, version control     |
| [beads-viewer](skills/beads-viewer)                           | Graph-aware triage engine for Beads projects                            |
| [beads-workflow](skills/beads-workflow)                       | Convert plans into tasks with dependencies                              |
| [better-auth](skills/better-auth)                             | Self-hosted TypeScript auth with social auth, 2FA, passkeys, RBAC       |
| [brand-designer](skills/brand-designer)                       | Brand identity, logo design, visual brand systems                       |
| [ci-cd](skills/ci-cd)                                         | CI/CD pipelines, GitHub Actions, deployment strategies                  |
| [claude-chrome](skills/claude-chrome)                         | Browser automation via the Anthropic Chrome extension                   |
| [data-visualizer](skills/data-visualizer)                     | Charts and dashboards with Recharts, Chart.js, D3.js                    |
| [db-enforcer](skills/db-enforcer)                             | PostgreSQL and Prisma database integrity                                |
| [de-slopify](skills/de-slopify)                               | Remove AI writing artifacts from documentation                          |
| [design-system](skills/design-system)                         | Design tokens, theming, component architecture                          |
| [destructive-command-guard](skills/destructive-command-guard) | Rust hook that blocks dangerous commands before execution               |
| [docs](skills/docs)                                           | Technical writing, docs-as-code, Mermaid diagrams                       |
| [e2e-testing](skills/e2e-testing)                             | Playwright orchestration, visual regression, CI sharding                |
| [expert-instruction](skills/expert-instruction)               | Instruction protocol for senior engineering agents                      |
| [figma-developer](skills/figma-developer)                     | Convert Figma designs to React components, sync design tokens           |
| [frontend-builder](skills/frontend-builder)                   | React/Next.js frontend development                                      |
| [ghostty](skills/ghostty)                                     | Ghostty terminal emulator CLI control                                   |
| [git-workflow](skills/git-workflow)                           | Branching strategies, trunk-based development, stacked changes          |
| [github](skills/github)                                       | GitHub CLI for repos, issues, PRs, actions, releases                    |
| [hydration-guardian](skills/hydration-guardian)               | React/Next.js hydration mismatch debugging                              |
| [icon-design](skills/icon-design)                             | Semantic icon selection with Lucide, Heroicons, Phosphor                |
| [knowledge-base-manager](skills/knowledge-base-manager)       | RAG and graph knowledge base design                                     |
| [knowledge-graph-builder](skills/knowledge-graph-builder)     | Knowledge graph modeling and semantic search                            |
| [localization-engineer](skills/localization-engineer)         | i18n, multi-language support, localization                              |
| [mcp-expert](skills/mcp-expert)                               | MCP server development and multi-agent tooling                          |
| [motion](skills/motion)                                       | Framer Motion / CSS animations, gestures, scroll effects                |
| [orchestration](skills/orchestration)                         | Coordinate skills and frameworks across project lifecycle               |
| [pdf](skills/pdf)                                             | PDF extraction, generation, and security                                |
| [performance-optimizer](skills/performance-optimizer)         | Application performance and scaling optimization                        |
| [planning](skills/planning)                                   | Planning methodology and session management                             |
| [playwright](skills/playwright)                               | Browser automation, stealth mode, anti-bot bypass                       |
| [postgres-tuning](skills/postgres-tuning)                     | PostgreSQL query optimization and async I/O tuning                      |
| [prompt](skills/prompt)                                       | Prompt engineering, reasoning models, tree-of-thoughts                  |
| [quality-auditor](skills/quality-auditor)                     | Code quality gatekeeper and auditing                                    |
| [rag-implementer](skills/rag-implementer)                     | Retrieval-augmented generation systems                                  |
| [react](skills/react)                                         | React 19+ patterns, performance, component architecture                 |
| [react-tanstack-senior](skills/react-tanstack-senior)         | Senior React with full TanStack ecosystem                               |
| [realtime-sync](skills/realtime-sync)                         | WebTransport, real-time sync, AI stream orchestration                   |
| [remotion](skills/remotion)                                   | Video creation in React with Remotion                                   |
| [repo-updater](skills/repo-updater)                           | Multi-repo synchronization with AI-assisted review                      |
| [responsive-images](skills/responsive-images)                 | srcset, sizes, lazy loading, WebP/AVIF                                  |
| [scrum-conductor](skills/scrum-conductor)                     | AI-enhanced Scrum orchestration                                         |
| [secure-ai](skills/secure-ai)                                 | AI security, prompt injection defense, zero-trust                       |
| [security](skills/security)                                   | STRIDE threat modeling, OWASP Top 10                                    |
| [security-audit](skills/security-audit)                       | Row-level security and forensic auditing                                |
| [seo](skills/seo)                                             | SEO optimization and content strategy                                   |
| [shadcn-ui](skills/shadcn-ui)                                 | shadcn/ui component system                                              |
| [skill-management](skills/skill-management)                   | Create, review, and validate Claude Code skills                         |
| [ssh](skills/ssh)                                             | SSH access, key management, tunnels, transfers                          |
| [tailwind](skills/tailwind)                                   | Tailwind CSS v4+ configuration and design tokens                        |
| [tanstack-integration](skills/tanstack-integration)           | Strategic TanStack library adoption guide                               |
| [tanstack-query](skills/tanstack-query)                       | TanStack Query v5 server state management                               |
| [tanstack-router](skills/tanstack-router)                     | Type-safe file-based React routing                                      |
| [tanstack-start](skills/tanstack-start)                       | Full-stack React framework on TanStack Router                           |
| [tanstack-table](skills/tanstack-table)                       | Headless data tables for React                                          |
| [threejs](skills/threejs)                                     | Three.js WebGPU 3D rendering                                            |
| [tiptap](skills/tiptap)                                       | Rich text editors with Tiptap + React + Tailwind                        |
| [tldr-expert](skills/tldr-expert)                             | Semantic code intelligence and token optimization                       |
| [turborepo](skills/turborepo)                                 | Monorepo build system, task caching and orchestration                   |
| [ui-ux-polish](skills/ui-ux-polish)                           | Iterative UI/UX polishing workflow                                      |
| [usability-tester](skills/usability-tester)                   | Usability testing and UX issue identification                           |
| [ux-designer](skills/ux-designer)                             | User journeys, wireframes, prototypes                                   |
| [zustand](skills/zustand)                                     | Zustand v5 state management for React                                   |

## Contributing

Each skill lives in `skills/[skill-name]/` and contains a `SKILL.md` with YAML frontmatter. See [CLAUDE.md](CLAUDE.md) for skill standards and authoring guidelines.

```sh
# Validate a skill
pnpm validate:skills skills/[skill-name]

# Validate all skills
pnpm validate:skills
```

## License

MIT
