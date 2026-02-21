---
title: Retrieval Methods and Pipeline Design
description: Hybrid retrieval, query enhancement, re-ranking, context assembly, parent document retrieval, contextual compression, multi-query, MMR, and advanced fusion techniques
tags:
  [
    retrieval,
    hybrid-search,
    re-ranking,
    context-assembly,
    query-enhancement,
    mmr,
    rrf,
    parent-document,
    contextual-compression,
    multi-query,
  ]
---

# Retrieval Methods and Pipeline Design

## Phase 4: Retrieval Pipeline

**Goal**: Build sophisticated retrieval beyond simple similarity search

**Actions**:

- Implement hybrid retrieval: semantic search + keyword (BM25)
- Add query enhancement: expansion, reformulation, multi-query
- Apply contextual filtering: metadata, temporal constraints, relevance ranking
- Design for query types: factual (precision), analytical (breadth), creative (diversity)
- Handle edge cases: no relevant results found

### Advanced Techniques

- **Re-ranking**: Use cross-encoder after initial retrieval (e.g., `cross-encoder/ms-marco-MiniLM-L-12-v2`) to improve precision
- **Query routing**: Route different query types to specialized retrieval strategies
- **Ensemble methods**: Combine multiple retrieval approaches with reciprocal rank fusion
- **Adaptive retrieval**: Adjust top-k based on query complexity
- **Query expansion / HyDE**: Generate hypothetical answers to expand sparse queries into richer representations
- **GraphRAG**: Build knowledge graphs from documents; traverse entity relationships for multi-hop reasoning queries
- **Contextual retrieval**: Prepend LLM-generated context summaries to chunks before embedding to resolve ambiguous references
- **ColBERT-style late interaction**: Token-level similarity scoring between queries and documents for fine-grained matching

### Validation

- Retrieval accuracy tested across diverse query types
- Hybrid retrieval outperforms single-method baselines
- Query latency meets requirements (<500ms ideal)
- Edge cases and fallbacks tested

## Parent Document Retriever

Store small chunks for embedding and retrieval but return the full parent document (or a larger section) for context. Small chunks produce more precise embeddings; large context windows give the LLM enough surrounding information to generate accurate answers.

**When to use**: Long documents where individual passages lose meaning without surrounding context. Legal contracts, technical manuals, research papers with cross-referencing sections.

**When to avoid**: Short documents where chunks already capture the full context, or when token budget is tight.

```ts
interface ParentDocumentStore {
  parentDocuments: Map<string, string>;
  childChunks: Map<string, { text: string; parentId: string }>;
}

function buildParentDocumentIndex(
  documents: { id: string; text: string }[],
  chunkSize: number,
  chunkOverlap: number,
): ParentDocumentStore {
  const store: ParentDocumentStore = {
    parentDocuments: new Map(),
    childChunks: new Map(),
  };

  for (const doc of documents) {
    store.parentDocuments.set(doc.id, doc.text);

    const chunks = splitIntoChunks(doc.text, chunkSize, chunkOverlap);
    for (let i = 0; i < chunks.length; i++) {
      const chunkId = `${doc.id}_chunk_${i}`;
      store.childChunks.set(chunkId, {
        text: chunks[i],
        parentId: doc.id,
      });
    }
  }

  return store;
}

async function parentDocumentRetrieval(
  query: string,
  store: ParentDocumentStore,
  vectorDb: VectorStore,
  topK: number,
): Promise<string[]> {
  const childResults = await vectorDb.similaritySearch(query, topK);

  const parentIds = new Set<string>();
  for (const result of childResults) {
    const chunk = store.childChunks.get(result.id);
    if (chunk) parentIds.add(chunk.parentId);
  }

  return [...parentIds].map((id) => store.parentDocuments.get(id)!);
}
```

A common variant uses a **mid-level parent**: instead of returning the full document, return the section or page containing the matched chunk. This balances precision with context.

## Contextual Compression

After retrieval, extract only the relevant portions from each document using an LLM. Reduces noise in the context window so the generator sees focused, high-signal content.

**When to use**: Retrieved chunks contain relevant information buried inside irrelevant surrounding text. Common with larger chunk sizes or parent document retrieval.

**When to avoid**: Latency-sensitive pipelines where the extra LLM call is too expensive, or when chunks are already tightly scoped (proposition chunking).

```ts
async function compressRetrievedDocuments(
  query: string,
  documents: { text: string; source: string }[],
  llm: LLMClient,
): Promise<{ text: string; source: string }[]> {
  const compressed: { text: string; source: string }[] = [];

  for (const doc of documents) {
    const extraction = await llm.complete({
      prompt: [
        `Given the following question and document, extract only the parts `,
        `of the document that are directly relevant to answering the question. `,
        `If nothing is relevant, respond with "IRRELEVANT".\n\n`,
        `Question: ${query}\n\n`,
        `Document:\n${doc.text}`,
      ].join(''),
    });

    if (extraction.trim() !== 'IRRELEVANT') {
      compressed.push({ text: extraction, source: doc.source });
    }
  }

  return compressed;
}
```

