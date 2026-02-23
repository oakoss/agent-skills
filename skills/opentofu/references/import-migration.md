---
title: Import and Migration
description: Importing existing resources, Terraform-to-OpenTofu migration, import blocks, and state migration patterns
tags: [import, migration, terraform, state, moved, import-block]
---

# Import and Migration

## Importing Existing Resources

### CLI Import

```bash
tofu import aws_instance.web i-1234567890abcdef0
tofu import 'aws_security_group.web' sg-0123456789abcdef0
tofu import 'module.vpc.aws_vpc.main' vpc-0123456789abcdef0
```

Write the matching resource block first, then import:

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
}
```

After import, run `tofu plan` to verify the configuration matches the imported resource. Adjust attributes until the plan shows no changes.

### Import Block (Declarative)

```hcl
import {
  to = aws_instance.web
  id = "i-1234567890abcdef0"
}

resource "aws_instance" "web" {
  ami           = "ami-0123456789abcdef0"
  instance_type = "t3.micro"
  subnet_id     = "subnet-0123456789abcdef0"

  tags = {
    Name = "web-server"
  }
}
```

Import blocks are processed during `tofu plan` and `tofu apply`. Remove the import block after the resource is successfully imported.

### Generate Configuration from Import

```bash
tofu plan -generate-config-out=generated.tf
```

This generates HCL for imported resources, reducing manual configuration writing.

## Bulk Import Pattern

```hcl
locals {
  existing_buckets = {
    logs    = "mycompany-logs-bucket"
    backups = "mycompany-backups-bucket"
    assets  = "mycompany-assets-bucket"
  }
}

import {
  for_each = local.existing_buckets
  to       = aws_s3_bucket.imported[each.key]
  id       = each.value
}

resource "aws_s3_bucket" "imported" {
  for_each = local.existing_buckets
  bucket   = each.value
}
```

## Moved Blocks for Refactoring

When renaming or restructuring resources without destroying and recreating:

```hcl
moved {
  from = aws_instance.web
  to   = aws_instance.app
}

moved {
  from = module.old_vpc
  to   = module.networking
}

moved {
  from = aws_instance.web
  to   = module.compute.aws_instance.web
}
```

Moved blocks can be removed after all team members have applied the change.

## Terraform to OpenTofu Migration

### Step 1: Install OpenTofu

```bash
brew install opentofu
```

### Step 2: Replace CLI Commands

| Terraform           | OpenTofu       |
| ------------------- | -------------- |
| `terraform init`    | `tofu init`    |
| `terraform plan`    | `tofu plan`    |
| `terraform apply`   | `tofu apply`   |
| `terraform destroy` | `tofu destroy` |

### Step 3: Initialize with Existing State

```bash
tofu init
```

OpenTofu reads existing `.terraform.lock.hcl` and state files. No state migration needed for most backends.

### Step 4: Verify

```bash
tofu plan
```

A clean plan (no changes) confirms successful migration.

### Key Differences

- The `terraform {}` block name is retained for compatibility
- Provider registry defaults to `registry.opentofu.org` (mirrors most `registry.terraform.io` providers)
- State encryption is available (OpenTofu-exclusive)
- Some provider-defined functions may differ

## State Migration Between Backends

```bash
tofu init -migrate-state
```

Update the backend configuration, then run init with `-migrate-state` to copy state to the new backend.

```bash
tofu init -reconfigure
```

Use `-reconfigure` to reset backend configuration without migrating state.
