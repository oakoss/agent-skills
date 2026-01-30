---
title: ReAct Patterns
description: Thought-Action-Observation loop for autonomous agents, tool discovery, error recovery, ambiguity handling, and traceability
tags: [ReAct, agent, tool-use, reasoning, action, observation, autonomous]
---

## The Thought-Action-Observation Loop

ReAct (Reasoning and Acting) is the standard pattern for autonomous agents that interact with external tools:

```text
Thought: "I need to check the user's balance before approving the refund."
Action: get_user_balance(userId: "123")
Observation: {"balance": 50.00}
Thought: "The refund is 100.00. I cannot approve this automatically."
```

## Prompting for ReAct

```text
You operate in a loop: Thought, Action, Observation.

Thought: Describe your reasoning about the task.
Action: Execute one of the allowed tools.
Observation: Read the result of the action.

Continue until you have reached the goal or a terminal error.
```

## Tool Discovery

Agents perform best when they know the full scope of their abilities. Provide a concise, typed list of available tools at the beginning of every session:

```text
Available tools:
- search(query: string) -> SearchResult[]
- get_user(id: string) -> User
- send_email(to: string, subject: string, body: string) -> boolean
- calculate(expression: string) -> number
```

Include parameter types, return types, and brief descriptions for each tool.

## Error Recovery

If an action returns an unexpected observation, the agent must generate a "Recovery Thought" and attempt an alternative action rather than giving up:

```text
Thought: "The search returned no results. I'll try a broader query."
Action: search(query: "account billing")
Observation: [3 results found]
Thought: "Found relevant results. Proceeding with the first match."
```

### Recovery Strategies

| Failure Type              | Recovery Strategy                                    |
| ------------------------- | ---------------------------------------------------- |
| Tool returns empty result | Broaden the query or try alternative tool            |
| Tool returns error        | Retry with corrected parameters                      |
| Unexpected data format    | Parse what is available, request clarification       |
| Timeout                   | Retry with simpler request or report partial results |
| Permission denied         | Escalate to user or try alternative approach         |

## Handling Ambiguity

When the task is ambiguous or multiple interpretations are possible:

```text
Thought: "The user asked to 'clean up the data.' This could mean:
  1. Remove duplicates
  2. Fix formatting
  3. Handle missing values
I'll ask for clarification."
Action: ask_user("What kind of cleanup? Remove duplicates, fix formatting, or handle missing values?")
```

## Multi-Step Planning

For complex tasks, plan multiple steps before acting:

```text
Thought: "To generate the monthly report, I need to:
  1. Fetch sales data for the period
  2. Calculate totals and averages
  3. Generate charts
  4. Format into PDF
  Starting with step 1."
Action: fetch_sales_data(period: "2026-01")
```

## Traceability and Logging

Log the entire ReAct loop for audit and improvement:

| Field       | Purpose                              |
| ----------- | ------------------------------------ |
| Thought     | Shows reasoning behind each decision |
| Action      | Records the tool call and parameters |
| Observation | Captures the raw tool output         |
| Timestamp   | Enables performance analysis         |
| Step number | Tracks loop depth                    |

This enables:

- **Audit**: Understanding exactly why an agent took an action
- **Learning**: Improving the system prompt based on failed loops
- **Debugging**: Identifying where agent reasoning went wrong

## Best Practices

1. Always provide the full tool list with typed signatures
2. Require the agent to reason before acting (no blind tool calls)
3. Implement recovery strategies for common failure modes
4. Set a maximum loop depth to prevent infinite cycles
5. Log all steps for auditability and iterative improvement
6. Ask for clarification when the task is genuinely ambiguous
