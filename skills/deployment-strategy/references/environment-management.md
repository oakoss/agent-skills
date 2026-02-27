---
title: Environment Management
description: Environment promotion workflows, configuration management, environment parity, and secrets handling for multi-stage deployments
tags:
  [
    environments,
    promotion,
    staging,
    production,
    secrets,
    configuration,
    parity,
    gitops,
  ]
---

# Environment Management

## Environment Promotion Model

A promotion model defines how changes flow from development through to production. Each stage acts as a quality gate that catches issues before they reach users.

### Three-Environment Model

```text
Development -> Staging -> Production
     |             |            |
  Feature      Pre-prod      Live
  testing      validation    users
```

| Environment | Purpose                              | Deploy Trigger                  | Data                    |
| ----------- | ------------------------------------ | ------------------------------- | ----------------------- |
| Development | Feature integration, rapid iteration | Push to feature branch          | Synthetic / seed data   |
| Staging     | Pre-production validation, QA, load  | Merge to main or manual promote | Anonymized prod replica |
| Production  | Live user traffic                    | Promotion gate from staging     | Real user data          |

### Promotion Gates Between Environments

Each promotion requires passing automated and manual gates before proceeding.

```text
Dev -> Staging gates:
  - All unit tests pass
  - Linting and type checks pass
  - Container image builds successfully

Staging -> Production gates:
  - Integration tests pass against staging
  - Performance benchmarks within thresholds
  - Security scan passes (no critical vulnerabilities)
  - Manual approval from on-call engineer (production only)
  - Database migration tested against staging data
```

### GitHub Actions Promotion Workflow

```yaml
name: Promote to Production

on:
  workflow_dispatch:
    inputs:
      staging-sha:
        description: 'Staging deployment SHA to promote'
        required: true

jobs:
  verify-staging:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ inputs.staging-sha }}

      - name: Run integration tests against staging
        run: |
          npm ci
          npm run test:integration -- --target=staging

      - name: Verify staging health
        run: |
          curl -sf https://staging.example.com/healthz || exit 1

  promote:
    needs: verify-staging
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        run: |
          kubectl set image deployment/my-app \
            my-app=my-registry/my-app:${{ inputs.staging-sha }} \
            -n production

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/my-app \
            -n production --timeout=300s

      - name: Verify production health
        run: |
          sleep 30
          curl -sf https://app.example.com/healthz || exit 1
```

### GitOps Promotion with Argo CD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/deployment-manifests
    targetRevision: main
    path: environments/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

In GitOps, promotion happens by updating the image tag in the environment-specific directory of the deployment manifests repository. A pull request to change `environments/production/kustomization.yaml` triggers review and automated sync.

### Kustomize Environment Overlays

```text
deployment-manifests/
  base/
    deployment.yaml
    service.yaml
    kustomization.yaml
  environments/
    development/
      kustomization.yaml
    staging/
      kustomization.yaml
    production/
      kustomization.yaml
```

```yaml
# environments/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
images:
  - name: my-app
    newName: my-registry/my-app
    newTag: 'abc123'
replicas:
  - name: my-app
    count: 5
patches:
  - target:
      kind: Deployment
      name: my-app
    patch: |
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/memory
        value: "512Mi"
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/memory
        value: "1Gi"
```

## Environment Parity

Minimize differences between environments to catch issues early. Drift between staging and production is the most common cause of "works in staging, breaks in production" failures.

### Parity Checklist

| Dimension           | Parity Goal                                                      |
| ------------------- | ---------------------------------------------------------------- |
| Infrastructure      | Same container images, same Kubernetes manifests (with overlays) |
| Dependencies        | Same database engine and version, same cache engine              |
| Configuration shape | Same environment variable names, different values                |
| Data volume         | Staging should handle representative load (10-50% of prod)       |
| Network topology    | Same service mesh, ingress, and DNS configuration patterns       |
| TLS / certificates  | Use TLS in all environments, not just production                 |

### What Should Differ

