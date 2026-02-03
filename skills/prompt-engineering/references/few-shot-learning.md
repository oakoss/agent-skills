---
title: Few-Shot Learning
description: Example selection strategies, format consistency, token budget management, edge case handling, and prompt templates for classification, extraction, and transformation
tags:
  [
    few-shot,
    examples,
    semantic-similarity,
    diversity,
    token-budget,
    classification,
    extraction,
  ]
---

## Example Selection Strategies

### Semantic Similarity

Select examples most similar to the input query using embedding-based retrieval:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticExampleSelector:
    def __init__(self, examples, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.examples = examples
        self.example_embeddings = self.model.encode([ex['input'] for ex in examples])

    def select(self, query, k=3):
        query_embedding = self.model.encode([query])
        similarities = np.dot(self.example_embeddings, query_embedding.T).flatten()
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [self.examples[i] for i in top_indices]
```

Best for: Question answering, text classification, extraction tasks.

### Diversity Sampling

Maximize coverage of different patterns and edge cases using clustering:

```python
from sklearn.cluster import KMeans

class DiversityExampleSelector:
    def __init__(self, examples, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.examples = examples
        self.embeddings = self.model.encode([ex['input'] for ex in examples])

    def select(self, k=5):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(self.embeddings)

        diverse_examples = []
        for center in kmeans.cluster_centers_:
            distances = np.linalg.norm(self.embeddings - center, axis=1)
            closest_idx = np.argmin(distances)
            diverse_examples.append(self.examples[closest_idx])

        return diverse_examples
```

Best for: Demonstrating task variability, edge case handling.

### Difficulty-Based Selection

Gradually increase example complexity to scaffold learning:

```python
class ProgressiveExampleSelector:
    def __init__(self, examples):
        self.examples = sorted(examples, key=lambda x: x['difficulty'])

    def select(self, k=3):
        step = len(self.examples) // k
        return [self.examples[i * step] for i in range(k)]
```

Best for: Complex reasoning tasks, code generation.

## Format Consistency

All examples must follow identical formatting:

```python
# Good: Consistent format
examples = [
    {"input": "What is the capital of France?", "output": "Paris"},
    {"input": "What is the capital of Germany?", "output": "Berlin"}
]

# Bad: Inconsistent format
examples = [
    "Q: What is the capital of France? A: Paris",
    {"question": "What is the capital of Germany?", "answer": "Berlin"}
]
```

Include examples spanning the expected difficulty range:

```python
examples = [
    {"input": "2 + 2", "output": "4"},
    {"input": "15 * 3 + 8", "output": "53"},
    {"input": "(12 + 8) * 3 - 15 / 5", "output": "57"}
]
```

## Token Budget Management

Typical distribution for a 4K context window:

```text
System Prompt:        500 tokens  (12%)
Few-Shot Examples:   1500 tokens  (38%)
User Input:           500 tokens  (12%)
Response:            1500 tokens  (38%)
```

Dynamically truncate examples to fit the budget:

```python
class TokenAwareSelector:
    def __init__(self, examples, tokenizer, max_tokens=1500):
        self.examples = examples
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens

    def select(self, query, k=5):
        selected = []
        total_tokens = 0
        candidates = self.rank_by_relevance(query)

        for example in candidates[:k]:
            example_tokens = len(self.tokenizer.encode(
                f"Input: {example['input']}\nOutput: {example['output']}\n\n"
            ))

            if total_tokens + example_tokens <= self.max_tokens:
                selected.append(example)
                total_tokens += example_tokens
            else:
                break

        return selected
```

## Edge Case Handling

Include boundary examples to handle unexpected inputs:

```python
edge_case_examples = [
    {"input": "", "output": "Please provide input text."},
    {"input": "..." + "word " * 1000, "output": "Input exceeds maximum length."},
    {"input": "bank", "output": "Ambiguous: Could refer to financial institution or river bank."},
    {"input": "!@#$%", "output": "Invalid input format. Please provide valid text."}
]
```

## Prompt Templates

### Classification

```python
def build_classification_prompt(examples, query, labels):
    prompt = f"Classify the text into one of these categories: {', '.join(labels)}\n\n"
    for ex in examples:
        prompt += f"Text: {ex['input']}\nCategory: {ex['output']}\n\n"
    prompt += f"Text: {query}\nCategory:"
    return prompt
```

### Extraction

```python
def build_extraction_prompt(examples, query):
    prompt = "Extract structured information from the text.\n\n"
    for ex in examples:
        prompt += f"Text: {ex['input']}\nExtracted: {json.dumps(ex['output'])}\n\n"
    prompt += f"Text: {query}\nExtracted:"
    return prompt
```

### Transformation

```python
def build_transformation_prompt(examples, query):
    prompt = "Transform the input according to the pattern shown in examples.\n\n"
    for ex in examples:
        prompt += f"Input: {ex['input']}\nOutput: {ex['output']}\n\n"
    prompt += f"Input: {query}\nOutput:"
    return prompt
```

## Common Mistakes

1. **Too many examples**: More is not always better; can dilute focus
2. **Irrelevant examples**: Examples should match the target task closely
3. **Inconsistent formatting**: Confuses the model about expected output format
4. **Overfitting to examples**: Model copies patterns too literally
5. **Ignoring token limits**: Running out of space for actual input and response
