---
title: Key Management
description: SSH key generation, Ed25519 and FIDO2 keys, ssh-agent, multiplexing, and security hardening
tags:
  [
    ed25519,
    fido2,
    ssh-keygen,
    ssh-agent,
    multiplexing,
    security,
    ControlMaster,
    authorized-keys,
    certificate-auth,
  ]
---

# Key Management

## Key Generation

### Ed25519 (Recommended)

Ed25519 is the recommended algorithm for all new SSH keys. It provides strong security with small key sizes (256-bit), fast operations, and resistance to side-channel attacks:

```bash
ssh-keygen -t ed25519 -C "user@machine"
```

Use a descriptive comment to identify the key's purpose and origin. Use a strong passphrase when prompted.

Specify a custom filename to organize keys by purpose:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/prod_ed25519 -C "deploy@production"
```

### RSA (Legacy Compatibility)

Use RSA only when Ed25519 is not supported by the remote system. Always use 4096-bit minimum:

```bash
ssh-keygen -t rsa -b 4096 -C "user@machine"
```

### FIDO2 Hardware-Backed Keys

FIDO2 keys (`ed25519-sk`) bind the private key to a physical security key (YubiKey, SoloKey, etc.). The private key never leaves the hardware device. Requires OpenSSH 8.2+ (8.3+ for `verify-required`).

Generate a FIDO2 key:

```bash
ssh-keygen -t ed25519-sk -C "user@machine (FIDO2)"
```

Generate a resident FIDO2 key (stored on the security key, portable across machines):

```bash
ssh-keygen -t ed25519-sk -O resident -O verify-required -C "user@machine (FIDO2)"
```

- `-O resident` stores the credential on the hardware key for portability
- `-O verify-required` requires physical touch (PIN or biometric) during authentication

Recover resident keys on a new machine:

```bash
ssh-keygen -K
```

This extracts key handles from the security key and writes them to disk. The "private key" file contains only a reference; the actual private key remains on the hardware.

### Key Algorithm Comparison

| Algorithm  | Key Size        | Security             | Speed  | Compatibility                             |
| ---------- | --------------- | -------------------- | ------ | ----------------------------------------- |
| Ed25519    | 256-bit         | Strong               | Fast   | OpenSSH 6.5+, universal on modern systems |
| Ed25519-SK | 256-bit         | Strongest (hardware) | Fast   | OpenSSH 8.2+, requires FIDO2 device       |
| RSA 4096   | 4096-bit        | Strong               | Slower | Universal, including legacy systems       |
| ECDSA      | 256/384/521-bit | Strong               | Fast   | Avoid (implementation concerns)           |

## Deploying Public Keys

Copy a public key to a remote server's `authorized_keys`:

```bash
ssh-copy-id user@host
```

Copy a specific key:

```bash
ssh-copy-id -i ~/.ssh/prod_ed25519.pub user@host
```

Manual deployment when `ssh-copy-id` is not available:

```bash
ssh user@host "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" < ~/.ssh/id_ed25519.pub
```

## SSH Agent

The SSH agent caches decrypted private keys in memory, eliminating repeated passphrase entry during a session.

Start the agent (if not already running):

```bash
eval "$(ssh-agent -s)"
```

Add a key to the agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

Add with macOS Keychain integration (persists across reboots):

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

List loaded keys:

```bash
ssh-add -l
```

Remove all keys from the agent:

```bash
ssh-add -D
```

### Automatic Agent Key Loading

Configure SSH to add keys to the agent automatically on first use. In `~/.ssh/config`:

```text
Host *
    AddKeysToAgent yes
```

On macOS, also add Keychain support:

```text
Host *
    AddKeysToAgent yes
    UseKeychain yes
```

## Connection Multiplexing

Multiplexing reuses a single TCP connection for multiple SSH sessions to the same host. Subsequent connections authenticate instantly and skip the TCP/TLS handshake.

### Configuration

Add to `~/.ssh/config`:

```text
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

Create the socket directory:

```bash
mkdir -p ~/.ssh/sockets
```

- `ControlMaster auto` creates a master connection if none exists, reuses if one does
- `ControlPath` defines the socket file location; include `%r` (user), `%h` (host), `%p` (port) for unique sockets
- `ControlPersist 600` keeps the master alive for 10 minutes after the last session disconnects

### Managing Multiplexed Connections

Check if a master connection is active:

```bash
ssh -O check myserver
```

Gracefully stop accepting new sessions (existing sessions continue):

```bash
ssh -O stop myserver
```

Immediately terminate the master and all sessions:

```bash
ssh -O exit myserver
```

### Per-Host Multiplexing

Enable multiplexing only for frequently accessed hosts:

```text
Host production-*
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 30m

Host dev-*
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 5m
```

## Security Hardening

### Server-Side Configuration

Key settings for `/etc/ssh/sshd_config`:

```text
PasswordAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes
MaxAuthTries 3
MaxSessions 10
AllowUsers deploy admin
```

- `PasswordAuthentication no` forces key-based authentication, eliminating brute-force password attacks
- `PermitRootLogin prohibit-password` allows root login only with keys (or use `no` to disable entirely)
- `AllowUsers` restricts which users can log in via SSH

### Client-Side Security Practices

Restrict key usage in `~/.ssh/config`:

```text
Host *
    IdentitiesOnly yes
```

This prevents the SSH client from offering every key in the agent to every server. Without it, a server sees all your loaded keys, which leaks information.

### Restricting Keys in authorized_keys

Limit what a key can do on the server:

```text
command="/usr/local/bin/deploy.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA... deploy@ci
```

| Option                | Effect                                                    |
| --------------------- | --------------------------------------------------------- |
| `command="..."`       | Only runs the specified command, ignoring client requests |
| `no-port-forwarding`  | Disables all port forwarding                              |
| `no-X11-forwarding`   | Disables X11 forwarding                                   |
| `no-agent-forwarding` | Disables agent forwarding                                 |
| `from="10.0.0.0/8"`   | Restricts key usage to specific source IPs                |

### File Permissions

SSH enforces strict file permissions. Incorrect permissions cause silent authentication failures:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/authorized_keys
```

### Brute-Force Protection

Install `fail2ban` on servers to automatically block IPs after repeated failed login attempts:

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
```

The default configuration monitors SSH and bans offending IPs. Customize ban thresholds in `/etc/fail2ban/jail.local`.

## SSH Certificate Authentication

For organizations managing many servers, SSH certificates provide centralized trust without distributing individual public keys to every server.

### How It Works

1. A Certificate Authority (CA) key pair is created
2. User public keys are signed by the CA, producing a certificate
3. Servers trust the CA public key, automatically accepting any certificate it signed

### Signing a User Key

```bash
ssh-keygen -s /path/to/ca_key -I "user-identity" -n deploy -V +52w ~/.ssh/id_ed25519.pub
```

| Flag | Purpose                                             |
| ---- | --------------------------------------------------- |
| `-s` | Path to the CA private key                          |
| `-I` | Certificate identity (for logging/auditing)         |
| `-n` | Principals (usernames) the certificate is valid for |
| `-V` | Validity period (e.g., `+52w` for one year)         |

### Server Trust Configuration

Add the CA public key to the server's `sshd_config`:

```text
TrustedUserCAKeys /etc/ssh/ca_user_key.pub
```

Certificates can be combined with FIDO2 keys for hardware-backed, centrally managed authentication.
