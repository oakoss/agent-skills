---
title: Quality Control
description: Automated quality metrics, retrieval testing, drift detection, quality dashboards, and continuous monitoring for knowledge bases
tags:
  [
    knowledge-base,
    quality,
    validation,
    metrics,
    monitoring,
    testing,
    drift-detection,
    recall,
  ]
---

# Quality Control

## Quality Metrics

| Metric         | Description                         | Target   |
| -------------- | ----------------------------------- | -------- |
| Accuracy       | % correct answers to test questions | >90%     |
| Coverage       | % user questions answerable         | >80%     |
| Freshness      | Average age of knowledge            | <30 days |
| Consistency    | % without conflicts/contradictions  | >95%     |
| Source quality | % from authoritative sources        | >90%     |

## Automated Quality Metrics

### Accuracy Sampling

```ts
interface TestQuestion {
  question: string;
  expectedAnswer: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
}

interface AccuracyResult {
  totalQuestions: number;
  correctCount: number;
  accuracy: number;
  failures: Array<{
    question: string;
    expected: string;
    actual: string;
    similarity: number;
  }>;
}

async function measureAccuracy(
  testSet: TestQuestion[],
  queryFn: (question: string) => Promise<string>,
  similarityFn: (a: string, b: string) => Promise<number>,
  threshold = 0.8,
): Promise<AccuracyResult> {
  const failures: AccuracyResult['failures'] = [];
  let correctCount = 0;

  for (const test of testSet) {
    const actual = await queryFn(test.question);
    const similarity = await similarityFn(test.expectedAnswer, actual);

    if (similarity >= threshold) {
      correctCount++;
    } else {
      failures.push({
        question: test.question,
        expected: test.expectedAnswer,
        actual,
        similarity,
      });
    }
  }

  return {
    totalQuestions: testSet.length,
    correctCount,
    accuracy: correctCount / testSet.length,
    failures,
  };
}
```

### Coverage Measurement

```ts
interface CoverageResult {
  totalQueries: number;
  answeredCount: number;
  coverage: number;
  unanswered: Array<{
    query: string;
    topScore: number;
  }>;
}

async function measureCoverage(
  userQueries: string[],
  searchFn: (
    query: string,
  ) => Promise<Array<{ content: string; score: number }>>,
  relevanceThreshold = 0.7,
): Promise<CoverageResult> {
  const unanswered: CoverageResult['unanswered'] = [];
  let answeredCount = 0;

  for (const query of userQueries) {
    const results = await searchFn(query);
    const topScore = results[0]?.score ?? 0;

    if (topScore >= relevanceThreshold) {
      answeredCount++;
    } else {
      unanswered.push({ query, topScore });
    }
  }

  return {
    totalQueries: userQueries.length,
    answeredCount,
    coverage: answeredCount / userQueries.length,
    unanswered,
  };
}
```

### Freshness Scoring

```ts
interface FreshnessResult {
  totalDocuments: number;
  averageAgeDays: number;
  staleCount: number;
  staleDocuments: Array<{
    id: string;
    title: string;
    ageDays: number;
    lastUpdated: string;
  }>;
}

async function measureFreshness(
  documents: Array<{ id: string; title: string; updatedAt: string }>,
  maxAgeDays = 30,
): Promise<FreshnessResult> {
  const now = Date.now();
  const staleDocuments: FreshnessResult['staleDocuments'] = [];
  let totalAge = 0;

  for (const doc of documents) {
    const ageDays = (now - new Date(doc.updatedAt).getTime()) / 86_400_000;
    totalAge += ageDays;

    if (ageDays > maxAgeDays) {
      staleDocuments.push({
        id: doc.id,
        title: doc.title,
        ageDays: Math.round(ageDays),
        lastUpdated: doc.updatedAt,
      });
    }
  }

  return {
    totalDocuments: documents.length,
    averageAgeDays: Math.round(totalAge / documents.length),
    staleCount: staleDocuments.length,
    staleDocuments,
  };
}
```

## Retrieval Quality Testing

Test suite pattern: query known answers and measure recall at K.

```ts
interface RetrievalTestCase {
  query: string;
  relevantDocIds: string[];
}

interface RetrievalMetrics {
  meanRecallAtK: number;
  meanPrecisionAtK: number;
  meanReciprocalRank: number;
  perQuery: Array<{
    query: string;
    recallAtK: number;
    precisionAtK: number;
    reciprocalRank: number;
  }>;
}

async function evaluateRetrieval(
  testCases: RetrievalTestCase[],
  searchFn: (query: string) => Promise<Array<{ id: string; score: number }>>,
  k = 10,
): Promise<RetrievalMetrics> {
  const perQuery: RetrievalMetrics['perQuery'] = [];

  for (const tc of testCases) {
    const results = await searchFn(tc.query);
    const topK = results.slice(0, k);
    const retrievedIds = new Set(topK.map((r) => r.id));
    const relevantSet = new Set(tc.relevantDocIds);

    const hits = topK.filter((r) => relevantSet.has(r.id)).length;
    const recallAtK = hits / relevantSet.size;
    const precisionAtK = hits / k;

    let reciprocalRank = 0;
    for (let i = 0; i < topK.length; i++) {
      if (relevantSet.has(topK[i].id)) {
        reciprocalRank = 1 / (i + 1);
        break;
      }
    }

    perQuery.push({
      query: tc.query,
      recallAtK,
      precisionAtK,
      reciprocalRank,
    });
  }

  const n = perQuery.length;
  return {
    meanRecallAtK: perQuery.reduce((s, q) => s + q.recallAtK, 0) / n,
    meanPrecisionAtK: perQuery.reduce((s, q) => s + q.precisionAtK, 0) / n,
    meanReciprocalRank: perQuery.reduce((s, q) => s + q.reciprocalRank, 0) / n,
    perQuery,
  };
}
```

