---
title: Supply Chain and MCP Security
description: AI supply chain integrity including model provenance, AI-BOM, data poisoning defense, and Model Context Protocol security hardening
tags:
  [
    supply-chain,
    model-provenance,
    data-poisoning,
    ai-bom,
    mcp-security,
    tool-poisoning,
    model-integrity,
  ]
---

# Supply Chain and MCP Security

AI supply chains introduce risks beyond traditional software dependencies. Third-party models, training datasets, embeddings, and tool integrations (MCP) all represent attack surfaces. This covers OWASP LLM03:2025 (Supply Chain) and LLM04:2025 (Data and Model Poisoning).

## Model Provenance and Integrity

Verify the origin and integrity of all third-party models before deployment. Pre-trained weights, fine-tuning checkpoints, and helper models can all be tampered with.

```ts
interface ModelManifest {
  modelId: string;
  source: string;
  version: string;
  checksum: string;
  checksumAlgorithm: 'sha256' | 'sha512';
  signedBy: string;
  verifiedAt: string;
}

async function verifyModelIntegrity(
  modelPath: string,
  manifest: ModelManifest,
): Promise<boolean> {
  const fileHash = await computeHash(modelPath, manifest.checksumAlgorithm);
  if (fileHash !== manifest.checksum) {
    throw new Error(
      `Model integrity check failed: expected ${manifest.checksum}, got ${fileHash}`,
    );
  }

  const signatureValid = await verifySignature(manifest);
  if (!signatureValid) {
    throw new Error(
      `Model signature verification failed for ${manifest.modelId}`,
    );
  }

  return true;
}
```

**Model sourcing checklist:**

- Download models only from verified sources (official registries, signed releases)
- Verify checksums and digital signatures before loading
- Maintain a model registry with provenance records for all deployed models
- Pin model versions in configuration; never use "latest" in production
- Scan model files for known malicious payloads (pickle deserialization attacks)

## AI Bill of Materials (AI-BOM)

Traditional SBOMs do not capture the full scope of AI supply chain risk. Models, datasets, embeddings, and orchestration layers influence application behavior as much as source code.

**What to track in an AI-BOM:**

| Component           | Metadata to Record                                              |
| ------------------- | --------------------------------------------------------------- |
| Models              | Name, version, source, checksum, license, training data summary |
| Datasets            | Source, version, schema, access controls, preprocessing steps   |
| Embeddings          | Model used, dimensions, creation date, source documents         |
| MCP servers         | Name, version, tools exposed, permissions required              |
| AI SDK dependencies | Package, version, known vulnerabilities                         |
| Prompt templates    | Version, hash, last reviewed date                               |

```ts
interface AiBomEntry {
  componentType:
    | 'model'
    | 'dataset'
    | 'embedding'
    | 'mcp-server'
    | 'sdk'
    | 'prompt';
  name: string;
  version: string;
  source: string;
  checksum: string;
  license: string;
  lastAuditDate: string;
  knownVulnerabilities: string[];
}
```

Standards supporting AI-BOM: CycloneDX 1.6 (ML-BOM support) and SPDX 3.0 (AI profiles).

## Data Poisoning Defense (LLM04)

Data poisoning occurs when attackers deliberately manipulate training data, fine-tuning datasets, or RAG knowledge bases to alter model behavior.

**Types of poisoning:**

- **Availability poisoning** -- degrades overall model performance
- **Targeted poisoning** -- introduces bias for specific inputs or categories
- **Backdoor poisoning** -- embeds hidden triggers that activate on specific patterns

**Mitigation strategies:**

- Validate and audit all training and fine-tuning data sources
- Implement anomaly detection on training data distributions
- Use data provenance tracking for all datasets
- Monitor model behavior for unexpected changes after data updates
- Maintain rollback capability to previous known-good model versions

```ts
async function validateTrainingData(
  dataset: DatasetEntry[],
): Promise<ValidationResult> {
  const anomalies = await detectDistributionShift(dataset);
  const duplicates = findExactDuplicates(dataset);
  const suspiciousPatterns = scanForInjectionPayloads(dataset);

  return {
    isClean: anomalies.length === 0 && suspiciousPatterns.length === 0,
    anomalyCount: anomalies.length,
    duplicateCount: duplicates.length,
    suspiciousEntries: suspiciousPatterns,
    recommendation: suspiciousPatterns.length > 0 ? 'quarantine' : 'approved',
  };
}
```

## MCP Security Fundamentals

Model Context Protocol (MCP) allows LLMs to interact with external tools and services. MCP servers are high-value targets because they store authentication tokens for multiple services and execute actions with application-level privileges.

