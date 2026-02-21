---
title: Curation and Ingestion
description: Document ingestion pipeline, chunking strategies, deduplication, metadata enrichment, content cleaning, and provenance tracking
tags:
  [
    knowledge-base,
    curation,
    ingestion,
    deduplication,
    provenance,
    metadata,
    chunking,
    embedding,
  ]
---

# Curation and Ingestion

## Knowledge Sources

| Source Type | Examples                                   |
| ----------- | ------------------------------------------ |
| Internal    | Databases, documents, wikis, Slack, emails |
| External    | Public data, APIs, third-party sources     |
| Tribal      | SME interviews, recorded conversations     |

## Document Ingestion Pipeline

End-to-end flow: load, clean, chunk, embed, store.

```ts
interface RawDocument {
  content: string;
  mimeType: string;
  sourceUrl: string;
  fetchedAt: string;
}

interface ProcessedChunk {
  content: string;
  embedding: number[];
  metadata: ChunkMetadata;
  contentHash: string;
}

interface ChunkMetadata {
  sourceUrl: string;
  chunkIndex: number;
  totalChunks: number;
  category?: string;
  tags: string[];
  fetchedAt: string;
  processedAt: string;
}

async function ingestDocument(
  raw: RawDocument,
  embedFn: (text: string) => Promise<number[]>,
): Promise<ProcessedChunk[]> {
  const cleaned = cleanContent(raw.content, raw.mimeType);
  const chunks = chunkText(cleaned, { maxTokens: 512, overlap: 64 });
  const now = new Date().toISOString();

  const processed = await Promise.all(
    chunks.map(async (text, i) => ({
      content: text,
      embedding: await embedFn(text),
      contentHash: await hashContent(text),
      metadata: {
        sourceUrl: raw.sourceUrl,
        chunkIndex: i,
        totalChunks: chunks.length,
        tags: [],
        fetchedAt: raw.fetchedAt,
        processedAt: now,
      },
    })),
  );

  const deduplicated = await deduplicateChunks(processed);
  return deduplicated;
}
```

### Chunking Strategy

```ts
interface ChunkOptions {
  maxTokens: number;
  overlap: number;
  separators?: string[];
}

function chunkText(text: string, opts: ChunkOptions): string[] {
  const { maxTokens, overlap, separators = ['\n\n', '\n', '. ', ' '] } = opts;
  const chunks: string[] = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (estimateTokens(remaining) <= maxTokens) {
      chunks.push(remaining.trim());
      break;
    }

    let splitPoint = -1;
    const searchWindow = remaining.slice(0, maxTokens * 4);

    for (const sep of separators) {
      const lastIndex = searchWindow.lastIndexOf(sep);
      if (lastIndex > 0) {
        splitPoint = lastIndex + sep.length;
        break;
      }
    }

    if (splitPoint <= 0) splitPoint = maxTokens * 4;

    chunks.push(remaining.slice(0, splitPoint).trim());
    const overlapStart = Math.max(0, splitPoint - overlap * 4);
    remaining = remaining.slice(overlapStart);
  }

  return chunks.filter((c) => c.length > 0);
}

function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}
```

## Content Cleaning

### HTML Stripping

```ts
function stripHtml(html: string): string {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<nav[\s\S]*?<\/nav>/gi, '')
    .replace(/<footer[\s\S]*?<\/footer>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim();
}
```

### Cleaning by MIME Type

```ts
function cleanContent(content: string, mimeType: string): string {
  switch (mimeType) {
    case 'text/html':
      return stripHtml(content);
    case 'text/markdown':
      return normalizeMarkdown(content);
    case 'text/plain':
      return content.replace(/\s+/g, ' ').trim();
    default:
      return content.trim();
  }
}

function normalizeMarkdown(md: string): string {
  return md
    .replace(/^#{1,6}\s+/gm, (match) => match)
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '$1')
    .replace(/(`{3}[\s\S]*?`{3})/g, '$1')
    .replace(/\s+/g, ' ')
    .trim();
}
```

### Table Detection

```ts
interface ExtractedTable {
  headers: string[];
  rows: string[][];
}

function extractMarkdownTables(md: string): ExtractedTable[] {
  const tablePattern = /\|(.+)\|\n\|[-| :]+\|\n((?:\|.+\|\n?)*)/g;
  const tables: ExtractedTable[] = [];

  let match: RegExpExecArray | null;
  while ((match = tablePattern.exec(md)) !== null) {
    const headers = match[1]
      .split('|')
      .map((h) => h.trim())
      .filter(Boolean);
    const rowLines = match[2].trim().split('\n');
    const rows = rowLines.map((line) =>
      line
        .split('|')
        .map((c) => c.trim())
        .filter(Boolean),
    );
    tables.push({ headers, rows });
  }

  return tables;
}
```

