---
title: Plan to Beads
description: Converting markdown plans into granular beads with dependencies, exact prompts for conversion, and what the output includes
tags: [conversion, prompts, plan, dependencies, tasks, subtasks]
---

# Plan to Beads

## Why Convert Plans to Beads?

A markdown plan fits in a context window and lets a model reason about the entire system at once. But plans are not executable by agent swarms. Beads bridge this gap: each bead is a self-contained task that any agent can pick up independently.

Key properties of well-formed beads:

- **Self-contained** -- Never need to refer back to the original markdown plan
- **Self-documenting** -- Include background, reasoning, justifications, considerations
- **Dependency-aware** -- Explicit structure of what blocks what
- **Rich descriptions** -- Long markdown descriptions, not short bullet points

## Conversion Prompt (Full Version)

Replace `YOUR_PLAN_FILE.md` with the actual filename.

```text
OK so now read ALL of YOUR_PLAN_FILE.md; please take ALL of that and elaborate on it and use it to create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the over-arching goals of the project.). The beads should be so detailed that we never need to consult back to the original markdown plan document. Remember to ONLY use the `bd` tool to create and modify the beads and add the dependencies. Use ultrathink.
```

## Conversion Prompt (Short Version)

Use when the plan is already in context (for example, you just discussed it).

```text
OK so please take ALL of that and elaborate on it more and then create a comprehensive and granular set of beads for all this with tasks, subtasks, and dependency structure overlaid, with detailed comments so that the whole thing is totally self-contained and self-documenting (including relevant background, reasoning/justification, considerations, etc.-- anything we'd want our "future self" to know about the goals and intentions and thought process and how it serves the over-arching goals of the project.) Use only the `bd` tool to create and modify the beads and add the dependencies. Use ultrathink.
```

## What Conversion Creates

The conversion prompt produces:

- **Tasks and subtasks** with clear, non-overlapping scope
- **Dependency links** declaring what must complete before what
- **Detailed descriptions** containing:
  - Background context explaining why this work matters
  - Reasoning and justification for the chosen approach
  - Technical considerations and constraints
  - How it serves the overarching project goals

## Example Bead Structure

A well-formed bead after conversion looks like this:

```markdown
ID: BD-123
Title: Implement OAuth2 login flow
Type: feature
Priority: P1
Status: open

Dependencies: [BD-100 (User model), BD-101 (Session management)]
Blocks: [BD-200 (Protected routes), BD-201 (User dashboard)]

Description:
Implement OAuth2 login flow supporting Google and GitHub providers.

## Background

This is the primary authentication mechanism for the application.
Users should be able to sign in with existing Google/GitHub accounts
to reduce friction.

## Technical Approach

- Use NextAuth.js for OAuth2 implementation
- Store provider tokens encrypted in Supabase
- Create unified user record on first login
- Handle account linking for multiple providers

## Success Criteria

- User can click "Sign in with Google/GitHub"
- OAuth flow completes and redirects to dashboard
- User record created/updated in database
- Session cookie set correctly
- Logout clears session properly

## Test Plan

- Unit: Token encryption/decryption
- Unit: User record creation
- E2E: Full OAuth flow (mock provider)
- E2E: Account linking scenario

## Considerations

- Handle provider API rate limits
- Graceful degradation if provider is down
- GDPR compliance for EU users
```

## Tips for Better Conversions

- Ensure the plan file is complete before converting; partial plans produce incomplete beads
- Use "ultrathink" in the prompt to encourage deeper reasoning about structure
- After conversion, immediately run a polish pass to catch gaps
- Check that every section of the original plan maps to at least one bead
