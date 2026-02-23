---
title: DynamoDB
description: DynamoDB single-table design, GSI/LSI patterns, streams, SDK operations, and CDK table configuration
tags:
  [
    dynamodb,
    single-table,
    gsi,
    lsi,
    streams,
    query,
    nosql,
    partition-key,
    sort-key,
  ]
---

# DynamoDB

## CDK Table Definition

```ts
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

const table = new dynamodb.Table(this, 'AppTable', {
  tableName: 'MyAppTable',
  partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
  stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
  pointInTimeRecoverySpecification: { pointInTimeRecoveryEnabled: true },
  removalPolicy: cdk.RemovalPolicy.RETAIN,
});
```

## Global Secondary Indexes (GSI)

GSIs have their own partition and sort keys, enabling alternate access patterns. They have separate throughput and support eventual consistency only.

```ts
table.addGlobalSecondaryIndex({
  indexName: 'GSI1',
  partitionKey: { name: 'gsi1pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'gsi1sk', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});

table.addGlobalSecondaryIndex({
  indexName: 'GSI2',
  partitionKey: { name: 'gsi2pk', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.INCLUDE,
  nonKeyAttributes: ['email', 'name', 'status'],
});
```

## Local Secondary Indexes (LSI)

LSIs share the table partition key but with an alternate sort key. Must be defined at table creation time. Support strongly consistent reads.

```ts
const table = new dynamodb.Table(this, 'Table', {
  partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
  billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
});

table.addLocalSecondaryIndex({
  indexName: 'LSI1',
  sortKey: { name: 'createdAt', type: dynamodb.AttributeType.STRING },
  projectionType: dynamodb.ProjectionType.ALL,
});
```

## Single-Table Design

Store multiple entity types in one table using composite keys. Design access patterns before choosing key schema.

### Key Schema Example

| Entity    | pk                    | sk                | GSI1pk            | GSI1sk            |
| --------- | --------------------- | ----------------- | ----------------- | ----------------- |
| User      | `USER#<userId>`       | `PROFILE`         | `EMAIL#<email>`   | `USER#<userId>`   |
| Order     | `USER#<userId>`       | `ORDER#<orderId>` | `ORDER#<orderId>` | `<status>#<date>` |
| Product   | `PRODUCT#<productId>` | `METADATA`        | `CATEGORY#<cat>`  | `<price>`         |
| OrderItem | `ORDER#<orderId>`     | `ITEM#<itemId>`   | -                 | -                 |

### Access Patterns

| Pattern          | Operation      | Key Condition                                     |
| ---------------- | -------------- | ------------------------------------------------- |
| Get user profile | `GetItem`      | `pk = USER#123, sk = PROFILE`                     |
| List user orders | `Query`        | `pk = USER#123, sk begins_with ORDER#`            |
| Get order by ID  | `Query` (GSI1) | `gsi1pk = ORDER#456`                              |
| Orders by status | `Query` (GSI1) | `gsi1pk = ORDER#456, gsi1sk begins_with SHIPPED#` |
| User by email    | `Query` (GSI1) | `gsi1pk = EMAIL#user@example.com`                 |

## SDK Operations

### PutItem

```ts
import { DynamoDBClient, PutItemCommand } from '@aws-sdk/client-dynamodb';
import { marshall } from '@aws-sdk/util-dynamodb';

const client = new DynamoDBClient({ region: 'us-east-1' });

await client.send(
  new PutItemCommand({
    TableName: 'MyAppTable',
    Item: marshall({
      pk: 'USER#123',
      sk: 'PROFILE',
      name: 'Jane Doe',
      email: 'jane@example.com',
      gsi1pk: 'EMAIL#jane@example.com',
      gsi1sk: 'USER#123',
    }),
    ConditionExpression: 'attribute_not_exists(pk)',
  }),
);
```

### Query