## Deduplication

### Content Hashing

```ts
import { createHash } from 'node:crypto';

async function hashContent(text: string): Promise<string> {
  const normalized = text.toLowerCase().replace(/\s+/g, ' ').trim();
  return createHash('sha256').update(normalized).digest('hex');
}

async function deduplicateChunks(
  chunks: ProcessedChunk[],
): Promise<ProcessedChunk[]> {
  const seen = new Map<string, ProcessedChunk>();

  for (const chunk of chunks) {
    const existing = seen.get(chunk.contentHash);
    if (!existing) {
      seen.set(chunk.contentHash, chunk);
      continue;
    }
    mergeMetadata(existing.metadata, chunk.metadata);
  }

  return Array.from(seen.values());
}
```

### Semantic Similarity Threshold

```ts
function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let normA = 0;
  let normB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

async function findSemanticDuplicates(
  chunks: ProcessedChunk[],
  threshold = 0.95,
): Promise<Array<[ProcessedChunk, ProcessedChunk]>> {
  const duplicates: Array<[ProcessedChunk, ProcessedChunk]> = [];

  for (let i = 0; i < chunks.length; i++) {
    for (let j = i + 1; j < chunks.length; j++) {
      const sim = cosineSimilarity(chunks[i].embedding, chunks[j].embedding);
      if (sim >= threshold) {
        duplicates.push([chunks[i], chunks[j]]);
      }
    }
  }

  return duplicates;
}
```

## Metadata Enrichment

### Auto-Tagging with LLM

```ts
interface TagResult {
  tags: string[];
  category: string;
  confidence: number;
}

async function autoTag(
  content: string,
  llmFn: (prompt: string) => Promise<string>,
): Promise<TagResult> {
  const prompt = `Classify this knowledge base content.
Return JSON: { "tags": string[], "category": string, "confidence": number }

Tags: 3-5 descriptive keywords.
Category: one of [policy, procedure, reference, tutorial, faq, api-docs].
Confidence: 0-1 how certain you are.

Content:
${content.slice(0, 2000)}`;

  const raw = await llmFn(prompt);
  return JSON.parse(raw) as TagResult;
}
```

### Source Tracking and Freshness

```ts
interface SourceRecord {
  url: string;
  lastChecked: string;
  lastModified: string;
  contentHash: string;
  checkIntervalHours: number;
}

async function checkSourceFreshness(
  source: SourceRecord,
): Promise<{ stale: boolean; newHash?: string }> {
  const response = await fetch(source.url, { method: 'HEAD' });
  const lastModified = response.headers.get('last-modified');

  if (lastModified && new Date(lastModified) > new Date(source.lastModified)) {
    const full = await fetch(source.url);
    const newHash = await hashContent(await full.text());
    return { stale: newHash !== source.contentHash, newHash };
  }

  return { stale: false };
}
```

## Provenance Tracking

Every knowledge entry needs:

- Source URL or reference
- Last updated timestamp
- Author/contributor
- Confidence score (if applicable)

```ts
function mergeMetadata(target: ChunkMetadata, source: ChunkMetadata): void {
  const targetDate = new Date(target.fetchedAt);
  const sourceDate = new Date(source.fetchedAt);
  if (sourceDate > targetDate) {
    target.fetchedAt = source.fetchedAt;
    target.sourceUrl = source.sourceUrl;
  }
  target.tags = [...new Set([...target.tags, ...source.tags])];
}
```

## Curation Best Practices

| Practice               | Description                                     |
| ---------------------- | ----------------------------------------------- |
| Single source of truth | One canonical answer per question               |
| Deduplication          | Merge similar knowledge entries                 |
| Conflict resolution    | When sources disagree, establish priority rules |
| Metadata richness      | More metadata = better filtering and search     |
| Chunking at boundaries | Split at paragraphs/sections, not mid-sentence  |
| Overlap between chunks | 10-15% overlap preserves context at boundaries  |

## Validation Checklist

- Knowledge extracted and structured
- Content cleaned and normalized per MIME type
- Chunks sized within token limits with semantic boundaries
- Duplicate content detected and merged
- Quality metrics above threshold (accuracy >95%)
- Provenance tracked for all entries
- Sample queries return relevant results
