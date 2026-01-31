---
title: Planning Document Templates
description: Templates for IMPLEMENTATION_PHASES.md, ARCHITECTURE.md, DATABASE_SCHEMA.md, API_ENDPOINTS.md, and other planning documents
tags:
  [templates, implementation-phases, architecture, database, api, planning-docs]
---

# Planning Document Templates

## IMPLEMENTATION_PHASES.md

The core planning document for every project. Each phase is context-safe (5-8 files, 2-4 hours).

```markdown
# Implementation Phases: [Project Name]

**Project Type**: [Web App / Dashboard / API / Tool]
**Stack**: [Primary technologies]
**Estimated Total**: [X hours]

---

## Phase 1: [Name]

**Type**: [Infrastructure/Database/API/UI/Integration/Testing]
**Estimated**: [X hours]
**Files**: [file1.ts, file2.tsx, ...]

### File Map

- `src/[file].ts` (~XXX lines)
  - **Purpose**: [What this file does]
  - **Key exports**: [Main functions/components/types]
  - **Dependencies**: [What it imports]
  - **Used by**: [What uses it]

### Data Flow

[Mermaid diagram for complex interactions]

### Critical Dependencies

**Internal**: [Codebase files this phase depends on]
**External**: [npm packages needed]
**Configuration**: [Environment variables, config files]

### Gotchas and Known Issues

- **[Issue]**: [Description and solution]

### Tasks

- [ ] Task 1
- [ ] Task 2
- [ ] Test basic functionality

### Verification Criteria

- [ ] Specific test 1
- [ ] Specific test 2

### Exit Criteria

[Clear definition of when this phase is complete]

---

## Notes

### Testing Strategy

[Inline per-phase / Separate testing phase / Hybrid]

### Deployment Strategy

[Deploy per phase / Deploy at milestones / Final deploy]

### Context Management

Phases sized to fit within a single session including implementation,
verification, debugging, and documentation updates.

### Dependencies

1. Infrastructure (no dependencies)
2. Database (depends on Infrastructure)
3. API (depends on Infrastructure + Database)
4. UI (depends on API)
5. Integration (depends on relevant phases)
6. Testing (depends on all implementation phases)
```

## ARCHITECTURE.md

Generate when the project has multiple services, complex system boundaries, or non-trivial data flows.

```markdown
# Architecture: [Project Name]

**Deployment**: [Platform]
**Frontend**: [Framework + libraries]
**Backend**: [Framework + runtime]

---

## System Overview

[ASCII diagram showing major components and their connections]

---

## Components Breakdown

### Frontend

**Responsibilities**: User interaction, client validation, optimistic updates, state management
**Key Libraries**: [List with purpose of each]

### Backend

**Responsibilities**: Routing, auth, validation, business logic, database ops
**Route Structure**: [Overview of route organization]
**Middleware Pipeline**: [Request flow through middleware]

### Database

**Access Pattern**: [How the backend queries the database]
**Migrations**: [Where migrations live and how to run them]

### External Services

[List each service with purpose and integration method]

---

## Data Flow Patterns

### [Flow Name]

[Step-by-step flow description showing how data moves through the system]

---

## Security

**Authentication**: [Method and provider]
**Authorization**: [How ownership/permissions are checked]
**Input Validation**: [Client and server validation strategy]
**Secrets**: [How secrets are managed across environments]

---

## Scaling Considerations

[Current limits and what to change if you need to scale beyond them]
```

## DATABASE_SCHEMA.md

Generate when the project has 3+ tables.

```markdown
# Database Schema: [Project Name]

**Database**: [Engine]
**Migrations**: [Location]
**ORM**: [ORM or raw SQL]

---

## Tables

### `[table_name]`

**Purpose**: [What this table stores]

| Column       | Type    | Constraints           | Notes                  |
| ------------ | ------- | --------------------- | ---------------------- |
| `id`         | INTEGER | PRIMARY KEY           | Auto-increment         |
| `user_id`    | INTEGER | FOREIGN KEY, NOT NULL | References `users(id)` |
| `[field]`    | [TYPE]  | [CONSTRAINTS]         | [Notes]                |
| `created_at` | INTEGER | NOT NULL              | Unix timestamp         |

**Indexes**: [List indexes with purpose]
**Relationships**: [Foreign key relationships]

---

## Relationships Diagram

[ASCII diagram showing table relationships]

---

## Migrations

### Migration 0001: [Description]

**File**: `migrations/0001_[name].sql`
**Creates**: [Tables created]
**Run**: `[command to execute migration]`

---

## Seed Data

[Sample data for development and testing]

---

## Query Patterns

[Common queries used by the application]

---

## Constraints

**Database level**: Primary keys, foreign keys, unique constraints, not null
**Application level**: Format validation, length limits, enum values, business rules
```

## API_ENDPOINTS.md

Generate when the project has 5+ endpoints.

```markdown
# API Endpoints: [Project Name]

**Base URL**: `/api`
**Auth**: [Authentication method]
**Validation**: [Validation library]

---

## Response Format

### Success

[Standard success response structure]

### Error

[Standard error response structure with error codes]

---

## [Resource] Endpoints

### GET `/api/[resource]`

**Purpose**: [What this endpoint does]
**Auth**: [Required/None]
**Query Parameters**: [List with defaults]
**Response 200**: [Response body example]

### POST `/api/[resource]`

**Purpose**: [What this endpoint does]
**Auth**: [Required/None]
**Request Body**: [Request body with validation schema]
**Response 201**: [Response body example]
**Response 400**: [Validation error example]

### PATCH `/api/[resource]/:id`

**Purpose**: [What this endpoint does]
**Auth**: [Required/None]
**Request Body**: [Partial update fields]
**Response 200**: [Response body example]

### DELETE `/api/[resource]/:id`

**Purpose**: [What this endpoint does]
**Auth**: [Required/None]
**Response 204**: No content

---

## Middleware

**CORS**: [Origins, methods, headers]
**Auth**: [JWT verification, context injection]
**Validation**: [Request body validation against schemas]
**Error Handler**: [Catch unhandled errors, sanitize responses]
```

## When to Generate Each Document

| Document              | Trigger                                        |
| --------------------- | ---------------------------------------------- |
| IMPLEMENTATION_PHASES | Always -- core planning doc for every project  |
| SESSION               | Always -- progress tracking hub                |
| DATABASE_SCHEMA       | 3+ tables                                      |
| API_ENDPOINTS         | 5+ endpoints                                   |
| ARCHITECTURE          | Multiple services or complex system boundaries |
| CRITICAL_WORKFLOWS    | Complex setup steps, order-sensitive workflows |
| INSTALLATION_COMMANDS | Recommended for all projects                   |
| ENV_VARIABLES         | Needs API keys or secrets                      |
| TESTING               | Testing strategy needs documentation           |

## Template Usage Guidelines

- Replace all `[placeholders]` with project-specific values
- Remove optional sections that do not apply
- Add project-specific sections as needed
- Keep templates in a `docs/` directory in the project root
- Reference templates from SESSION.md for easy navigation
