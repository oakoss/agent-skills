---
title: Tunneling
description: SSH port forwarding, SOCKS proxy, jump hosts, and ProxyJump configuration
tags: [tunneling, port-forwarding, socks-proxy, jump-host, bastion, ProxyJump]
---

# Tunneling

## Local Port Forwarding

Local forwarding makes a remote service accessible on a local port. Traffic flows: local port -> SSH tunnel -> remote host -> target.

Access a remote web server locally:

```bash
ssh -L 8080:localhost:80 user@host
```

This binds `localhost:8080` on your machine. Connections to it are forwarded through the SSH tunnel to port 80 on the remote host.

### Forwarding to a Third Host

Forward through the SSH host to a different machine on the remote network:

```bash
ssh -L 5432:db-server:5432 user@jumphost
```

This makes `db-server:5432` (accessible from `jumphost`) available at `localhost:5432`. The connection from `jumphost` to `db-server` is unencrypted unless `db-server` provides its own TLS.

### Background Tunnel

Open a tunnel without an interactive shell, running in the background:

```bash
ssh -fNL 8080:localhost:80 user@host
```

| Flag | Purpose                                 |
| ---- | --------------------------------------- |
| `-f` | Fork to background after authentication |
| `-N` | No remote command (tunnel only)         |
| `-L` | Local port forward                      |

### Bind to All Interfaces

By default, local forwards bind to `localhost` only. To make the tunnel accessible from other machines on your network:

```bash
ssh -L 0.0.0.0:8080:localhost:80 user@host
```

Requires `GatewayPorts yes` on the SSH server for remote forwards.

## Remote Port Forwarding

Remote forwarding exposes a local service to the remote host. Traffic flows: remote port -> SSH tunnel -> your machine -> target.

```bash
ssh -R 9000:localhost:3000 user@host
```

Connections to port 9000 on the remote host are forwarded to `localhost:3000` on your machine. Useful for exposing a local development server to a remote environment.

### Persistent Remote Tunnel

Combine with background and no-command flags:

```bash
ssh -fNR 9000:localhost:3000 user@host
```

### Server-Side Configuration

The SSH server must allow remote forwarding. In `/etc/ssh/sshd_config`:

```text
GatewayPorts clientspecified
```

Without this, remote forwards bind only to `localhost` on the server, preventing external access.

## Dynamic Port Forwarding (SOCKS Proxy)

Dynamic forwarding creates a local SOCKS5 proxy. Applications configured to use this proxy route all traffic through the SSH tunnel:

```bash
ssh -D 1080 user@host
```

This creates a SOCKS5 proxy at `localhost:1080`. Configure browsers or applications to use `localhost:1080` as a SOCKS5 proxy to route traffic through the remote host.

Background SOCKS proxy:

```bash
ssh -fND 1080 user@host
```

### Use with curl

Test the proxy with curl:

```bash
curl --socks5-hostname localhost:1080 https://example.com
```

The `--socks5-hostname` flag routes DNS through the proxy as well, preventing DNS leaks.

## Jump Hosts (ProxyJump)

ProxyJump (`-J` flag, available since OpenSSH 7.3) connects to a target through one or more intermediate hosts without agent forwarding. This is more secure than `ForwardAgent` because the jump host never has access to your SSH keys.

### Command-Line Usage

Single jump host:

```bash
ssh -J jumphost user@internal-server
```

Multiple jump hosts (comma-separated):

```bash
ssh -J jump1,jump2 user@internal-server
```

With explicit users and ports:

```bash
ssh -J admin@jump1:2222,deploy@jump2:22 user@target
```

### SSH Config

Define jump host relationships in `~/.ssh/config`:

```text
Host bastion
    HostName bastion.example.com
    User admin
    IdentityFile ~/.ssh/bastion_ed25519

Host internal
    HostName 10.0.0.50
    User deploy
    ProxyJump bastion
    IdentityFile ~/.ssh/internal_ed25519
```

Then connect directly:

```bash
ssh internal
```

### Chained ProxyJump in Config

Chain multiple hops by referencing config aliases:

```text
Host jump1
    HostName jump1.example.com
    User admin

Host jump2
    HostName jump2.internal
    ProxyJump jump1
    User admin

Host target
    HostName 10.0.0.100
    ProxyJump jump2
    User deploy
```

### File Transfer Through Jump Hosts

rsync and scp work with ProxyJump:

```bash
rsync -avzP -e "ssh -J jumphost" ./files/ user@target:/path/
```

```bash
scp -J jumphost local.txt user@target:/path/
```

### Port Forwarding Through Jump Hosts

Combine tunneling with jump hosts:

```bash
ssh -L 8080:localhost:80 -J jumphost user@internal-server
```

## ProxyJump vs. Legacy ProxyCommand

ProxyJump replaces the older `ProxyCommand` directive. Use ProxyJump for all new configurations:

```text
# Legacy (avoid for new setups)
Host internal
    ProxyCommand ssh -W %h:%p bastion

# Current (preferred)
Host internal
    ProxyJump bastion
```

ProxyJump advantages over ProxyCommand:

- Simpler syntax
- Supports comma-separated chaining
- No shell escaping issues
- Works with `-J` on the command line