```ts
import { DynamoDBClient, QueryCommand } from '@aws-sdk/client-dynamodb';
import { unmarshall } from '@aws-sdk/util-dynamodb';

const client = new DynamoDBClient({ region: 'us-east-1' });

const result = await client.send(
  new QueryCommand({
    TableName: 'MyAppTable',
    KeyConditionExpression: 'pk = :pk AND begins_with(sk, :prefix)',
    ExpressionAttributeValues: {
      ':pk': { S: 'USER#123' },
      ':prefix': { S: 'ORDER#' },
    },
    ScanIndexForward: false,
    Limit: 20,
  }),
);

const orders = result.Items?.map(unmarshall) ?? [];
```

### Query on GSI

```ts
const result = await client.send(
  new QueryCommand({
    TableName: 'MyAppTable',
    IndexName: 'GSI1',
    KeyConditionExpression: 'gsi1pk = :email',
    ExpressionAttributeValues: {
      ':email': { S: 'EMAIL#jane@example.com' },
    },
  }),
);
```

### UpdateItem with Expressions

```ts
import { DynamoDBClient, UpdateItemCommand } from '@aws-sdk/client-dynamodb';

const client = new DynamoDBClient({ region: 'us-east-1' });

await client.send(
  new UpdateItemCommand({
    TableName: 'MyAppTable',
    Key: {
      pk: { S: 'USER#123' },
      sk: { S: 'PROFILE' },
    },
    UpdateExpression: 'SET #name = :name, updatedAt = :now ADD loginCount :inc',
    ExpressionAttributeNames: { '#name': 'name' },
    ExpressionAttributeValues: {
      ':name': { S: 'Jane Smith' },
      ':now': { S: new Date().toISOString() },
      ':inc': { N: '1' },
    },
    ConditionExpression: 'attribute_exists(pk)',
  }),
);
```

### TransactWriteItems

```ts
import {
  DynamoDBClient,
  TransactWriteItemsCommand,
} from '@aws-sdk/client-dynamodb';

const client = new DynamoDBClient({ region: 'us-east-1' });

await client.send(
  new TransactWriteItemsCommand({
    TransactItems: [
      {
        Put: {
          TableName: 'MyAppTable',
          Item: {
            pk: { S: 'ORDER#789' },
            sk: { S: 'METADATA' },
            status: { S: 'CREATED' },
          },
        },
      },
      {
        Update: {
          TableName: 'MyAppTable',
          Key: { pk: { S: 'USER#123' }, sk: { S: 'PROFILE' } },
          UpdateExpression: 'ADD orderCount :inc',
          ExpressionAttributeValues: { ':inc': { N: '1' } },
        },
      },
    ],
  }),
);
```

## DynamoDB Streams

Streams capture item-level changes for event-driven architectures.

| Stream View Type     | Captures                              |
| -------------------- | ------------------------------------- |
| `KEYS_ONLY`          | Only the key attributes               |
| `NEW_IMAGE`          | Entire item after modification        |
| `OLD_IMAGE`          | Entire item before modification       |
| `NEW_AND_OLD_IMAGES` | Both before and after (most flexible) |

Stream records are ordered by partition key, enabling sequential processing per item.

## DynamoDB Document Client

Higher-level abstraction that handles marshalling automatically.

```ts
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  PutCommand,
  QueryCommand,
} from '@aws-sdk/lib-dynamodb';

const ddbClient = new DynamoDBClient({ region: 'us-east-1' });
const docClient = DynamoDBDocumentClient.from(ddbClient);

await docClient.send(
  new PutCommand({
    TableName: 'MyAppTable',
    Item: { pk: 'USER#123', sk: 'PROFILE', name: 'Jane', tags: ['admin'] },
  }),
);

const result = await docClient.send(
  new QueryCommand({
    TableName: 'MyAppTable',
    KeyConditionExpression: 'pk = :pk',
    ExpressionAttributeValues: { ':pk': 'USER#123' },
  }),
);
```

## Capacity Planning

| Billing Mode                | When to Use                                         |
| --------------------------- | --------------------------------------------------- |
| PAY_PER_REQUEST (on-demand) | Unpredictable traffic, new tables, development      |
| PROVISIONED                 | Predictable steady-state traffic, cost optimization |
| PROVISIONED + Auto Scaling  | Predictable with periodic spikes                    |
