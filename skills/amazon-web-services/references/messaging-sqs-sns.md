---
title: Messaging with SQS and SNS
description: SQS queues, SNS topics, dead-letter queues, fan-out patterns, FIFO queues, and CDK configuration
tags:
  [sqs, sns, queue, topic, fan-out, dead-letter, fifo, messaging, event-driven]
---

# Messaging with SQS and SNS

## SQS Queue (CDK)

```ts
import * as cdk from 'aws-cdk-lib';
import * as sqs from 'aws-cdk-lib/aws-sqs';

const dlq = new sqs.Queue(this, 'DeadLetterQueue', {
  queueName: 'my-app-dlq',
  retentionPeriod: cdk.Duration.days(14),
});

const queue = new sqs.Queue(this, 'ProcessingQueue', {
  queueName: 'my-app-queue',
  visibilityTimeout: cdk.Duration.seconds(60),
  retentionPeriod: cdk.Duration.days(4),
  deadLetterQueue: {
    queue: dlq,
    maxReceiveCount: 3,
  },
});
```

Always attach a dead-letter queue. Messages that fail `maxReceiveCount` times move to the DLQ for investigation.

## FIFO Queue

FIFO queues guarantee exactly-once processing and message ordering within a message group.

```ts
const fifoQueue = new sqs.Queue(this, 'OrderQueue', {
  queueName: 'orders.fifo',
  fifo: true,
  contentBasedDeduplication: true,
  visibilityTimeout: cdk.Duration.seconds(30),
  deadLetterQueue: {
    queue: new sqs.Queue(this, 'OrderDLQ', {
      queueName: 'orders-dlq.fifo',
      fifo: true,
    }),
    maxReceiveCount: 3,
  },
});
```

FIFO queue names must end with `.fifo`. Maximum throughput is 300 messages/second (3,000 with high throughput mode).

## Send Messages (SDK)

```ts
import {
  SQSClient,
  SendMessageCommand,
  SendMessageBatchCommand,
} from '@aws-sdk/client-sqs';

const sqs = new SQSClient({ region: 'us-west-2' });

await sqs.send(
  new SendMessageCommand({
    QueueUrl: process.env.QUEUE_URL,
    MessageBody: JSON.stringify({ orderId: '123', action: 'process' }),
    MessageAttributes: {
      EventType: { DataType: 'String', StringValue: 'order_created' },
    },
  }),
);
```

### Batch Send

```ts
await sqs.send(
  new SendMessageBatchCommand({
    QueueUrl: process.env.QUEUE_URL,
    Entries: items.map((item, idx) => ({
      Id: `msg-${idx}`,
      MessageBody: JSON.stringify(item),
    })),
  }),
);
```

Maximum 10 messages per batch. Total batch size limit is 256 KB.

## Receive and Process Messages (SDK)

```ts
import {
  SQSClient,
  ReceiveMessageCommand,
  DeleteMessageCommand,
} from '@aws-sdk/client-sqs';

const sqs = new SQSClient({ region: 'us-west-2' });
const queueUrl = process.env.QUEUE_URL!;

const result = await sqs.send(
  new ReceiveMessageCommand({
    QueueUrl: queueUrl,
    MaxNumberOfMessages: 10,
    WaitTimeSeconds: 20,
    MessageAttributeNames: ['All'],
  }),
);

for (const message of result.Messages ?? []) {
  const body = JSON.parse(message.Body!);
  await processMessage(body);

  await sqs.send(
    new DeleteMessageCommand({
      QueueUrl: queueUrl,
      ReceiptHandle: message.ReceiptHandle!,
    }),
  );
}
```

`WaitTimeSeconds: 20` enables long polling, reducing empty responses and API costs.

## Lambda SQS Handler with Batch Item Failures

```ts
import type { SQSEvent, SQSBatchResponse } from 'aws-lambda';

export const handler = async (event: SQSEvent): Promise<SQSBatchResponse> => {
  const batchItemFailures: SQSBatchResponse['batchItemFailures'] = [];

  for (const record of event.Records) {
    try {
      const body = JSON.parse(record.body);
      await processMessage(body);
    } catch {
      batchItemFailures.push({ itemIdentifier: record.messageId });
    }
  }

  return { batchItemFailures };
};
```

Enable `reportBatchItemFailures` on the event source mapping so only failed messages return to the queue.

## SNS Topic (CDK)

```ts
import * as sns from 'aws-cdk-lib/aws-sns';
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';

const topic = new sns.Topic(this, 'OrderEvents', {
  topicName: 'order-events',
});

topic.addSubscription(new subscriptions.SqsSubscription(queue));
topic.addSubscription(new subscriptions.LambdaSubscription(notifyFn));
topic.addSubscription(new subscriptions.EmailSubscription('alerts@myapp.com'));
```

## Fan-Out Pattern

SNS topic publishes to multiple SQS queues, each processing independently.

```ts
const orderTopic = new sns.Topic(this, 'OrderTopic');

const fulfillmentQueue = new sqs.Queue(this, 'FulfillmentQueue');
const analyticsQueue = new sqs.Queue(this, 'AnalyticsQueue');
const notificationQueue = new sqs.Queue(this, 'NotificationQueue');

orderTopic.addSubscription(new subscriptions.SqsSubscription(fulfillmentQueue));
orderTopic.addSubscription(new subscriptions.SqsSubscription(analyticsQueue));
orderTopic.addSubscription(
  new subscriptions.SqsSubscription(notificationQueue),
);
```

### Filtered Subscriptions

```ts
orderTopic.addSubscription(
  new subscriptions.SqsSubscription(highPriorityQueue, {
    filterPolicy: {
      priority: sns.SubscriptionFilter.stringFilter({
        allowlist: ['high', 'critical'],
      }),
    },
  }),
);
```

## Publish to SNS (SDK)

```ts
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';

const sns = new SNSClient({ region: 'us-east-1' });

await sns.send(
  new PublishCommand({
    TopicArn: process.env.TOPIC_ARN,
    Message: JSON.stringify({ orderId: '123', status: 'shipped' }),
    MessageAttributes: {
      priority: { DataType: 'String', StringValue: 'high' },
    },
  }),
);
```

## SQS vs SNS Comparison

| Feature          | SQS                               | SNS                          |
| ---------------- | --------------------------------- | ---------------------------- |
| Pattern          | Point-to-point                    | Pub/sub                      |
| Consumers        | Single consumer per message       | Multiple subscribers         |
| Persistence      | Messages retained until processed | No persistence (push-based)  |
| Ordering         | FIFO queues support ordering      | FIFO topics support ordering |
| Max message size | 256 KB                            | 256 KB                       |
| Use case         | Work queues, task buffering       | Event fanout, notifications  |

## Visibility Timeout Guidelines

| Processing Time | Visibility Timeout |
| --------------- | ------------------ |
| < 5s            | 30s                |
| 5-30s           | 60s                |
| 30s-2min        | 5min               |
| > 2min          | 6x processing time |

Set visibility timeout to at least 6x the expected processing time. If a Lambda processes the queue, set it to match or exceed the Lambda timeout.
