---
name: prompt
description: 'Prompt engineering and agentic orchestration patterns. Use when crafting prompts for reasoning models, implementing chain-of-thought or Tree-of-Thoughts, designing ReAct loops, building few-shot examples, optimizing prompt performance, or structuring system prompts. Use for prompt templates, multi-step agent workflows, and structured thinking protocols.'
---

# Prompt Engineering

Advanced prompt design for LLMs and autonomous agents. Covers reasoning patterns, template systems, optimization workflows, and agentic orchestration.

**When to use**: Designing prompts that require structured reasoning, building agent loops, optimizing LLM output quality, or creating reusable prompt templates.

**When NOT to use**: Simple factual queries, direct lookups, or creative writing that benefits from open-ended generation.

## Quick Reference

| Pattern             | API / Technique                           | Key Point                               |
| ------------------- | ----------------------------------------- | --------------------------------------- |
| Zero-shot CoT       | `"Let's think step by step"` trigger      | Elicits reasoning without examples      |
| Few-shot CoT        | Explicit reasoning chain examples         | One good example beats many rules       |
| Self-consistency    | Multiple paths + majority vote            | Higher accuracy on complex tasks        |
| Tree-of-Thoughts    | Generate 3+ strategies, eliminate weakest | Parallel exploration with pruning       |
| ReAct loop          | Thought-Action-Observation cycle          | Agent reasons and acts in unison        |
| System prompt       | Role + Expertise + Guidelines + Format    | Foundation for all LLM behavior         |
| Prompt template     | Modular composition with variable slots   | Reusable, validated, cacheable          |
| A/B testing         | Statistical comparison of prompt variants | Isolate variables, measure significance |
| Reasoning models    | Objective-based prompting for o3/Pro      | Let the model plan its own reasoning    |
| Structured thinking | Understanding-Analysis-Execution protocol | Forces verification before acting       |
| Confidence scoring  | Model self-reports certainty per claim    | Quantifies reliability of output        |
| Token optimization  | Compress context, remove filler words     | Reduce latency and cost                 |

## Common Mistakes

| Mistake                                                | Correct Pattern                                                 |
| ------------------------------------------------------ | --------------------------------------------------------------- |
| Overloading a single prompt with too many instructions | Use hierarchical rules with clear priority ordering             |
| Forcing rigid step-by-step on reasoning models         | Use objective-based prompts; reasoning models plan natively     |
| Setting maxOutputTokens too low for reasoning models   | Allocate sufficient tokens for internal chain-of-thought        |
| Using static examples for complex tasks                | Select examples dynamically via semantic similarity             |
| Inconsistent formatting across few-shot examples       | All examples must follow identical input-output structure       |
| Manually parsing unstructured LLM output               | Use ResponseSchema (JSON mode) for structured output            |
| Ignoring token budget allocation                       | Reserve tokens for system prompt, examples, input, and response |
| Skipping baseline measurement before optimizing        | Establish metrics first, then change one variable at a time     |

## Delegation

- **Explore prompt variants and compare model responses**: Use `Explore` agent to test prompt strategies across different inputs
- **Build multi-step agentic workflows with tool use**: Use `Task` agent to implement and validate ReAct loops and autonomous chains
- **Design hierarchical prompt architecture for complex systems**: Use `Plan` agent to structure prompt systems with verification loops

## References

- [Chain-of-Thought](references/chain-of-thought.md) -- Step-by-step reasoning, self-consistency, least-to-most decomposition
- [Few-Shot Learning](references/few-shot-learning.md) -- Example selection strategies, token-aware truncation, edge cases
- [Prompt Templates](references/prompt-templates.md) -- Template architecture, modular composition, validation, caching
- [Prompt Optimization](references/prompt-optimization.md) -- A/B testing, failure analysis, metrics, version control
- [System Prompts](references/system-prompts.md) -- Role definition, constraint specification, dynamic adaptation
- [Reasoning Model Optimization](references/reasoning-model-optimization.md) -- Objective-based prompting for o3, deep research triggers
- [Tree-of-Thoughts](references/tree-of-thoughts.md) -- Parallel branch exploration, evaluation, synthesis
- [ReAct Patterns](references/react-patterns.md) -- Thought-Action-Observation loop, tool discovery, error recovery
- [Structured Thinking](references/structured-thinking.md) -- Adversarial critic protocol, confidence scoring, metadata tagging
