---
title: Debugging
description: Container inspection, log analysis, network troubleshooting, image layer analysis, and common Docker debugging workflows
tags: [debugging, logs, exec, inspect, dive, network, troubleshooting, layers]
---

# Debugging

## Container Inspection

### Logs

```bash
# Follow logs in real-time
docker logs -f <container>

# Show last 100 lines
docker logs --tail 100 <container>

# Logs with timestamps
docker logs -t <container>

# Logs since a specific time
docker logs --since 2024-01-01T00:00:00Z <container>
docker logs --since 30m <container>

# Compose: all services
docker compose logs -f

# Compose: specific service
docker compose logs -f api
```

### Exec into Running Container

```bash
# Interactive shell
docker exec -it <container> sh
docker exec -it <container> /bin/bash

# Run a specific command
docker exec <container> env
docker exec <container> cat /etc/resolv.conf

# Exec as root (if container runs as non-root)
docker exec -u 0 <container> sh
```

### Inspect Container State

```bash
# Full container details (JSON)
docker inspect <container>

# Specific fields
docker inspect --format='{{.State.Status}}' <container>
docker inspect --format='{{.NetworkSettings.IPAddress}}' <container>
docker inspect --format='{{json .Config.Env}}' <container> | jq .
docker inspect --format='{{.State.Health.Status}}' <container>

# View health check logs
docker inspect --format='{{json .State.Health}}' <container> | jq '.Log[-3:]'

# Mounted volumes
docker inspect --format='{{json .Mounts}}' <container> | jq .
```

### Resource Usage

```bash
# Live resource stats
docker stats

# One-shot stats
docker stats --no-stream

# Specific container
docker stats <container>
```

## Image Layer Analysis

### docker history

```bash
# Show layers and sizes
docker history myapp:latest

# Full commands (not truncated)
docker history --no-trunc myapp:latest

# Human-readable sizes
docker history --format "table {{.Size}}\t{{.CreatedBy}}" myapp:latest
```

### dive (Interactive Layer Explorer)

```bash
# Install
# brew install dive (macOS)
# apt install dive (Debian)

# Analyze an image
dive myapp:latest

# CI mode (fail if image efficiency below threshold)
dive myapp:latest --ci --lowestEfficiency 0.9
```

dive shows:

- Layer-by-layer file changes (added, modified, removed)
- Image efficiency score
- Wasted space from files added then removed in later layers
- File tree at each layer

## Network Troubleshooting

### Inspect Networks

```bash
# List networks
docker network ls

# Inspect a network (shows connected containers)
docker network inspect bridge
docker network inspect myapp_default

# Find container's IP address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <container>
```

### DNS Resolution

```bash
# Test DNS resolution from inside a container
docker exec <container> nslookup db
docker exec <container> getent hosts db

# Check /etc/resolv.conf
docker exec <container> cat /etc/resolv.conf

# Ping another service
docker exec <container> ping -c 3 db
```

### Port and Connectivity

```bash
# Check published ports
docker port <container>

# Test TCP connectivity from inside a container
docker exec <container> nc -zv db 5432
docker exec <container> wget -qO- http://api:3000/health

# Check if a port is listening inside the container
docker exec <container> netstat -tlnp
docker exec <container> ss -tlnp
```

### Common Network Issues

| Symptom                              | Likely Cause                     | Fix                                                            |
| ------------------------------------ | -------------------------------- | -------------------------------------------------------------- |
| Cannot resolve service name          | Containers on different networks | Put both on the same Compose network                           |
| Connection refused                   | Service not listening on 0.0.0.0 | Bind to `0.0.0.0`, not `127.0.0.1`                             |
| Port already in use on host          | Another process using the port   | Change host port mapping or stop conflicting process           |
| Container can reach host but not web | DNS not configured               | Check `--dns` flag or `/etc/resolv.conf`                       |
| Intermittent timeouts                | Network mode or MTU mismatch     | Check `docker network inspect`, try `--net=host` for debugging |

## Build Debugging

### Build with Verbose Output

```bash
# Show build output (not collapsed)
docker build --progress=plain .

# No cache (force full rebuild)
docker build --no-cache .

# Build up to a specific stage
docker build --target builder .
```

### Debug a Failed Build Step

```bash
# Build interactively from a specific stage
docker build --target builder -t debug-build .
docker run -it debug-build sh
# Now you can inspect the filesystem at that build stage
```

### Compose Debugging

```bash
# Validate Compose file
docker compose config

# Show resolved environment variables
docker compose config | grep -A5 environment

# Dry run (show what would happen)
docker compose up --dry-run

# Force recreate containers
docker compose up -d --force-recreate

# Rebuild images
docker compose up -d --build
```

## Cleanup

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -f

# Remove unused images (including tagged ones not used by containers)
docker image prune -a -f

# Remove unused volumes (careful: deletes data)
docker volume prune -f

# Nuclear option: remove everything unused
docker system prune -a --volumes -f

# Show disk usage
docker system df
docker system df -v
```

## Quick Debugging Workflow

```bash
# 1. Check if container is running and healthy
docker ps -a | grep myapp
docker inspect --format='{{.State.Health.Status}}' myapp

# 2. Check recent logs
docker logs --tail 50 myapp

# 3. Check environment
docker exec myapp env

# 4. Check network connectivity
docker exec myapp nslookup db
docker exec myapp nc -zv db 5432

# 5. Check filesystem
docker exec myapp ls -la /app
docker exec myapp df -h

# 6. Interactive debugging
docker exec -it myapp sh
```
