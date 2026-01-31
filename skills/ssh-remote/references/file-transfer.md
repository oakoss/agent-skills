---
title: File Transfer
description: File transfer patterns using rsync and scp over SSH, including compression, resume, and bandwidth control
tags: [rsync, scp, sftp, file-transfer, sync, backup, compression]
---

# File Transfer

## rsync (Preferred)

rsync is the recommended tool for SSH file transfers. It transfers only changed data blocks (delta sync), supports compression, can resume interrupted transfers, and preserves file metadata. rsync uses SSH as its transport by default.

### Basic Patterns

Sync a local directory to a remote host:

```bash
rsync -avz ./local/ user@host:/remote/path/
```

Sync from remote to local:

```bash
rsync -avz user@host:/remote/path/ ./local/
```

The trailing slash on the source path matters:

- `./local/` syncs the contents of `local` into the destination
- `./local` syncs the directory itself, creating `local/` inside the destination

### Common Flags

```bash
rsync -avzP ./local/ user@host:/remote/path/
```

| Flag        | Purpose                                                                    |
| ----------- | -------------------------------------------------------------------------- |
| `-a`        | Archive mode: recursive, preserves permissions, timestamps, symlinks       |
| `-v`        | Verbose output                                                             |
| `-z`        | Compress during transfer (saves bandwidth on slow links)                   |
| `-P`        | Combines `--partial` (keep partial files) and `--progress` (show progress) |
| `-n`        | Dry run: show what would transfer without making changes                   |
| `--delete`  | Remove files on destination that do not exist on source                    |
| `--exclude` | Skip matching patterns                                                     |
| `--bwlimit` | Limit bandwidth usage                                                      |

### Dry Run Before Sync

Always preview destructive operations (especially with `--delete`):

```bash
rsync -avzn --delete ./local/ user@host:/remote/path/
```

Add `--itemize-changes` for a detailed breakdown of what changed:

```bash
rsync -avzn --itemize-changes ./local/ user@host:/remote/path/
```

### Exclude Patterns

Skip files or directories from the sync:

```bash
rsync -avz --exclude='node_modules' --exclude='.git' ./project/ user@host:/deploy/
```

Use an exclude file for complex patterns:

```bash
rsync -avz --exclude-from='.rsyncignore' ./project/ user@host:/deploy/
```

### Bandwidth Limiting

Limit bandwidth to avoid saturating the network link:

```bash
rsync -avzP --bwlimit=10m ./large-data/ user@host:/backup/
```

The `--bwlimit` value accepts suffixes: `k` (KiB/s), `m` (MiB/s).

### Optimizing Transfer Speed

For high-bandwidth links where CPU is the bottleneck, skip compression and use a faster cipher:

```bash
rsync -avP -e "ssh -T -c aes128-gcm@openssh.com -o Compression=no -x" ./data/ user@host:/data/
```

- `-T` disables pseudo-terminal allocation
- `-c aes128-gcm@openssh.com` uses hardware-accelerated AES-GCM cipher
- `-o Compression=no` skips SSH-level compression (rsync handles its own)
- `-x` disables X11 forwarding

### rsync with SSH Multiplexing

Combine rsync with SSH multiplexing for repeated transfers to the same host:

```bash
rsync -avzP -e "ssh -o ControlMaster=auto -o ControlPath=~/.ssh/sockets/%r@%h-%p -o ControlPersist=600" ./data/ user@host:/data/
```

Or configure multiplexing globally in `~/.ssh/config` and rsync will use it automatically.

### Mirror with Delete

Create an exact mirror of the source (removes extra files on destination):

```bash
rsync -avz --delete ./source/ user@host:/mirror/
```

## scp (Legacy)

The SCP protocol is deprecated by the OpenSSH project due to security design issues. The `scp` command still exists in modern OpenSSH but uses SFTP internally. For new workflows, prefer rsync or sftp.

### Basic scp Patterns

Copy a file to a remote host:

```bash
scp local.txt user@host:/remote/path/
```

Copy a file from a remote host:

```bash
scp user@host:/remote/file.txt ./local/
```

Copy a directory recursively:

```bash
scp -r ./local_dir user@host:/remote/path/
```

### When scp Is Acceptable

- Quick one-off file copies where rsync is not installed on the remote host
- Environments where only the `scp` command is available
- Simple CI/CD pipelines copying single artifacts

For anything recurring, large, or requiring resume capability, use rsync.

## sftp

sftp provides an interactive file transfer session over SSH:

```bash
sftp user@host
```

Common sftp commands within the session:

```text
put local-file.txt /remote/path/
get /remote/file.txt ./local/
ls /remote/path/
mkdir /remote/new-dir
```

Non-interactive sftp for scripting (batch mode):

```bash
sftp -b commands.txt user@host
```

Where `commands.txt` contains one sftp command per line.
