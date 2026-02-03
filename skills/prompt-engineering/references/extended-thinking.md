---
title: Extended Thinking and Tool Use
description: Claude extended thinking configuration, budget management, interleaved thinking with tool use, the think tool pattern for agentic reasoning, and thinking block preservation
tags:
  [
    extended-thinking,
    interleaved-thinking,
    think-tool,
    tool-use,
    budget-tokens,
    agentic,
    reasoning,
  ]
---

## Extended Thinking Overview

Extended thinking gives Claude enhanced reasoning by creating dedicated `thinking` content blocks before the response. The model reasons through the problem internally, then delivers a final answer informed by that reasoning.

### Enabling Extended Thinking

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{
        "role": "user",
        "content": "Design an authentication system for a multi-tenant SaaS app."
    }]
)

for block in response.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Response: {block.text}")
```

### Budget Token Guidelines

The `budget_tokens` parameter controls the maximum tokens Claude can use for internal reasoning:

| Budget          | Use Case                                              |
| --------------- | ----------------------------------------------------- |
| 1,024 (minimum) | Light reasoning, simple analysis                      |
| 4,000-10,000    | Standard coding and analytical tasks                  |
| 16,000-32,000   | Complex multi-step reasoning, architecture design     |
| 32,000+         | Deep analysis; use batch processing to avoid timeouts |

Start at the minimum and increase incrementally. Claude may not use the full budget, especially above 32K tokens.

### When to Use Extended Thinking

**Use for**: Complex math, multi-step coding, architectural decisions, detailed analysis, debugging intricate issues.

**Skip for**: Simple factual queries, basic classification, creative writing, latency-sensitive applications.

### Key Constraints

- `budget_tokens` must be less than `max_tokens`
- Incompatible with `temperature` and `top_k` modifications
- Cannot pre-fill responses when thinking is enabled
- Performs best in English; output can be in any supported language
- Summarized thinking is returned for Claude 4 models (full thinking for Claude 3.7)

## Prompting Tips for Extended Thinking

Give high-level instructions rather than prescriptive step-by-step guidance. The model's approach to problems may exceed a manually prescribed thinking process:

```text
Good: "Analyze this codebase for security vulnerabilities and propose
       a remediation plan."

Bad:  "Step 1: Read each file. Step 2: Check for SQL injection.
       Step 3: Check for XSS. Step 4: ..."
```

Do not pass Claude's thinking blocks back in user text blocks. This does not improve performance and may degrade results. Thinking blocks should only appear in assistant messages.

To get clean output without repeated reasoning:

```text
Provide only the final answer. Do not repeat your reasoning
in the response.
```

## Interleaved Thinking with Tool Use

Claude 4 models support interleaved thinking, which allows reasoning between tool calls. This enables more sophisticated decision-making after receiving tool results.

### Without Interleaved Thinking

```text
Turn 1: [thinking] + [tool_use: calculator]
  -> tool result: "7500"
Turn 2: [tool_use: database_query]  (no thinking)
  -> tool result: "5200"
Turn 3: [text: final answer]  (no thinking)
```

### With Interleaved Thinking

```text
Turn 1: [thinking: "I need to calculate first..."] + [tool_use: calculator]
  -> tool result: "7500"
Turn 2: [thinking: "Got $7,500. Now compare to average..."] + [tool_use: database_query]
  -> tool result: "5200"
Turn 3: [thinking: "$7,500 vs $5,200 = 44% increase..."] + [text: final answer]
```

Enable interleaved thinking with the beta header:

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[weather_tool],
    messages=[{"role": "user", "content": "..."}],
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    }
)
```

With interleaved thinking, `budget_tokens` can exceed `max_tokens` because the limit applies across all thinking blocks in the turn.

### Preserving Thinking Blocks

When using tool use with thinking, pass thinking blocks back unmodified in the assistant message:

```python
thinking_block = next(
    b for b in response.content if b.type == "thinking"
)
tool_use_block = next(
    b for b in response.content if b.type == "tool_use"
)

continuation = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    tools=[weather_tool],
    messages=[
        {"role": "user", "content": "What's the weather?"},
        {"role": "assistant", "content": [thinking_block, tool_use_block]},
        {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": "20°C, sunny"
        }]}
    ]
)
```

Do not rearrange or modify thinking blocks. The entire sequence must match the original model output.

### Toggling Thinking Mid-Turn

You cannot toggle thinking in the middle of a tool use loop. The entire assistant turn must operate in a single thinking mode. If a mid-turn conflict occurs, the API silently disables thinking for that request.

Plan your thinking strategy at the start of each turn rather than toggling mid-turn.

## The Think Tool Pattern

The think tool is a no-op tool that gives agents structured space to reason during multi-step workflows. Unlike extended thinking (which happens before the response), the think tool provides reasoning space mid-turn:

```python
think_tool = {
    "name": "think",
    "description": (
        "Use this tool to think about something. It will not "
        "obtain new information or change the database, but just "
        "append the thought to the log. Use it when complex "
        "reasoning or some cache memory is needed."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "thought": {
                "type": "string",
                "description": "Your reasoning or analysis"
            }
        },
        "required": ["thought"]
    }
}
```

The tool implementation does nothing -- it simply returns the thought as confirmation. The value comes from giving the model a structured place to reason between tool calls.

### Think Tool vs Extended Thinking

| Feature            | Extended Thinking                 | Think Tool                     |
| ------------------ | --------------------------------- | ------------------------------ |
| When it runs       | Before generating the response    | During response generation     |
| Depth of reasoning | Deep, comprehensive analysis      | Focused, situation-specific    |
| Best for           | Complex initial reasoning         | Reflecting on new tool results |
| Token cost         | Budget-controlled thinking tokens | Standard tool call tokens      |

For Claude 4 models with interleaved thinking support, extended thinking with interleaved thinking is generally preferred over the think tool, as it provides better integration. The think tool remains useful for other model providers or when extended thinking is unavailable.

### Pairing Think Tool with Optimized Prompts

The think tool performs best when paired with guidance on when to use it:

```text
You have access to a "think" tool. Use it to:
- Analyze whether tool results match expectations
- Plan multi-step sequences before executing
- Reconcile contradictory information from different sources
- Evaluate whether you have sufficient context to proceed
```

## Best Practices

1. Start with minimum thinking budgets and scale up based on task complexity
2. Use interleaved thinking for multi-tool workflows on Claude 4 models
3. Always preserve thinking blocks unmodified when passing them back with tool results
4. Do not pass thinking blocks back as user text -- this degrades performance
5. Use batch processing for thinking budgets above 32K tokens
6. Plan thinking strategy at the start of each turn; do not toggle mid-turn
7. Give high-level objectives rather than prescriptive reasoning steps
8. For non-Claude models, the think tool pattern provides similar mid-turn reasoning benefits