## Drift Detection

### Embedding Distribution Monitoring

```ts
interface DriftReport {
  meanShift: number;
  varianceChange: number;
  drifted: boolean;
  details: string;
}

function computeMeanEmbedding(embeddings: number[][]): number[] {
  const dim = embeddings[0].length;
  const mean = new Array<number>(dim).fill(0);

  for (const emb of embeddings) {
    for (let i = 0; i < dim; i++) {
      mean[i] += emb[i];
    }
  }

  return mean.map((v) => v / embeddings.length);
}

function embeddingVariance(embeddings: number[][], mean: number[]): number {
  let totalDist = 0;
  for (const emb of embeddings) {
    let dist = 0;
    for (let i = 0; i < mean.length; i++) {
      dist += (emb[i] - mean[i]) ** 2;
    }
    totalDist += Math.sqrt(dist);
  }
  return totalDist / embeddings.length;
}

function detectDrift(
  baselineEmbeddings: number[][],
  currentEmbeddings: number[][],
  shiftThreshold = 0.1,
): DriftReport {
  const baselineMean = computeMeanEmbedding(baselineEmbeddings);
  const currentMean = computeMeanEmbedding(currentEmbeddings);

  let shift = 0;
  for (let i = 0; i < baselineMean.length; i++) {
    shift += (baselineMean[i] - currentMean[i]) ** 2;
  }
  const meanShift = Math.sqrt(shift);

  const baselineVar = embeddingVariance(baselineEmbeddings, baselineMean);
  const currentVar = embeddingVariance(currentEmbeddings, currentMean);
  const varianceChange = Math.abs(currentVar - baselineVar) / baselineVar;

  const drifted = meanShift > shiftThreshold;

  return {
    meanShift,
    varianceChange,
    drifted,
    details: drifted
      ? `Mean shifted by ${meanShift.toFixed(4)} (threshold: ${shiftThreshold})`
      : 'No significant drift detected',
  };
}
```

### Schema Change Detection

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'kb_documents'
ORDER BY ordinal_position;
```

Compare against a stored baseline and alert on added, removed, or type-changed columns.

## Quality Dashboard

Key metrics to track and their alert thresholds:

| Metric              | Green    | Yellow     | Red      |
| ------------------- | -------- | ---------- | -------- |
| Accuracy            | >90%     | 80-90%     | <80%     |
| Coverage            | >80%     | 70-80%     | <70%     |
| Freshness (avg age) | <30 days | 30-60 days | >60 days |
| Consistency         | >95%     | 90-95%     | <90%     |
| Recall@10           | >0.8     | 0.6-0.8    | <0.6     |
| MRR                 | >0.7     | 0.5-0.7    | <0.5     |
| Query latency (p50) | <100ms   | 100-500ms  | >500ms   |
| Query latency (p99) | <500ms   | 500ms-2s   | >2s      |
| Embedding drift     | <0.05    | 0.05-0.1   | >0.1     |

### Metrics Collection

```ts
interface KBHealthMetrics {
  accuracy: number;
  coverage: number;
  freshness: { averageAgeDays: number; stalePercent: number };
  consistency: number;
  retrieval: { recallAt10: number; mrr: number };
  latency: { p50Ms: number; p99Ms: number };
  drift: { meanShift: number; drifted: boolean };
  collectedAt: string;
}

async function collectHealthMetrics(
  testQuestions: TestQuestion[],
  userQueries: string[],
  queryFn: (q: string) => Promise<string>,
  searchFn: (
    q: string,
  ) => Promise<Array<{ id: string; score: number; content: string }>>,
  similarityFn: (a: string, b: string) => Promise<number>,
): Promise<KBHealthMetrics> {
  const [accuracy, coverage] = await Promise.all([
    measureAccuracy(testQuestions, queryFn, similarityFn),
    measureCoverage(userQueries, async (q) =>
      (await searchFn(q)).map((r) => ({ content: r.content, score: r.score })),
    ),
  ]);

  return {
    accuracy: accuracy.accuracy,
    coverage: coverage.coverage,
    freshness: { averageAgeDays: 0, stalePercent: 0 },
    consistency: 0,
    retrieval: { recallAt10: 0, mrr: 0 },
    latency: { p50Ms: 0, p99Ms: 0 },
    drift: { meanShift: 0, drifted: false },
    collectedAt: new Date().toISOString(),
  };
}
```

## Validation Strategies

### Human Review

- Sample random knowledge entries
- Subject matter expert validation
- User feedback loops

### Automated Checks

| Check               | Purpose                     |
| ------------------- | --------------------------- |
| Duplicate detection | Find near-identical entries |
| Conflict detection  | Find contradictory facts    |
| Staleness detection | Flag outdated information   |
| Citation validation | Verify sources still exist  |

## User Satisfaction Targets

| Metric                       | Target |
| ---------------------------- | ------ |
| Query relevance (user-rated) | >85%   |
| Users finding KB valuable    | >80%   |
| Median query time            | <100ms |
| Uptime                       | >99.9% |
