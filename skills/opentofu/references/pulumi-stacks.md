---
title: Pulumi Stacks and Configuration
description: Stack management, config/secrets, state backends, policy as code, and automation API
tags: [pulumi, stack, config, secret, automation-api, policy, backend, state]
---

# Pulumi Stacks and Configuration

## Stack Management

Stacks represent isolated instances of a Pulumi program (similar to OpenTofu workspaces).

```bash
pulumi stack init dev
pulumi stack init staging
pulumi stack init production
pulumi stack select dev
pulumi stack ls
```

## Configuration

```bash
pulumi config set aws:region us-east-1
pulumi config set instanceType t3.micro
pulumi config set --secret databasePassword s3cret!
```

### Reading Config in Code

```ts
import * as pulumi from '@pulumi/pulumi';

const config = new pulumi.Config();

const instanceType = config.get('instanceType') || 't3.micro';
const dbPassword = config.requireSecret('databasePassword');
const port = config.getNumber('port') || 8080;
```

```python
import pulumi

config = pulumi.Config()

instance_type = config.get("instanceType") or "t3.micro"
db_password = config.require_secret("databasePassword")
port = config.get_int("port") or 8080
```

### Structured Configuration

```bash
pulumi config set --path 'database.host' db.example.com
pulumi config set --path 'database.port' 5432
pulumi config set --path --secret 'database.password' s3cret
```

```ts
const config = new pulumi.Config();

interface DatabaseConfig {
  host: string;
  port: number;
  password: pulumi.Output<string>;
}

const dbConfig = config.requireObject<DatabaseConfig>('database');
```

## Secrets Management

Pulumi encrypts secrets in the stack config file (`Pulumi.<stack>.yaml`).

### Secrets Providers

```bash
pulumi stack init dev --secrets-provider="awskms://alias/pulumi-secrets?region=us-east-1"

pulumi stack init dev --secrets-provider="gcpkms://projects/my-project/locations/global/keyRings/pulumi/cryptoKeys/secrets"

pulumi stack init dev --secrets-provider="passphrase"
```

### Programmatic Secrets

```ts
const secret = pulumi.secret('my-secret-value');

const dbPassword = config.requireSecret('databasePassword');

const instance = new aws.ec2.Instance('app', {
  userData: pulumi.interpolate`#!/bin/bash\nexport DB_PASS=${dbPassword}`,
});
```

## State Backends

```bash
pulumi login
pulumi login s3://my-pulumi-state
pulumi login gs://my-pulumi-state
pulumi login azblob://my-pulumi-state
pulumi login file://~/.pulumi-state
```

## Automation API

Embed Pulumi operations inside application code for programmatic infrastructure management.

```ts
import * as automation from '@pulumi/pulumi/automation';
import * as aws from '@pulumi/aws';

async function deploy() {
  const program = async () => {
    const bucket = new aws.s3.Bucket('auto-bucket');
    return { bucketName: bucket.id };
  };

  const stack = await automation.LocalWorkspace.createOrSelectStack({
    stackName: 'dev',
    projectName: 'automation-example',
    program,
  });

  await stack.setConfig('aws:region', { value: 'us-east-1' });

  const upResult = await stack.up({ onOutput: console.log });
  console.log('Outputs:', upResult.outputs);

  const previewResult = await stack.preview();
  console.log('Changes:', previewResult.changeSummary);
}

deploy().catch(console.error);
```

### Automation API: Destroy and Remove

```ts
async function teardown(stackName: string) {
  const stack = await automation.LocalWorkspace.selectStack({
    stackName,
    projectName: 'automation-example',
    program: async () => {},
  });

  await stack.destroy({ onOutput: console.log });
  await stack.workspace.removeStack(stackName);
}
```

## Policy as Code (CrossGuard)

Define compliance rules that run during `pulumi preview` and `pulumi up`.

```ts
import * as policy from '@pulumi/policy';

new policy.PolicyPack('aws-policies', {
  policies: [
    {
      name: 'no-public-s3',
      description: 'S3 buckets must not have public ACLs',
      enforcementLevel: 'mandatory',
      validateResource: policy.validateResourceOfType(
        aws.s3.Bucket,
        (bucket, args, reportViolation) => {
          if (
            bucket.acl === 'public-read' ||
            bucket.acl === 'public-read-write'
          ) {
            reportViolation('S3 buckets must not use public ACLs.');
          }
        },
      ),
    },
    {
      name: 'required-tags',
      description: 'All resources must have required tags',
      enforcementLevel: 'mandatory',
      validateResource: (args, reportViolation) => {
        const tags = (args.props as Record<string, unknown>).tags as
          | Record<string, string>
          | undefined;
        if (tags && !tags['Environment']) {
          reportViolation('All resources must have an Environment tag.');
        }
      },
    },
  ],
});
```

```bash
pulumi preview --policy-pack ./policies
pulumi up --policy-pack ./policies
```

## Stack References

Read outputs from other stacks:

```ts
const networkStack = new pulumi.StackReference('org/networking/production');

const vpcId = networkStack.getOutput('vpcId');
const subnetIds = networkStack.getOutput('privateSubnetIds');

const instance = new aws.ec2.Instance('app', {
  subnetId: subnetIds.apply((ids) => (ids as string[])[0]),
  vpcSecurityGroupIds: [
    networkStack.getOutput('appSecurityGroupId') as pulumi.Output<string>,
  ],
});
```
