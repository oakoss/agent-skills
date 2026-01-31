---
title: Connections
description: Basic SSH connections, SSH config file setup, remote command execution, and debugging
tags: [ssh, config, remote-commands, verbose, pseudo-terminal, known-hosts]
---

# Connections

## Basic Connection

Connect to a remote server with default settings:

```bash
ssh user@hostname
```

Connect on a non-default port:

```bash
ssh -p 2222 user@hostname
```

Connect with a specific identity (private key) file:

```bash
ssh -i ~/.ssh/my_key user@hostname
```

## SSH Config File

The client config file at `~/.ssh/config` defines per-host settings that simplify repeated connections. Entries are matched top-down; the first matching `Host` block wins for each directive.

```text
Host myserver
    HostName 192.168.1.100
    User deploy
    Port 22
    IdentityFile ~/.ssh/myserver_key
```

After defining a config entry, connect with just the alias:

```bash
ssh myserver
```

### Wildcard Defaults

Apply settings to all hosts with a wildcard block. Place this at the end of the config file so host-specific blocks take precedence:

```text
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    AddKeysToAgent yes
    IdentitiesOnly yes
```

- `ServerAliveInterval` sends keepalive packets to prevent idle disconnects
- `ServerAliveCountMax` disconnects after this many missed keepalives
- `AddKeysToAgent yes` automatically adds keys to the running ssh-agent
- `IdentitiesOnly yes` prevents offering every key in the agent to every host

### Multiple Identity Files

Specify different keys for different services:

```text
Host github.com
    IdentityFile ~/.ssh/github_ed25519

Host gitlab.com
    IdentityFile ~/.ssh/gitlab_ed25519

Host production
    HostName prod.example.com
    User deploy
    IdentityFile ~/.ssh/prod_ed25519
```

## Running Remote Commands

Execute a single command on the remote host and return:

```bash
ssh user@host "ls -la /var/log"
```

Chain multiple commands:

```bash
ssh user@host "cd /app && git pull && systemctl restart myapp"
```

Allocate a pseudo-terminal for interactive commands. Without `-t`, commands that expect a terminal (like `htop`, `vim`, `top`) fail or produce garbled output:

```bash
ssh -t user@host "htop"
```

Force pseudo-terminal allocation even when stdin is not a terminal (useful in scripts piping commands):

```bash
ssh -tt user@host "sudo systemctl restart nginx"
```

### Passing Environment Variables

Send local environment variables to the remote host (requires `AcceptEnv` on the server):

```bash
ssh -o SendEnv=MY_VAR user@host "echo \$MY_VAR"
```

## Known Hosts Management

When connecting to a host for the first time, SSH prompts to verify the host key fingerprint. Accepted keys are stored in `~/.ssh/known_hosts`.

Remove an outdated host key (after server rebuild or IP change):

```bash
ssh-keygen -R hostname
```

Pre-scan and add a host key without interactive prompts (useful in automation):

```bash
ssh-keyscan -t ed25519 hostname >> ~/.ssh/known_hosts
```

Scan for a specific key type to avoid adding weaker algorithms:

```bash
ssh-keyscan -t ed25519 -p 2222 hostname >> ~/.ssh/known_hosts
```

### Hash Known Hosts

For privacy, hash hostnames in `known_hosts` so they are not readable if the file is compromised:

```text
Host *
    HashKnownHosts yes
```

## Debugging Connection Issues

SSH provides three verbosity levels. Start with `-v` and increase if needed:

```bash
ssh -v user@host
```

```bash
ssh -vv user@host
```

```bash
ssh -vvv user@host
```

Key things to look for in verbose output:

- Which config file and `Host` block matched
- Which identity files were offered
- Authentication methods attempted and their order
- Key exchange and cipher negotiation
- Host key verification status

### Common Connection Failures

| Symptom                            | Likely Cause                              | Fix                                               |
| ---------------------------------- | ----------------------------------------- | ------------------------------------------------- |
| `Connection refused`               | SSH daemon not running or wrong port      | Verify `sshd` is running and port is correct      |
| `Permission denied (publickey)`    | Wrong key or key not in `authorized_keys` | Check `IdentityFile`, verify public key on server |
| `Host key verification failed`     | Server key changed (rebuild, MITM)        | Verify legitimacy, then `ssh-keygen -R host`      |
| `Connection timed out`             | Firewall blocking, wrong IP               | Check network path, verify hostname/IP            |
| `Too many authentication failures` | Agent offering too many keys              | Use `IdentitiesOnly yes` in config                |
