---
title: Prompt Optimization
description: Systematic refinement workflow, A/B testing framework, failure analysis, performance metrics, token and latency optimization, and version control
tags:
  [
    optimization,
    A/B-testing,
    metrics,
    failure-analysis,
    versioning,
    latency,
    accuracy,
  ]
---

## Systematic Refinement Process

### Baseline Establishment

Always measure initial performance before optimizing:

```python
def establish_baseline(prompt, test_cases):
    results = {
        'accuracy': 0,
        'avg_tokens': 0,
        'avg_latency': 0,
        'success_rate': 0
    }

    for test_case in test_cases:
        response = llm.complete(prompt.format(**test_case['input']))
        results['accuracy'] += evaluate_accuracy(response, test_case['expected'])
        results['avg_tokens'] += count_tokens(response)
        results['avg_latency'] += measure_latency(response)
        results['success_rate'] += is_valid_response(response)

    n = len(test_cases)
    return {k: v/n for k, v in results.items()}
```

### Iterative Refinement

```text
Initial Prompt -> Test -> Analyze Failures -> Refine -> Test -> Repeat
```

```python
class PromptOptimizer:
    def __init__(self, initial_prompt, test_suite):
        self.prompt = initial_prompt
        self.test_suite = test_suite
        self.history = []

    def optimize(self, max_iterations=10):
        for i in range(max_iterations):
            results = self.evaluate_prompt(self.prompt)
            self.history.append({
                'iteration': i,
                'prompt': self.prompt,
                'results': results
            })

            if results['accuracy'] > 0.95:
                break

            failures = self.analyze_failures(results)
            refinements = self.generate_refinements(failures)
            self.prompt = self.select_best_refinement(refinements)

        return self.get_best_prompt()
```

## A/B Testing Framework

```python
class PromptABTest:
    def __init__(self, variant_a, variant_b):
        self.variant_a = variant_a
        self.variant_b = variant_b

    def run_test(self, test_queries, metrics=['accuracy', 'latency']):
        results = {
            'A': {m: [] for m in metrics},
            'B': {m: [] for m in metrics}
        }

        for query in test_queries:
            variant = 'A' if random.random() < 0.5 else 'B'
            prompt = self.variant_a if variant == 'A' else self.variant_b

            response, metrics_data = self.execute_with_metrics(
                prompt.format(query=query['input'])
            )

            for metric in metrics:
                results[variant][metric].append(metrics_data[metric])

        return self.analyze_results(results)

    def analyze_results(self, results):
        from scipy import stats

        analysis = {}
        for metric in results['A'].keys():
            a_values = results['A'][metric]
            b_values = results['B'][metric]
            t_stat, p_value = stats.ttest_ind(a_values, b_values)

            analysis[metric] = {
                'A_mean': np.mean(a_values),
                'B_mean': np.mean(b_values),
                'statistically_significant': p_value < 0.05,
                'winner': 'B' if np.mean(b_values) > np.mean(a_values) else 'A'
            }

        return analysis
```

## Optimization Strategies

### Token Reduction

```python
def optimize_for_tokens(prompt):
    optimizations = [
        ('in order to', 'to'),
        ('due to the fact that', 'because'),
        ('at this point in time', 'now'),
        (' actually ', ' '),
        (' basically ', ' '),
        (' really ', ' ')
    ]

    optimized = prompt
    for old, new in optimizations:
        optimized = optimized.replace(old, new)
    return optimized
```

### Common Optimization Patterns

```text
Add Structure:   "Analyze this text" -> "Analyze for: 1. Main topic 2. Key arguments 3. Conclusion"
Add Examples:    "Extract entities" -> "Extract entities\n\nExample:\nText: Apple released iPhone\nEntities: {company: Apple, product: iPhone}"
Add Constraints: "Summarize this" -> "Summarize in exactly 3 bullet points, 15 words each"
Add Verification: "Calculate..." -> "Calculate... Then verify your calculation is correct before responding."
```

## Failure Analysis

