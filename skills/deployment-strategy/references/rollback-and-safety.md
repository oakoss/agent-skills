---
title: Rollback and Safety
description: Rollback procedures, health checks, feature flags, progressive delivery, and blast radius management for safe deployments
tags:
  [
    rollback,
    health-checks,
    feature-flags,
    progressive-delivery,
    blast-radius,
    readiness,
    liveness,
  ]
---

# Rollback and Safety

## Rollback Procedures

Every production deployment must have a tested rollback plan before the deploy begins. The rollback method depends on the deployment strategy and platform.

### Rollback by Platform

| Platform         | Rollback Method                                     | Speed   |
| ---------------- | --------------------------------------------------- | ------- |
| Kubernetes       | `kubectl rollout undo deployment/name`              | Seconds |
| Vercel / Netlify | Promote previous deployment from dashboard or CLI   | Seconds |
| AWS ECS          | Update service to previous task definition revision | Minutes |
| AWS CodeDeploy   | Automatic rollback on alarm trigger                 | Minutes |
| Docker Compose   | `docker compose up -d` with previous image tag      | Seconds |
| Argo Rollouts    | `kubectl argo rollouts abort name`                  | Seconds |

### Kubernetes Rollback Commands

```bash
kubectl rollout undo deployment/my-app

kubectl rollout undo deployment/my-app --to-revision=3

kubectl rollout history deployment/my-app

kubectl rollout status deployment/my-app
```

### Automated Rollback with Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 5m }
        - analysis:
            templates:
              - templateName: error-rate-check
            args:
              - name: service-name
                value: my-app
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate-check
spec:
  metrics:
    - name: error-rate
      interval: 60s
      successCondition: result[0] < 0.05
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus.monitoring:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

If the error rate exceeds 5% in three consecutive checks, the rollout aborts and traffic reverts to the stable version automatically.

### AWS CodeDeploy Automatic Rollback

```yaml
Resources:
  DeploymentGroup:
    Type: AWS::CodeDeploy::DeploymentGroup
    Properties:
      ApplicationName: !Ref Application
      DeploymentGroupName: production
      DeploymentStyle:
        DeploymentOption: WITH_TRAFFIC_CONTROL
        DeploymentType: BLUE_GREEN
      AutoRollbackConfiguration:
        Enabled: true
        Events:
          - DEPLOYMENT_FAILURE
          - DEPLOYMENT_STOP_ON_ALARM
      AlarmConfiguration:
        Alarms:
          - Name: HighErrorRate
          - Name: HighLatency
        Enabled: true
```

## Health Checks

Health checks verify that application instances are functioning correctly. Configure three types of probes for comprehensive health monitoring.

### Probe Types

| Probe     | Purpose                              | Failure Action             |
| --------- | ------------------------------------ | -------------------------- |
| Startup   | Slow-starting containers finish init | Kill and restart container |
| Readiness | Instance is ready to accept traffic  | Remove from load balancer  |
| Liveness  | Instance is alive and not deadlocked | Kill and restart container |

### Kubernetes Health Probe Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
        - name: my-app
          image: my-app:2.0.0
          ports:
            - containerPort: 8080
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            failureThreshold: 30
            periodSeconds: 2
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 0
            periodSeconds: 10
            failureThreshold: 3
```

### Health Check Endpoint Implementation

```ts
import { type Request, type Response } from 'express';

interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  checks: Record<string, { status: string; latencyMs?: number }>;
}

async function checkDatabase(pool: unknown): Promise<boolean> {
  try {
    await (pool as { query: (q: string) => Promise<unknown> }).query(
      'SELECT 1',
    );
    return true;
  } catch {
    return false;
  }
}

async function checkRedis(client: unknown): Promise<boolean> {
  try {
    const result = await (client as { ping: () => Promise<string> }).ping();
    return result === 'PONG';
  } catch {
    return false;
  }
}

export function healthzHandler(_req: Request, res: Response): void {
  res.status(200).json({ status: 'ok' });
}

