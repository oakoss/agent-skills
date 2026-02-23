---
title: State Encryption
description: OpenTofu-exclusive state and plan encryption with key providers, methods, and migration patterns
tags: [encryption, state, plan, aes-gcm, pbkdf2, aws-kms, gcp-kms, key-provider]
---

# State Encryption

State encryption is an OpenTofu-exclusive feature that encrypts state and plan files at rest. This protects sensitive data stored in state from unauthorized access.

## Encryption Architecture

OpenTofu encryption uses two components:

1. **Key provider** -- generates or retrieves encryption keys (PBKDF2, AWS KMS, GCP KMS, OpenBao)
2. **Encryption method** -- uses those keys to encrypt/decrypt (AES-GCM)

## PBKDF2 Key Provider

Derives encryption keys from a passphrase. Suitable for individual use or when a KMS is unavailable.

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "main" {
      passphrase = var.state_passphrase
    }

    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }

    state {
      method = method.aes_gcm.main
    }

    plan {
      method = method.aes_gcm.main
    }
  }
}

variable "state_passphrase" {
  type      = string
  sensitive = true
}
```

## AWS KMS Key Provider

Uses AWS Key Management Service for enterprise-grade key management.

```hcl
terraform {
  encryption {
    key_provider "aws_kms" "main" {
      kms_key_id = "alias/tofu-state-key"
      region     = "us-east-1"
      key_spec   = "AES_256"
    }

    method "aes_gcm" "main" {
      keys = key_provider.aws_kms.main
    }

    state {
      method = method.aes_gcm.main
    }

    plan {
      method = method.aes_gcm.main
    }
  }
}
```

## GCP KMS Key Provider

```hcl
terraform {
  encryption {
    key_provider "gcp_kms" "main" {
      kms_encryption_key = "projects/my-project/locations/global/keyRings/tofu/cryptoKeys/state"
      key_length         = 32
    }

    method "aes_gcm" "main" {
      keys = key_provider.gcp_kms.main
    }

    state {
      method = method.aes_gcm.main
    }

    plan {
      method = method.aes_gcm.main
    }
  }
}
```

## Encrypting Remote State Data Sources

When reading encrypted state from another configuration:

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "remote" {
      passphrase = var.remote_state_passphrase
    }

    method "aes_gcm" "remote" {
      keys = key_provider.pbkdf2.remote
    }

    remote_state_data_sources {
      default {
        method = method.aes_gcm.remote
      }
    }
  }
}

data "terraform_remote_state" "networking" {
  backend = "s3"
  config = {
    bucket = "state-bucket"
    key    = "networking/terraform.tfstate"
    region = "us-east-1"
  }
}
```

## Migration: Unencrypted to Encrypted

Use the `fallback` block to read existing unencrypted state while writing encrypted:

```hcl
terraform {
  encryption {
    method "unencrypted" "migrate" {}

    key_provider "pbkdf2" "main" {
      passphrase = var.state_passphrase
    }

    method "aes_gcm" "main" {
      keys = key_provider.pbkdf2.main
    }

    state {
      method = method.aes_gcm.main
      fallback {
        method = method.unencrypted.migrate
      }
    }

    plan {
      method = method.aes_gcm.main
      fallback {
        method = method.unencrypted.migrate
      }
    }
  }
}
```

After running `tofu apply` once with the fallback, the state is re-written encrypted. Remove the `fallback` block afterward to prevent accidental unencrypted reads.

## Key Rotation

Rotate keys by adding the old key as a fallback:

```hcl
terraform {
  encryption {
    key_provider "pbkdf2" "new" {
      passphrase = var.new_passphrase
    }

    key_provider "pbkdf2" "old" {
      passphrase = var.old_passphrase
    }

    method "aes_gcm" "new" {
      keys = key_provider.pbkdf2.new
    }

    method "aes_gcm" "old" {
      keys = key_provider.pbkdf2.old
    }

    state {
      method = method.aes_gcm.new
      fallback {
        method = method.aes_gcm.old
      }
    }

    plan {
      method = method.aes_gcm.new
      fallback {
        method = method.aes_gcm.old
      }
    }
  }
}
```

Run `tofu apply` to re-encrypt state with the new key, then remove the fallback.
