---
title: Tree-of-Thoughts
description: Parallel branch exploration, evaluation criteria, search algorithms, branch elimination, and final synthesis in Tree-of-Thoughts prompting
tags:
  [tree-of-thoughts, ToT, branching, evaluation, synthesis, parallel-reasoning]
---

## Core Structure

Tree-of-Thoughts (ToT) allows LLMs to explore multiple reasoning paths simultaneously, backtracking when a branch leads to a dead end.

1. **Thought Generation**: Propose multiple initial strategies for solving the problem
2. **State Evaluation**: Evaluate each strategy based on viability and potential
3. **Search Algorithm**: Deepen the most promising strategies (depth-first or breadth-first)

## Implementation Prompt

```text
Problem: [Insert complex problem]

1. Generate 3 distinct strategies to solve this.
2. For each strategy, identify one critical flaw.
3. Eliminate the strategy with the most severe flaw.
4. For the remaining strategies, generate 2 sub-steps each.
5. Synthesize the final solution by merging the best elements of the remaining paths.
```

## Python Implementation

```python
class TreeOfThought:
    def __init__(self, llm_client, max_depth=3, branches_per_step=3):
        self.client = llm_client
        self.max_depth = max_depth
        self.branches_per_step = branches_per_step

    def solve(self, problem):
        initial_thoughts = self.generate_thoughts(problem, depth=0)

        best_path = None
        best_score = -1

        for thought in initial_thoughts:
            path, score = self.explore_branch(problem, thought, depth=1)
            if score > best_score:
                best_score = score
                best_path = path

        return best_path

    def generate_thoughts(self, problem, context="", depth=0):
        prompt = f"""Problem: {problem}
{context}

Generate {self.branches_per_step} different next steps in solving this problem:

1."""
        response = self.client.complete(prompt)
        return self.parse_thoughts(response)

    def evaluate_thought(self, problem, thought_path):
        prompt = f"""Problem: {problem}

Reasoning path so far:
{thought_path}

Rate this reasoning path from 0-10 for:
- Correctness
- Likelihood of reaching solution
- Logical coherence

Score:"""
        return float(self.client.complete(prompt))
```

## Evaluation Criteria

Ask the model to act as a "Judge" for its own thoughts:

| Criterion         | Description                                               |
| ----------------- | --------------------------------------------------------- |
| Confidence Score  | Rate 1-10 how likely this path reaches a correct solution |
| Reasoning Gap     | What information is still missing?                        |
| Simulated Outcome | What happens if this path is executed?                    |
| Logical Coherence | Are the steps internally consistent?                      |
| Feasibility       | Can this strategy be implemented given constraints?       |

## When to Use ToT

- **Creative coding**: Designing novel algorithms or architectures
- **Strategic planning**: Evaluating market moves, product roadmaps, or tradeoffs
- **Complex debugging**: Finding race conditions or issues spanning multiple systems
- **Design decisions**: Comparing approaches with multiple valid solutions

### When NOT to Use ToT

- **Simple classification or summarization**: Overkill; use standard prompting
- **Tasks solvable by CoT**: ToT adds significant cost without proportional benefit
- **Latency-sensitive applications**: Each branch multiplies API calls and response time
- **Long-range planning**: ToT struggles with tasks requiring deep long-term exploration

### Cost Considerations

ToT is resource-intensive. Each branch requires separate model calls for generation and evaluation, multiplying token usage and latency. For a 3-branch, 3-depth tree, expect roughly 9-12x the cost of a single completion. Use ToT selectively for genuinely difficult problems where simpler methods fail.

## Merging Branches

Final synthesis is the most important step. The model must not simply pick one branch, but integrate the learnings from all explored paths:

```text
Given the explored reasoning paths:

Path A: [summary] - Strengths: [X], Weaknesses: [Y]
Path B: [summary] - Strengths: [X], Weaknesses: [Y]

Synthesize a final solution that:
1. Incorporates the strongest elements from each path
2. Avoids the identified weaknesses
3. Creates a coherent, unified approach
```

## Best Practices

1. Start with 3 branches (more adds latency without proportional quality)
2. Prune early and aggressively based on evaluation scores
3. Use structured evaluation criteria for consistent scoring
4. Always synthesize rather than simply selecting the best single branch
5. Log all explored branches for auditability and learning
