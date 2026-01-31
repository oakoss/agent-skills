---
title: Output Validation and Encoding
description: Zero-trust output handling for LLM responses including context-aware encoding, parameterized queries, CSP enforcement, RAG sanitization, and semantic filtering
tags:
  [
    output-validation,
    improper-output-handling,
    xss-prevention,
    sql-injection,
    rag-security,
    semantic-filtering,
    content-security-policy,
  ]
---

# Output Validation and Encoding

LLM output is untrusted input. Treat model responses with the same rigor applied to user-submitted data: validate, sanitize, and encode before passing downstream. This addresses OWASP LLM05:2025 (Improper Output Handling), LLM08:2025 (Vector and Embedding Weaknesses), and LLM09:2025 (Misinformation).

## Zero-Trust Output Principle

Never trust LLM output. Models generate unpredictable content including executable code, file paths, queries, and markup. Passing this directly to system functions like `exec()`, `eval()`, database queries, or HTML renderers creates injection vectors.

```ts
async function processLlmResponse(response: string): Promise<string> {
  const sanitized = sanitizeOutput(response);
  const validated = await validateOutputSchema(sanitized);
  const encoded = encodeForContext(validated, 'html');
  return encoded;
}
```

## Context-Aware Output Encoding

Encode LLM output based on where it will be consumed. Different contexts require different encoding strategies.

```ts
function encodeForContext(
  output: string,
  context: 'html' | 'sql' | 'shell' | 'url' | 'markdown',
): string {
  switch (context) {
    case 'html':
      return escapeHtml(output);
    case 'sql':
      throw new Error('Use parameterized queries instead of encoding');
    case 'shell':
      throw new Error('Use execFile with argument arrays instead of encoding');
    case 'url':
      return encodeURIComponent(output);
    case 'markdown':
      return sanitizeMarkdown(output);
  }
}
```

| Output Context   | Encoding Strategy                           | Anti-Pattern                   |
| ---------------- | ------------------------------------------- | ------------------------------ |
| HTML rendering   | HTML entity encoding, CSP headers           | Direct innerHTML insertion     |
| SQL queries      | Parameterized queries / prepared statements | String concatenation into SQL  |
| Shell commands   | `execFile` with argument arrays             | Template literals in `exec()`  |
| URL parameters   | `encodeURIComponent`                        | Raw string concatenation       |
| JSON responses   | Schema validation with Zod                  | Passing raw model output       |
| Markdown display | Sanitize HTML within markdown               | Rendering unsanitized markdown |

## Parameterized Queries for LLM-Generated SQL

Never construct SQL from LLM output using string concatenation. Use parameterized queries for all database operations involving model output.

```ts
async function executeGeneratedQuery(
  llmOutput: { table: string; filters: Record<string, string> },
  db: Database,
) {
  const allowedTables = ['products', 'categories', 'reviews'];
  if (!allowedTables.includes(llmOutput.table)) {
    throw new Error(`Table not in allowlist: ${llmOutput.table}`);
  }

  const conditions = Object.entries(llmOutput.filters);
  const whereClause = conditions
    .map(([key], i) => `${sanitizeColumnName(key)} = $${i + 1}`)
    .join(' AND ');
  const values = conditions.map(([_, value]) => value);

  return db.query(
    `SELECT * FROM ${llmOutput.table} WHERE ${whereClause}`,
    values,
  );
}

function sanitizeColumnName(name: string): string {
  if (!/^[a-z_][a-z0-9_]*$/i.test(name)) {
    throw new Error(`Invalid column name: ${name}`);
  }
  return name;
}
```

## Content Security Policy for LLM Output

Implement strict CSP headers to mitigate XSS from LLM-generated content rendered in the browser.

```ts
const cspHeaders = {
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "connect-src 'self'",
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
  ].join('; '),
};
```

## HTML Sanitization for Rendered Output

When LLM output is rendered as HTML or markdown, sanitize it to remove executable content.

```ts
import DOMPurify from 'isomorphic-dompurify';

function sanitizeLlmHtml(llmOutput: string): string {
  return DOMPurify.sanitize(llmOutput, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'code', 'pre'],
    ALLOWED_ATTR: [],
    ALLOW_DATA_ATTR: false,
  });
}
```

## Schema Validation for Structured Output

When LLMs produce structured data (JSON, function calls), validate against a strict schema before use.

```ts
import { z } from 'zod';

const LlmActionSchema = z.object({
  action: z.enum(['search', 'summarize', 'translate']),
  target: z.string().max(500),
  parameters: z.record(z.string().max(200)).optional(),
});

async function parseModelAction(llmOutput: string) {
  const parsed = JSON.parse(llmOutput);
  const validated = LlmActionSchema.parse(parsed);
  return validated;
}
```

## RAG Output Sanitization (LLM08)

In Retrieval-Augmented Generation systems, untrusted documents can inject malicious content through the retrieval pipeline. Sanitize both retrieved content and the model's final output.

**Retrieved content risks:**

- Poisoned documents containing injection payloads
- Documents with embedded instructions that manipulate model behavior
- Unauthorized documents accessed through permissive vector store queries

**Mitigation strategies:**

```ts
async function sanitizeRetrievedContent(
  documents: RetrievedDocument[],
): Promise<SanitizedDocument[]> {
  return documents.map((doc) => ({
    ...doc,
    content: stripInstructionPatterns(doc.content),
    metadata: {
      ...doc.metadata,
      trustLevel: classifyDocumentTrust(doc.source),
    },
  }));
}

function stripInstructionPatterns(content: string): string {
  const instructionPatterns = [
    /ignore\s+(previous|all|above)\s+instructions/gi,
    /you\s+are\s+now\s+a/gi,
    /new\s+instructions?:/gi,
    /system\s*:\s*/gi,
  ];

  let cleaned = content;
  for (const pattern of instructionPatterns) {
    cleaned = cleaned.replace(pattern, '[FILTERED]');
  }
  return cleaned;
}
```

**Permission-aware vector stores:**

- Enforce document-level access controls in the vector database
- Filter retrieved documents based on the requesting user's permissions
- Tag documents with classification levels and enforce retrieval policies

## Semantic Filtering for Misinformation (LLM09)

When model outputs are used for decision-making or presented as factual, apply semantic validation.

- Cross-reference critical claims against authoritative data sources
- Flag outputs with low confidence scores for human review
- Implement citation requirements for factual assertions
- Use structured output formats that separate facts from interpretations

```ts
interface ValidatedOutput {
  content: string;
  confidenceScore: number;
  citations: string[];
  requiresHumanReview: boolean;
}

function assessOutputReliability(
  output: string,
  metadata: ModelMetadata,
): ValidatedOutput {
  const confidenceScore = metadata.logProbabilities
    ? calculateConfidence(metadata.logProbabilities)
    : 0;

  return {
    content: output,
    confidenceScore,
    citations: extractCitations(output),
    requiresHumanReview: confidenceScore < 0.7 || metadata.containsNumbers,
  };
}
```

## Output Validation Checklist

| Check                         | Required    | Context                              |
| ----------------------------- | ----------- | ------------------------------------ |
| HTML entity encoding          | Yes         | Browser rendering                    |
| Parameterized queries         | Yes         | Database operations                  |
| Schema validation (Zod)       | Yes         | Structured output / function calls   |
| CSP headers                   | Yes         | Web applications serving LLM content |
| DOMPurify sanitization        | Yes         | HTML/markdown rendering              |
| Instruction pattern stripping | Yes         | RAG retrieved content                |
| Confidence scoring            | Recommended | Factual/decision-making outputs      |
| Human review gate             | Recommended | High-stakes outputs                  |
