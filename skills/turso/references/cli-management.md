---
title: CLI Management
description: Turso CLI commands for database creation, group management, token generation, and local development
tags: [turso-cli, db-create, db-shell, group, tokens, locations]
---

# CLI Management

## Installation

```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

## Authentication

```bash
turso auth login
turso auth token
```

## Database Commands

### Create a Database

```bash
turso db create my-app
turso db create my-app --group us-east
```

### List Databases

```bash
turso db list
```

### Show Database Details

```bash
turso db show my-app
turso db show my-app --url
```

### Open Interactive Shell

```bash
turso db shell my-app
turso db shell my-app "SELECT * FROM users LIMIT 5"
```

### Delete a Database

```bash
turso db destroy my-app -y
```

## Group Commands

Groups define the locations where databases are replicated.

### Create a Group

```bash
turso group create us-east
turso group create us-east --location iad
```

### Add Location to Group

```bash
turso group locations add us-east lhr
```

### List Groups

```bash
turso group list
```

## Token Commands

### Create Database Token

```bash
turso db tokens create my-app
turso db tokens create my-app --read-only
turso db tokens create my-app --expiration 7d3h
```

### Invalidate Tokens

```bash
turso db tokens invalidate my-app
```

## Location Management

### List Available Locations

```bash
turso db locations
```

### Show Closest Location

```bash
turso db locations --closest
```

## Connection URLs

Database URLs follow the pattern:

```text
libsql://[database-name]-[org-slug].turso.io
```

Retrieve the URL programmatically:

```bash
turso db show my-app --url
```

## Local Development

### Create a Local Database File

```bash
turso dev --db-file local.db
```

Starts a local libSQL server for development without needing a cloud database.

### Environment Variables

```bash
export TURSO_DATABASE_URL="$(turso db show my-app --url)"
export TURSO_AUTH_TOKEN="$(turso db tokens create my-app)"
```

## Common CLI Workflows

### Full Setup

```bash
turso auth login
turso group create default --location iad
turso db create my-app --group default
turso db show my-app --url
turso db tokens create my-app
```

### Schema from File

```bash
turso db shell my-app < schema.sql
```

### Create Database from Existing

```bash
turso db create my-app-staging --from-db my-app
```

### Dump Database

```bash
turso db shell my-app .dump > backup.sql
```
