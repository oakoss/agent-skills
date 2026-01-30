---
title: Chain-of-Thought
description: Step-by-step reasoning, self-consistency voting, least-to-most decomposition, verification, and domain-specific CoT templates
tags:
  [
    chain-of-thought,
    reasoning,
    self-consistency,
    verification,
    least-to-most,
    CoT,
  ]
---

## Zero-Shot CoT

Add a trigger phrase to elicit step-by-step reasoning without examples:

```python
def zero_shot_cot(query):
    return f"""{query}

Let's think step by step:"""
```

The model outputs numbered reasoning steps followed by a final answer.

## Few-Shot CoT

Provide examples with explicit reasoning chains:

```python
few_shot_examples = """
Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls. Each can has 3 balls. How many tennis balls does he have now?
A: Let's think step by step:
1. Roger starts with 5 balls
2. He buys 2 cans, each with 3 balls
3. Balls from cans: 2 x 3 = 6 balls
4. Total: 5 + 6 = 11 balls
Answer: 11

Q: The cafeteria had 23 apples. If they used 20 to make lunch and bought 6 more, how many do they have?
A: Let's think step by step:
1. Started with 23 apples
2. Used 20 for lunch: 23 - 20 = 3 apples left
3. Bought 6 more: 3 + 6 = 9 apples
Answer: 9

Q: {user_query}
A: Let's think step by step:"""
```

## Self-Consistency

Generate multiple reasoning paths and take the majority vote for higher accuracy:

```python
from collections import Counter

def self_consistency_cot(query, n=5, temperature=0.7):
    prompt = f"{query}\n\nLet's think step by step:"

    responses = []
    for _ in range(n):
        response = llm.complete(prompt, temperature=temperature)
        responses.append(extract_final_answer(response))

    answer_counts = Counter(responses)
    final_answer = answer_counts.most_common(1)[0][0]

    return {
        'answer': final_answer,
        'confidence': answer_counts[final_answer] / n,
        'all_responses': responses
    }
```

## Least-to-Most Prompting

Break complex problems into simpler subproblems, solving sequentially:

```python
def least_to_most_prompt(complex_query):
    decomp_prompt = f"""Break down this complex problem into simpler subproblems:

Problem: {complex_query}

Subproblems:"""

    subproblems = get_llm_response(decomp_prompt)

    solutions = []
    context = ""

    for subproblem in subproblems:
        solve_prompt = f"""{context}

Solve this subproblem:
{subproblem}

Solution:"""
        solution = get_llm_response(solve_prompt)
        solutions.append(solution)
        context += f"\n\nPreviously solved: {subproblem}\nSolution: {solution}"

    final_prompt = f"""Given these solutions to subproblems:
{context}

Provide the final answer to: {complex_query}

Final Answer:"""

    return get_llm_response(final_prompt)
```

## Verification Step

Add explicit verification to catch reasoning errors:

```python
def cot_with_verification(query):
    reasoning_response = get_llm_response(
        f"{query}\n\nLet's solve this step by step:"
    )

    verification_prompt = f"""Original problem: {query}

Proposed solution:
{reasoning_response}

Verify this solution by:
1. Checking each step for logical errors
2. Verifying arithmetic calculations
3. Ensuring the final answer makes sense

Is this solution correct? If not, what's wrong?

Verification:"""

    verification = get_llm_response(verification_prompt)

    if "incorrect" in verification.lower() or "error" in verification.lower():
        revision_prompt = f"""The previous solution had errors:
{verification}

Please provide a corrected solution to: {query}

Corrected solution:"""
        return get_llm_response(revision_prompt)

    return reasoning_response
```

## Domain-Specific Templates

### Math Problems

```python
math_cot_template = """
Problem: {problem}

Solution:
Step 1: Identify what we know
- {list_known_values}

Step 2: Identify what we need to find
- {target_variable}

Step 3: Choose relevant formulas
- {formulas}

Step 4: Substitute values
- {substitution}

Step 5: Calculate
- {calculation}

Step 6: Verify and state answer
- {verification}

Answer: {final_answer}
"""
```

### Code Debugging

```python
debug_cot_template = """
Code with error:
{code}

Error message:
{error}

Debugging process:
Step 1: Understand the error message
- {interpret_error}

Step 2: Locate the problematic line
- {identify_line}

Step 3: Analyze why this line fails
- {root_cause}

Step 4: Determine the fix
- {proposed_fix}

Step 5: Verify the fix addresses the error
- {verification}

Fixed code:
{corrected_code}
"""
```

## Adaptive Reasoning Depth

Dynamically increase reasoning depth until the solution is complete:

```python
def adaptive_cot(problem, initial_depth=3):
    depth = initial_depth

    while depth <= 10:
        response = generate_cot(problem, num_steps=depth)

        if is_solution_complete(response):
            return response

        depth += 2

    return response
```

## When to Use CoT

**Use CoT for**: Math and arithmetic, logical reasoning, multi-step planning, code generation, complex decision making.

**Skip CoT for**: Simple factual queries, direct lookups, creative writing, latency-sensitive applications.

## Best Practices

1. Use numbered steps or clear delimiters as step markers
2. Show all work -- do not skip intermediate steps
3. Add explicit verification steps for critical tasks
4. State all assumptions explicitly
5. Consider boundary conditions and edge cases
6. Provide reasoning pattern examples before the actual query
