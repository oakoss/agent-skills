---
title: IAM Security
description: IAM roles, policies, least-privilege patterns, service principals, and CDK grant methods
tags:
  [iam, security, policy, role, least-privilege, principal, permissions, trust]
---

# IAM Security

## Core Concepts

IAM controls who (principal) can do what (action) on which resources (resource). Every AWS request is evaluated against IAM policies.

- **Principal**: Entity making the request (user, role, service)
- **Action**: API operation (`s3:GetObject`, `dynamodb:PutItem`)
- **Resource**: ARN of the target (`arn:aws:s3:::my-bucket/*`)
- **Condition**: Optional constraints (IP range, time, tags)

## CDK Grant Methods (Preferred)

CDK L2 constructs provide `grant*` methods that automatically create least-privilege policies.

```ts
import type { Function as LambdaFunction } from 'aws-cdk-lib/aws-lambda';
import type { Table } from 'aws-cdk-lib/aws-dynamodb';
import type { Bucket } from 'aws-cdk-lib/aws-s3';
import type { Queue } from 'aws-cdk-lib/aws-sqs';

declare const fn: LambdaFunction;
declare const table: Table;
declare const bucket: Bucket;
declare const queue: Queue;

table.grantReadWriteData(fn);
bucket.grantRead(fn);
queue.grantSendMessages(fn);
```

Each `grant*` call creates an IAM policy scoped to the specific resource ARN and only the actions needed.

## Custom Policy Statements

When grant methods are insufficient, create explicit policy statements.

```ts
import * as iam from 'aws-cdk-lib/aws-iam';

fn.addToRolePolicy(
  new iam.PolicyStatement({
    effect: iam.Effect.ALLOW,
    actions: ['ses:SendEmail', 'ses:SendRawEmail'],
    resources: ['arn:aws:ses:us-east-1:123456789012:identity/myapp.com'],
  }),
);
```

## Service Roles

Create roles that AWS services assume to perform actions on your behalf.

```ts
import * as iam from 'aws-cdk-lib/aws-iam';

const ecsTaskRole = new iam.Role(this, 'EcsTaskRole', {
  assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com'),
  description: 'Role for ECS tasks to access application resources',
});

table.grantReadWriteData(ecsTaskRole);
bucket.grantReadWrite(ecsTaskRole);
```

## Common Service Principals

| Service        | Principal                  |
| -------------- | -------------------------- |
| Lambda         | `lambda.amazonaws.com`     |
| ECS Tasks      | `ecs-tasks.amazonaws.com`  |
| API Gateway    | `apigateway.amazonaws.com` |
| CloudFront     | `cloudfront.amazonaws.com` |
| Step Functions | `states.amazonaws.com`     |
| EventBridge    | `events.amazonaws.com`     |
| CodeBuild      | `codebuild.amazonaws.com`  |

## Least-Privilege Patterns

### Scoped to Specific DynamoDB Operations

```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem",
    "dynamodb:UpdateItem",
    "dynamodb:Query"
  ],
  "Resource": [
    "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable",
    "arn:aws:dynamodb:us-east-1:123456789012:table/MyTable/index/*"
  ]
}
```

### S3 Bucket with Path Restriction

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:PutObject"],
  "Resource": "arn:aws:s3:::my-bucket/uploads/${aws:PrincipalTag/userId}/*",
  "Condition": {
    "StringEquals": {
      "s3:x-amz-acl": "bucket-owner-full-control"
    }
  }
}
```

### Cross-Account Access

```ts
const crossAccountRole = new iam.Role(this, 'CrossAccountRole', {
  assumedBy: new iam.AccountPrincipal('987654321098'),
  externalIds: ['shared-secret-id'],
});

bucket.grantRead(crossAccountRole);
```

## Policy Conditions

```ts
new iam.PolicyStatement({
  effect: iam.Effect.ALLOW,
  actions: ['s3:PutObject'],
  resources: [bucket.arnForObjects('*')],
  conditions: {
    StringEquals: {
      's3:x-amz-server-side-encryption': 'aws:kms',
    },
    IpAddress: {
      'aws:SourceIp': '203.0.113.0/24',
    },
  },
});
```

## Permission Boundaries

Restrict the maximum permissions a role can have, even if broader policies are attached.

```ts
const boundary = new iam.ManagedPolicy(this, 'Boundary', {
  statements: [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:*', 'dynamodb:*', 'lambda:*', 'logs:*', 'sqs:*', 'sns:*'],
      resources: ['*'],
    }),
    new iam.PolicyStatement({
      effect: iam.Effect.DENY,
      actions: ['iam:*', 'organizations:*', 'account:*'],
      resources: ['*'],
    }),
  ],
});

const role = new iam.Role(this, 'AppRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
  permissionsBoundary: boundary,
});
```

## Common Anti-Patterns

| Anti-Pattern             | Correct Approach                          |
| ------------------------ | ----------------------------------------- |
| `Action: "*"`            | List specific actions needed              |
| `Resource: "*"`          | Scope to specific ARNs                    |
| Shared IAM users         | Use roles with temporary credentials      |
| Long-lived access keys   | Use IAM roles, instance profiles, or OIDC |
| Inline policies on users | Use managed policies attached to roles    |
| No permission boundary   | Set boundaries for delegated admin roles  |

## Secrets Manager Integration

Never store secrets in environment variables or code. Use Secrets Manager with automatic rotation.

```ts
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

const secret = new secretsmanager.Secret(this, 'DbCredentials', {
  secretName: 'prod/db/credentials',
  generateSecretString: {
    secretStringTemplate: JSON.stringify({ username: 'admin' }),
    generateStringKey: 'password',
    excludePunctuation: true,
    passwordLength: 32,
  },
});

secret.grantRead(fn);
```

### Read Secret in Lambda

```ts
import {
  SecretsManagerClient,
  GetSecretValueCommand,
} from '@aws-sdk/client-secrets-manager';

const client = new SecretsManagerClient({ region: process.env.AWS_REGION });

const { SecretString } = await client.send(
  new GetSecretValueCommand({ SecretId: 'prod/db/credentials' }),
);

const credentials = JSON.parse(SecretString!);
```
