---
title: CloudFront and Route 53 Networking
description: CloudFront CDN distributions, caching strategies, Origin Access Control, Route 53 DNS, and CDK configuration
tags:
  [
    cloudfront,
    cdn,
    route53,
    dns,
    caching,
    origin,
    distribution,
    certificate,
    alias,
  ]
---

# CloudFront and Route 53 Networking

## CloudFront Distribution with S3 Origin (CDK)

```ts
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3 from 'aws-cdk-lib/aws-s3';

const bucket = new s3.Bucket(this, 'AssetsBucket', {
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
});

const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
    allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
    compress: true,
  },
  priceClass: cloudfront.PriceClass.PRICE_CLASS_100,
});
```

`S3BucketOrigin.withOriginAccessControl` creates an OAC automatically and configures the bucket policy. This is the current method, replacing the legacy OAI approach.

## Multiple Origins and Behaviors

```ts
import * as cdk from 'aws-cdk-lib';

const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: origins.S3BucketOrigin.withOriginAccessControl(assetsBucket),
    viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
    cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
  },
  additionalBehaviors: {
    '/api/*': {
      origin: new origins.HttpOrigin('api.myapp.com'),
      viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
      cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
      allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
      originRequestPolicy:
        cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
    },
    '/static/*': {
      origin: origins.S3BucketOrigin.withOriginAccessControl(staticBucket),
      cachePolicy: new cloudfront.CachePolicy(this, 'LongCache', {
        defaultTtl: cdk.Duration.days(30),
        maxTtl: cdk.Duration.days(365),
        minTtl: cdk.Duration.days(1),
        headerBehavior: cloudfront.CacheHeaderBehavior.none(),
        queryStringBehavior: cloudfront.CacheQueryStringBehavior.none(),
      }),
    },
  },
});
```

## Custom Cache Policy

```ts
import * as cdk from 'aws-cdk-lib';

const apiCachePolicy = new cloudfront.CachePolicy(this, 'ApiCache', {
  cachePolicyName: 'api-cache-policy',
  defaultTtl: cdk.Duration.seconds(0),
  maxTtl: cdk.Duration.hours(1),
  minTtl: cdk.Duration.seconds(0),
  headerBehavior: cloudfront.CacheHeaderBehavior.allowList(
    'Authorization',
    'Accept',
  ),
  queryStringBehavior: cloudfront.CacheQueryStringBehavior.all(),
  cookieBehavior: cloudfront.CacheCookieBehavior.none(),
  enableAcceptEncodingGzip: true,
  enableAcceptEncodingBrotli: true,
});
```

## Built-In Cache Policies

| Policy                                       | TTL                  | Headers | Query Strings | Use Case               |
| -------------------------------------------- | -------------------- | ------- | ------------- | ---------------------- |
| `CACHING_OPTIMIZED`                          | 24h default, 1yr max | None    | None          | Static assets          |
| `CACHING_DISABLED`                           | 0                    | None    | None          | Dynamic API calls      |
| `CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS` | 24h default          | None    | None          | Pre-compressed content |

## CloudFront Functions

Lightweight edge functions for URL rewrites, header manipulation, and simple redirects.

```ts
const rewriteFunction = new cloudfront.Function(this, 'RewriteFunction', {
  code: cloudfront.FunctionCode.fromInline(`
    function handler(event) {
      var request = event.request;
      var uri = request.uri;

      if (uri.endsWith('/')) {
        request.uri += 'index.html';
      } else if (!uri.includes('.')) {
        request.uri += '/index.html';
      }

      return request;
    }
  `),
  runtime: cloudfront.FunctionRuntime.JS_2_0,
});

const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
    functionAssociations: [
      {
        function: rewriteFunction,
        eventType: cloudfront.FunctionEventType.VIEWER_REQUEST,
      },
    ],
  },
});
```

## CloudFront with Custom Domain and Certificate

```ts
import * as acm from 'aws-cdk-lib/aws-certificatemanager';
import * as route53 from 'aws-cdk-lib/aws-route53';

const zone = route53.HostedZone.fromLookup(this, 'Zone', {
  domainName: 'myapp.com',
});

const certificate = new acm.Certificate(this, 'Cert', {
  domainName: 'cdn.myapp.com',
  validation: acm.CertificateValidation.fromDns(zone),
});

const distribution = new cloudfront.Distribution(this, 'CDN', {
  defaultBehavior: {
    origin: origins.S3BucketOrigin.withOriginAccessControl(bucket),
  },
  domainNames: ['cdn.myapp.com'],
  certificate,
});
```

CloudFront certificates must be in `us-east-1`. If the stack is in another region, create the certificate in a separate `us-east-1` stack.

## Route 53 DNS Configuration

### Hosted Zone Lookup

```ts
import * as route53 from 'aws-cdk-lib/aws-route53';

const zone = route53.HostedZone.fromLookup(this, 'Zone', {
  domainName: 'myapp.com',
});
```

### Alias Records for AWS Resources

```ts
import * as targets from 'aws-cdk-lib/aws-route53-targets';

new route53.ARecord(this, 'CloudFrontAlias', {
  zone,
  recordName: 'cdn',
  target: route53.RecordTarget.fromAlias(
    new targets.CloudFrontTarget(distribution),
  ),
});

new route53.ARecord(this, 'AlbAlias', {
  zone,
  recordName: 'api',
  target: route53.RecordTarget.fromAlias(new targets.LoadBalancerTarget(alb)),
});
```

Alias records are free (no Route 53 query charges) and support apex domains.

### Common Record Types

```ts
new route53.CnameRecord(this, 'CnameRecord', {
  zone,
  recordName: 'mail',
  domainName: 'mail.provider.com',
});

new route53.TxtRecord(this, 'TxtRecord', {
  zone,
  recordName: '_verification',
  values: ['verify=abc123'],
});

new route53.MxRecord(this, 'MxRecord', {
  zone,
  values: [
    { priority: 10, hostName: 'mx1.provider.com' },
    { priority: 20, hostName: 'mx2.provider.com' },
  ],
});
```

## Cache Invalidation

```bash
aws cloudfront create-invalidation --distribution-id E12345 --paths "/*"
```

```ts
import {
  CloudFrontClient,
  CreateInvalidationCommand,
} from '@aws-sdk/client-cloudfront';

const cf = new CloudFrontClient({ region: 'us-east-1' });

await cf.send(
  new CreateInvalidationCommand({
    DistributionId: 'E12345',
    InvalidationBatch: {
      CallerReference: Date.now().toString(),
      Paths: {
        Quantity: 2,
        Items: ['/index.html', '/api/*'],
      },
    },
  }),
);
```

First 1,000 invalidation paths per month are free. Use wildcard paths to reduce path count.

## Security Headers

```ts
const responseHeadersPolicy = new cloudfront.ResponseHeadersPolicy(
  this,
  'SecurityHeaders',
  {
    securityHeadersBehavior: {
      strictTransportSecurity: {
        accessControlMaxAge: cdk.Duration.days(365),
        includeSubdomains: true,
        override: true,
      },
      contentTypeOptions: { override: true },
      frameOptions: {
        frameOption: cloudfront.HeadersFrameOption.DENY,
        override: true,
      },
      referrerPolicy: {
        referrerPolicy:
          cloudfront.HeadersReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN,
        override: true,
      },
    },
  },
);
```
