---
title: Workspaces
description: Workspace management, multi-environment strategies, and workspace-aware configurations
tags: [workspace, environment, multi-env, workspace-select, workspace-new]
---

# Workspaces

## Workspace Basics

Workspaces provide isolated state within the same configuration. Each workspace has its own state file.

```bash
tofu workspace list
tofu workspace new staging
tofu workspace new production
tofu workspace select staging
tofu workspace show
```

## Workspace-Aware Configuration

```hcl
locals {
  environment = terraform.workspace

  instance_types = {
    dev        = "t3.micro"
    staging    = "t3.small"
    production = "m5.large"
  }

  instance_counts = {
    dev        = 1
    staging    = 2
    production = 3
  }
}

resource "aws_instance" "app" {
  count         = local.instance_counts[local.environment]
  instance_type = local.instance_types[local.environment]
  ami           = data.aws_ami.ubuntu.id

  tags = {
    Name        = "app-${local.environment}-${count.index}"
    Environment = local.environment
  }
}
```

## Workspace vs Directory-Based Environments

### Workspace Approach

Single configuration, multiple workspaces:

```bash
tofu workspace select production
tofu apply -var-file="envs/production.tfvars"
```

**Pros:** Less code duplication, single source of truth.
**Cons:** All environments share same provider config, harder to diverge.

### Directory-Based Approach

Separate directories per environment:

```sh
environments/
  dev/
    main.tf
    backend.tf
    terraform.tfvars
  staging/
    main.tf
    backend.tf
    terraform.tfvars
  production/
    main.tf
    backend.tf
    terraform.tfvars
modules/
  vpc/
  compute/
```

**Pros:** Full isolation, independent provider versions, different backends.
**Cons:** More files to maintain, risk of drift between environments.

### Hybrid Approach (Recommended)

Shared modules with per-environment root configurations:

```hcl
module "infrastructure" {
  source = "../../modules/infrastructure"

  environment    = "production"
  instance_type  = "m5.large"
  instance_count = 3
  vpc_cidr       = "10.1.0.0/16"
}
```

## Workspace-Aware Backend Keys

```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-tofu-state"
    key            = "myapp/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tofu-state-locks"
    workspace_key_prefix = "environments"
  }
}
```

State paths become: `environments/<workspace>/myapp/terraform.tfstate`

## Workspace Delete

```bash
tofu workspace select default
tofu workspace delete staging
```

A workspace must have empty state before deletion. Destroy resources first:

```bash
tofu workspace select staging
tofu destroy
tofu workspace select default
tofu workspace delete staging
```