For higher throughput, batch the compression calls or use a smaller model (e.g., GPT-4o-mini or Claude Haiku) dedicated to extraction. The compression step typically adds 200-500ms latency per document but can reduce total context tokens by 50-70%.

## Multi-Query Retrieval

Generate multiple query variations from the original question, retrieve for each, then deduplicate and merge results. Captures different facets of ambiguous or complex queries that a single embedding would miss.

```ts
async function multiQueryRetrieval(
  originalQuery: string,
  llm: LLMClient,
  vectorDb: VectorStore,
  topK: number,
  numVariations = 3,
): Promise<RetrievalResult[]> {
  const variations = await llm.complete({
    prompt: [
      `Generate ${numVariations} different versions of the following question `,
      `to help retrieve relevant documents from a vector database. `,
      `Each version should approach the question from a different angle.\n\n`,
      `Original question: ${originalQuery}\n\n`,
      `Return only the questions, one per line.`,
    ].join(''),
  });

  const queries = [originalQuery, ...variations.trim().split('\n')];

  const allResults = new Map<string, RetrievalResult>();

  for (const query of queries) {
    const results = await vectorDb.similaritySearch(query, topK);
    for (const result of results) {
      const existing = allResults.get(result.id);
      if (!existing || result.score > existing.score) {
        allResults.set(result.id, result);
      }
    }
  }

  return [...allResults.values()].sort((a, b) => b.score - a.score);
}
```

Multi-query retrieval pairs well with reciprocal rank fusion (below) for combining results instead of naive max-score deduplication.

## Maximal Marginal Relevance (MMR)

Balance relevance and diversity in results to avoid redundant passages. MMR iteratively selects documents that are both relevant to the query and dissimilar to already-selected documents.

**Formula**: `MMR = argmax[lambda * sim(query, doc) - (1 - lambda) * max(sim(doc, selected))]`

- `lambda = 1.0`: pure relevance (equivalent to standard similarity search)
- `lambda = 0.0`: pure diversity (maximum dissimilarity from selected docs)
- `lambda = 0.5-0.7`: typical production range balancing both

```ts
function mmrSelection(
  queryEmbedding: number[],
  candidates: { id: string; embedding: number[]; text: string }[],
  k: number,
  lambda = 0.6,
): typeof candidates {
  const selected: typeof candidates = [];
  const remaining = [...candidates];

  for (let i = 0; i < k && remaining.length > 0; i++) {
    let bestIdx = 0;
    let bestScore = -Infinity;

    for (let j = 0; j < remaining.length; j++) {
      const relevance = cosineSimilarity(
        queryEmbedding,
        remaining[j].embedding,
      );

      let maxSimilarity = 0;
      for (const sel of selected) {
        const sim = cosineSimilarity(remaining[j].embedding, sel.embedding);
        maxSimilarity = Math.max(maxSimilarity, sim);
      }

      const mmrScore = lambda * relevance - (1 - lambda) * maxSimilarity;

      if (mmrScore > bestScore) {
        bestScore = mmrScore;
        bestIdx = j;
      }
    }

    selected.push(remaining[bestIdx]);
    remaining.splice(bestIdx, 1);
  }

  return selected;
}
```

MMR is especially valuable when retrieved chunks come from similar sections of the same document. Without MMR, the top-K results might all contain near-identical information, wasting context window tokens.

## Cross-Encoder Reranking

Initial retrieval uses bi-encoders (separate query and document embeddings) for speed. Reranking uses a cross-encoder that processes query and document together for higher accuracy, at the cost of being ~100x slower per pair.

**Pipeline**: Retrieve 50-100 candidates with bi-encoder, then rerank the top candidates with a cross-encoder, return the top-K reranked results.

### Cohere Rerank API

```ts
import { CohereClient } from 'cohere-ai';

async function cohereRerank(
  query: string,
  documents: { text: string; id: string }[],
  topN: number,
): Promise<{ id: string; text: string; relevanceScore: number }[]> {
  const cohere = new CohereClient({ token: process.env.COHERE_API_KEY });

  const response = await cohere.rerank({
    query,
    documents: documents.map((d) => d.text),
    topN,
    model: 'rerank-v3.5',
  });

  return response.results.map((r) => ({
    id: documents[r.index].id,
    text: documents[r.index].text,
    relevanceScore: r.relevanceScore,
  }));
}
```

### Local Cross-Encoder Reranking

```ts
async function crossEncoderRerank(
  query: string,
  documents: { text: string; id: string }[],
  model: CrossEncoderModel,
  topN: number,
): Promise<{ id: string; text: string; score: number }[]> {
  const pairs = documents.map((doc) => ({
    id: doc.id,
    text: doc.text,
    score: model.predict(query, doc.text),
  }));

  return pairs.sort((a, b) => b.score - a.score).slice(0, topN);
}
```

