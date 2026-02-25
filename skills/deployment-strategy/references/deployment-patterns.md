---
title: Deployment Patterns
description: Blue-green, canary, rolling, and recreate deployment strategies with configuration examples and tradeoff analysis
tags:
  [
    blue-green,
    canary,
    rolling,
    recreate,
    zero-downtime,
    traffic-splitting,
    deployment,
  ]
---

# Deployment Patterns

## Strategy Comparison

| Strategy   | Downtime | Rollback Speed | Resource Cost        | Risk Level | Complexity |
| ---------- | -------- | -------------- | -------------------- | ---------- | ---------- |
| Blue-green | None     | Instant        | 2x during deploy     | Low        | Medium     |
| Canary     | None     | Fast           | +5-10% during deploy | Very low   | High       |
| Rolling    | None     | Moderate       | +25% during deploy   | Medium     | Low        |
| Recreate   | Brief    | Slow           | 1x                   | High       | Low        |

## Blue-Green Deployment

Two identical environments run in parallel. Traffic switches atomically from the current (blue) to the new (green) environment. The old environment stays available for instant rollback.

### When to Use

- Applications requiring instant rollback capability
- Stateless services where environment duplication is straightforward
- Releases that need full validation before any user traffic

### Kubernetes Blue-Green with Service Selector

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    version: green
  ports:
    - port: 80
      targetPort: 8080
```

Deploy the green version alongside blue, validate it, then update the Service selector from `version: blue` to `version: green`. Roll back by reverting the selector.

### Kubernetes Blue-Green Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-green
  labels:
    app: my-app
    version: green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: green
  template:
    metadata:
      labels:
        app: my-app
        version: green
    spec:
      containers:
        - name: my-app
          image: my-app:2.0.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 15
            periodSeconds: 20
```

### Blue-Green Traffic Switch Script

```bash
#!/usr/bin/env bash
set -euo pipefail

NEW_VERSION="${1:?Usage: switch-traffic.sh <green|blue>}"
SERVICE_NAME="my-app"
NAMESPACE="production"

kubectl patch service "$SERVICE_NAME" \
  -n "$NAMESPACE" \
  -p "{\"spec\":{\"selector\":{\"version\":\"$NEW_VERSION\"}}}"

echo "Traffic switched to $NEW_VERSION"

kubectl rollout status deployment/"$SERVICE_NAME-$NEW_VERSION" \
  -n "$NAMESPACE" --timeout=120s
```

### AWS ALB Blue-Green with Target Groups

```yaml
Resources:
  BlueTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: my-app-blue
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /healthz
      HealthCheckIntervalSeconds: 10
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3

  GreenTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: my-app-green
      Port: 8080
      Protocol: HTTP
      VpcId: !Ref VpcId
      HealthCheckPath: /healthz
      HealthCheckIntervalSeconds: 10
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3

  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ALB
      Port: 443
      Protocol: HTTPS
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref BlueTargetGroup
```

Switch traffic by updating the listener's default action to point to GreenTargetGroup.

## Canary Deployment

Routes a small percentage of traffic to the new version while the majority continues hitting the stable version. Monitors error rates, latency, and business metrics before gradually increasing the canary percentage.

### When to Use

- High-traffic services where full rollout risk is unacceptable
- Releases requiring real-world validation under production load
- Services with thorough monitoring and alerting

### Canary Progression Example

```text
Phase 1:  5% canary, 95% stable  (10 min observation)
Phase 2: 25% canary, 75% stable  (15 min observation)
Phase 3: 50% canary, 50% stable  (15 min observation)
Phase 4: 100% canary              (full rollout)
```

Halt and roll back at any phase if error rate exceeds threshold.

### Argo Rollouts Canary Configuration

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 10m }
        - setWeight: 25
        - pause: { duration: 15m }
        - setWeight: 50
        - pause: { duration: 15m }
        - setWeight: 100
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
            routes:
              - primary
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:2.0.0
          ports:
            - containerPort: 8080
```

### Istio Virtual Service for Traffic Splitting

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app-vsvc
spec:
  hosts:
    - my-app.example.com
  http:
    - route:
        - destination:
            host: my-app-stable
          weight: 95
        - destination:
            host: my-app-canary
          weight: 5
```

### Nginx Ingress Canary Annotations

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: 'true'
    nginx.ingress.kubernetes.io/canary-weight: '5'
spec:
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-canary
                port:
                  number: 80
```

## Rolling Deployment

Incrementally replaces old instances with new ones. The default strategy in Kubernetes. Controls the pace of updates using maxSurge and maxUnavailable parameters.

### When to Use

- Standard application updates without special rollback requirements
- Services that can tolerate running mixed versions briefly
- Default choice when blue-green or canary complexity is not justified

### Kubernetes Rolling Update Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:2.0.0
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
```

### Rolling Update Parameter Guide

| Parameter      | Effect                              | Conservative | Aggressive |
| -------------- | ----------------------------------- | ------------ | ---------- |
| maxSurge       | Extra pods created during update    | 1 (25%)      | 50%        |
| maxUnavailable | Pods that can be down during update | 0            | 25%        |

- `maxSurge: 1, maxUnavailable: 0` ensures full capacity at all times (safest, slowest)
- `maxSurge: 25%, maxUnavailable: 25%` balances speed and safety (Kubernetes default)

### Rollback a Rolling Update

```bash
kubectl rollout undo deployment/my-app

kubectl rollout undo deployment/my-app --to-revision=3

kubectl rollout history deployment/my-app
```

## Recreate Deployment

Terminates all existing pods before creating new ones. Accepts brief downtime in exchange for simplicity and avoiding mixed-version states.

### When to Use

- Development and staging environments where downtime is acceptable
- Applications that cannot run two versions simultaneously (incompatible schemas, singleton resources)
- Batch processing workloads with no user-facing traffic

### Kubernetes Recreate Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: my-app:2.0.0
```

## Strategy Decision Framework

```text
Need instant rollback?
  YES -> Blue-green
  NO  -> Continue

Can you monitor canary metrics?
  YES -> High-traffic service?
    YES -> Canary
    NO  -> Rolling
  NO  -> Continue

Can you tolerate brief downtime?
  YES -> Recreate
  NO  -> Rolling (with maxUnavailable: 0)
```
