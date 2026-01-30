---
name: skill-management
description: |
  Create, review, and validate Claude Code skills. Covers YAML frontmatter, descriptions, progressive disclosure, token efficiency, 9-phase audits, severity classification, and manifest-implementation drift detection.

  Use when: creating new skills, improving descriptions, auditing existing skills, detecting version drift, validating implementations match manifests, or debugging skill discovery issues.
user-invocable: true
---

# Skill Management

Create, audit, and validate Claude Code skills with production-quality standards.

---

## Quick Reference

```bash
# Scaffold a new skill
/create-skill my-skill-name

# Review an existing skill
/review-skill <skill-name>

# Verify metadata
./scripts/check-metadata.sh <skill-name>

# Check all skill versions
./scripts/check-all-versions.sh

# Run automated review
./scripts/review-skill.sh <skill-name>
```

### Skill Directory Structure

```sh
skills/my-skill/
├── SKILL.md          # Main documentation (required)
├── README.md         # Auto-trigger keywords (required)
├── scripts/          # Executable helpers (deterministic tasks)
├── references/       # Extended docs (loaded on demand)
└── assets/           # Templates, config files, images
```

### YAML Frontmatter

```yaml
---
name: lowercase-hyphen-case # Max 64 chars, gerund form preferred
description: | # Max 1024 chars, 250-350 ideal
  [What it does in active voice. Key technologies named.]

  Use when: [3-5 scenarios], [2-3 error keywords for discovery].
allowed-tools: # Optional: restrict tool access
  - Bash
  - Read
---
```

---

## Core Patterns

### Writing Effective Descriptions

The description determines if your skill gets discovered. Use this structure:

**Paragraph 1**: What you can build + key features (active voice)
**Paragraph 2**: When to use + error keywords for discovery

```yaml
# Bad: Passive, vague, no discovery keywords
description: |
  This skill helps you with database operations. It provides patterns
  for working with data and can be useful in many situations.

# Good: Active, specific, discoverable
description: |
  Build type-safe database queries with Drizzle ORM and Cloudflare D1.
  Covers schema definition, migrations, relations, and transaction patterns.

  Use when: setting up D1 database, writing Drizzle schemas, debugging
  "no such table" or "D1_ERROR" issues.
```

**Description checklist:**

- Active voice ("Build X" not "This skill provides X")
- Specific technologies named
- 3-5 "Use when" scenarios
- 2-3 distinctive error messages/keywords
- No meta-commentary about the skill itself
- 250-350 characters total

### Progressive Disclosure

Load information in layers to conserve context window tokens:

| Layer         | When Loaded    | Target Size  | Content                        |
| ------------- | -------------- | ------------ | ------------------------------ |
| **Metadata**  | Always         | 40-55 tokens | name + description             |
| **SKILL.md**  | When triggered | <5k words    | Instructions, patterns         |
| **Resources** | As needed      | Variable     | scripts/, references/, assets/ |

### Freedom Levels

Match instruction specificity to error probability:

| Level      | Format                | Use When                                   |
| ---------- | --------------------- | ------------------------------------------ |
| **High**   | Text instructions     | Multiple valid approaches                  |
| **Medium** | Pseudocode/patterns   | Preferred pattern with some flexibility    |
| **Low**    | Exact scripts/configs | Fragile operations where precision matters |

### Token Efficiency

- Move extended examples to `references/` -- keep SKILL.md under 5k words
- One good code example beats three mediocre ones
- Reference official docs instead of copying them
- If Claude already knows it, don't include it

---

## Reviewing Skills: 9-Phase Audit

Run `/review-skill <skill-name>` or use when detecting outdated patterns.

| Phase | Name                   | Check                                                        |
| ----- | ---------------------- | ------------------------------------------------------------ |
| 1     | Pre-Review             | Install skill, check version/date, test discovery            |
| 2     | Standards              | YAML validity, keywords, third-person style, directory       |
| 3     | Official Docs          | WebFetch/Context7 verify APIs, GitHub updates, npm versions  |
| 4     | Code Examples          | Imports exist, API signatures match, templates work          |
| 5     | Cross-File Consistency | SKILL.md vs README.md, bundled resources match actual files  |
| 6     | Dependencies           | Package versions current, breaking changes, staleness >90d   |
| 7     | Categorize             | Assign severity with evidence (GitHub/docs/npm links)        |
| 8     | Fix                    | Auto-fix unambiguous issues, ask user for architectural ones |
| 9     | Verify                 | Test discovery, templates work, no contradictions, commit    |

**Automated** (via `./scripts/review-skill.sh`): YAML syntax, package versions, broken links, TODOs, file org, staleness

**Manual** (AI): API methods vs docs, GitHub issues, production comparisons, code correctness, schema consistency

### Severity Classification

| Level    | Meaning                                                        |
| -------- | -------------------------------------------------------------- |
| Critical | Non-existent API/imports, invalid config, missing dependencies |
| High     | Contradictory examples, inconsistent patterns, outdated majors |
| Medium   | Stale minors (>90d), missing doc sections, incomplete errors   |
| Low      | Typos, formatting, missing optional metadata                   |

### Fix Decision

- **Auto-fix**: Unambiguous (correct import from docs), clear evidence, no architectural impact
- **Ask user**: Multiple valid approaches, breaking changes, architectural choices

### Version Bumps