| Dimension         | Development        | Staging                | Production      |
| ----------------- | ------------------ | ---------------------- | --------------- |
| Replica count     | 1                  | 2                      | 3-5+            |
| Resource limits   | Low                | Medium                 | Right-sized     |
| Log level         | debug              | info                   | info or warn    |
| External services | Mocks or sandboxes | Sandbox / staging APIs | Production APIs |
| Data              | Seed / synthetic   | Anonymized prod copy   | Real data       |
| Alerting          | Disabled           | Reduced sensitivity    | Full alerting   |

## Configuration Management

### Environment Variable Patterns

Separate configuration into layers: base defaults, environment-specific overrides, and secrets.

```yaml
# base-config.yaml (committed to repo)
app:
  name: my-app
  port: 8080
  log_format: json
  cors_origins: []
  rate_limit_rpm: 100
```

```yaml
# environment overrides (committed to repo, no secrets)
# staging.yaml
app:
  cors_origins:
    - https://staging.example.com
  rate_limit_rpm: 1000
  log_level: info

# production.yaml
app:
  cors_origins:
    - https://app.example.com
  rate_limit_rpm: 10000
  log_level: warn
```

### Twelve-Factor Config Approach

Configuration that changes between environments belongs in environment variables, not in code. Code should read config from environment and fail fast if required values are missing.

```ts
interface AppConfig {
  databaseUrl: string;
  redisUrl: string;
  apiKey: string;
  environment: 'development' | 'staging' | 'production';
  logLevel: string;
}

function loadConfig(): AppConfig {
  const required = ['DATABASE_URL', 'REDIS_URL', 'API_KEY'] as const;
  const missing = required.filter((key) => !process.env[key]);

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}`,
    );
  }

  return {
    databaseUrl: process.env.DATABASE_URL!,
    redisUrl: process.env.REDIS_URL!,
    apiKey: process.env.API_KEY!,
    environment:
      (process.env.NODE_ENV as AppConfig['environment']) ?? 'development',
    logLevel: process.env.LOG_LEVEL ?? 'info',
  };
}
```

## Secrets Management

Secrets must never be committed to source control. Use platform-provided secret stores with least-privilege access.

### Secrets Management Options

| Tool                   | Best For                                  | Integration               |
| ---------------------- | ----------------------------------------- | ------------------------- |
| GitHub Actions Secrets | CI/CD pipeline secrets                    | `${{ secrets.NAME }}`     |
| AWS Secrets Manager    | AWS-hosted applications                   | SDK or CSI driver         |
| Google Secret Manager  | GCP-hosted applications                   | SDK or CSI driver         |
| HashiCorp Vault        | Multi-cloud, on-prem, enterprise          | API, sidecar, CSI driver  |
| Kubernetes Secrets     | Cluster-scoped secrets (encrypt at rest)  | Volume mount or env var   |
| Doppler / Infisical    | Developer-friendly SaaS secret management | CLI, SDK, Kubernetes sync |

### Kubernetes External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: my-app-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: my-app-secrets
    creationPolicy: Owner
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: production/my-app/database-url
    - secretKey: API_KEY
      remoteRef:
        key: production/my-app/api-key
```

### Secret Rotation Pattern

```text
1. Generate new secret value
2. Update secret store (both old and new values valid)
3. Deploy application that uses new secret
4. Verify application works with new secret
5. Revoke old secret value
6. Audit: confirm no processes still use old secret
```

Never rotate secrets and deploy application changes simultaneously. Rotate secrets as a separate, isolated operation.

## Deployment Concurrency

Prevent overlapping deployments that can cause unpredictable states.

### GitHub Actions Concurrency Control

```yaml
name: Deploy
on:
  push:
    branches: [main]

concurrency:
  group: deploy-production
  cancel-in-progress: false

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - name: Deploy
        run: ./deploy.sh
```

Setting `cancel-in-progress: false` ensures the current deployment completes before the next one starts, preventing partial deployments.

### Kubernetes Resource Quotas for Deployment Safety

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-pdb
  namespace: production
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: my-app
```

A PodDisruptionBudget ensures a minimum number of pods remain available during voluntary disruptions like deployments, node drains, or cluster upgrades.
