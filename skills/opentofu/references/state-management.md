---
title: State Management
description: Remote backends, state locking, state operations, and backend configuration patterns
tags: [state, backend, s3, gcs, azure, locking, remote, state-mv, state-rm]
---

# State Management

## State Purpose

OpenTofu state maps real-world resources to configuration. It tracks metadata, dependencies, and current resource attributes. State must be stored securely and accessed with locking in team environments.

## Remote Backend Configuration

### S3 Backend (AWS)

```hcl
terraform {
  backend "s3" {
    bucket         = "mycompany-tofu-state"
    key            = "projects/myapp/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tofu-state-locks"
    encrypt        = true
  }
}
```

### GCS Backend (Google Cloud)

```hcl
terraform {
  backend "gcs" {
    bucket = "mycompany-tofu-state"
    prefix = "projects/myapp"
  }
}
```

### Azure Blob Backend

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "projects/myapp/terraform.tfstate"
  }
}
```

### HTTP Backend

```hcl
terraform {
  backend "http" {
    address        = "https://state.example.com/myapp"
    lock_address   = "https://state.example.com/myapp/lock"
    unlock_address = "https://state.example.com/myapp/lock"
  }
}
```

## Backend Configuration with Partial Config

Keep sensitive values out of HCL files by using partial configuration.

```hcl
terraform {
  backend "s3" {
    key = "projects/myapp/terraform.tfstate"
  }
}
```

```bash
tofu init \
  -backend-config="bucket=mycompany-tofu-state" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=tofu-state-locks"
```

Or use a backend config file:

```bash
tofu init -backend-config=backend.hcl
```

```hcl
bucket         = "mycompany-tofu-state"
region         = "us-east-1"
dynamodb_table = "tofu-state-locks"
encrypt        = true
```

## State Locking

State locking prevents concurrent operations from corrupting state.

| Backend    | Locking Mechanism     |
| ---------- | --------------------- |
| S3         | DynamoDB table        |
| GCS        | Built-in              |
| Azure Blob | Built-in (lease)      |
| Consul     | Built-in              |
| HTTP       | Lock/Unlock endpoints |

### Force Unlock (Emergency Only)

```bash
tofu force-unlock <lock-id>
```

## State Operations

### List Resources in State

```bash
tofu state list
```

### Show Resource Details

```bash
tofu state show aws_instance.web
```

### Move Resource Address

```bash
tofu state mv aws_instance.web aws_instance.app
tofu state mv 'module.old_name' 'module.new_name'
```

### Remove Resource from State

```bash
tofu state rm aws_instance.legacy
```

### Pull and Push State

```bash
tofu state pull > backup.tfstate
tofu state push backup.tfstate
```

## Reading Remote State

Access outputs from other configurations using `terraform_remote_state`:

```hcl
data "terraform_remote_state" "networking" {
  backend = "s3"

  config = {
    bucket = "mycompany-tofu-state"
    key    = "networking/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.networking.outputs.private_subnet_id
}
```

## State Bootstrap Pattern

Create the state backend resources before using them.

```hcl
resource "aws_s3_bucket" "state" {
  bucket = "mycompany-tofu-state"
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "locks" {
  name         = "tofu-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
```

After initial apply with local state, migrate to the S3 backend:

```bash
tofu init -migrate-state
```
