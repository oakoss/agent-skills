---
title: Project Documentation
description: README templates, architecture decision records, changelogs, migration guides, and onboarding documentation patterns
tags:
  [
    readme,
    adr,
    changelog,
    migration-guide,
    onboarding,
    keep-a-changelog,
    conventional-commits,
    semver,
  ]
---

# Project Documentation

## README Structure

A README is the front door to a project. It answers: what is this, how do I use it, and where do I go for more.

### Template

````markdown
# Project Name

[![CI](https://img.shields.io/github/actions/workflow/status/org/repo/ci.yml)](https://github.com/org/repo/actions)
[![npm](https://img.shields.io/npm/v/package-name)](https://www.npmjs.com/package/package-name)
[![License](https://img.shields.io/github/license/org/repo)](./LICENSE)

One-line description of what this project does and who it's for.

## Quick Start

` ` `bash
npm install package-name
` ` `

` ` `ts
import { createClient } from 'package-name';

const client = createClient({ apiKey: process.env.API_KEY });
const result = await client.doSomething({ input: 'hello' });
console.log(result);
` ` `

## Installation

` ` `bash

# npm

npm install package-name

# pnpm

pnpm add package-name

# yarn

yarn add package-name
` ` `

### Requirements

- Node.js >= 20
- TypeScript >= 5.0 (optional but recommended)

## Usage

### Basic Example

` ` `ts
import { createClient } from 'package-name';

const client = createClient({ apiKey: process.env.API_KEY });
` ` `

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
` ` `

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
````

### Numbering and Organization

```text
docs/
  adr/
    README.md          # Index of all ADRs with status
    adr-001-database.md
    adr-002-auth.md
    adr-003-monorepo.md
```

The README index lists every ADR with its status, making it easy to scan for current decisions vs. superseded ones.

### Status Lifecycle

```text
Proposed → Accepted → [Deprecated | Superseded by ADR-XXX]
```

Never delete or edit accepted ADRs. To reverse a decision, write a new ADR that supersedes the old one and update the status of the original.

## Changelog

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

Tools like `conventional-changelog` or `release-please` generate changelogs from commit messages. The commit type maps directly to changelog categories:

| Commit Type        | Changelog Category            |
| ------------------ | ----------------------------- |
| `feat:`            | Added                         |
| `fix:`             | Fixed                         |
| `perf:`            | Changed                       |
| `BREAKING CHANGE:` | Changed (with breaking label) |

## Migration Guides

Migration guides bridge the gap between versions. They are the most time-sensitive documentation: write them before or alongside the release.

### Template

```markdown
# Migrating from v1.x to v2.0

## Breaking Changes Summary

| Change                            | Action Required          |
| --------------------------------- | ------------------------ |
| `createInstance` → `createClient` | Rename all occurrences   |
| CommonJS dropped                  | Switch to ESM imports    |
| Node.js 18 unsupported            | Upgrade to Node.js >= 20 |

## Step-by-Step Migration

### 1. Update Node.js

Ensure you are running Node.js 20 or later:

` ` `bash
node --version  # Must be >= 20.0.0
` ` `

### 2. Rename `createInstance` to `createClient`

**Before (v1.x):**

` ` `ts
import { createInstance } from 'package-name';
const api = createInstance({ key: '...' });
` ` `

**After (v2.0):**

` ` `ts
import { createClient } from 'package-name';
const api = createClient({ key: '...' });
` ` `

### 3. Switch to ESM

**Before (v1.x CommonJS):**

` ` `js
const { createInstance } = require('package-name');
` ` `

**After (v2.0 ESM):**

` ` `ts
import { createClient } from 'package-name';
` ` `

Update `package.json`:

` ` `json
{
  "type": "module"
}
` ` `

## Codemods

Run the automated migration for renames:

` ` `bash
npx package-name-codemod v2
` ` `

This handles `createInstance` → `createClient` renames automatically.
```

### Key Principles

- **Breaking changes table up front** — scannable summary before detailed steps
- **Before/after code pairs** — show exact transformations
- **Codemods when possible** — automate mechanical changes
- **Test after each step** — recommend running tests between migration steps

## Onboarding Guide

An onboarding guide reduces the time from "git clone" to "first meaningful contribution."

### Template

```markdown
# Developer Onboarding

## Prerequisites

- Node.js >= 20 (use `nvm install` with the project's `.nvmrc`)
- pnpm >= 9
- Docker (for local database)

## First-Time Setup

` ` `bash
git clone https://github.com/org/repo.git
cd repo
pnpm install
cp .env.example .env.local    # Edit with your local values
pnpm db:setup                 # Start database and run migrations
pnpm dev                      # Start dev server at localhost:3000
` ` `

## Project Structure

` ` `sh
src/
  app/          # Next.js app router pages
  components/   # Shared UI components
  lib/          # Business logic and utilities
  server/       # API routes and server-side code
` ` `

## Key Concepts

- **Feature flags**: Managed via LaunchDarkly. See `src/lib/flags.ts`.
- **Database**: PostgreSQL via Prisma. Schema at `prisma/schema.prisma`.
- **Auth**: NextAuth.js with OAuth providers. Config at `src/lib/auth.ts`.

## Common Tasks

| Task             | Command               |
| ---------------- | --------------------- |
| Run dev server   | `pnpm dev`            |
| Run tests        | `pnpm test`           |
| Run linter       | `pnpm lint`           |
| Generate types   | `pnpm codegen`        |
| Create migration | `pnpm db:migrate:dev` |
| Reset database   | `pnpm db:reset`       |

## Your First Contribution

1. Pick an issue labeled `good-first-issue`
2. Create a branch: `git checkout -b feat/your-feature`
3. Make changes and add tests
4. Run `pnpm test && pnpm lint` before committing
5. Open a PR against `main`
```

### Key Principles

- **Test the guide** — have a new team member follow it; fix every stumbling block
- **Keep it current** — outdated setup instructions are worse than none
- **Link, don't duplicate** — reference existing docs rather than copying content
- **Include common tasks** — the commands developers run daily
