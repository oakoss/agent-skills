---
title: Core Techniques
description: Chain-of-thought reasoning, few-shot examples, structured output, role prompting, step-by-step decomposition, self-consistency, and prompt chaining
tags:
  [
    chain-of-thought,
    few-shot,
    structured-output,
    role-prompting,
    prompt-chaining,
    self-consistency,
    XML-tags,
    decomposition,
  ]
---

# Core Techniques

## Chain-of-Thought (CoT)

Chain-of-thought prompting asks the model to show its reasoning before giving a final answer. This improves accuracy on math, logic, and multi-step reasoning tasks.

### Basic CoT

```text
Solve this problem. Think step by step before giving your final answer.

Problem: A store has 45 apples. They sell 3/5 of them in the morning and 1/3 of the remainder in the afternoon. How many apples are left?
```

### Structured CoT with XML Tags

```text
<problem>
A store has 45 apples. They sell 3/5 of them in the morning and 1/3 of the remainder in the afternoon. How many apples are left?
</problem>

<instructions>
1. Show your reasoning inside <thinking> tags
2. Give your final answer inside <answer> tags as a single number
</instructions>
```

### When CoT Helps vs Hurts

| Helps                              | Hurts or wastes tokens               |
| ---------------------------------- | ------------------------------------ |
| Math and arithmetic                | Simple factual recall                |
| Multi-step logic                   | Classification with clear categories |
| Code debugging and analysis        | Translation tasks                    |
| Complex reasoning with constraints | Short-form generation                |
| Ambiguous problems needing nuance  | Tasks where speed matters most       |

## Few-Shot Examples

Few-shot prompting provides input/output pairs so the model learns the expected pattern. The model matches the format, style, and reasoning of the examples.

### Selecting Good Examples

- **Diverse**: Cover different categories and edge cases
- **Representative**: Match the distribution of real inputs
- **Consistent format**: Identical structure across all examples
- **3-5 examples**: Enough to establish pattern, not so many they dominate context

### Format Pattern

```text
Classify the customer message as one of: billing, technical, account, other.

Message: "I can't log into my account after changing my password"
Category: account

Message: "The export feature crashes when I select PDF format"
Category: technical

Message: "Why was I charged twice this month?"
Category: billing

Message: "Can you add dark mode to the dashboard?"
Category: other

Message: "My payment method keeps getting declined"
Category:
```

### Few-Shot with Reasoning

Combine few-shot with CoT by including reasoning in examples:

```text
Determine if the code change is a bug fix, feature, or refactor.

Diff: "Changed variable name from `x` to `userCount`"
Reasoning: Renaming a variable without changing behavior is a structural improvement.
Classification: refactor

Diff: "Added null check before accessing user.email"
Reasoning: Prevents a crash when user object is undefined. Fixes incorrect behavior.
Classification: bug fix

Diff: "Added export-to-CSV button to the reports page"
Reasoning: New functionality that did not exist before.
Classification: feature

Diff: "Changed sort order from ascending to descending for recent items"
Reasoning:
Classification:
```

## Structured Output

Requesting structured output (JSON, XML, markdown) makes responses predictable and parseable.

### JSON Output

```text
Extract the following fields from the product review. Return valid JSON only.

Schema:
{
  "sentiment": "positive" | "negative" | "neutral",
  "rating": number (1-5),
  "key_topics": string[],
  "recommendation": boolean
}

Review: "Great laptop for the price. Battery life could be better but the keyboard is fantastic. Would recommend to students on a budget."
```

### XML Tags for Section Separation

XML tags prevent instruction blending and make parsing reliable:

```text
<context>
You are reviewing pull requests for a TypeScript project that uses React and Tailwind CSS.
</context>

<instructions>
Review the code diff below. For each issue found:
1. Identify the file and line
2. Classify severity as error, warning, or suggestion
3. Explain the issue and provide a fix
</instructions>

<output_format>
Return your review as a markdown list grouped by file.
</output_format>

<diff>
{diff content here}
</diff>
```

### Markdown Formatting

For human-readable structured output:

