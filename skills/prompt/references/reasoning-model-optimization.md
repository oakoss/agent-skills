---
title: Reasoning Model Optimization
description: Objective-based prompting for reasoning models like o3 and Gemini Pro, deep research triggers, self-consistency at scale, and token efficiency
tags:
  [
    reasoning-models,
    o3,
    objective-based,
    deep-research,
    self-consistency,
    token-efficiency,
  ]
---

## Objective-Based Prompting

Reasoning models (OpenAI o3, Gemini Pro) use an internal "thought process" before emitting tokens. Optimizing for these models requires a shift from instruction-based prompting to objective-based prompting.

### Let the Model Think

Do not force the model into a rigid format too early.

- Use a high `maxOutputTokens` to allow the model to complete its internal chain-of-thought
- Explicitly asking "think step-by-step" is redundant for these models; they reason natively
- Instead, ask them to "verify your own strategy"

### Managing Latency vs. Quality

Reasoning tokens are slow and expensive. Route tasks to the appropriate model:

| Task Type                            | Recommended Model                      |
| ------------------------------------ | -------------------------------------- |
| Simple classification, summarization | Lightweight model (e.g., flash/mini)   |
| Architectural design, code auditing  | Reasoning model (e.g., o3)             |
| Complex math, multi-step logic       | Reasoning model with high token budget |

## Deep Research Triggers

When using models with deep research capabilities:

- Provide a "Research Goal" rather than a list of steps
- Example: "Conduct an exhaustive search for [Topic X]. Do not stop until you have found contradictory evidence or 10+ distinct sources."
- Let the model determine its own research path

## Self-Consistency at Scale

For high-stakes decisions:

1. Ask the model to generate 3 independent reasoning paths
2. Have a second model (e.g., a lightweight one) compare the paths and select the most logically sound one
3. Use the consensus result for the final answer

## Token Efficiency

- **Compress context**: Use symbol indexing or code summaries. Reasoning models perform better when relationships between symbols are clear without noise
- **Avoid redundant instructions**: Do not repeat what the model already does natively (e.g., step-by-step reasoning)
- **Front-load critical information**: Place the most important context at the beginning of the prompt

## Key Differences from Standard Models

| Standard Model                     | Reasoning Model                  |
| ---------------------------------- | -------------------------------- |
| Explicit step-by-step instructions | Objective-based goals            |
| Format early in the prompt         | Allow thinking before formatting |
| Short output tokens                | High output token budget         |
| Direct answer expected             | Verification loop expected       |
| Manual chain-of-thought            | Native internal reasoning        |

## Best Practices

1. State the objective clearly, not the method
2. Allocate generous output token budgets
3. Ask the model to verify and critique its own strategy
4. Use routing to send simple tasks to cheaper models
5. Compress context to reduce noise and improve reasoning clarity