```python
class FailureAnalyzer:
    def categorize_failures(self, test_results):
        categories = {
            'format_errors': [],
            'factual_errors': [],
            'logic_errors': [],
            'incomplete_responses': [],
            'hallucinations': [],
            'off_topic': []
        }

        for result in test_results:
            if not result['success']:
                category = self.determine_failure_type(
                    result['response'],
                    result['expected']
                )
                categories[category].append(result)

        return categories

    def generate_fixes(self, categorized_failures):
        fixes = []

        if categorized_failures['format_errors']:
            fixes.append({
                'issue': 'Format errors',
                'fix': 'Add explicit format examples and constraints',
                'priority': 'high'
            })

        if categorized_failures['hallucinations']:
            fixes.append({
                'issue': 'Hallucinations',
                'fix': 'Add grounding: "Base your answer only on provided context"',
                'priority': 'critical'
            })

        if categorized_failures['incomplete_responses']:
            fixes.append({
                'issue': 'Incomplete responses',
                'fix': 'Add: "Ensure your response fully addresses all parts"',
                'priority': 'medium'
            })

        return fixes
```

## Performance Metrics

```python
class PromptMetrics:
    @staticmethod
    def accuracy(responses, ground_truth):
        return sum(r == gt for r, gt in zip(responses, ground_truth)) / len(responses)

    @staticmethod
    def consistency(responses):
        from collections import defaultdict, Counter
        input_responses = defaultdict(list)

        for inp, resp in responses:
            input_responses[inp].append(resp)

        consistency_scores = []
        for inp, resps in input_responses.items():
            if len(resps) > 1:
                most_common_count = Counter(resps).most_common(1)[0][1]
                consistency_scores.append(most_common_count / len(resps))

        return np.mean(consistency_scores) if consistency_scores else 1.0

    @staticmethod
    def latency_p95(latencies):
        return np.percentile(latencies, 95)
```

## Common Failure Modes

### Model Ignores Instructions

**Symptoms:** Output does not follow specified format, skips steps, or ignores constraints.

| Cause                             | Fix                                                             |
| --------------------------------- | --------------------------------------------------------------- |
| Instruction buried in long text   | Move to the top of the prompt                                   |
| Competing instructions            | Remove contradictions, simplify                                 |
| Too many instructions at once     | Break into numbered steps or chain multiple calls               |
| Instruction phrased as suggestion | Use imperative voice: "Return JSON" not "You could return JSON" |
| Examples contradict instructions  | Ensure examples match the stated rules exactly                  |

### Hallucination Triggers

**Symptoms:** Model fabricates facts, invents API methods, or generates plausible-sounding nonsense.

| Trigger                              | Mitigation                                    |
| ------------------------------------ | --------------------------------------------- |
| Asking about niche or recent topics  | Provide source material in context            |
| "Tell me everything about X"         | Ask specific, bounded questions               |
| No escape hatch for uncertainty      | Add: "If unsure, say so rather than guessing" |
| Requesting citations without sources | Provide documents to cite from                |
| Asking model to recall exact numbers | Provide the data, ask model to analyze it     |

### Inconsistent Formatting

**Symptoms:** Output format varies across runs despite identical prompts.

- Provide an exact output template with placeholders
- Use JSON mode or structured output APIs when available
- Add a few-shot example showing the exact format expected
- Validate output programmatically and retry on format violations

## Temperature and Sampling

Temperature controls randomness in token selection. Match it to the task.

| Temperature | Use for                                    | Characteristics           |
| ----------- | ------------------------------------------ | ------------------------- |
| 0           | Deterministic tasks, unit tests, JSON      | Same output every time    |
| 0.1-0.3     | Code generation, factual Q&A, data parsing | Slight variation, focused |
| 0.4-0.7     | General writing, summarization, analysis   | Balanced creativity       |
| 0.8-1.0     | Brainstorming, creative writing, ideation  | High variety              |

Other parameters: **top_p** (nucleus sampling, use one or the other with temperature), **max_tokens** (set reasonable limit with 20% buffer), **stop sequences** (explicit stopping points).

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

- Place stable content (system prompt, few-shot examples) in cacheable blocks
- Keep dynamic content (user query, variable context) outside cached blocks
- Cached input tokens are typically 90% cheaper than uncached
- Cache has a TTL (usually 5 minutes for ephemeral) and refreshes on hit

## Best Practices

1. **Establish baseline**: Always measure initial performance
2. **Change one thing**: Isolate variables for clear attribution
3. **Test thoroughly**: Use diverse, representative test cases
4. **Validate significance**: Use statistical tests for A/B comparisons
5. **Version everything**: Enable rollback to previous versions
6. **Monitor production**: Continuously evaluate deployed prompts
