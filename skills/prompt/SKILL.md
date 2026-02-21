---
name: prompt
description: |
  Prompt engineering patterns for large language models. Covers chain-of-thought reasoning, few-shot examples, structured output formatting, system prompt design, context management, and prompt optimization techniques.

  Use when crafting system prompts, improving LLM output quality, structuring complex instructions, extracting structured data, or debugging inconsistent model responses.
license: MIT
metadata:
  author: oakoss
  version: '1.0'
---

# Prompt Engineering

## Overview

Prompt engineering is the practice of structuring inputs to large language models to produce reliable, high-quality outputs. It spans techniques from simple instruction formatting to multi-step reasoning chains and structured output extraction.

**When to use:** Crafting system prompts, extracting structured data from free text, improving reasoning accuracy, reducing hallucinations, building LLM-powered features, or debugging inconsistent model behavior.

**When NOT to use:** Tasks better solved with traditional programming (deterministic logic, exact string matching), problems requiring real-time data (use tool calls instead), or situations where a simpler heuristic outperforms LLM inference.

## Quick Reference

| Technique              | Pattern                                            | Key Points                                      |
| ---------------------- | -------------------------------------------------- | ----------------------------------------------- |
| Chain-of-thought       | "Think step by step before answering"              | Improves math, logic, multi-step reasoning      |
| Few-shot examples      | Provide 3-5 input/output pairs                     | Format consistently, cover edge cases           |
| Structured output      | Request JSON/XML with schema                       | Enforce with schema validation post-generation  |
| Role prompting         | "You are an expert in..."                          | Sets expertise context and response style       |
| Step-by-step           | Number sequential instructions                     | Reduces skipped steps, improves compliance      |
| XML/markdown structure | Use tags or headings to separate sections          | Prevents instruction blending, improves parsing |
| Prompt chaining        | Break complex tasks across multiple LLM calls      | Each call focused, easier to debug              |
| Self-consistency       | Generate multiple responses, pick consensus        | Higher accuracy for ambiguous problems          |
| Context prioritization | Instructions first, context second, examples last  | Models weight early tokens more heavily         |
| Temperature control    | Low (0-0.3) for factual, high (0.7-1) for creative | Match sampling to task requirements             |

## Common Mistakes

| Mistake                                      | Correct Pattern                                             |
| -------------------------------------------- | ----------------------------------------------------------- |
| Burying key instructions at the end          | Place critical instructions at the start of the prompt      |
| Asking for multiple unrelated tasks at once  | One task per prompt, chain if needed                        |
| No output format specification               | Explicitly define expected format (JSON, bullet list, etc.) |
| Vague instructions ("make it better")        | Specific criteria ("fix grammar, keep tone informal")       |
| Too many few-shot examples (10+)             | 3-5 diverse examples covering edge cases                    |
| Ignoring negative constraints                | State what NOT to do alongside what to do                   |
| Not testing with adversarial inputs          | Include edge cases and boundary conditions in testing       |
| Using temperature 1.0 for factual tasks      | Use low temperature (0-0.3) for deterministic outputs       |
| Repeating instructions verbatim for emphasis | Rephrase or restructure instead of repeating                |
| No fallback for uncertain responses          | Instruct model to say "I don't know" when uncertain         |

## Delegation

- **Prompt exploration**: Use `Explore` agent to research patterns across codebases
- **Prompt review**: Use `Task` agent to evaluate prompt effectiveness
- **Code review**: Delegate to `code-reviewer` agent for prompt integration code

> If the `expert-instruction` skill is available, delegate system prompt design and agent persona crafting to it.
> Otherwise, recommend: `pnpm dlx skills add oakoss/agent-skills -s expert-instruction -a claude-code -y`

## References

- [Core techniques: CoT, few-shot, structured output, and more](references/core-techniques.md)
- [Optimization and debugging: iteration, failure modes, and caching](references/optimization-and-debugging.md)
