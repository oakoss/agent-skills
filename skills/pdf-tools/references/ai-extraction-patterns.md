---
title: AI Extraction Patterns
description: Vision-based table extraction, AI-assisted OCR with Zod schema mapping, recursive document summarization, and multi-pass verification
tags: [extraction, AI, OCR, vision, tables, Zod, summarization]
---

## The Extraction Stack

1. **Layer 1 -- Raw Byte Parsing (unpdf)**: Extract text, metadata, and image locations quickly
2. **Layer 2 -- Vision Analysis (Gemini/GPT-4o)**: "Look" at the page to identify tables, headers, and signatures
3. **Layer 3 -- Schema Mapping (AI SDK)**: Force the output into a validated Zod/JSON structure

## AI-Driven Semantic Extraction

Use LLMs to turn unstructured PDF text into validated schemas:

```ts
import { unpdf } from 'unpdf';
import { generateObject } from 'ai';

async function extractInvoice(buffer: Buffer) {
  const { text } = await unpdf.extractText(buffer);

  const { object } = await generateObject({
    model: myModel,
    schema: invoiceSchema,
    prompt: `Extract structured data from this PDF text: ${text}`,
  });

  return object;
}
```

## Visual Table Extraction

Tables are the hardest part of PDF extraction. Borders are often missing or purely decorative. Use vision models to handle complex layouts:

```ts
import { generateObject } from 'ai';
import { z } from 'zod';

async function extractComplexTable(pdfBuffer: Buffer) {
  const pages = await pdfToImages(pdfBuffer);

  const { object } = await generateObject({
    model: google('gemini-2.0-pro'),
    schema: z.object({
      rows: z.array(z.record(z.string())),
    }),
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: 'Extract this table:' },
          { type: 'image', image: pages[1] },
        ],
      },
    ],
  });

  return object.rows;
}
```

### Prompting Strategy

Use domain-specific prompts for better extraction:

```text
Act as a forensic document analyst. Extract the table from page 2.
Do not just return text; return a JSON array where each object represents a row.
Identify headers even if they are merged cells.
```

## Recursive Document Summarization

For 100+ page documents, use token-efficient forensic scanning:

1. Extract Table of Contents (TOC)
2. Identify "high-value" pages (financial statements, signatures, terms)
3. Direct the AI model to process only those specific pages in high resolution

## Multi-Pass Verification

Prevent hallucinations with a verification step:

- **LLM-A extracts** structured data from the PDF
- **LLM-B verifies** the extraction against the original document
- Discrepancies are flagged for human review

## Common Pitfalls

| Pitfall                                | Fix                                               |
| -------------------------------------- | ------------------------------------------------- |
| Model invents values from blurry scans | Use multi-pass verification (extract then verify) |
| Large PDFs exceed context window       | Use RAG or page-by-page extraction                |
| Hidden OCR text layers confuse LLMs    | Prefer the vision layer as source of truth        |
| Inconsistent schema mapping            | Define strict Zod schemas with validation         |