```text
Analyze this API endpoint and return your analysis using this exact format:

## Summary
One sentence describing the endpoint.

## Issues
- **[severity]** Description of each issue

## Recommendations
1. Numbered list of improvements
```

## Role and Persona Prompting

Setting a role establishes expertise context, vocabulary, and response depth.

### When Roles Help

| Role adds value                         | Role adds little                 |
| --------------------------------------- | -------------------------------- |
| Domain-specific terminology needed      | General knowledge questions      |
| Expert-level depth required             | Simple formatting tasks          |
| Specific communication style matters    | Binary yes/no decisions          |
| Professional standards must be followed | Tasks with explicit instructions |

### Role Prompting Pattern

```text
You are a senior database administrator with 15 years of PostgreSQL experience. You specialize in query optimization and indexing strategies.

When reviewing queries:
- Identify missing indexes based on WHERE and JOIN clauses
- Flag N+1 query patterns
- Suggest EXPLAIN ANALYZE for performance-critical queries
- Recommend connection pooling when appropriate
```

### Combining Role with Constraints

```text
You are a technical writer for developer documentation.

Writing style:
- Active voice, present tense
- Second person ("you") for instructions
- Code examples for every concept
- No marketing language or superlatives

Constraints:
- Maximum 200 words per explanation
- Every code block must be runnable as-is
- Include error handling in all examples
```

## Step-by-Step Decomposition

Breaking complex tasks into numbered steps reduces skipped instructions and improves compliance.

### Sequential Instructions

```text
Process this dataset by following these steps in order:

Step 1: Filter rows where status is "active"
Step 2: Group the filtered rows by department
Step 3: Calculate the average salary per department
Step 4: Sort departments by average salary, descending
Step 5: Return the top 5 departments as a markdown table
```

### Conditional Steps

```text
Analyze the error log and follow the appropriate path:

Step 1: Identify the error type (syntax, runtime, or network)

If syntax error:
  Step 2a: Show the exact line with the error
  Step 3a: Provide the corrected code

If runtime error:
  Step 2b: Identify the failing condition
  Step 3b: Suggest a defensive check or try-catch

If network error:
  Step 2c: Check the endpoint and status code
  Step 3c: Suggest retry logic with exponential backoff
```

## Self-Consistency

Generate multiple independent responses to the same prompt, then select the consensus answer. Useful for problems where a single attempt may go wrong.

### Pattern

```text
I need you to solve this problem 3 times independently. For each attempt, use a different approach if possible. Then compare your answers and give the one you are most confident in.

Problem: {problem}

Attempt 1:
Attempt 2:
Attempt 3:

Final answer (with confidence level):
```

### When to Use Self-Consistency

- Math problems where arithmetic errors are common
- Code review where multiple valid interpretations exist
- Classification tasks with ambiguous inputs
- Any task where you need higher confidence in correctness

## Prompt Chaining

Breaking complex tasks across multiple LLM calls, where each call focuses on one subtask. The output of one call feeds into the next.

### Chain Design Principles

- Each step should have a single, clear objective
- Pass only relevant output between steps (filter noise)
- Add validation between steps to catch errors early
- Keep the chain as short as possible

### Example Chain: Code Review Pipeline

```text
Step 1 (Extract):
"List all functions modified in this diff. For each, return the function name, file, and lines changed."

Step 2 (Analyze):
"For each function listed below, identify potential bugs, performance issues, and style violations: {step_1_output}"

Step 3 (Prioritize):
"Rank the following issues by severity. Group into must-fix, should-fix, and nice-to-have: {step_2_output}"

Step 4 (Format):
"Format these review comments as GitHub PR review comments with file, line, severity, and suggestion: {step_3_output}"
```

### When to Chain vs Single Prompt

| Chain (multiple calls)                    | Single prompt                         |
| ----------------------------------------- | ------------------------------------- |
| Task has distinct phases                  | Task is straightforward               |
| Intermediate results need validation      | Output format is simple               |
| Context window would be exceeded          | Everything fits in one context window |
| Different steps need different parameters | Same parameters work for all parts    |
| Debugging individual steps matters        | Speed is the priority                 |
