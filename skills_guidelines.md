# Skills Migration Guidelines

Temporary guide for migrating skills from `.agents/skills/` and `.claude/skills/` into `skills/`. Delete this file when migration is complete.

## Source Locations

Skills were consolidated from multiple sources. When restructuring, check all of these for content:

| Location                                | Contents                                                               |
| --------------------------------------- | ---------------------------------------------------------------------- |
| `skills/[name]/SKILL.md`                | Current consolidated skill (primary source)                            |
| `.agents/skills/[name]/`                | External community skills (may have `rules/` or `references/` subdirs) |
| `.agents/skills/[name]-best-practices/` | Best-practices variant (rules, anti-patterns)                          |
| `.agents/skills/[name]-expert/`         | Expert variant (advanced patterns, known issues)                       |
| `.claude/skills/[name]/`                | Project-specific skills (NOT for public repo)                          |

Not all skills have variants in `.agents/`. Check what exists before starting.

## Restructuring Workflow

For each skill >500 lines:

1. **Read** the full `skills/[name]/SKILL.md`
2. **Check** for additional source content in `.agents/skills/[name]*/`
3. **Identify topics** — group content into coherent reference file topics
4. **Write reference files** — one per topic, self-contained with code
5. **Write lean SKILL.md** — tables and links only, 100-150 lines
6. **Validate** — run the checklist below
7. **Update** `skills_status_tracking.md` — move to Restructured table, add changelog entry

### Parallel Agent Strategy

For large skills (>800 lines), split reference file creation across parallel agents. Each agent writes 2-3 files. Always specify the full output path `skills/[name]/references/[file].md` — agents have written to wrong directories before.

## Validation Checklist

Run after restructuring each skill:

- [ ] SKILL.md is 100-150 lines
- [ ] SKILL.md has: frontmatter, overview, quick reference table, common mistakes table, delegation, references list
- [ ] No code examples in SKILL.md
- [ ] Every reference link in SKILL.md has a matching file in `references/`
- [ ] Every file in `references/` has a matching link in SKILL.md (no orphans)
- [ ] No reference file exceeds 500 lines
- [ ] Every reference file has YAML frontmatter (title, description, tags)
- [ ] Content from `.agents/skills/` variants was checked for gaps
- [ ] No content was silently dropped (compare original section headers)

## Common Reference File Topics

These topic names recur across skills. Use consistent naming:

| Topic           | Filename                 | Typical Content                        |
| --------------- | ------------------------ | -------------------------------------- |
| Getting started | `basic-patterns.md`      | Architecture, setup, core usage        |
| Error handling  | `error-handling.md`      | Strategies, boundaries, recovery       |
| TypeScript      | `typescript-patterns.md` | Type inference, generics, validation   |
| Testing         | `testing.md`             | Test setup, mocking, assertions        |
| SSR/Hydration   | `ssr-hydration.md`       | Server rendering, hydration, streaming |
| Performance     | `performance.md`         | Optimization, profiling, lazy loading  |
| Migration       | `migration.md`           | Version upgrades, breaking changes     |
| Known issues    | `known-issues.md`        | Bugs, workarounds, affected versions   |
| Configuration   | `configuration.md`       | Options, defaults, environment         |
| API reference   | `api-reference.md`       | Function signatures, parameters        |
| Accessibility   | `accessibility.md`       | WCAG, ARIA, keyboard navigation        |

Not every skill needs all of these. Choose topics based on the content.

## Template Skill

`tanstack-query` is the reference implementation. Use it as the template for restructuring other skills.