export async function readinessHandler(
  _req: Request,
  res: Response,
  deps: { pool: unknown; redis: unknown },
): Promise<void> {
  const start = Date.now();
  const dbOk = await checkDatabase(deps.pool);
  const dbLatency = Date.now() - start;

  const redisStart = Date.now();
  const redisOk = await checkRedis(deps.redis);
  const redisLatency = Date.now() - redisStart;

  const health: HealthStatus = {
    status: dbOk && redisOk ? 'healthy' : 'unhealthy',
    checks: {
      database: { status: dbOk ? 'up' : 'down', latencyMs: dbLatency },
      redis: { status: redisOk ? 'up' : 'down', latencyMs: redisLatency },
    },
  };

  res.status(health.status === 'healthy' ? 200 : 503).json(health);
}
```

## Feature Flags for Progressive Delivery

Feature flags decouple deployment from release. Code ships to production with new functionality disabled, then activates incrementally based on flag configuration.

### Feature Flag Lifecycle

```text
1. Create flag with owner and planned removal date
2. Implement behind flag (default: OFF)
3. Deploy to production (flag still OFF)
4. Enable for internal users / beta testers
5. Progressive rollout: 5% -> 25% -> 50% -> 100%
6. Monitor metrics at each stage
7. Remove flag and dead code after full rollout
```

### Feature Flag Implementation

```ts
interface FeatureFlag {
  name: string;
  enabled: boolean;
  rolloutPercentage: number;
  allowlist: string[];
}

function isFeatureEnabled(flag: FeatureFlag, userId: string): boolean {
  if (!flag.enabled) return false;
  if (flag.allowlist.includes(userId)) return true;

  const hash = simpleHash(userId + flag.name);
  return hash % 100 < flag.rolloutPercentage;
}

function simpleHash(input: string): number {
  let hash = 0;
  for (let i = 0; i < input.length; i++) {
    const char = input.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return Math.abs(hash);
}
```

### Feature Flag with Safe Defaults

```ts
async function getFlags(
  flagService: { getFlag: (name: string) => Promise<FeatureFlag> },
  flagName: string,
): Promise<FeatureFlag> {
  try {
    return await flagService.getFlag(flagName);
  } catch {
    return {
      name: flagName,
      enabled: false,
      rolloutPercentage: 0,
      allowlist: [],
    };
  }
}
```

When the flag service is unreachable, default to the safe state (feature disabled). This circuit breaker pattern prevents flag service outages from cascading into application failures.

### Feature Flag Hygiene

| Rule                           | Why                                                    |
| ------------------------------ | ------------------------------------------------------ |
| Assign an owner to every flag  | Prevents orphaned flags that nobody removes            |
| Set a planned removal date     | Creates accountability for cleanup                     |
| Limit active flags per service | More than 10 active flags signals excessive complexity |
| Test both flag states          | Ensures OFF path still works after months of ON        |
| Log flag evaluations           | Aids debugging and audit trails                        |

## Blast Radius Management

Blast radius is the scope of impact when a deployment fails. Reduce it by limiting who and what is affected by any single change.

### Techniques to Reduce Blast Radius

| Technique              | Blast Radius Reduction                              |
| ---------------------- | --------------------------------------------------- |
| Canary deployment      | Only 1-5% of users see the new version initially    |
| Feature flags          | Toggle specific features without redeploying        |
| Region-based rollout   | Deploy to one region first, expand after validation |
| User segment targeting | Enable for internal users, then beta, then everyone |
| Small batch deploys    | Deploy frequently with small changesets             |

### Region-Based Rollout Order

```text
Phase 1: Internal staging environment (all engineers)
Phase 2: Smallest production region (lowest traffic)
Phase 3: Secondary production regions
Phase 4: Primary production region (highest traffic)

Gate between each phase: error rate < 0.1%, p99 latency < target
```

## Database Migration Safety

Database changes are the most common source of failed rollbacks. Use the expand-contract pattern to keep both old and new application versions compatible with the database schema.

### Expand-Contract Pattern

```text
Step 1 (Expand): Add new column/table, deploy app that writes to BOTH old and new
Step 2 (Migrate): Backfill existing data from old to new location
Step 3 (Switch): Deploy app that reads from new, writes to BOTH
Step 4 (Contract): Remove old column/table after all instances use new schema
```

### Safe Migration Example

```sql
-- Step 1: Add new column (backward compatible)
ALTER TABLE users ADD COLUMN email_normalized VARCHAR(255);

-- Step 2: Backfill data
UPDATE users SET email_normalized = LOWER(TRIM(email)) WHERE email_normalized IS NULL;

-- Step 3: App now reads from email_normalized (deploy and verify)

-- Step 4: Drop old usage (only after all app instances use new column)
-- ALTER TABLE users DROP COLUMN email;  -- do this in a SEPARATE migration
```

Never combine schema changes with data migrations in the same deployment. Never drop columns or tables in the same release that stops writing to them.