**Core MCP risks:**

- **Tool poisoning** -- malicious tool descriptions that mislead the model
- **Code injection** -- unsanitized inputs passed to APIs, databases, or shell commands
- **Token theft** -- compromised MCP servers expose all connected service tokens
- **Overly broad permissions** -- tools with excessive access patterns

## MCP Tool Allowlisting

Restrict which MCP tools an agent can invoke. Never grant blanket access to all available tools.

```ts
interface McpToolPolicy {
  toolName: string;
  allowed: boolean;
  requiresApproval: boolean;
  maxCallsPerMinute: number;
  allowedParameters: Record<string, ParameterConstraint>;
}

const toolPolicies: McpToolPolicy[] = [
  {
    toolName: 'read_file',
    allowed: true,
    requiresApproval: false,
    maxCallsPerMinute: 30,
    allowedParameters: {
      path: { pattern: /^\/allowed\/paths\//, maxLength: 256 },
    },
  },
  {
    toolName: 'execute_command',
    allowed: true,
    requiresApproval: true,
    maxCallsPerMinute: 5,
    allowedParameters: {
      command: { allowlist: ['ls', 'cat', 'grep'], maxLength: 512 },
    },
  },
  {
    toolName: 'delete_file',
    allowed: false,
    requiresApproval: true,
    maxCallsPerMinute: 0,
    allowedParameters: {},
  },
];

function validateToolCall(
  toolName: string,
  params: Record<string, unknown>,
): { allowed: boolean; requiresApproval: boolean } {
  const policy = toolPolicies.find((p) => p.toolName === toolName);
  if (!policy || !policy.allowed) {
    return { allowed: false, requiresApproval: false };
  }
  return { allowed: true, requiresApproval: policy.requiresApproval };
}
```

## MCP Authentication and Transport

MCP servers must enforce authentication on all inbound requests. The MCP specification recommends OAuth 2.1 for authorization, but authentication is optional by default -- treat it as mandatory.

**Authentication requirements:**

- Verify identity of all MCP clients before processing requests
- Use OAuth 2.1 or mutual TLS for server-to-server communication
- Issue short-lived, scoped tokens for each MCP session
- Never use sessions for authentication; verify each request independently
- Use secure, non-deterministic session IDs

**Transport security:**

- Restrict MCP servers to internal networks when possible
- Use stdio transport for local integrations (avoids network exposure)
- Enforce end-to-end encryption for remote MCP connections
- Implement network segmentation to isolate MCP servers

## MCP Input/Output Validation

Validate all data flowing through MCP tool calls. MCP servers often pass inputs directly to APIs, databases, or shell commands.

```ts
import { z } from 'zod';

const McpToolInputSchema = z.object({
  toolName: z.string().max(100),
  arguments: z.record(z.unknown()),
});

async function handleMcpToolCall(rawInput: unknown) {
  const parsed = McpToolInputSchema.parse(rawInput);
  const policy = getToolPolicy(parsed.toolName);

  if (!policy.allowed) {
    throw new Error(`Tool ${parsed.toolName} is not in the allowlist`);
  }

  const sanitizedArgs = sanitizeToolArguments(
    parsed.arguments,
    policy.allowedParameters,
  );

  if (policy.requiresApproval) {
    const approved = await requestHumanApproval({
      tool: parsed.toolName,
      arguments: sanitizedArgs,
    });
    if (!approved) throw new Error('Tool call rejected by human reviewer');
  }

  const result = await executeTool(parsed.toolName, sanitizedArgs);
  return validateToolOutput(result);
}
```

## MCP Human-in-the-Loop

The MCP specification states there "SHOULD always be a human in the loop." Treat this as a MUST for any tool that modifies state.

**Require human approval for:**

- File write, delete, or modification operations
- Database mutations
- External API calls with side effects
- Credential or permission changes
- Any tool call that cannot be easily reversed

## Supply Chain Security Checklist

| Check                                                 | Category          |
| ----------------------------------------------------- | ----------------- |
| Model checksums verified before deployment            | Model integrity   |
| Model versions pinned (no "latest" in production)     | Model integrity   |
| AI-BOM maintained with all AI components              | Inventory         |
| Training data sources audited and validated           | Data poisoning    |
| MCP tools allowlisted per agent role                  | MCP security      |
| MCP server authentication enforced (OAuth 2.1)        | MCP security      |
| MCP servers isolated on internal networks             | MCP security      |
| Human approval required for state-modifying MCP tools | MCP security      |
| Rollback capability for models and datasets           | Incident response |
| Dependency scanning includes AI SDKs                  | Supply chain      |
