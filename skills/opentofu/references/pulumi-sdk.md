---
title: Pulumi SDK Patterns
description: Pulumi TypeScript and Python SDK patterns, component resources, inputs/outputs, and resource options
tags:
  [
    pulumi,
    typescript,
    python,
    component-resource,
    input,
    output,
    resource-options,
  ]
---

# Pulumi SDK Patterns

## TypeScript Project Setup

```bash
pulumi new typescript
```

### Basic Resource Creation

```ts
import * as aws from '@pulumi/aws';
import * as pulumi from '@pulumi/pulumi';

const bucket = new aws.s3.Bucket('my-bucket', {
  versioning: {
    enabled: true,
  },
  tags: {
    Environment: pulumi.getStack(),
    ManagedBy: 'pulumi',
  },
});

export const bucketName = bucket.id;
export const bucketArn = bucket.arn;
```

### Working with Outputs

Outputs are values that resolve asynchronously after resource creation.

```ts
import * as aws from '@pulumi/aws';
import * as pulumi from '@pulumi/pulumi';

const vpc = new aws.ec2.Vpc('main', {
  cidrBlock: '10.0.0.0/16',
});

const subnet = new aws.ec2.Subnet('public', {
  vpcId: vpc.id,
  cidrBlock: '10.0.1.0/24',
  mapPublicIpOnLaunch: true,
});

const instanceName = pulumi.interpolate`web-${vpc.id}`;

export const vpcId = vpc.id;
export const subnetId = subnet.id;
```

### apply and interpolate

```ts
import * as pulumi from '@pulumi/pulumi';

const bucket = new aws.s3.Bucket('data');

const bucketUrl = bucket.bucket.apply(
  (name) => `https://${name}.s3.amazonaws.com`,
);

const combined = pulumi
  .all([bucket.bucket, bucket.arn])
  .apply(([name, arn]) => `Bucket ${name} has ARN ${arn}`);
```

## Component Resources

Group related resources into reusable components.

```ts
import * as aws from '@pulumi/aws';
import * as pulumi from '@pulumi/pulumi';

interface VpcArgs {
  cidrBlock: string;
  azCount: number;
  tags?: Record<string, string>;
}

class Vpc extends pulumi.ComponentResource {
  public readonly vpcId: pulumi.Output<string>;
  public readonly publicSubnetIds: pulumi.Output<string>[];
  public readonly privateSubnetIds: pulumi.Output<string>[];

  constructor(
    name: string,
    args: VpcArgs,
    opts?: pulumi.ComponentResourceOptions,
  ) {
    super('custom:networking:Vpc', name, {}, opts);

    const vpc = new aws.ec2.Vpc(
      `${name}-vpc`,
      {
        cidrBlock: args.cidrBlock,
        enableDnsHostnames: true,
        tags: { ...args.tags, Name: name },
      },
      { parent: this },
    );

    this.vpcId = vpc.id;
    this.publicSubnetIds = [];
    this.privateSubnetIds = [];

    const azs = aws.getAvailabilityZonesOutput({ state: 'available' });

    for (let i = 0; i < args.azCount; i++) {
      const az = azs.names[i];

      const publicSubnet = new aws.ec2.Subnet(
        `${name}-public-${i}`,
        {
          vpcId: vpc.id,
          cidrBlock: `10.0.${i}.0/24`,
          availabilityZone: az,
          mapPublicIpOnLaunch: true,
        },
        { parent: this },
      );
      this.publicSubnetIds.push(publicSubnet.id);

      const privateSubnet = new aws.ec2.Subnet(
        `${name}-private-${i}`,
        {
          vpcId: vpc.id,
          cidrBlock: `10.0.${i + 100}.0/24`,
          availabilityZone: az,
        },
        { parent: this },
      );
      this.privateSubnetIds.push(privateSubnet.id);
    }

    this.registerOutputs({
      vpcId: this.vpcId,
      publicSubnetIds: this.publicSubnetIds,
      privateSubnetIds: this.privateSubnetIds,
    });
  }
}

const network = new Vpc('main', { cidrBlock: '10.0.0.0/16', azCount: 2 });
export const vpcId = network.vpcId;
```

## Python SDK

```bash
pulumi new python
```

```python
import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket("my-bucket",
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
    tags={
        "Environment": pulumi.get_stack(),
        "ManagedBy": "pulumi",
    },
)

pulumi.export("bucket_name", bucket.id)
pulumi.export("bucket_arn", bucket.arn)
```

### Python Component Resource

```python
import pulumi
import pulumi_aws as aws
from typing import Optional


class VpcArgs:
    def __init__(self, cidr_block: str, az_count: int,
                 tags: Optional[dict] = None):
        self.cidr_block = cidr_block
        self.az_count = az_count
        self.tags = tags or {}


class Vpc(pulumi.ComponentResource):
    vpc_id: pulumi.Output[str]

    def __init__(self, name: str, args: VpcArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("custom:networking:Vpc", name, {}, opts)

        self.vpc = aws.ec2.Vpc(f"{name}-vpc",
            cidr_block=args.cidr_block,
            enable_dns_hostnames=True,
            tags={**args.tags, "Name": name},
            opts=pulumi.ResourceOptions(parent=self),
        )
        self.vpc_id = self.vpc.id

        self.register_outputs({"vpc_id": self.vpc_id})
```

## Resource Options

```ts
const bucket = new aws.s3.Bucket(
  'protected',
  {},
  {
    protect: true,
    retainOnDelete: true,
    ignoreChanges: ['tags'],
    dependsOn: [otherResource],
    parent: parentComponent,
    provider: customProvider,
    aliases: [{ name: 'old-bucket-name' }],
  },
);
```

| Option                | Purpose                                    |
| --------------------- | ------------------------------------------ |
| `protect`             | Prevent accidental deletion                |
| `retainOnDelete`      | Keep cloud resource when removed from code |
| `ignoreChanges`       | Skip drift on specific properties          |
| `dependsOn`           | Explicit dependency ordering               |
| `parent`              | Organize in component tree                 |
| `provider`            | Use specific provider instance             |
| `aliases`             | Rename without replacement                 |
| `deleteBeforeReplace` | Delete old before creating new             |
