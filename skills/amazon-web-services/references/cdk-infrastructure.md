---
title: CDK Infrastructure
description: CDK v2 app/stack structure, construct patterns, environment configuration, testing with assertions, and deployment
tags:
  [
    cdk,
    infrastructure-as-code,
    construct,
    stack,
    testing,
    cloudformation,
    deployment,
    synth,
  ]
---

# CDK Infrastructure

## App and Stack Structure

```ts
import * as cdk from 'aws-cdk-lib';
import type { Construct } from 'constructs';

class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define resources here
  }
}

const app = new cdk.App();

new AppStack(app, 'MyApp-Dev', {
  env: { account: '123456789012', region: 'us-east-1' },
});

new AppStack(app, 'MyApp-Prod', {
  env: { account: '987654321098', region: 'us-east-1' },
});

app.synth();
```

## Construct Levels

| Level         | Description                        | Example                                 |
| ------------- | ---------------------------------- | --------------------------------------- |
| L1 (Cfn\*)    | Direct CloudFormation mapping      | `CfnBucket`, `CfnFunction`              |
| L2            | AWS-curated with sensible defaults | `Bucket`, `Function`                    |
| L3 (Patterns) | Multi-resource compositions        | `ApplicationLoadBalancedFargateService` |

Prefer L2 constructs. Use L1 only when L2 does not expose a needed property.

## Custom Construct

```ts
import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import type { Construct } from 'constructs';

interface ApiConstructProps {
  tableName: string;
  stage: string;
}

class ApiConstruct extends cdk.NestedStack {
  public readonly table: dynamodb.Table;
  public readonly handler: NodejsFunction;

  constructor(scope: Construct, id: string, props: ApiConstructProps) {
    super(scope, id);

    this.table = new dynamodb.Table(this, 'Table', {
      tableName: props.tableName,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy:
        props.stage === 'production'
          ? cdk.RemovalPolicy.RETAIN
          : cdk.RemovalPolicy.DESTROY,
    });

    this.handler = new NodejsFunction(this, 'Handler', {
      entry: 'src/handlers/api.ts',
      runtime: lambda.Runtime.NODEJS_20_X,
      environment: { TABLE_NAME: this.table.tableName },
    });

    this.table.grantReadWriteData(this.handler);
  }
}
```

## Stack Configuration with Context

```ts
const app = new cdk.App();
const stage = app.node.tryGetContext('stage') ?? 'dev';

new AppStack(app, `MyApp-${stage}`, {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});
```

```bash
cdk deploy -c stage=production
```

## CDK CLI Commands

```bash
cdk init app --language typescript     # Scaffold new project
cdk synth                               # Synthesize CloudFormation template
cdk diff                                # Preview changes
cdk deploy                              # Deploy stack
cdk deploy --all                        # Deploy all stacks
cdk deploy --hotswap                    # Fast deploy for dev (Lambda, StepFunctions)
cdk destroy                             # Remove stack
cdk ls                                  # List all stacks
```

## Testing with Assertions

### Fine-Grained Assertions

```ts
import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { AppStack } from '../lib/app-stack';

describe('AppStack', () => {
  const app = new cdk.App();
  const stack = new AppStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  test('creates DynamoDB table with PAY_PER_REQUEST billing', () => {
    template.hasResourceProperties('AWS::DynamoDB::Table', {
      BillingMode: 'PAY_PER_REQUEST',
      KeySchema: [
        { AttributeName: 'pk', KeyType: 'HASH' },
        { AttributeName: 'sk', KeyType: 'RANGE' },
      ],
    });
  });

  test('creates Lambda function with correct runtime', () => {
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'nodejs20.x',
      MemorySize: 256,
    });
  });

  test('Lambda has read/write access to DynamoDB', () => {
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: {
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: Match.arrayWith([
              'dynamodb:BatchGetItem',
              'dynamodb:GetItem',
              'dynamodb:Query',
            ]),
            Effect: 'Allow',
          }),
        ]),
      },
    });
  });

  test('creates expected number of SQS queues', () => {
    template.resourceCountIs('AWS::SQS::Queue', 2);
  });
});
```

### Snapshot Testing

```ts
import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { AppStack } from '../lib/app-stack';

test('matches snapshot', () => {
  const app = new cdk.App();
  const stack = new AppStack(app, 'TestStack');
  const template = Template.fromStack(stack);
  expect(template.toJSON()).toMatchSnapshot();
});
```

Combine fine-grained assertions for critical properties with snapshot tests for detecting unintended changes.

### Capture Values

```ts
import { Capture, Template } from 'aws-cdk-lib/assertions';

const envCapture = new Capture();

template.hasResourceProperties('AWS::Lambda::Function', {
  Environment: {
    Variables: envCapture,
  },
});

expect(envCapture.asObject()).toEqual(
  expect.objectContaining({
    TABLE_NAME: expect.any(String),
  }),
);
```

## Aspects for Policy Enforcement

```ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import type { IConstruct } from 'constructs';

class BucketEncryptionChecker implements cdk.IAspect {
  visit(node: IConstruct): void {
    if (node instanceof s3.CfnBucket) {
      if (!node.bucketEncryption) {
        cdk.Annotations.of(node).addError(
          'S3 buckets must have encryption enabled',
        );
      }
    }
  }
}

cdk.Aspects.of(app).add(new BucketEncryptionChecker());
```

## Tags

```ts
cdk.Tags.of(app).add('Project', 'my-app');
cdk.Tags.of(app).add('Environment', stage);
cdk.Tags.of(app).add('ManagedBy', 'cdk');
```

## Cross-Stack References

```ts
class NetworkStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    this.vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2 });
  }
}

interface AppStackProps extends cdk.StackProps {
  vpc: ec2.Vpc;
}

class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);
    // Use props.vpc
  }
}

const networkStack = new NetworkStack(app, 'Network');
new AppStack(app, 'App', { vpc: networkStack.vpc });
```

CDK automatically creates CloudFormation exports and imports for cross-stack references.

## Removal Policies

| Policy     | Behavior                            | Use Case                         |
| ---------- | ----------------------------------- | -------------------------------- |
| `DESTROY`  | Delete resource on stack deletion   | Dev/test environments            |
| `RETAIN`   | Keep resource when stack is deleted | Production databases, S3 buckets |
| `SNAPSHOT` | Create snapshot before deletion     | RDS databases                    |

Always use `RETAIN` for production stateful resources (databases, S3 buckets with data).

## Project Structure

```sh
my-cdk-app/
├── bin/
│   └── app.ts              # App entry point, stack instantiation
├── lib/
│   ├── stacks/
│   │   ├── network-stack.ts
│   │   └── app-stack.ts
│   └── constructs/
│       ├── api-construct.ts
│       └── database-construct.ts
├── src/
│   └── handlers/            # Lambda handler code
├── test/
│   └── stacks/
│       └── app-stack.test.ts
├── cdk.json
└── tsconfig.json
```

Separate CDK infrastructure code (`lib/`) from application code (`src/`). Keep Lambda handlers in `src/handlers/` so `NodejsFunction` can reference them.
