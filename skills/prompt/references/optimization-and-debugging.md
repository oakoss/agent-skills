---
title: Optimization and Debugging
description: Prompt iteration workflow, failure modes, context window management, temperature tuning, prompt caching, and A/B testing
tags:
  [
    optimization,
    debugging,
    context-window,
    temperature,
    caching,
    iteration,
    hallucination,
    failure-modes,
  ]
---

# Optimization and Debugging

## Prompt Iteration Workflow

Effective prompt engineering follows a systematic cycle, not ad-hoc tweaking.

### The Iteration Loop

```text
1. Baseline  → Write initial prompt, run on test inputs
2. Measure   → Score outputs against success criteria
3. Diagnose  → Identify failure patterns (see failure modes below)
4. Adjust    → Make ONE targeted change per iteration
5. Re-measure → Compare against baseline on the SAME test inputs
6. Repeat    → Until quality threshold is met
```

### Key Principles

- **Change one thing at a time** so you know what caused improvement
- **Keep a test set** of 10-20 representative inputs including edge cases
- **Track versions** with a simple log: version number, change made, score
- **Measure before optimizing**: a prompt that works 95% of the time may not need tuning

### Scoring Checklist

Define pass/fail criteria before iterating:

```text
- [ ] Correct answer / output
- [ ] Follows specified format exactly
- [ ] No hallucinated facts or fabricated references
- [ ] Appropriate length (not too verbose, not too terse)
- [ ] Handles edge cases (empty input, unusual formatting)
```

## Common Failure Modes

### Model Ignores Instructions

**Symptoms:** Output does not follow specified format, skips steps, or ignores constraints.

**Causes and fixes:**

| Cause                             | Fix                                                             |
| --------------------------------- | --------------------------------------------------------------- |
| Instruction buried in long text   | Move to the top of the prompt                                   |
| Competing instructions            | Remove contradictions, simplify                                 |
| Too many instructions at once     | Break into numbered steps or chain multiple calls               |
| Instruction phrased as suggestion | Use imperative voice: "Return JSON" not "You could return JSON" |
| Examples contradict instructions  | Ensure examples match the stated rules exactly                  |

### Hallucination Triggers

**Symptoms:** Model fabricates facts, invents API methods, or generates plausible-sounding nonsense.

**Common triggers and mitigations:**

| Trigger                              | Mitigation                                    |
| ------------------------------------ | --------------------------------------------- |
| Asking about niche or recent topics  | Provide source material in context            |
| "Tell me everything about X"         | Ask specific, bounded questions               |
| No escape hatch for uncertainty      | Add: "If unsure, say so rather than guessing" |
| Requesting citations without sources | Provide documents to cite from                |
| Asking model to recall exact numbers | Provide the data, ask model to analyze it     |

### Inconsistent Formatting

**Symptoms:** Output format varies across runs despite identical prompts.

**Fixes:**

- Provide an exact output template with placeholders
- Use JSON mode or structured output APIs when available
- Add a few-shot example showing the exact format expected
- Validate output programmatically and retry on format violations

## Context Window Management

Models have finite context windows. What you include and where you place it directly affects output quality.

### Priority Ordering

```text
┌──────────────────────────────────┐
│  1. System instructions          │  ← Highest weight
│  2. Critical constraints         │
│  3. Output format specification  │
│  4. Relevant context / documents │
│  5. Few-shot examples            │
│  6. User query                   │  ← Recency boost
└──────────────────────────────────┘
```

Models attend more strongly to content at the **beginning** and **end** of the context. The middle gets less attention (the "lost in the middle" effect).

### What to Include vs Exclude

| Include                                | Exclude                                  |
| -------------------------------------- | ---------------------------------------- |
| Directly relevant context              | Background info the model already knows  |
| Specific constraints and format rules  | Verbose explanations of obvious concepts |
| Examples that demonstrate edge cases   | Duplicate or near-duplicate examples     |
| Error messages and stack traces (full) | Entire files when only a section matters |

### Trimming Strategies

- **Summarize long documents** before including them as context
- **Extract relevant sections** rather than including entire files
- **Remove boilerplate** (license headers, import blocks) from code context
- **Use references** ("as shown in the schema above") instead of repeating content

## Temperature and Sampling

