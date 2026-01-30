---
title: Pack Configuration and Environment Variables
description: Modular pack system for organizing detection patterns by category with environment variable controls
tags: [packs, configuration, environment-variables, database, kubernetes, cloud]
---

# Pack Configuration and Environment Variables

## Modular Pack System

DCG uses a modular "pack" system to organize patterns by category.

### Core Packs (Always Enabled)

| Pack              | Description                   |
| ----------------- | ----------------------------- |
| `core.git`        | Destructive git commands      |
| `core.filesystem` | Dangerous rm -rf outside temp |

### Database Packs

| Pack                  | Description                    |
| --------------------- | ------------------------------ |
| `database.postgresql` | DROP/TRUNCATE in PostgreSQL    |
| `database.mysql`      | DROP/TRUNCATE in MySQL/MariaDB |
| `database.mongodb`    | dropDatabase, drop()           |
| `database.redis`      | FLUSHALL/FLUSHDB               |
| `database.sqlite`     | DROP in SQLite                 |

### Container Packs

| Pack                 | Description                       |
| -------------------- | --------------------------------- |
| `containers.docker`  | docker system prune, docker rm -f |
| `containers.compose` | docker-compose down --volumes     |
| `containers.podman`  | podman system prune               |

### Kubernetes Packs

| Pack                   | Description               |
| ---------------------- | ------------------------- |
| `kubernetes.kubectl`   | kubectl delete namespace  |
| `kubernetes.helm`      | helm uninstall            |
| `kubernetes.kustomize` | kustomize delete patterns |

### Cloud Provider Packs

| Pack          | Description                  |
| ------------- | ---------------------------- |
| `cloud.aws`   | Destructive AWS CLI commands |
| `cloud.gcp`   | Destructive gcloud commands  |
| `cloud.azure` | Destructive az commands      |

### Infrastructure Packs

| Pack                       | Description                |
| -------------------------- | -------------------------- |
| `infrastructure.terraform` | terraform destroy          |
| `infrastructure.ansible`   | Dangerous ansible patterns |
| `infrastructure.pulumi`    | pulumi destroy             |

### System Packs

| Pack                 | Description                     |
| -------------------- | ------------------------------- |
| `system.disk`        | dd, mkfs, fdisk operations      |
| `system.permissions` | Dangerous chmod/chown patterns  |
| `system.services`    | systemctl stop/disable patterns |

### Other Packs

| Pack               | Description                    |
| ------------------ | ------------------------------ |
| `strict_git`       | Extra paranoid git protections |
| `package_managers` | npm unpublish, cargo yank      |

### Configuring Packs

```toml
# ~/.config/dcg/config.toml
[packs]
enabled = [
    "database.postgresql",
    "containers.docker",
    "kubernetes",  # Enables all kubernetes sub-packs
]
```

## Environment Variables

| Variable                                   | Description                        |
| ------------------------------------------ | ---------------------------------- |
| `DCG_PACKS="containers.docker,kubernetes"` | Enable packs (comma-separated)     |
| `DCG_DISABLE="kubernetes.helm"`            | Disable packs/sub-packs            |
| `DCG_VERBOSE=1`                            | Verbose output                     |
| `DCG_COLOR=auto\|always\|never`            | Color mode                         |
| `DCG_BYPASS=1`                             | Bypass DCG entirely (escape hatch) |
