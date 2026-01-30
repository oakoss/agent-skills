---
title: Agentic Zero-Trust Security
description: Zero-trust security patterns for autonomous AI agents including identity management, resource isolation, HITL gates, and anomaly detection
tags: [zero-trust, agent-security, OIDC, HITL, anomaly-detection, WASM-sandbox]
---

# Agentic Zero-Trust Security

Autonomous AI agents are non-human actors that require the same rigor as human identity management. Zero-trust principles ensure agents cannot exceed their granted authority.

## Non-Human Identity (NHI) Management

Every agent must have a verifiable identity. Use OIDC (OpenID Connect) for agent-to-service authentication.

```ts
interface AgentIdentity {
  agentId: string;
  issuer: string;
  scopes: string[];
  issuedAt: number;
  expiresAt: number;
}

async function authenticateAgent(token: string): Promise<AgentIdentity> {
  const decoded = await verifyOIDCToken(token, {
    issuer: process.env.AGENT_OIDC_ISSUER,
    audience: process.env.SERVICE_AUDIENCE,
  });

  if (decoded.expiresAt < Date.now() / 1000) {
    throw new Error('Agent token expired -- rotation required');
  }

  return decoded as AgentIdentity;
}
```

**Key practices:**

- Rotate agent API keys every 24 hours
- Use short-lived tokens (15-minute expiry) for sensitive operations
- Maintain an agent registry with capability declarations
- Log all agent authentication events

## Resource Isolation

Agents should run in isolated environments when executing generated code. WASM runtimes and sandboxed containers prevent breakout.

```ts
interface AgentSandbox {
  runtime: 'wasm' | 'container' | 'vm';
  allowedAPIs: string[];
  memoryLimitMB: number;
  timeoutMs: number;
  networkAccess: 'none' | 'allowlist';
}

const restrictedSandbox: AgentSandbox = {
  runtime: 'wasm',
  allowedAPIs: ['fetch', 'crypto'],
  memoryLimitMB: 256,
  timeoutMs: 30_000,
  networkAccess: 'allowlist',
};
```

**Tool access control:**

- Limit tool access to specific, pre-defined resources per task
- Enforce allowlists for file paths, API endpoints, and database tables
- Revoke access immediately after task completion

## Mandatory Human-in-the-Loop (HITL)

Critical business logic requires human approval before execution.

```ts
interface HITLRequest {
  agentId: string;
  action: string;
  rationale: string;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  requiredApprovers: number;
}

async function requestApproval(request: HITLRequest): Promise<boolean> {
  if (request.riskLevel === 'low') return true;

  const approval = await notifyApprovers(request);
  await auditLog({
    event: 'hitl_decision',
    agentId: request.agentId,
    action: request.action,
    approved: approval.granted,
    approver: approval.userId,
    timestamp: Date.now(),
  });

  return approval.granted;
}
```

**HITL-required actions:**

- Financial transactions above threshold
- Data deletion or modification of production records
- Credential rotation or access grant changes
- External API calls with side effects
- Code deployment to production environments

## Anomaly Detection for Agents

Monitor agent behavior for deviations from the expected baseline.

**Signals to monitor:**

- Unusual volume of API calls (rate spike detection)
- Attempts to access unauthorized modules or files
- Sudden changes in reasoning patterns or output length
- Requests for scopes outside the agent's declared capabilities
- Sequential probing of access boundaries

```ts
interface AgentBehaviorMetrics {
  apiCallsPerMinute: number;
  uniqueEndpointsAccessed: number;
  averageResponseLength: number;
  scopeViolationAttempts: number;
}

function detectAnomaly(
  current: AgentBehaviorMetrics,
  baseline: AgentBehaviorMetrics,
): boolean {
  const thresholds = {
    apiCallSpike: 3.0,
    endpointSpread: 2.0,
    responseLengthDeviation: 2.5,
  };

  return (
    current.apiCallsPerMinute >
      baseline.apiCallsPerMinute * thresholds.apiCallSpike ||
    current.uniqueEndpointsAccessed >
      baseline.uniqueEndpointsAccessed * thresholds.endpointSpread ||
    current.scopeViolationAttempts > 0
  );
}
```

## Token-Level Attack Defense

Protect against attacks that target the token layer.

| Attack              | Defense                                                   |
| ------------------- | --------------------------------------------------------- |
| Prompt leaking      | Design system prompts to be non-extractable               |
| Data smuggling      | Scan outputs for encoded secrets (base64, steganography)  |
| Token manipulation  | Validate token integrity before processing                |
| Replay attacks      | Use nonces and timestamp-bound tokens                     |
| Privilege injection | Validate all capability claims against the agent registry |
