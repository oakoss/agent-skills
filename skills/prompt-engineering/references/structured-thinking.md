---
title: Structured Thinking
description: Adversarial critic protocol, Understanding-Analysis-Execution framework, confidence-weighted responses, metadata tagging, and dynamic example injection
tags:
  [
    structured-thinking,
    protocols,
    adversarial,
    confidence,
    metadata,
    verification,
  ]
---

## Understanding-Analysis-Execution Protocol

Force the model to slow down and verify context before acting:

1. **Understanding**: Re-state the user's goal in your own words
2. **Analysis**: Identify dependencies, risks, and edge cases
3. **Execution**: Perform the task in small, verifiable units

```text
Before taking action, follow this protocol:

Step 1 (Understanding): Restate what you've been asked to do.
Step 2 (Analysis): Identify 2-3 risks, dependencies, or assumptions.
Step 3 (Execution): Proceed with the task in small, verifiable steps.
```

## Adversarial Critic Protocol

For high-stakes tasks (e.g., security audits, architecture decisions):

```text
Phase 1 (The Proposer): Generate a solution to the problem.
Phase 2 (The Attacker): Find three ways the solution could fail.
Phase 3 (The Refiner): Update the solution to mitigate the attacks.
```

This three-role approach forces the model to stress-test its own output before presenting a final answer.

### Example Application

```text
Problem: Design an authentication system for a multi-tenant SaaS app.

[Proposer] Solution: Use JWT tokens with tenant-scoped claims...

[Attacker] Failure modes:
1. Token theft via XSS allows cross-tenant access
2. Long-lived refresh tokens create persistent compromise risk
3. No mechanism to revoke individual sessions

[Refiner] Updated solution:
- Add HttpOnly cookies to prevent XSS token theft
- Implement token rotation with short expiry
- Add session revocation via a server-side blocklist
```

## Dynamic Example Injection

Use semantic similarity (RAG) to inject the most relevant few-shot examples based on the current query:

```text
Rule: Never use static examples for complex tasks. Use a similarity
search to find the best-match example from your example store.

Process:
1. Embed the user query
2. Search the example store for the closest match
3. Inject the matched example into the prompt
4. Generate the response using the contextual example
```

## Confidence-Weighted Responses

Require the model to quantify its certainty:

```text
For each recommendation, provide a confidence level:
- HIGH (90%+): Strong evidence, well-understood domain
- MEDIUM (60-89%): Reasonable evidence, some assumptions
- LOW (below 60%): Limited evidence, significant uncertainty

Example: "I am 90% sure about the fix for File A, but only 40%
sure about File B due to missing context."
```

### Benefits of Confidence Scoring

| Benefit         | Description                                    |
| --------------- | ---------------------------------------------- |
| Prioritization  | Act on high-confidence items first             |
| Risk management | Flag low-confidence items for human review     |
| Calibration     | Track accuracy vs. stated confidence over time |
| Transparency    | Users understand which parts are uncertain     |

## Metadata Tagging in Prompts

Use metadata tags to signal the intent of prompt blocks:

| Tag               | Purpose                               |
| ----------------- | ------------------------------------- |
| `<rule>`          | Immutable behavioral constraint       |
| `<context>`       | Dynamic information about the project |
| `<gold_standard>` | A reference implementation to match   |
| `<preference>`    | Soft guideline, may be overridden     |

```text
<rule>Never modify files outside the src/ directory.</rule>
<context>This is a Next.js 16 project using Tailwind 4.</context>
<gold_standard>See the auth module at src/lib/auth.ts for the preferred pattern.</gold_standard>
<preference>Prefer functional components over class components.</preference>
```

## Combining Protocols

For maximum quality, chain protocols together:

1. **Understanding-Analysis-Execution** to ensure the task is correctly understood
2. **Adversarial Critic** to stress-test the proposed solution
3. **Confidence Scoring** to quantify reliability of the final answer

## Best Practices

1. Use the Understanding phase to catch misinterpretations early
2. Apply the Adversarial Critic only for high-stakes decisions (it adds latency)
3. Calibrate confidence scores by tracking actual accuracy over time
4. Keep metadata tags consistent across all prompts in a system
5. Combine protocols selectively based on task complexity
