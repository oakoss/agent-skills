---
title: Lambda Functions
description: Lambda function configuration, layers, cold start optimization, event sources, and CDK patterns
tags:
  [
    lambda,
    serverless,
    cold-start,
    layers,
    event-source,
    nodejs,
    bundling,
    timeout,
  ]
---

# Lambda Functions

## CDK NodejsFunction (Recommended)

The `NodejsFunction` construct bundles TypeScript/JavaScript with esbuild automatically.

```ts
import * as cdk from 'aws-cdk-lib';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import * as lambda from 'aws-cdk-lib/aws-lambda';

const fn = new NodejsFunction(this, 'ProcessOrder', {
  entry: 'src/handlers/process-order.ts',
  handler: 'handler',
  runtime: lambda.Runtime.NODEJS_20_X,
  memorySize: 256,
  timeout: cdk.Duration.seconds(30),
  environment: {
    TABLE_NAME: table.tableName,
    STAGE: 'production',
  },
  bundling: {
    minify: true,
    sourceMap: true,
    externalModules: ['@aws-sdk/*'],
  },
});

table.grantReadWriteData(fn);
```

The `externalModules: ['@aws-sdk/*']` excludes the SDK from the bundle since Lambda provides it in the runtime.

## Basic Lambda Function

```ts
import * as lambda from 'aws-cdk-lib/aws-lambda';

const fn = new lambda.Function(this, 'MyFunction', {
  runtime: lambda.Runtime.NODEJS_20_X,
  handler: 'index.handler',
  code: lambda.Code.fromAsset('lambda/my-function'),
  memorySize: 128,
  timeout: cdk.Duration.seconds(10),
});
```

## Handler Pattern

```ts
import type { APIGatewayProxyEvent, APIGatewayProxyResult } from 'aws-lambda';

export const handler = async (
  event: APIGatewayProxyEvent,
): Promise<APIGatewayProxyResult> => {
  const body = JSON.parse(event.body ?? '{}');

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Success', data: body }),
  };
};
```

## Lambda Layers

Share dependencies or utility code across multiple functions.

```ts
const sharedLayer = new lambda.LayerVersion(this, 'SharedLayer', {
  code: lambda.Code.fromAsset('layers/shared'),
  compatibleRuntimes: [lambda.Runtime.NODEJS_20_X],
  description: 'Shared utilities and common dependencies',
});

const fn = new NodejsFunction(this, 'MyFunction', {
  entry: 'src/handlers/my-function.ts',
  layers: [sharedLayer],
  bundling: {
    externalModules: ['@aws-sdk/*', '/opt/nodejs/*'],
  },
});
```

Layer code is available at `/opt/nodejs/` in the Lambda execution environment.

## Cold Start Optimization

| Technique                           | Impact                                   | Trade-off                         |
| ----------------------------------- | ---------------------------------------- | --------------------------------- |
| Increase memory                     | Proportionally faster CPU                | Higher cost per invocation        |
| Minimize bundle size                | Faster code loading                      | Requires bundler config           |
| Use `NODEJS_20_X` or later          | Faster startup than older runtimes       | Maintain runtime updates          |
| Provisioned concurrency             | Eliminates cold starts                   | Constant cost even when idle      |
| Keep initialization outside handler | Reuse across invocations                 | Connection limits in concurrency  |
| Lazy-load heavy dependencies        | Faster initial response for simple paths | Slower first use of loaded module |

### Provisioned Concurrency

```ts
const alias = fn.addAlias('live');

const scaling = alias.addAutoScaling({
  minCapacity: 5,
  maxCapacity: 50,
});

scaling.scaleOnUtilization({ utilizationTarget: 0.7 });
```

### Connection Reuse

```ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

// Initialized once per container, reused across invocations
const client = new DynamoDBClient({ region: process.env.AWS_REGION });

export const handler = async (event: unknown) => {
  // client is reused across warm invocations
  return client.send(/* ... */);
};
```

## Event Sources

### SQS Event Source

```ts
import * as eventsources from 'aws-cdk-lib/aws-lambda-event-sources';
import type { Queue } from 'aws-cdk-lib/aws-sqs';

declare const queue: Queue;

fn.addEventSource(
  new eventsources.SqsEventSource(queue, {
    batchSize: 10,
    maxBatchingWindow: cdk.Duration.seconds(5),
    reportBatchItemFailures: true,
  }),
);
```

### S3 Event Source

```ts
import * as eventsources from 'aws-cdk-lib/aws-lambda-event-sources';
import type { Bucket } from 'aws-cdk-lib/aws-s3';

declare const bucket: Bucket;

fn.addEventSource(
  new eventsources.S3EventSource(bucket, {
    events: [s3.EventType.OBJECT_CREATED],
    filters: [{ prefix: 'uploads/', suffix: '.csv' }],
  }),
);
```

### DynamoDB Streams Event Source

```ts
import * as eventsources from 'aws-cdk-lib/aws-lambda-event-sources';
import type { Table } from 'aws-cdk-lib/aws-dynamodb';

declare const table: Table;

fn.addEventSource(
  new eventsources.DynamoEventSource(table, {
    startingPosition: lambda.StartingPosition.TRIM_HORIZON,
    batchSize: 100,
    retryAttempts: 3,
    bisectBatchOnError: true,
  }),
);
```

### API Gateway Integration

```ts
import * as apigw from 'aws-cdk-lib/aws-apigateway';

const api = new apigw.RestApi(this, 'Api', {
  restApiName: 'MyService',
  deployOptions: { stageName: 'prod' },
});

api.root
  .addResource('orders')
  .addMethod('POST', new apigw.LambdaIntegration(fn));
```

## Function URL (No API Gateway)

```ts
const fnUrl = fn.addFunctionUrl({
  authType: lambda.FunctionUrlAuthType.NONE,
  cors: {
    allowedOrigins: ['https://myapp.com'],
    allowedMethods: [lambda.HttpMethod.POST],
  },
});

new cdk.CfnOutput(this, 'FunctionUrl', { value: fnUrl.url });
```

## Invocation via SDK

```ts
import { LambdaClient, InvokeCommand } from '@aws-sdk/client-lambda';

const client = new LambdaClient({ region: 'us-west-2' });

const response = await client.send(
  new InvokeCommand({
    FunctionName: 'my-function',
    InvocationType: 'RequestResponse',
    Payload: JSON.stringify({ action: 'process', data: [1, 2, 3] }),
  }),
);

const result = JSON.parse(response.Payload!.transformToString());

if (response.FunctionError) {
  throw new Error(`Lambda error: ${response.FunctionError}`);
}
```

## Memory and Timeout Guidelines

| Workload                 | Memory       | Timeout  |
| ------------------------ | ------------ | -------- |
| API handler (simple)     | 128-256 MB   | 10-30s   |
| API handler (DB queries) | 256-512 MB   | 30s      |
| File processing          | 512-1024 MB  | 60-300s  |
| Heavy computation        | 1024-3008 MB | 300-900s |

Maximum timeout is 900 seconds (15 minutes). For longer tasks, use Step Functions or ECS tasks.
