---
name: secure-ai
description: 'Secures AI integrations against prompt injection, privilege escalation, and data leakage. Use when implementing defense-in-depth for LLM pipelines, applying zero-trust controls to autonomous agents, hardening server actions that interact with AI services, or auditing AI system access patterns and identity management.'
---

# Secure AI

## Overview

Secures AI integration layers through multi-layered defense, structural isolation, and zero-trust orchestration. Covers prompt injection defense, agentic security, secure server actions, rate limiting, and secret management for applications that interact with LLMs.

**When to use:** Securing LLM-powered features against prompt injection, implementing zero-trust for autonomous agents, hardening server actions for AI endpoints, auditing AI access patterns.

**When NOT to use:** General web application security without AI components, frontend-only security concerns, non-AI API hardening.

## Quick Reference

| Pattern                 | Approach                                        | Key Points                                             |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------ |
| Structural isolation    | Separate system/user message roles              | Never mix instructions and user data in one string     |
| Input boundaries        | Delimit user data with markers                  | Helps models identify where untrusted data begins/ends |
| Guardian model          | Pre-scan input with a fast model                | Detect injection patterns before main reasoning model  |
| Least privilege         | Capability-based scopes per sub-task            | Agents get only the tools needed for current work      |
| Human-in-the-loop       | Require human sign-off for destructive actions  | Financial or data-altering events need approval        |
| Non-human identity      | OIDC-based agent authentication                 | Verifiable identity for every agent, rotate keys daily |
| Server-only AI logic    | `server-only` imports for all AI code           | Keys and reasoning never leak to client bundle         |
| Input validation        | Zod schemas on all AI-facing server actions     | Never pass raw user input to AI services               |
| Rate limiting           | Per-user/IP token budget via Redis              | Prevent denial-of-wallet attacks on AI endpoints       |
| Stream scrubbing        | Filter sensitive strings from AI output streams | Remove internal IDs, secrets before reaching client    |
| Sandboxed content fetch | URL validation and allowlists                   | Treat all fetched external data as untrusted           |
| Secret management       | Environment variables with CI leak scanning     | Use gitleaks in CI to prevent committed secrets        |

## Core Security Philosophies

1. **Isolation is absolute** -- user data must never be treated as system instruction
2. **Least privilege for agents** -- grant only the tools needed for the current sub-task
3. **Human verification of destruction** -- destructive actions require a human signature
4. **No secrets in client** -- all AI logic and keys reside in server-only environments
5. **Adversarial mindset** -- assume both users and agents will try to bypass rules

## Common Mistakes

| Mistake                                                            | Correct Pattern                                                       |
| ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| Mixing user input and system instructions in the same prompt field | Use structural isolation with separate system and user message roles  |
| Using thin system prompts easily bypassed via roleplay attacks     | Build hierarchical guardrails with defense-in-depth layers            |
| Giving agents unlimited tool access for all tasks                  | Apply capability-based scopes granting only tools needed per sub-task |
| Using static API keys for AI service authentication                | Use OIDC with dynamic key rotation and short-lived tokens             |
| Fetching unvalidated URLs from user input in AI pipelines          | Sandbox all content fetching with URL validation and allowlists       |
| Passing raw user input directly to AI services                     | Validate all input with Zod schemas before AI processing              |
| Streaming AI responses without output filtering                    | Scrub sensitive strings from streams before they reach the client     |

## Delegation

- **Scan codebase for prompt injection vulnerabilities**: Use `Explore` agent to search for user data flowing into system prompts and unvalidated inputs
- **Implement zero-trust agent orchestration**: Use `Task` agent to add identity verification, WASM sandboxing, and human approval gates
- **Design secure AI integration architecture**: Use `Plan` agent to map trust boundaries, agent scopes, and audit requirements

## References

- [Prompt Injection Defense](references/prompt-injection-defense.md) -- multi-layered isolation, guardian models, input boundaries
- [Agentic Zero-Trust Security](references/agentic-security-zero-trust.md) -- non-human identity, resource isolation, anomaly detection
- [Secure Server Actions](references/secure-server-actions.md) -- server-only patterns, input validation, rate limiting, stream security
- [Security Audit Protocols](references/security-audit-protocols.md) -- monitoring agent behavior, token-level attacks, compliance checklists
