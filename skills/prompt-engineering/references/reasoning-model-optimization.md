---
title: Reasoning Model Optimization
description: Objective-based prompting for reasoning models like OpenAI o3/o4-mini and Claude with extended thinking, developer messages, token budget management, and model routing
tags:
  [
    reasoning-models,
    o3,
    o4-mini,
    extended-thinking,
    objective-based,
    developer-messages,
    token-efficiency,
  ]
---

## Objective-Based Prompting

Reasoning models (OpenAI o3, o4-mini) use an internal chain-of-thought before emitting tokens. Claude models with extended thinking enabled behave similarly. Optimizing for these models requires a shift from instruction-based prompting to objective-based prompting.

### Let the Model Think

Do not force the model into a rigid format too early.

- Allocate a high output token budget to allow the model to complete its internal reasoning
- Explicitly asking "think step-by-step" is redundant for reasoning models; they reason natively
- Instead, state the objective and ask the model to "verify your own strategy"

```text
Objective: Design a database schema for a multi-tenant SaaS application
that supports per-tenant data isolation, shared reference data, and
efficient cross-tenant analytics queries.

Verify your strategy handles: tenant deletion, schema migrations,
and query performance at 10K tenants.
```

### Do Not Over-Prompt Reasoning

Asking a reasoning model to plan more extensively or reason harder before each action can degrade performance. These models already produce internal chains of thought. Additional reasoning prompts add noise rather than signal.

```text
Bad:  "Think very carefully and plan your approach step by step
       before calling any tools."
Good: "Find the root cause of the authentication failure in the
       user service."
```

## OpenAI o-Series Best Practices

### Developer Messages

OpenAI o3 and o4-mini use developer messages (rather than system messages) to distinguish developer instructions from user input:

```python
messages = [
    {"role": "developer", "content": "You are a code review assistant..."},
    {"role": "user", "content": "Review this pull request..."}
]
```

Developer messages provide guidance on tool disambiguation, tool invocation order, and proactiveness control.

### Function Descriptions as Contracts

For o3/o4-mini, the function description is the primary place to specify when a tool should be invoked and how arguments should be constructed:

```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_codebase",
        "description": (
            "Search the codebase for files matching a query. "
            "Use this when the user asks about code structure, "
            "function definitions, or implementation details. "
            "The query should be a natural language description, "
            "not a regex pattern."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "file_type": {"type": "string", "enum": ["ts", "py", "go"]}
            },
            "required": ["query"]
        }
    }
}]
```

### Persisted Reasoning Items

With o3 and o4-mini, pass back all reasoning items from previous responses. The API automatically includes relevant reasoning items in context and ignores irrelevant ones, improving performance while minimizing token usage:

```python
response = client.responses.create(
    model="o3",
    input=messages,
    store=True
)
```

## Claude Extended Thinking

Claude models support extended thinking, which creates dedicated thinking blocks before the response. Enable it with a budget parameter:

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": "..."}]
)
```

### Budget Guidelines

| Budget Range    | Use Case                                |
| --------------- | --------------------------------------- |
| 1,024 (minimum) | Simple tasks where some reasoning helps |
| 4,000-10,000    | Standard analytical and coding tasks    |
| 16,000-32,000   | Complex multi-step reasoning            |
| 32,000+         | Use batch processing to avoid timeouts  |

Start at the minimum and increase incrementally. Claude may not use the full budget, especially above 32K.

### Key Constraints

- `budget_tokens` must be less than `max_tokens`
- Thinking is incompatible with `temperature` and `top_k` modifications
- Cannot pre-fill responses when thinking is enabled
- Extended thinking performs best in English (output can be any language)

## Model Routing

Route tasks to the appropriate model based on complexity:

| Task Type                            | Recommended Model                                     |
| ------------------------------------ | ----------------------------------------------------- |
| Simple classification, summarization | Lightweight model (Claude Haiku, GPT-4.1-mini, flash) |
| Standard coding, analysis            | Mid-tier model (Claude Sonnet, GPT-4.1)               |
| Architectural design, code auditing  | Reasoning model (o3, Claude with extended thinking)   |
| Complex math, multi-step logic       | Reasoning model with high token budget                |

## Self-Consistency at Scale

For high-stakes decisions:

1. Ask the model to generate 3 independent reasoning paths
2. Have a second model (lightweight) compare the paths and select the most logically sound
3. Use the consensus result for the final answer

## Token Efficiency

- **Compress context**: Use symbol indexing or code summaries; reasoning models perform better when relationships are clear without noise
- **Avoid redundant instructions**: Do not repeat what reasoning models do natively (step-by-step reasoning)
- **Front-load critical information**: Place the most important context at the beginning of the prompt

## Key Differences from Standard Models

| Standard Model                     | Reasoning Model                     |
| ---------------------------------- | ----------------------------------- |
| Explicit step-by-step instructions | Objective-based goals               |
| Format early in the prompt         | Allow thinking before formatting    |
| Short output token budget          | High output token budget            |
| Direct answer expected             | Verification loop expected          |
| Manual chain-of-thought            | Native internal reasoning           |
| System message for instructions    | Developer message (OpenAI o-series) |

## Best Practices

1. State the objective clearly, not the method
2. Allocate generous output token budgets
3. Ask the model to verify and critique its own strategy
4. Use routing to send simple tasks to cheaper models
5. Compress context to reduce noise and improve reasoning clarity
6. Do not add explicit reasoning prompts to reasoning models
7. Use developer messages for OpenAI o-series models
8. Start with minimum thinking budgets and scale up for Claude
