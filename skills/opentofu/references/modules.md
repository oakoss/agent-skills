---
title: Modules
description: Module structure, composition, registry modules, input validation, and reusable infrastructure patterns
tags: [module, composition, registry, validation, source, output, variable]
---

# Modules

## Module Structure

A module is a directory containing `.tf` files. Every OpenTofu configuration is a root module.

```sh
modules/
  vpc/
    main.tf
    variables.tf
    outputs.tf
  database/
    main.tf
    variables.tf
    outputs.tf
```

## Basic Module Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  cidr_block  = "10.0.0.0/16"
  environment = var.environment
  project     = var.project
}

module "database" {
  source = "./modules/database"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  db_name    = var.db_name
}
```

## Module Sources

```hcl
module "from_local" {
  source = "./modules/vpc"
}

module "from_registry" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
}

module "from_github" {
  source = "github.com/org/terraform-modules//vpc?ref=v1.2.0"
}

module "from_s3" {
  source = "s3::https://s3-eu-west-1.amazonaws.com/bucket/vpc.zip"
}
```

## Module Variables with Validation

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "cidr_block" {
  type        = string
  description = "VPC CIDR block"

  validation {
    condition     = can(cidrhost(var.cidr_block, 0))
    error_message = "Must be a valid CIDR block."
  }
}

variable "instance_count" {
  type    = number
  default = 1

  validation {
    condition     = var.instance_count > 0 && var.instance_count <= 10
    error_message = "Instance count must be between 1 and 10."
  }
}
```

## Module Outputs

```hcl
output "vpc_id" {
  value       = aws_vpc.main.id
  description = "ID of the created VPC"
}

output "private_subnet_ids" {
  value       = [for s in aws_subnet.private : s.id]
  description = "IDs of private subnets"
}

output "database_endpoint" {
  value       = aws_db_instance.main.endpoint
  description = "RDS instance endpoint"
  sensitive   = true
}
```

## Module Composition Pattern

### Root Module Composing Child Modules

```hcl
module "networking" {
  source = "./modules/networking"

  environment    = var.environment
  vpc_cidr       = var.vpc_cidr
  azs            = var.availability_zones
  public_subnets = var.public_subnet_cidrs
}

module "compute" {
  source = "./modules/compute"

  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.private_subnet_ids
  security_group_id = module.networking.app_sg_id
  instance_type     = var.instance_type
  min_size          = var.environment == "production" ? 3 : 1
  max_size          = var.environment == "production" ? 10 : 3
}

module "monitoring" {
  source = "./modules/monitoring"

  asg_name         = module.compute.asg_name
  lb_arn_suffix    = module.compute.lb_arn_suffix
  alarm_sns_topic  = var.alarm_sns_topic
}
```

## for_each with Modules

```hcl
variable "services" {
  type = map(object({
    port          = number
    instance_type = string
    replicas      = number
  }))
}

module "service" {
  source   = "./modules/ecs-service"
  for_each = var.services

  name          = each.key
  port          = each.value.port
  instance_type = each.value.instance_type
  replicas      = each.value.replicas
  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.private_subnet_ids
}
```

## Passing Providers to Modules

```hcl
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}

module "cdn" {
  source = "./modules/cdn"

  providers = {
    aws           = aws.us_east
    aws.secondary = aws.eu_west
  }

  domain_name = var.domain_name
}
```

## Module Testing

OpenTofu supports built-in test files (`.tftest.hcl`):

```hcl
run "create_vpc" {
  command = plan

  variables {
    cidr_block  = "10.0.0.0/16"
    environment = "dev"
    project     = "test"
  }

  assert {
    condition     = aws_vpc.main.cidr_block == "10.0.0.0/16"
    error_message = "VPC CIDR block did not match expected value."
  }
}

run "validate_outputs" {
  command = apply

  variables {
    cidr_block  = "10.0.0.0/16"
    environment = "dev"
    project     = "test"
  }

  assert {
    condition     = output.vpc_id != ""
    error_message = "VPC ID output must not be empty."
  }
}
```
