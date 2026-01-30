---
title: Anti-Patterns Guide
description: Catalog of code, architecture, security, testing, and process anti-patterns to identify during quality audits
tags:
  [
    anti-patterns,
    code-smells,
    security-vulnerabilities,
    testing-antipatterns,
    process-issues,
  ]
---

# Anti-Patterns Guide

A catalog of anti-patterns to identify during quality audits, organized by category.

## Code Anti-Patterns

| Anti-Pattern           | Signal                                   | Severity |
| ---------------------- | ---------------------------------------- | -------- |
| God objects            | Single class/module doing everything     | High     |
| Spaghetti code         | No clear flow, tangled dependencies      | High     |
| Copy-paste programming | Duplicated blocks with minor variations  | Medium   |
| Magic numbers          | Unexplained literals in logic            | Medium   |
| Global state abuse     | Mutable shared state without controls    | High     |
| Deep nesting           | 4+ levels of indentation                 | Medium   |
| Long methods           | Functions exceeding 50 lines             | Medium   |
| Primitive obsession    | Using primitives instead of value types  | Low      |
| Feature envy           | Method uses more of another class's data | Medium   |
| Dead code              | Unreachable or unused code paths         | Low      |

### Detection Strategies

```bash
# Find functions over 50 lines (approximate)
rg -c "^}" -g "*.ts" | sort -t: -k2 -rn | head -20

# Find potential magic numbers
rg "\b(?:100|200|404|500|1000|3600|86400)\b" -g "*.ts" --stats

# Find duplicated string literals
rg -o '"[^"]{10,}"' -g "*.ts" --no-filename | sort | uniq -c | sort -rn | head -10

# Find deeply nested code
rg "^\s{16,}" -g "*.ts" -c | sort -t: -k2 -rn
```

## Architecture Anti-Patterns

| Anti-Pattern          | Signal                                        | Severity |
| --------------------- | --------------------------------------------- | -------- |
| Tight coupling        | Changes cascade across modules                | High     |
| Circular dependencies | A depends on B depends on A                   | High     |
| Missing abstractions  | Implementation details leak across boundaries | Medium   |
| Over-engineering      | Unnecessary complexity for simple problems    | Medium   |
| Anemic domain model   | Data structures with no behavior              | Medium   |
| Big ball of mud       | No discernible architecture pattern           | Critical |
| Leaky abstraction     | Internal details exposed through interface    | Medium   |
| Vendor lock-in        | Core logic depends on specific vendor APIs    | High     |

### Detection Strategies

```bash
# Find circular imports (approximate)
rg "^import.*from" -g "*.ts" --no-heading | sort > /tmp/imports.txt

# Find files importing from many different modules
rg -c "^import" -g "*.ts" | sort -t: -k2 -rn | head -20

# Find files that are imported by many others (high coupling)
for f in src/**/*.ts; do echo "$(rg -l "$f" -g "*.ts" | wc -l) $f"; done | sort -rn | head -20
```

## Security Anti-Patterns

| Anti-Pattern           | Signal                            | Severity |
| ---------------------- | --------------------------------- | -------- |
| Hardcoded secrets      | API keys, passwords in source     | Critical |
| SQL injection          | Unsanitized user input in queries | Critical |
| XSS vulnerabilities    | Unescaped output in templates     | High     |
| Missing authentication | Endpoints without auth checks     | Critical |
| Insecure defaults      | Debug mode in production          | High     |
| Excessive permissions  | Over-scoped API keys or roles     | Medium   |
| Missing rate limiting  | Endpoints without throttling      | Medium   |
| Logging sensitive data | PII or secrets in log output      | High     |

### Detection Strategies

```bash
# Find potential hardcoded secrets
rg -i "(api.?key|secret|password|token)\s*[:=]" -g "*.ts" -g "!*.test.*"

# Find potential SQL injection
rg "query\(.*\$\{" -g "*.ts"
rg "execute\(.*\+" -g "*.ts"

# Find missing auth checks in API routes
rg "export (async )?function (GET|POST|PUT|DELETE)" -g "*/api/**/*.ts" -l
```

## Testing Anti-Patterns

| Anti-Pattern           | Signal                                          | Severity |
| ---------------------- | ----------------------------------------------- | -------- |
| No tests               | Zero coverage                                   | Critical |
| Flaky tests            | Non-deterministic pass/fail                     | High     |
| Test duplication       | Same scenario tested multiple ways              | Medium   |
| Testing implementation | Tests break on refactor without behavior change | High     |
| Missing edge cases     | Only happy path tested                          | Medium   |
| Slow tests             | Test suite takes >10 minutes                    | Medium   |
| Test pollution         | Tests depend on execution order                 | High     |
| Over-mocking           | Tests verify mocks, not behavior                | Medium   |

### Detection Strategies

```bash
# Check test coverage
npx vitest --coverage --reporter=json

# Find tests without assertions
rg "it\(|test\(" -A 20 -g "*.test.*" | rg -v "expect\(|assert"

# Find test files with no tests
fd ".test." -e ts -x sh -c 'rg -c "it\(|test\(" {} | grep ":0$"'
```

## Process Anti-Patterns

| Anti-Pattern           | Why It Fails                          | Correct Alternative        |
| ---------------------- | ------------------------------------- | -------------------------- |
| "LGTM" mentality       | Superficial review hides deep bugs    | Deep semantic audit        |
| Bypassing types        | `any` and `@ts-ignore` cause drift    | Total type integrity       |
| Mixing paradigms       | Confuses AI context and humans        | Strict pattern consistency |
| Silent delivery        | User does not know what was validated | Verification reporting     |
| Debt for speed         | "We'll fix it later" = never          | Zero-debt policy           |
| No code ownership      | Nobody responsible for quality        | Clear ownership model      |
| Review without context | Reviewer lacks domain knowledge       | Domain-expert review       |

## Audit Checklist (Pre-Commit)

Before declaring any task finished, verify:

1. **Contract integrity** -- code matches defined interfaces (Zod schemas, TypeScript types)
2. **Architectural alignment** -- idiomatic patterns for the stack
3. **Security sanitization** -- all inputs validated, no secrets in logs or code
4. **Performance hygiene** -- no N+1 queries, images optimized, bundle size checked
5. **Cleanliness audit** -- no `console.log`, debug artifacts, or commented-out code
6. **Traceability** -- the "why" is documented for non-obvious decisions
