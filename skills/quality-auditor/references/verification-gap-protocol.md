---
title: Verification Gap Protocol
description: Methodology for verifying AI-generated code quality, critic agent patterns, rejection protocols, and risk-based review strategies
tags:
  [
    verification-gap,
    ai-code-review,
    critic-agents,
    rejection-protocol,
    risk-based-review,
  ]
---

# Verification Gap Protocol

AI-assisted development accounts for a significant and growing share of committed code. The bottleneck has shifted from writing code to reviewing, validating, and governing it. This protocol ensures velocity does not compromise integrity.

## The Verification Gap

The verification gap is the distance between what AI-generated code appears to do and what it actually does in production. AI output can produce functions that compile and pass basic tests yet introduce redundancy, fragile logic, security vulnerabilities, or compliance risks.

**Key risks of unverified AI code:**

- Compiles and runs but contains subtle logic errors
- Passes unit tests but fails under real-world edge cases
- Introduces architectural drift by not following project conventions
- Creates security vulnerabilities through incomplete input validation
- Adds unnecessary complexity or dead code paths
- Generates plausible but incorrect implementations of business rules

## Closing the Gap

### 1. Critic Agent Pattern

Use high-reasoning models to audit the output of faster code-generation models. The critic agent reviews with a different perspective than the generator.

**Critic agent responsibilities:**

- Verify contract integrity (does output match interfaces, schemas, types?)
- Check architectural alignment (does it follow project patterns?)
- Validate security sanitization (are inputs validated, secrets protected?)
- Assess performance hygiene (N+1 queries, bundle size, resource usage)
- Confirm cleanliness (no debug artifacts, commented-out code, TODOs)

**How to implement:**

```ts
// Example: structured audit output from a critic agent
type AuditResult = {
  dimension: string;
  score: number;
  evidence: string[];
  issues: Array<{
    severity: 'critical' | 'high' | 'medium' | 'low';
    file: string;
    line: number;
    description: string;
    suggestion: string;
  }>;
};
```

### 2. Verifiable Goals

Every PR must produce a measurable signal of success. No code merges without at least one verifiable gate passing.

**Required signals:**

| Gate          | Tool                | Pass Criteria              |
| ------------- | ------------------- | -------------------------- |
| Type safety   | TypeScript compiler | Zero errors in strict mode |
| Lint          | ESLint / Biome      | Zero errors                |
| Tests         | Vitest / Playwright | All pass, coverage met     |
| Build         | Bundler / compiler  | Successful build           |
| Security scan | npm audit / Snyk    | No high/critical vulns     |
| Format        | Prettier / Biome    | No formatting diffs        |

**Verification script example:**

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Running verification gates..."

echo "1. Type check"
npx tsc --noEmit --strict

echo "2. Lint"
npx eslint . --max-warnings 0

echo "3. Tests"
npx vitest run --coverage

echo "4. Build"
npm run build

echo "5. Security audit"
npm audit --audit-level=high

echo "All gates passed."
```

### 3. Human Oversight

Mandatory human sign-off for critical paths. Not all code requires the same level of review.

**Critical paths requiring human review:**

- Authentication and authorization logic
- Payment processing and financial calculations
- Data migration and schema changes
- Cryptographic operations
- Privacy-sensitive data handling (PII, HIPAA, GDPR)
- Infrastructure and deployment configuration

**Standard paths for automated review:**

- UI component styling
- Test additions for existing features
- Documentation updates
- Dependency version bumps (with passing gates)
- Configuration file changes

## AI Code Standards

### Excellence Over Mimicry

Do not repeat bad local patterns just because they exist in the codebase. AI-generated code should follow idiomatic standards for the stack, even if existing code does not.

```ts
// BAD: Mimicking a poor existing pattern found in the codebase
function getUser(id: any) {
  const res: any = db.query(`SELECT * FROM users WHERE id = ${id}`);
  return res;
}

// GOOD: Idiomatic, type-safe, parameterized
async function getUser(id: string): Promise<User | null> {
  return db.user.findUnique({ where: { id } });
}
```

### No Black Boxes

Every complex function must explain its reasoning. AI-generated code is particularly prone to producing "it works" implementations without documenting non-obvious decisions.

```ts
// BAD: No explanation for the magic
function calculateDiscount(total: number): number {
  return total > 100 ? total * 0.85 : total > 50 ? total * 0.9 : total;
}

// GOOD: Business rules documented
function calculateDiscount(total: number): number {
  // Tiered discount per 2024 pricing agreement:
  // - Orders over $100: 15% discount
  // - Orders over $50: 10% discount
  // - Below $50: no discount
  if (total > 100) return total * 0.85;
  if (total > 50) return total * 0.9;
  return total;
}
```

### Metadata Tagging

Tag AI-generated files for future auditing. This helps track which code was generated vs hand-written, enabling targeted reviews during audits.

```ts
// @generated - AI-assisted implementation
// @audit-date - 2026-01-15
// @generator - claude-opus-4-5
```

## The Rejection Protocol

If the audit fails any check in the supreme checklist:

### Step 1: Stop

Do not proceed with the commit, push, or report. A failed audit means the code is not ready.

### Step 2: Analyze

Identify the specific deviation:

- Which gate failed?
- What is the root cause?
- Is this a pattern issue or an isolated problem?

### Step 3: Remediate

Apply the fix immediately. Do not defer:

- Fix the type error, not suppress it
- Add the missing test, not skip the check
- Resolve the security issue, not add a TODO
- Correct the pattern, not document the workaround

### Step 4: Re-Audit

Restart the checklist from step 1. A partial re-run is not sufficient because fixes can introduce new issues.

## The Supreme Audit Checklist

Before any AI-generated code is accepted:

| Check                   | What to Verify                                              |
| ----------------------- | ----------------------------------------------------------- |
| Contract integrity      | Code matches defined interfaces (Zod, TypeScript types)     |
| Architectural alignment | Idiomatic patterns for the stack (not cargo-culted)         |
| Security sanitization   | All inputs validated, no secrets in logs or code            |
| Performance hygiene     | No N+1 queries, images optimized, bundle size within budget |
| Cleanliness audit       | No `console.log`, debug artifacts, commented-out code       |
| Traceability            | Non-obvious decisions documented with "why" comments        |
| Test coverage           | New code has tests, existing tests still pass               |
| Dependency audit        | No new high/critical vulnerabilities introduced             |

## Context-Aware Review

Surface-level static analysis catches formatting and basic lint issues but misses deeper problems. Effective AI code review must also assess:

- **Architectural fit** -- does the change align with the system's design direction?
- **Requirement alignment** -- does the implementation match what was actually requested?
- **Convention consistency** -- does the code follow the team's established patterns?
- **Future maintainability** -- will this code be easy to modify in six months?
- **Integration safety** -- does the change interact correctly with existing code?

## Quality Metrics for AI Code

Track these metrics to measure the effectiveness of AI code review:

| Metric                 | Target            | Why It Matters                       |
| ---------------------- | ----------------- | ------------------------------------ |
| Post-merge defect rate | <2% of AI-gen PRs | Catches issues the review missed     |
| Review iteration count | <3 rounds per PR  | Measures AI output quality           |
| Time from PR to merge  | <24 hours         | Measures review bottleneck           |
| Gate pass rate         | >90% on first run | Measures code generation quality     |
| Revert rate            | <1% of merged PRs | Measures overall process reliability |
