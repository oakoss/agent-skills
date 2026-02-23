---
title: Containers with ECS and Fargate
description: ECS/Fargate container deployment, ECR image management, task definitions, and CDK pattern constructs
tags:
  [
    ecs,
    fargate,
    ecr,
    container,
    docker,
    task-definition,
    load-balancer,
    deployment,
  ]
---

# Containers with ECS and Fargate

## ECR Repository (CDK)

```ts
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as cdk from 'aws-cdk-lib';

const repo = new ecr.Repository(this, 'AppRepo', {
  repositoryName: 'my-app',
  imageScanOnPush: true,
  lifecycleRules: [
    {
      maxImageCount: 10,
      description: 'Keep last 10 images',
    },
  ],
  removalPolicy: cdk.RemovalPolicy.DESTROY,
});
```

## Push Image to ECR (CLI)

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

docker build -t my-app .
docker tag my-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

## Fargate Service with Load Balancer (CDK)

The `ApplicationLoadBalancedFargateService` pattern construct handles ALB, target group, security groups, and service discovery.

```ts
import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ecs_patterns from 'aws-cdk-lib/aws-ecs-patterns';
import * as ecr from 'aws-cdk-lib/aws-ecr';

const cluster = new ecs.Cluster(this, 'AppCluster', {
  clusterName: 'my-app-cluster',
});

const repo = ecr.Repository.fromRepositoryName(this, 'Repo', 'my-app');

const service = new ecs_patterns.ApplicationLoadBalancedFargateService(
  this,
  'AppService',
  {
    cluster,
    cpu: 512,
    memoryLimitMiB: 1024,
    desiredCount: 2,
    taskImageOptions: {
      image: ecs.ContainerImage.fromEcrRepository(repo, 'latest'),
      containerPort: 3000,
      environment: {
        NODE_ENV: 'production',
      },
    },
    publicLoadBalancer: true,
    circuitBreaker: { rollback: true },
  },
);

service.targetGroup.configureHealthCheck({
  path: '/health',
  interval: cdk.Duration.seconds(30),
  healthyThresholdCount: 2,
  unhealthyThresholdCount: 3,
});
```

## Auto Scaling

```ts
const scaling = service.service.autoScaleTaskCount({
  minCapacity: 2,
  maxCapacity: 10,
});

scaling.scaleOnCpuUtilization('CpuScaling', {
  targetUtilizationPercent: 70,
  scaleInCooldown: cdk.Duration.seconds(60),
  scaleOutCooldown: cdk.Duration.seconds(60),
});

scaling.scaleOnMemoryUtilization('MemoryScaling', {
  targetUtilizationPercent: 80,
});
```

## Custom Task Definition

For more control over container configuration, define the task directly.

```ts
const taskDef = new ecs.FargateTaskDefinition(this, 'TaskDef', {
  cpu: 1024,
  memoryLimitMiB: 2048,
});

const container = taskDef.addContainer('app', {
  image: ecs.ContainerImage.fromEcrRepository(repo, 'latest'),
  logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'my-app' }),
  environment: {
    NODE_ENV: 'production',
  },
  secrets: {
    DB_URL: ecs.Secret.fromSecretsManager(dbSecret),
  },
  healthCheck: {
    command: ['CMD-SHELL', 'curl -f http://localhost:3000/health || exit 1'],
    interval: cdk.Duration.seconds(30),
    timeout: cdk.Duration.seconds(5),
    retries: 3,
  },
});

container.addPortMappings({ containerPort: 3000 });
```

## Secrets in ECS Tasks

```ts
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

const dbSecret = secretsmanager.Secret.fromSecretNameV2(
  this,
  'DbSecret',
  'prod/db/credentials',
);

taskDef.addContainer('app', {
  image: ecs.ContainerImage.fromEcrRepository(repo),
  secrets: {
    DB_HOST: ecs.Secret.fromSecretsManager(dbSecret, 'host'),
    DB_PASSWORD: ecs.Secret.fromSecretsManager(dbSecret, 'password'),
  },
});
```

Secrets are injected as environment variables at container start. The task execution role is automatically granted read access.

## CDK Docker Image Asset

Build and push directly from CDK without managing ECR separately.

```ts
import * as ecs from 'aws-cdk-lib/aws-ecs';

const service = new ecs_patterns.ApplicationLoadBalancedFargateService(
  this,
  'Service',
  {
    cluster,
    taskImageOptions: {
      image: ecs.ContainerImage.fromAsset('./app', {
        buildArgs: { NODE_ENV: 'production' },
      }),
      containerPort: 3000,
    },
  },
);
```

`fromAsset` builds the Docker image locally and pushes it to an auto-managed ECR repository during `cdk deploy`.

## Fargate Sizing Guide

| Workload         | CPU            | Memory  | Notes                               |
| ---------------- | -------------- | ------- | ----------------------------------- |
| Lightweight API  | 256 (.25 vCPU) | 512 MB  | Minimal Node.js service             |
| Standard API     | 512 (.5 vCPU)  | 1024 MB | Typical web application             |
| Compute-heavy    | 1024 (1 vCPU)  | 2048 MB | Image processing, heavy computation |
| Memory-heavy     | 1024 (1 vCPU)  | 4096 MB | Large data processing               |
| High performance | 4096 (4 vCPU)  | 8192 MB | Maximum Fargate configuration       |

Fargate charges per-second based on vCPU and memory. Provision the minimum needed and use auto scaling.

## ECS Exec for Debugging

Enable interactive command execution in running containers.

```ts
const service = new ecs.FargateService(this, 'Service', {
  cluster,
  taskDefinition: taskDef,
  enableExecuteCommand: true,
});
```

```bash
aws ecs execute-command --cluster my-cluster --task TASK_ID --container app --interactive --command "/bin/sh"
```

## Deployment Strategies

| Strategy        | CDK Config                           | Behavior                            |
| --------------- | ------------------------------------ | ----------------------------------- |
| Rolling update  | Default                              | Replace tasks gradually             |
| Circuit breaker | `circuitBreaker: { rollback: true }` | Auto-rollback on deployment failure |
| Blue/green      | Use CodeDeploy                       | Zero-downtime with traffic shifting |

The circuit breaker monitors deployment health and rolls back if new tasks fail to stabilize.
