---
title: S3 Storage
description: S3 bucket operations, presigned URLs for secure uploads/downloads, lifecycle policies, and CDK bucket configuration
tags: [s3, presigned-url, upload, download, lifecycle, bucket, storage, cors]
---

# S3 Storage

## SDK v3 Client Setup

```ts
import { S3Client } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'us-east-1' });
```

## Upload Objects

```ts
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'us-east-1' });

await s3.send(
  new PutObjectCommand({
    Bucket: 'my-bucket',
    Key: 'uploads/document.pdf',
    Body: fileBuffer,
    ContentType: 'application/pdf',
  }),
);
```

## Download Objects

```ts
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'us-east-1' });

const response = await s3.send(
  new GetObjectCommand({
    Bucket: 'my-bucket',
    Key: 'uploads/document.pdf',
  }),
);

const bodyString = await response.Body?.transformToString();
```

## Presigned URLs

Generate time-limited URLs for secure client-side uploads and downloads without exposing AWS credentials.

### Download URL

```ts
import { S3Client, GetObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3 = new S3Client({ region: 'us-east-1' });

const downloadUrl = await getSignedUrl(
  s3,
  new GetObjectCommand({
    Bucket: 'my-bucket',
    Key: 'private-file.pdf',
  }),
  { expiresIn: 3600 },
);
```

### Upload URL

```ts
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { getSignedUrl } from '@aws-sdk/s3-request-presigner';

const s3 = new S3Client({ region: 'us-east-1' });

const uploadUrl = await getSignedUrl(
  s3,
  new PutObjectCommand({
    Bucket: 'my-bucket',
    Key: 'uploads/new-file.jpg',
    ContentType: 'image/jpeg',
  }),
  {
    expiresIn: 900,
    signableHeaders: new Set(['content-type']),
  },
);
```

The client must include the matching `Content-Type` header when using the presigned upload URL. Maximum expiration is 7 days (604800 seconds).

### Client-Side Upload with Presigned URL

```ts
await fetch(uploadUrl, {
  method: 'PUT',
  headers: { 'Content-Type': 'image/jpeg' },
  body: file,
});
```

## Lifecycle Policies

```ts
import {
  S3Client,
  PutBucketLifecycleConfigurationCommand,
} from '@aws-sdk/client-s3';

const s3 = new S3Client({ region: 'us-east-1' });

await s3.send(
  new PutBucketLifecycleConfigurationCommand({
    Bucket: 'my-bucket',
    LifecycleConfiguration: {
      Rules: [
        {
          ID: 'archive-old-objects',
          Status: 'Enabled',
          Filter: { Prefix: 'logs/' },
          Transitions: [
            { Days: 30, StorageClass: 'STANDARD_IA' },
            { Days: 90, StorageClass: 'GLACIER' },
          ],
          Expiration: { Days: 365 },
        },
        {
          ID: 'cleanup-incomplete-uploads',
          Status: 'Enabled',
          Filter: { Prefix: '' },
          AbortIncompleteMultipartUpload: { DaysAfterInitiation: 7 },
        },
      ],
    },
  }),
);
```

## CDK Bucket Configuration

```ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucket = new s3.Bucket(this, 'AppBucket', {
  bucketName: 'my-app-assets',
  versioned: true,
  encryption: s3.BucketEncryption.S3_MANAGED,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  removalPolicy: cdk.RemovalPolicy.RETAIN,
  lifecycleRules: [
    {
      id: 'archive-old',
      transitions: [
        {
          storageClass: s3.StorageClass.INFREQUENT_ACCESS,
          transitionAfter: cdk.Duration.days(30),
        },
        {
          storageClass: s3.StorageClass.GLACIER,
          transitionAfter: cdk.Duration.days(90),
        },
      ],
      expiration: cdk.Duration.days(365),
    },
    {
      id: 'cleanup-multipart',
      abortIncompleteMultipartUploadAfter: cdk.Duration.days(7),
    },
  ],
});
```

## CORS Configuration for Browser Uploads

```ts
const bucket = new s3.Bucket(this, 'UploadBucket', {
  cors: [
    {
      allowedMethods: [s3.HttpMethods.PUT, s3.HttpMethods.POST],
      allowedOrigins: ['https://myapp.com'],
      allowedHeaders: ['*'],
      maxAge: 3600,
    },
  ],
});
```

## S3 Event Notifications

```ts
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';
import type { Function as LambdaFunction } from 'aws-cdk-lib/aws-lambda';

declare const processUpload: LambdaFunction;

bucket.addEventNotification(
  s3.EventType.OBJECT_CREATED,
  new s3n.LambdaDestination(processUpload),
  { prefix: 'uploads/', suffix: '.pdf' },
);
```

## Storage Classes

| Class        | Use Case                                  | Retrieval                      |
| ------------ | ----------------------------------------- | ------------------------------ |
| STANDARD     | Frequently accessed data                  | Immediate                      |
| STANDARD_IA  | Infrequent access, rapid retrieval needed | Immediate                      |
| ONE_ZONE_IA  | Infrequent, non-critical, single AZ       | Immediate                      |
| GLACIER_IR   | Archive with immediate retrieval          | Immediate                      |
| GLACIER      | Archive, minutes to hours retrieval       | 1-5 min (expedited) to 3-5 hrs |
| DEEP_ARCHIVE | Long-term archive, rarely accessed        | 12-48 hrs                      |
