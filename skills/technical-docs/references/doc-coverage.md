---
title: Doc Coverage
description: Feature inventory, gap analysis, doc-first and code-first audit workflows, evidence capture, red flags, README structure, ADR format, and changelog templates
tags:
  [
    coverage,
    audit,
    gap-analysis,
    inventory,
    sync,
    exports,
    readme,
    adr,
    changelog,
    keep-a-changelog,
  ]
---

## Feature Inventory Targets

Scan the codebase for these documentation-worthy items:

- Public exports: classes, functions, types, and module entry points
- Configuration options: `*Settings` types, default config objects, builder patterns
- Environment variables or runtime flags
- CLI commands, scripts, and example entry points
- User-facing behaviors: retry, timeouts, streaming, errors, logging, telemetry
- Deprecations, removals, or renamed settings

## Doc-First Pass

Review each documentation page and check for:

- Missing opt-in flags, env vars, or customization options the page implies
- New features that belong on that page based on user intent and navigation
- Outdated defaults or removed options still referenced

## Code-First Pass

Map features to the closest existing page based on the docs navigation:

- Prefer updating existing pages over creating new ones unless the topic is clearly new
- Use conceptual pages for cross-cutting concerns (auth, errors, streaming, tracing, tools)
- Keep quick-start flows minimal; move advanced details into deeper pages

## Doc Sync Audit

Compare current code against documentation to find drift:

```bash
# Diff current branch against main
git diff main...HEAD -- src/

# Find undocumented exports
rg "export (const|function|class)" src/ --type ts

# Compare with docs structure
ls -R docs/
```

## Evidence Capture

When documenting gaps:

- Record the file path and symbol/setting name
- Note defaults or behavior-critical details for accuracy checks
- Avoid large code dumps; a short identifier is enough

## Red Flags for Outdated Docs

| Red Flag                                      | Action                                |
| --------------------------------------------- | ------------------------------------- |
| Option names/types no longer exist in code    | Remove or update the documentation    |
| Default values do not match implementation    | Correct the documented defaults       |
| Features removed in code but still documented | Mark as removed or delete the section |
| New behaviors without corresponding docs      | Prioritize by user impact             |

## When to Propose Structural Changes

- A page mixes unrelated audiences (quick-start + deep reference) without separation
- Multiple pages duplicate the same concept without cross-links
- New feature areas have no obvious home in the navigation structure

## Diff Mode Guidance

When auditing a feature branch against main:

- Focus only on changed behavior: new exports, modified defaults, removed features, renamed settings
- Use `git diff main...HEAD` to constrain analysis
- Document removals explicitly so docs can be pruned

## Patch Guidance

- Keep edits scoped and aligned with existing tone and format
- Update cross-links when moving or renaming sections
- Leave translated docs untouched; English-only updates

## README Structure Template

A README is the front door to a project. It answers: what is this, how do I use it, and where do I go for more. Keep under 200 lines; link out for depth.

````markdown
# Project Name