### When to Rerank vs When Not To

| Reranking adds value                               | Skip reranking                          |
| -------------------------------------------------- | --------------------------------------- |
| Initial retrieval returns >20 candidates           | Result set is already small (<10)       |
| Noisy results from hybrid search fusion            | Latency budget is under 100ms total     |
| Domain-specific queries where bi-encoders struggle | Bi-encoder is fine-tuned on domain data |
| High-stakes answers (legal, medical, compliance)   | Cost per query must stay under $0.001   |

Reranking typically adds 100-300ms latency. For Cohere Rerank, cost is ~$1 per 1000 search queries (reranking 100 documents each).

## Reciprocal Rank Fusion (RRF)

Combine results from multiple retrieval methods (semantic search, BM25, metadata filters) into a single ranked list without needing normalized scores. RRF is score-agnostic, making it ideal for fusing results from systems with incompatible score scales.

**Formula**: `RRF_score(doc) = sum(1 / (k + rank_i(doc)))` for each retrieval method `i`

The constant `k` (typically 60) dampens the impact of high rankings from any single method.

```ts
function reciprocalRankFusion(
  rankedLists: { id: string; text: string }[][],
  k = 60,
): { id: string; text: string; score: number }[] {
  const scores = new Map<string, { text: string; score: number }>();

  for (const list of rankedLists) {
    for (let rank = 0; rank < list.length; rank++) {
      const doc = list[rank];
      const existing = scores.get(doc.id);
      const rrfScore = 1 / (k + rank + 1);

      if (existing) {
        existing.score += rrfScore;
      } else {
        scores.set(doc.id, { text: doc.text, score: rrfScore });
      }
    }
  }

  return [...scores.entries()]
    .map(([id, { text, score }]) => ({ id, text, score }))
    .sort((a, b) => b.score - a.score);
}
```

### Hybrid Search with RRF

```ts
async function hybridSearchWithRRF(
  query: string,
  vectorDb: VectorStore,
  bm25Index: BM25Index,
  topK: number,
): Promise<{ id: string; text: string; score: number }[]> {
  const [semanticResults, keywordResults] = await Promise.all([
    vectorDb.similaritySearch(query, topK * 2),
    bm25Index.search(query, topK * 2),
  ]);

  const fused = reciprocalRankFusion([semanticResults, keywordResults]);

  return fused.slice(0, topK);
}
```

RRF is the default fusion method in Elasticsearch and Weaviate hybrid search. It consistently outperforms simple score averaging or weighted combination because it handles score distribution mismatches between retrieval methods.

## Phase 5: Context Assembly

**Goal**: Transform retrieved chunks into optimal LLM context

**Actions**:

- Rank and select: prioritize by relevance score, recency, source authority
- Synthesize: merge related chunks, avoid redundancy
- Compress: use LLMLingua or similar for token optimization
- Mitigate "lost in the middle": place critical info at start/end
- Adapt dynamically: adjust context based on conversation history

### Context Engineering Integration

- Blend RAG results with system instructions and user prompts
- Maintain conversation coherence across multi-turn interactions
- Implement context persistence for follow-up queries
- Balance context size vs. information density

### Validation

- Context relevance validated against human judgments
- Token optimization maintains accuracy
- Multi-turn conversations maintain coherence
- Assembly latency <200ms

## Standard RAG Response Format

```json
{
  "answer": "Generated response incorporating retrieved information",
  "sources": [
    {
      "content": "Retrieved text chunk",
      "source": "Document/URL identifier",
      "relevance_score": 0.95,
      "chunk_id": "unique_identifier"
    }
  ],
  "confidence": 0.87,
  "retrieval_metadata": {
    "chunks_retrieved": 5,
    "retrieval_time_ms": 150,
    "generation_time_ms": 800
  }
}
```

## Retrieval Method Selection Guide

| Method                  | Latency Impact | Best For                                   | Pair With              |
| ----------------------- | -------------- | ------------------------------------------ | ---------------------- |
| Hybrid search (RRF)     | +10-50ms       | All production systems (baseline)          | Reranking              |
| Parent document         | +20-50ms       | Long documents, context-dependent passages | Contextual compression |
| Multi-query             | +500-1500ms    | Ambiguous or complex queries               | RRF                    |
| MMR                     | +10-30ms       | Reducing redundancy in results             | Any retrieval method   |
| Cross-encoder reranking | +100-300ms     | Noisy initial results, high-stakes answers | Hybrid search          |
| Contextual compression  | +200-500ms     | Large chunks, parent document retrieval    | Parent document        |
| HyDE                    | +500-1000ms    | Short or vague queries                     | Hybrid search          |
