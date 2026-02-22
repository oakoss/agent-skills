---
title: API Patterns
description: Coolify REST API authentication, permission scopes, common endpoints for applications, databases, services, and deployments
tags:
  [api, authentication, permissions, endpoints, curl, applications, databases]
---

# API Patterns

## Authentication

All API requests require a Bearer token created in the Coolify dashboard under Settings > API Tokens.

```bash
curl -s \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  https://coolify.example.com/api/v1/version
```

The `Accept: application/json` header is required — without it, some endpoints return "Unauthenticated" even with a valid token.

## Permission Scopes

| Scope            | Read | Write | Deploy | Sensitive Data |
| ---------------- | ---- | ----- | ------ | -------------- |
| `read-only`      | Yes  | No    | No     | Redacted       |
| `read:sensitive` | Yes  | No    | No     | Visible        |
| `view:sensitive` | Yes  | Yes   | Yes    | Visible        |
| `deploy`         | No   | No    | Yes    | No             |
| `*`              | Yes  | Yes   | Yes    | Visible        |

Fields like `is_auto_deploy_enabled`, API keys, and passwords are redacted unless the token has `view:sensitive` or `*` scope.

## Environment Variables

Set the Coolify instance URL and token as environment variables:

```bash
export COOLIFY_URL="https://coolify.example.com"
export COOLIFY_TOKEN="1|your-token-here"
```

## Common Endpoints

### Applications

```bash
# List all applications
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/applications" | jq .

# Get application details
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/applications/<uuid>"

# Create a public Git application
curl -s -X POST \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "<project-uuid>",
    "server_uuid": "<server-uuid>",
    "environment_name": "production",
    "git_repository": "https://github.com/org/repo",
    "git_branch": "main",
    "build_pack": "nixpacks",
    "ports_exposes": "3000"
  }' \
  "$COOLIFY_URL/api/v1/applications/public"

# Update application settings
curl -s -X PATCH \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "is_auto_deploy_enabled": true,
    "health_check_path": "/health",
    "health_check_interval": 30
  }' \
  "$COOLIFY_URL/api/v1/applications/<uuid>"

# Delete application
curl -s -X DELETE \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/applications/<uuid>"
```

### Deployments

```bash
# Trigger deployment (by UUID)
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/deploy?uuid=<app-uuid>&force=true"

# Trigger deployment (by webhook URL)
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  "$COOLIFY_URL/api/v1/applications/<uuid>/deploy"

# List deployments
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/deployments"

# Get deployment details
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/deployments/<deployment-uuid>"
```

### Databases

```bash
# List all databases
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/databases"

# Create a PostgreSQL database
curl -s -X POST \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "<project-uuid>",
    "server_uuid": "<server-uuid>",
    "environment_name": "production",
    "type": "postgresql",
    "name": "my-database"
  }' \
  "$COOLIFY_URL/api/v1/databases"
```

### Services

```bash
# List all services (280+ one-click services)
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/services"

# Get service details
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/services/<uuid>"
```

### Projects and Environments

```bash
# List projects
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/projects"

# Get project with environments
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/projects/<uuid>"
```

### Servers

```bash
# List servers (requires elevated permissions)
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/servers"

# Get server details
curl -s -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Accept: application/json" \
  "$COOLIFY_URL/api/v1/servers/<uuid>"
```

## Updatable Application Fields

The PATCH endpoint accepts these fields:

| Category  | Fields                                                               |
| --------- | -------------------------------------------------------------------- |
| Identity  | `name`, `description`, `domains`                                     |
| Source    | `git_repository`, `git_branch`, `git_commit_sha`                     |
| Build     | `build_pack`, `build_command`, `install_command`, `start_command`    |
| Deploy    | `is_auto_deploy_enabled`, `instant_deploy`, `is_force_https_enabled` |
| Paths     | `base_directory`, `publish_directory`, `dockerfile_location`         |
| Health    | `health_check_path`, `health_check_port`, `health_check_interval`    |
| Resources | `limits_memory`, `limits_cpus`, `limits_cpu_shares`                  |
| Hooks     | `pre_deployment_command`, `post_deployment_command`                  |
| Docker    | `dockerfile`, `docker_compose_location`, `custom_docker_run_options` |
| Webhooks  | `manual_webhook_secret_github`, `manual_webhook_secret_gitlab`       |
| Static    | `is_static`, `is_spa`, `redirect`                                    |

## Error Handling

| HTTP Status | Meaning          | Common Cause                              |
| ----------- | ---------------- | ----------------------------------------- |
| 401         | Unauthenticated  | Missing/invalid token or no Accept header |
| 403         | Forbidden        | Token lacks required permission scope     |
| 404         | Not Found        | Invalid UUID or resource deleted          |
| 422         | Validation Error | Missing required fields in request body   |
| 500         | Server Error     | Check Coolify logs on the server          |