[![CI](https://img.shields.io/github/actions/workflow/status/org/repo/ci.yml)](https://github.com/org/repo/actions)
[![npm](https://img.shields.io/npm/v/package-name)](https://www.npmjs.com/package/package-name)
[![License](https://img.shields.io/github/license/org/repo)](./LICENSE)

One-line description of what this project does and who it's for.

## Quick Start

```bash
npm install package-name
```

```ts
import { createClient } from 'package-name';

const client = createClient({ apiKey: process.env.API_KEY });
const result = await client.doSomething({ input: 'hello' });
console.log(result);
```

## Installation

```bash
# npm
npm install package-name

# pnpm
pnpm add package-name

# yarn
yarn add package-name
```

### Requirements

- Node.js >= 20
- TypeScript >= 5.0 (optional but recommended)

## Usage

### Configuration Options

| Option    | Type     | Default       | Description            |
| --------- | -------- | ------------- | ---------------------- |
| `apiKey`  | `string` | —             | Required. Your API key |
| `baseUrl` | `string` | `'https://…'` | API base URL           |
| `timeout` | `number` | `30000`       | Request timeout (ms)   |
| `retries` | `number` | `3`           | Max retry attempts     |

## API Reference

See the [full API documentation](./docs/api.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](./LICENSE)
````

### Key Principles

- **Badges first** — CI status, version, license give instant project health signals
- **One-line description** — no jargon, no marketing; what it does in plain language
- **Quick start before full install** — most users want to copy-paste and go
- **Tables for config** — scannable, consistent, easy to maintain
- **Link out for depth** — README stays under 200 lines; detailed docs live elsewhere

## Architecture Decision Records (ADRs)

ADRs capture the WHY behind significant technical decisions. They are immutable once accepted: supersede rather than edit.

### When to Write an ADR

- Choosing a framework, database, or major dependency
- Changing authentication or authorization strategy
- Adopting or dropping a pattern (monorepo, microservices, etc.)
- Any decision that a new team member would question

### ADR Template

```markdown
# ADR-001: Use PostgreSQL for Primary Data Store

## Status

Accepted

## Context

The application requires ACID transactions, complex queries with joins,
and strong consistency guarantees. The team has production experience with
PostgreSQL. Current data volume is ~10GB with projected growth to 500GB
over 2 years.

## Decision

Use PostgreSQL 16 as the primary data store, accessed via Prisma ORM.

## Consequences

### Positive

- ACID compliance for financial transaction data
- Rich query capabilities (JSON, full-text search, CTEs)
- Team familiarity reduces onboarding time

### Negative

- Horizontal scaling requires read replicas or sharding
- Schema migrations need coordination across services
- Higher operational overhead than managed NoSQL options

### Neutral

- Need to establish backup and disaster recovery procedures
- Connection pooling (PgBouncer) required above ~100 concurrent connections
```

### Numbering and Organization

```text
docs/
  adr/
    README.md          # Index of all ADRs with status
    adr-001-database.md
    adr-002-auth.md
    adr-003-monorepo.md
```

### Status Lifecycle

```text
Proposed → Accepted → [Deprecated | Superseded by ADR-XXX]
```

Never delete or edit accepted ADRs. To reverse a decision, write a new ADR that supersedes the old one and update the status of the original.

## Changelog (Keep a Changelog)

Follow [Keep a Changelog](https://keepachangelog.com/) format, aligned with semantic versioning.

### Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- New `retries` configuration option for automatic retry on failure

### Fixed

- Connection timeout now respects the configured `timeout` value

## [2.1.0] - 2025-03-15

### Added

- Batch processing support via `client.batchProcess()`
- TypeScript 5.5 support

### Changed

- Default timeout increased from 10s to 30s

### Deprecated

- `client.process()` single-item method; use `client.batchProcess()` instead

## [2.0.0] - 2025-01-10

### Changed

- **BREAKING:** Renamed `createInstance` to `createClient`
- **BREAKING:** Minimum Node.js version is now 20

### Removed

- **BREAKING:** Dropped CommonJS support; ESM only

[Unreleased]: https://github.com/org/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/org/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/org/repo/releases/tag/v2.0.0
```

### Categories

| Category       | When to Use                       |
| -------------- | --------------------------------- |
| **Added**      | New features                      |
| **Changed**    | Changes to existing functionality |
| **Deprecated** | Features that will be removed     |
| **Removed**    | Features that were removed        |
| **Fixed**      | Bug fixes                         |
| **Security**   | Vulnerability patches             |

### Auto-generation from Conventional Commits

| Commit Type        | Changelog Category            |
| ------------------ | ----------------------------- |
| `feat:`            | Added                         |
| `fix:`             | Fixed                         |
| `perf:`            | Changed                       |
| `BREAKING CHANGE:` | Changed (with breaking label) |
