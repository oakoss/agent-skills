---
title: POSIX Scripting
description: POSIX-compliant shell scripting, signal handling, process management, job control, traps, and portable patterns
tags: [posix, sh, signal, trap, process, job-control, portable, ipc, socket]
---

# POSIX Scripting

## Portable Shebang

```sh
#!/bin/sh
```

Use `/bin/sh` for POSIX scripts. Avoid `#!/bin/bash` unless Bash features are required.

## POSIX-Compatible Constructs

### Conditionals

```sh
# POSIX test (use [ ] not [[ ]])
if [ "$var" = "value" ]; then
  echo "match"
fi

# String checks
[ -n "$var" ]       # Non-empty
[ -z "$var" ]       # Empty
[ "$a" = "$b" ]     # Equal (single =, not ==)
[ "$a" != "$b" ]    # Not equal

# Numeric comparison
[ "$a" -eq "$b" ]   # Equal
[ "$a" -lt "$b" ]   # Less than
[ "$a" -gt "$b" ]   # Greater than

# File tests
[ -f "$path" ]      # Regular file exists
[ -d "$path" ]      # Directory exists
[ -r "$path" ]      # Readable
[ -w "$path" ]      # Writable
[ -x "$path" ]      # Executable
[ -s "$path" ]      # Non-empty file
[ -L "$path" ]      # Symbolic link
```

### Functions (POSIX Syntax)

```sh
# POSIX: no "function" keyword
my_func() {
  local var="$1"
  echo "$var"
  return 0
}
```

### String Operations (No Bashisms)

```sh
# Parameter expansion (POSIX)
${var#pattern}      # Remove shortest prefix match
${var##pattern}     # Remove longest prefix match
${var%pattern}      # Remove shortest suffix match
${var%%pattern}     # Remove longest suffix match

# Extract filename
filename="${path##*/}"

# Extract directory
dirname="${path%/*}"

# Extract extension
ext="${filename##*.}"

# Remove extension
base="${filename%.*}"
```

### Loops

```sh
# Iterate over arguments
for arg in "$@"; do
  echo "$arg"
done

# C-style not POSIX; use while instead
i=0
while [ "$i" -lt 10 ]; do
  echo "$i"
  i=$((i + 1))
done

# Read lines from file
while IFS= read -r line; do
  echo "$line"
done < file.txt
```

## Signal Handling

### Trap Syntax

```sh
trap 'handler_commands' SIGNAL_LIST

# Common signals
trap 'cleanup' EXIT          # Always runs on exit
trap 'cleanup; exit 1' INT   # Ctrl-C
trap 'cleanup; exit 1' TERM  # kill (default signal)
trap '' HUP                  # Ignore hangup
trap 'reload_config' USR1    # Custom: reload
```

### Cleanup Pattern

```sh
cleanup() {
  rm -f "$tmpfile"
  [ -n "$pid" ] && kill "$pid" 2>/dev/null
}

trap cleanup EXIT

tmpfile=$(mktemp)
```

### Signal Reference

| Signal  | Number | Default   | Common Use                           |
| ------- | ------ | --------- | ------------------------------------ |
| `HUP`   | 1      | Terminate | Reload config, terminal closed       |
| `INT`   | 2      | Terminate | Ctrl-C                               |
| `QUIT`  | 3      | Core dump | Ctrl-\\                              |
| `TERM`  | 15     | Terminate | Graceful shutdown request            |
| `USR1`  | 10     | Terminate | Custom (reload, log rotate)          |
| `USR2`  | 12     | Terminate | Custom                               |
| `PIPE`  | 13     | Terminate | Broken pipe                          |
| `WINCH` | 28     | Ignore    | Terminal resize                      |
| `EXIT`  | N/A    | N/A       | Shell exit (trap-only pseudo-signal) |

### Graceful Shutdown

```sh
shutdown_requested=0

handle_term() {
  shutdown_requested=1
}

trap handle_term TERM INT

while [ "$shutdown_requested" -eq 0 ]; do
  do_work
  sleep 1
done

cleanup
```

## Process Management

### Background Processes

```sh
long_task &
bg_pid=$!

# Wait for specific process
wait "$bg_pid"
exit_code=$?

# Wait for all background jobs
wait
```

### Parallel Execution with Limits

```sh
max_jobs=4
running=0

for item in "$@"; do
  process_item "$item" &
  running=$((running + 1))
  if [ "$running" -ge "$max_jobs" ]; then
    wait -n 2>/dev/null || wait
    running=$((running - 1))
  fi
done
wait
```

### PID File Management

```sh
pidfile="/var/run/myservice.pid"

acquire_lock() {
  if [ -f "$pidfile" ]; then
    local old_pid
    old_pid=$(cat "$pidfile")
    if kill -0 "$old_pid" 2>/dev/null; then
      echo "Already running (PID $old_pid)" >&2
      return 1
    fi
    rm -f "$pidfile"
  fi
  echo $$ > "$pidfile"
}

release_lock() {
  rm -f "$pidfile"
}

trap release_lock EXIT
acquire_lock || exit 1
```

### Subshell Isolation

```sh
# Changes inside subshell do not affect parent
(
  cd /tmp || exit 1
  export MY_VAR="local"
  do_work
)
# PWD and MY_VAR unchanged here
```

## IPC Patterns

### Named Pipes (FIFOs)

```sh
fifo="/tmp/myfifo.$$"
mkfifo "$fifo"
trap 'rm -f "$fifo"' EXIT

# Writer
echo "message" > "$fifo" &

# Reader
while IFS= read -r msg; do
  echo "Received: $msg"
done < "$fifo"
```

### Unix Socket IPC from Shell

```sh
# Send command via socat
echo '{"command":"status"}' | socat - UNIX-CONNECT:/tmp/myapp.sock

# Listen on socket (simple server)
socat UNIX-LISTEN:/tmp/myapp.sock,fork EXEC:./handler.sh
```

### Here Document for Input

```sh
command <<'HEREDOC'
  Multi-line input
  No variable expansion with quoted delimiter
HEREDOC

command <<HEREDOC
  Expands $VARIABLES
  And $(commands)
HEREDOC
```

## Portable Patterns

### Safe Temporary Files

```sh
tmpdir=$(mktemp -d) || exit 1
trap 'rm -rf "$tmpdir"' EXIT

tmpfile="$tmpdir/work"
```

### Command Existence Check

```sh
has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

if has_cmd curl; then
  curl -fsSL "$url"
elif has_cmd wget; then
  wget -qO- "$url"
else
  echo "curl or wget required" >&2
  exit 1
fi
```

### Strict Mode

```sh
set -eu
# -e: exit on error
# -u: error on undefined variable

# For pipelines (not POSIX but widely supported)
set -o pipefail 2>/dev/null || true
```

### OS Detection

```sh
detect_os() {
  case "$(uname -s)" in
    Linux*)  echo "linux" ;;
    Darwin*) echo "macos" ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
    FreeBSD*) echo "freebsd" ;;
    *)       echo "unknown" ;;
  esac
}

detect_arch() {
  case "$(uname -m)" in
    x86_64|amd64) echo "x86_64" ;;
    aarch64|arm64) echo "arm64" ;;
    armv7*)       echo "armv7" ;;
    *)            echo "unknown" ;;
  esac
}
```

### Logging

```sh
log_info()  { printf '[INFO]  %s\n' "$*" >&2; }
log_warn()  { printf '[WARN]  %s\n' "$*" >&2; }
log_error() { printf '[ERROR] %s\n' "$*" >&2; }

die() {
  log_error "$@"
  exit 1
}
```