- **Major** (v1 to v2): API patterns change
- **Minor** (v1.0 to v1.1): New features, backward compatible
- **Patch** (v1.0.0 to v1.0.1): Bug fixes only

---

## Validating Skills: Implementation vs Manifest

Detect drift between what a skill promises and what it delivers.

### Validation Dimensions

| Dimension               | What It Checks                                      |
| ----------------------- | --------------------------------------------------- |
| Description Accuracy    | Implementation matches manifest description         |
| Precondition Validation | Claimed preconditions are actually checked in code  |
| Effect Verification     | Code produces all claimed effects                   |
| API Surface Analysis    | Exported functions match manifest                   |
| Drift Detection         | Implementation has diverged from manifest over time |
| Coverage Scoring        | Percentage of manifest that is actually implemented |

### When to Validate

- After updating skill implementations
- During quality audits
- When manifests feel outdated or incorrect
- Before releasing new versions

### Pass Criteria

```text
Overall score >= 0.8 AND zero high-severity issues
Score = average(description_accuracy, precondition_coverage, effect_coverage)
```

---

## Anti-Patterns

### Vague descriptions

```yaml
# Won't be discovered
description: "Helps with authentication"

# Will be discovered
description: |
  Implement authentication with Clerk - React components, middleware,
  and Cloudflare Workers integration with JWT verification.

  Use when: adding auth to React apps, protecting API routes, or
  troubleshooting "clerk/backend" import errors.
```

### Duplicating Claude's existing knowledge

```text
# Bad: Claude already knows JavaScript basics
## Variables
Use `const` for constants and `let` for variables...

# Good: Focus on what Claude might get wrong
## Critical: Cloudflare Workers Differences
- No `process.env` - use `env` parameter from fetch handler
- No Node.js `fs` module - use R2 or KV for storage
```

### Missing error keywords

Include common error messages users hit so the skill gets triggered:

```yaml
description: |
  ...
  Use when: troubleshooting "Cannot read properties of undefined",
  "NEXT_REDIRECT" errors, or hydration mismatches.
```

### Overly rigid instructions

```text
# Bad: Breaks if API changes
Always call api.configure({ version: "2.1.0" }) first.

# Good: Flexible with rationale
Configure the API client before making calls. The version should match
your installed package version (check package.json).
```

### No production validation

Skills should be tested in real projects, not just theoretically correct. Include evidence of production testing in the skill.

### Orphan bundled resources

Listed files that don't actually exist in the skill directory. Always verify cross-file references during review.

---

## Troubleshooting

### Skill not discovered

1. Check description has relevant keywords matching user queries
2. Verify README.md has auto-trigger keywords
3. Ensure skill is symlinked to `~/.claude/skills/`
4. Test with natural language: "Help me set up [technology]"

### Skill content too large

1. Move examples to `references/` directory
2. Keep SKILL.md under 5k words
3. Link to official docs instead of copying
4. Prune anything Claude already knows

### Validation score too low

1. Check for missing features described but not implemented
2. Look for undocumented features (implemented but not in manifest)
3. Verify all preconditions are enforced in code
4. Confirm all claimed effects are actually produced

### Common review findings

| Issue                  | Frequency  | Fix                                     |
| ---------------------- | ---------- | --------------------------------------- |
| Fake API adapters      | Common     | Verify imports exist in actual packages |
| Stale API methods      | Common     | Check signatures against current docs   |
| Schema inconsistency   | Moderate   | Align table/field names across files    |
| Version drift (>90d)   | Frequent   | Run `./scripts/check-versions.sh`       |
| Contradictory examples | Moderate   | Pick one canonical pattern per concept  |
| Broken links           | Occasional | Verify all URLs resolve                 |

---

## Quality Checklist

Before committing a skill:

- [ ] Name is lowercase-hyphen-case, max 40 chars
- [ ] Description is 250-350 chars with "Use when:" section
- [ ] SKILL.md under 5k words
- [ ] All code examples tested and working
- [ ] Package versions verified current
- [ ] Known issues documented with sources (GitHub issues, etc.)
- [ ] Production tested (not just theoretically correct)
- [ ] README.md has auto-trigger keywords
- [ ] Cross-file consistency verified (SKILL.md vs README.md vs resources)
- [ ] No high-severity issues remaining

---

## Common Mistakes

| Mistake                                                            | Correct Pattern                                                                  |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| Writing vague descriptions without discovery keywords              | Include specific technologies, 3-5 "Use when" scenarios, and 2-3 error messages  |
| Duplicating knowledge Claude already has (e.g., JavaScript basics) | Focus on what Claude might get wrong — edge cases, platform differences, gotchas |
| Putting all content in SKILL.md without progressive disclosure     | Keep SKILL.md under 5k words; move examples to `references/` directory           |
| Listing bundled files in SKILL.md that do not exist on disk        | Always verify cross-file references during review — orphan links break trust     |
| Using passive voice or first-person in descriptions                | Use third-person active voice: "Builds X" not "This skill helps you build X"     |

## Delegation

- **Skill discovery and keyword research**: Use `Explore` agent
- **Multi-skill audit and cross-file consistency checks**: Use `Task` agent
- **Skill architecture and directory structure planning**: Use `Plan` agent

## References

- **Official Spec**: <https://github.com/anthropics/skills/blob/main/agent_skills_spec.md>
