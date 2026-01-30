---
title: Error Handling
description: Common failure modes in multi-agent systems, recovery strategies, circuit breakers, graceful degradation, and logging
tags:
  [
    error-handling,
    recovery,
    circuit-breaker,
    graceful-degradation,
    logging,
    traceability,
  ]
---

# Error Handling in Multi-Agent Systems

## Common Failure Modes

| Failure Mode     | Description                                    | Frequency |
| ---------------- | ---------------------------------------------- | --------- |
| Objective Drift  | Subagent forgets the original goal             | High      |
| Tool Failure     | MCP server is offline or returns an error      | Medium    |
| Context Overflow | Subagent runs out of tokens                    | Medium    |
| Infinite Loops   | Agents delegating back and forth indefinitely  | Low       |
| Hallucination    | Agent generates plausible but incorrect output | Medium    |
| Silent Failure   | Agent completes without error but wrong result | High      |

## Recovery Strategies

### 1. Reset and Re-prompt

If a subagent's output is nonsensical or fails validation, reset its context and re-issue the command with more specific constraints.

```text
First attempt: "Implement the auth module"
Failed: Output was unrelated database code

Re-prompt: "Implement JWT authentication in src/lib/auth.ts.
  Must export: validateSession(token: string): Promise<Session | null>
  Must use: jsonwebtoken library
  Must read: existing Session type from src/types/auth.ts"
```

### 2. Circuit Breakers

If an agent fails a specific tool call repeatedly, trip the circuit breaker:

| Failure Count | Action                                   |
| ------------- | ---------------------------------------- |
| 1             | Retry with same parameters               |
| 2             | Retry with modified parameters           |
| 3             | Trip circuit breaker, escalate to parent |

After the circuit breaker trips, the parent agent must either:

- Try an alternative capability
- Escalate to the user
- Mark the step as blocked and continue with remaining steps

### 3. Graceful Degradation

If a complex capability fails, fall back to simpler alternatives:

```text
Primary:   AI-powered code analysis
Fallback:  Static analysis tool
Last resort: Manual review flag
```

The system should always produce some useful output, even if degraded.

### 4. Objective Drift Prevention

| Technique             | Implementation                                     |
| --------------------- | -------------------------------------------------- |
| Manifest of Objective | Every subagent receives explicit goal statement    |
| Output validation     | Parent checks output against expected deliverables |
| Periodic checkpoints  | Long-running tasks report progress to parent       |
| Context anchoring     | Include goal statement at start and end of prompt  |

## Logging and Traceability

Every agent interaction must be logged for debugging.

### Trace Log Schema

| Field       | Type   | Description                            |
| ----------- | ------ | -------------------------------------- |
| timestamp   | string | ISO-8601 format                        |
| agentId     | string | The subagent's identifier              |
| parentId    | string | The delegating agent's identifier      |
| action      | string | DELEGATE, TOOL_CALL, RESPONSE, ERROR   |
| duration    | number | Milliseconds                           |
| tokenCount  | number | Tokens consumed                        |
| toolResults | object | Tool call inputs and outputs           |
| errorInfo   | object | Error type, message, stack (if failed) |

### Debugging Multi-Agent Failures

1. **Identify the failing agent** -- Check trace logs for ERROR actions
2. **Examine the delegation chain** -- Follow parentId links back to the root
3. **Check context quality** -- Was the right information passed?
4. **Verify tool availability** -- Are MCP servers responding?
5. **Review objective alignment** -- Did the agent understand the task?

## Anti-Patterns

| Anti-Pattern              | Problem                           | Fix                            |
| ------------------------- | --------------------------------- | ------------------------------ |
| No error handling at all  | Silent failures cascade           | Validate every subagent output |
| Infinite retries          | Runaway token spend               | Use circuit breakers (max 3)   |
| Ignoring partial results  | Throws away useful work           | Gracefully degrade             |
| No trace logging          | Cannot debug multi-agent failures | Log every interaction          |
| Retrying with same prompt | Gets same wrong result            | Modify constraints on retry    |
