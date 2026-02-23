---
title: HCL Fundamentals
description: HCL syntax, resource blocks, data sources, provider configuration, and lifecycle management
tags: [hcl, resource, data-source, provider, lifecycle, depends_on, for_each]
---

# HCL Fundamentals

## Provider Configuration

Providers are plugins that interact with cloud platforms and services.

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      ManagedBy   = "opentofu"
      Environment = var.environment
    }
  }
}
```

### Multiple Provider Instances

```hcl
provider "aws" {
  alias  = "us_west"
  region = "us-west-2"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}

resource "aws_s3_bucket" "replica" {
  provider = aws.eu_west
  bucket   = "my-replica-bucket"
}
```

## Resource Blocks

Resources are the primary building block. Each resource belongs to a provider.

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public.id

  tags = {
    Name = "${var.project}-web"
  }
}
```

### Resource Lifecycle

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = true
    ignore_changes        = [tags["UpdatedAt"]]
  }
}
```

### Resource Dependencies

```hcl
resource "aws_iam_role_policy" "app" {
  role   = aws_iam_role.app.name
  policy = data.aws_iam_policy_document.app.json
}

resource "aws_instance" "app" {
  ami                  = data.aws_ami.ubuntu.id
  instance_type        = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.app.name

  depends_on = [aws_iam_role_policy.app]
}
```

## Data Sources

Data sources fetch information from providers or external systems.

```hcl
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_vpc" "main" {
  filter {
    name   = "tag:Name"
    values = [var.vpc_name]
  }
}
```

## Iteration Patterns

### for_each with Map

```hcl
variable "buckets" {
  type = map(object({
    versioning = bool
    acl        = string
  }))
}

resource "aws_s3_bucket" "this" {
  for_each = var.buckets
  bucket   = each.key
}

resource "aws_s3_bucket_versioning" "this" {
  for_each = { for k, v in var.buckets : k => v if v.versioning }
  bucket   = aws_s3_bucket.this[each.key].id

  versioning_configuration {
    status = "Enabled"
  }
}
```

### for_each with Set of Strings

```hcl
variable "subnet_ids" {
  type = set(string)
}

resource "aws_route_table_association" "this" {
  for_each       = var.subnet_ids
  subnet_id      = each.value
  route_table_id = aws_route_table.main.id
}
```

### Dynamic Blocks

```hcl
variable "ingress_rules" {
  type = list(object({
    port        = number
    protocol    = string
    cidr_blocks = list(string)
  }))
}

resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = ingress.value.protocol
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
```

## Expressions

### Conditional Expression

```hcl
resource "aws_instance" "this" {
  instance_type = var.environment == "production" ? "m5.large" : "t3.micro"
}
```

### String Templates

```hcl
locals {
  bucket_name = "${var.project}-${var.environment}-${var.region}"
  config = templatefile("${path.module}/config.tpl", {
    db_host = aws_db_instance.main.address
    db_port = aws_db_instance.main.port
  })
}
```

### Collection Functions

```hcl
locals {
  public_subnets  = [for s in aws_subnet.public : s.id]
  private_subnets = { for s in aws_subnet.private : s.availability_zone => s.id }
  all_tags        = merge(var.common_tags, { Environment = var.environment })
  flat_list       = flatten([var.list_a, var.list_b])
}
```

## Provisioners

Provisioners run scripts on resources after creation. Use as a last resort.

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y",
      "sudo apt-get install -y nginx",
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.ssh_key_path)
      host        = self.public_ip
    }
  }
}
```
