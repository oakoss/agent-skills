---
title: Variables and Outputs
description: Variable types, defaults, validation, sensitive values, outputs, and locals
tags: [variable, output, locals, sensitive, validation, tfvars, type-constraint]
---

# Variables and Outputs

## Variable Types

```hcl
variable "name" {
  type    = string
  default = "myapp"
}

variable "instance_count" {
  type    = number
  default = 2
}

variable "enable_monitoring" {
  type    = bool
  default = true
}

variable "tags" {
  type = map(string)
  default = {
    ManagedBy = "opentofu"
  }
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "service_config" {
  type = object({
    name     = string
    port     = number
    replicas = number
    env      = map(string)
  })
}

variable "services" {
  type = list(object({
    name = string
    port = number
  }))
}
```

## Variable Validation

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "ami_id" {
  type = string

  validation {
    condition     = startswith(var.ami_id, "ami-")
    error_message = "AMI ID must start with 'ami-'."
  }
}

variable "cidr_block" {
  type = string

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR block."
  }
}
```

## Sensitive Variables

```hcl
variable "database_password" {
  type      = string
  sensitive = true
}

variable "api_key" {
  type      = string
  sensitive = true
}
```

Sensitive values are redacted in plan and apply output but stored in state. Combine with state encryption for full protection.

## Setting Variable Values

### terraform.tfvars (Auto-Loaded)

```hcl
environment = "production"
instance_type = "m5.large"
tags = {
  Team    = "platform"
  Project = "myapp"
}
```

### Environment-Specific Files

```bash
tofu plan -var-file="environments/production.tfvars"
```

### Environment Variables

```bash
export TF_VAR_database_password="secret123"
export TF_VAR_environment="production"
tofu plan
```

### Command Line

```bash
tofu plan -var="instance_count=3" -var="environment=staging"
```

### Variable Precedence (Highest to Lowest)

1. `-var` and `-var-file` flags
2. `*.auto.tfvars` files (alphabetical)
3. `terraform.tfvars`
4. Environment variables (`TF_VAR_*`)
5. Default values

## Outputs

```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the VPC"
}

output "public_ip" {
  value       = aws_eip.web.public_ip
  description = "Public IP of the web server"
}

output "database_endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "RDS endpoint"
  sensitive   = true
}

output "instance_ids" {
  value = { for k, v in aws_instance.app : k => v.id }
}
```

### Conditional Outputs

```hcl
output "cdn_domain" {
  value       = var.enable_cdn ? aws_cloudfront_distribution.main[0].domain_name : null
  description = "CloudFront domain name (null if CDN disabled)"
}
```

## Locals

Locals compute intermediate values to reduce repetition.

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"

  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "opentofu"
  }

  private_subnet_cidrs = [for i, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, i)
  ]

  public_subnet_cidrs = [for i, az in var.availability_zones :
    cidrsubnet(var.vpc_cidr, 8, i + 100)
  ]
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags       = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
}
```

## Type Constraints

```hcl
variable "optional_config" {
  type = object({
    name    = string
    port    = optional(number, 8080)
    enabled = optional(bool, true)
  })
}
```

The `optional()` modifier allows omitting fields with defaults, reducing boilerplate in variable definitions.