Temperature controls randomness in token selection. Match it to the task.

### Temperature Guidelines

| Temperature | Use for                                    | Characteristics           |
| ----------- | ------------------------------------------ | ------------------------- |
| 0           | Deterministic tasks, unit tests, JSON      | Same output every time    |
| 0.1-0.3     | Code generation, factual Q&A, data parsing | Slight variation, focused |
| 0.4-0.7     | General writing, summarization, analysis   | Balanced creativity       |
| 0.8-1.0     | Brainstorming, creative writing, ideation  | High variety              |

### Other Sampling Parameters

- **top_p (nucleus sampling)**: Alternative to temperature. Use one or the other, not both. `top_p: 0.9` keeps the top 90% probability mass.
- **max_tokens**: Set a reasonable limit to prevent runaway generation. Estimate expected output length and add 20% buffer.
- **stop sequences**: Define explicit stopping points to prevent extra output.

## Prompt Caching

Repeated system prompts consume tokens on every request. Caching reduces cost and latency.

### Anthropic Cache Control Pattern

```ts
const response = await anthropic.messages.create({
  model: 'claude-sonnet-4-20250514',
  max_tokens: 1024,
  system: [
    {
      type: 'text',
      text: longSystemPrompt,
      cache_control: { type: 'ephemeral' },
    },
  ],
  messages: [{ role: 'user', content: userQuery }],
});
```

### Caching Best Practices

- Place stable content (system prompt, few-shot examples) in cacheable blocks
- Keep dynamic content (user query, variable context) outside cached blocks
- Cache breakpoints require minimum token thresholds (check provider docs)
- Monitor cache hit rates to verify caching is effective

### Cost Impact

- Cached input tokens are typically 90% cheaper than uncached
- First request pays full price (cache write), subsequent requests benefit
- Cache has a TTL (usually 5 minutes for ephemeral) and refreshes on hit

## A/B Testing Prompts

Comparing prompt variants systematically rather than relying on intuition.

### Testing Framework

```text
1. Define success metric (accuracy, format compliance, user rating)
2. Create test set of 20+ representative inputs
3. Run variant A (baseline) and variant B (candidate) on all inputs
4. Score each output against success metric
5. Compare aggregate scores
6. Deploy winner, archive loser with notes
```

### What to Test

| Variable              | Example variants                          |
| --------------------- | ----------------------------------------- |
| Instruction placement | Start vs end of prompt                    |
| Level of detail       | Terse instructions vs detailed breakdown  |
| Number of examples    | 2 vs 5 few-shot examples                  |
| Output format         | JSON vs markdown vs plain text            |
| Reasoning inclusion   | With CoT vs without CoT                   |
| Constraint style      | Positive ("do X") vs negative ("don't Y") |

## Debugging Bad Outputs

When a prompt produces incorrect or unexpected results, diagnose systematically.

### Diagnostic Technique: Show Reasoning

Add "explain your reasoning step by step" temporarily to see where the model goes wrong:

```text
{original prompt}

Before giving your final answer, explain your reasoning step by step inside <reasoning> tags. Then give your answer inside <answer> tags.
```

### Debugging Checklist

```text
1. Is the instruction clear and unambiguous?
   → Read it as if you have no context. Would you know what to do?

2. Does the output format match what you asked for?
   → Check for format spec vs actual output mismatch

3. Are examples consistent with instructions?
   → Examples override instructions when they conflict

4. Is relevant context actually in the prompt?
   → Models cannot access information not provided

5. Is the task too complex for a single prompt?
   → Break into a chain if the model consistently misses steps

6. Is temperature appropriate?
   → Lower temperature for tasks requiring precision
```

### Common Debug Patterns

| Symptom                | Likely cause                 | Quick fix                                 |
| ---------------------- | ---------------------------- | ----------------------------------------- |
| Wrong format           | No format example provided   | Add one concrete output example           |
| Partial completion     | Too many steps in one prompt | Chain into multiple calls                 |
| Contradictory output   | Conflicting instructions     | Audit prompt for contradictions           |
| Overly verbose         | No length constraint         | Add "Maximum N sentences" or "Be concise" |
| Refuses valid request  | Overly broad safety phrasing | Narrow constraint scope                   |
| Fabricates information | Asked to recall without data | Provide source material in context        |
