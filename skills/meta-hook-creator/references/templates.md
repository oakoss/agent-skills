---
title: Hook Templates
description: Ready-to-use hook templates for blocking commands, protecting files, formatting, notifications, and more
tags:
  [
    templates,
    block,
    protect,
    format,
    notification,
    auto-approve,
    environment,
    stop,
  ]
---

# Hook Templates

## Block Dangerous Commands

Block shell commands matching a pattern. Uses exit 2 to prevent the tool call.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'COMMAND=$(jq -r \".tool_input.command\"); if echo \"$COMMAND\" | grep -q \"rm -rf\"; then echo \"Blocked: destructive command\" >&2; exit 2; fi'"
          }
        ]
      }
    ]
  }
}
```

Script-based version with JSON decision output:

```bash
#!/bin/bash
# .claude/hooks/block-dangerous.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  echo '{"decision":"block","reason":"Destructive command blocked by hook"}'
else
  exit 0
fi
```

## Protect Files from Modification

Block writes to sensitive files like `.env`, lock files, or config.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'PATH_VAL=$(jq -r \".tool_input.file_path // empty\"); if [[ \"$PATH_VAL\" == *.env* ]] || [[ \"$PATH_VAL\" == *lock* ]]; then echo \"Blocked: protected file\" >&2; exit 2; fi'"
          }
        ]
      }
    ]
  }
}
```

## Auto-Format After Write

Run a formatter after Claude writes or edits TypeScript files.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'FILE=$(jq -r \".tool_input.file_path // empty\"); if [[ \"$FILE\" == *.ts ]] || [[ \"$FILE\" == *.tsx ]]; then npx prettier --write \"$FILE\" 2>/dev/null; fi'",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## Desktop Notification on Permission Request

Send a macOS notification when Claude needs permission approval.

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude needs permission\" with title \"Claude Code\"'"
          }
        ]
      }
    ]
  }
}
```

For Linux, use `notify-send`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send 'Claude Code' 'Claude needs permission'"
          }
        ]
      }
    ]
  }
}
```

## Auto-Approve Safe Commands

Automatically approve specific safe commands without prompting.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'CMD=$(jq -r \".tool_input.command\"); if [[ \"$CMD\" == npm\\ test* ]] || [[ \"$CMD\" == npx\\ prettier* ]]; then echo \"{\\\"hookSpecificOutput\\\":{\\\"hookEventName\\\":\\\"PreToolUse\\\",\\\"permissionDecision\\\":\\\"allow\\\",\\\"permissionDecisionReason\\\":\\\"Safe command auto-approved\\\"}}\"; fi'"
          }
        ]
      }
    ]
  }
}
```

## Environment Setup on Session Start

Set environment variables that persist for all Bash commands in the session.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'if [ -n \"$CLAUDE_ENV_FILE\" ]; then echo \"export NODE_ENV=development\" >> \"$CLAUDE_ENV_FILE\"; echo \"export PATH=\\\"\\$PATH:./node_modules/.bin\\\"\" >> \"$CLAUDE_ENV_FILE\"; fi'"
          }
        ]
      }
    ]
  }
}
```

Script-based version that captures environment from a setup command:

```bash
#!/bin/bash
# .claude/hooks/setup-env.sh
ENV_BEFORE=$(export -p | sort)

source ~/.nvm/nvm.sh
nvm use 20

if [ -n "$CLAUDE_ENV_FILE" ]; then
  ENV_AFTER=$(export -p | sort)
  comm -13 <(echo "$ENV_BEFORE") <(echo "$ENV_AFTER") >> "$CLAUDE_ENV_FILE"
fi

exit 0
```

## Force Continue Until Tests Pass (Prompt Hook)

Use an LLM-based hook to evaluate whether Claude should stop.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Evaluate if Claude should stop: $ARGUMENTS. Check if all tasks are complete and no errors remain. Respond with {\"ok\": true} to allow stopping or {\"ok\": false, \"reason\": \"explanation\"} to continue.",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Run Tests After File Changes (Async)

Run tests in the background without blocking Claude. Results are delivered on the next turn.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/run-tests-async.sh",
            "async": true,
            "timeout": 300
          }
        ]
      }
    ]
  }
}
```

```bash
#!/bin/bash
# .claude/hooks/run-tests-async.sh
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE_PATH" != *.ts && "$FILE_PATH" != *.js ]]; then
  exit 0
fi

RESULT=$(npm test 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "{\"systemMessage\": \"Tests passed after editing $FILE_PATH\"}"
else
  echo "{\"systemMessage\": \"Tests failed after editing $FILE_PATH: $RESULT\"}"
fi
```

## Python Hooks

For complex logic, use Python with uv for dependency management. Python hooks are more readable and maintainable than inline bash for multi-step logic.

### Python Hook Template

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""Hook description."""

import json
import sys

def main() -> int:
    input_data = json.loads(sys.stdin.read())

    # Extract relevant fields
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")

    # Your logic here

    # Exit codes: 0=success, 1=error, 2=block (PreToolUse only)
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### PreToolUse Validator

Block dangerous commands before execution using regex patterns:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import re
import sys

BLOCKED_PATTERNS = [
    (r"\brm\s+-rf\b", "Blocked: rm -rf is dangerous"),
    (r"--force\b", "Blocked: --force operations disabled"),
]

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

command = data.get("tool_input", {}).get("command", "")

for pattern, message in BLOCKED_PATTERNS:
    if re.search(pattern, command, re.I):
        print(message, file=sys.stderr)
        sys.exit(2)

sys.exit(0)
```

### UserPromptSubmit with Context

Add context to every user prompt:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import sys
import datetime

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

# Add context to conversation
context = f"Current time: {datetime.datetime.now()}"
print(context)

sys.exit(0)
```

### Auto-Approve Documentation Files

Automatically approve read access to documentation without prompting:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

tool_name = data.get("tool_name", "")
file_path = data.get("tool_input", {}).get("file_path", "")

if tool_name == "Read" and file_path.endswith((".md", ".txt", ".json")):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": "Documentation auto-approved"
        },
        "suppressOutput": True
    }
    print(json.dumps(output))

sys.exit(0)
```

### Schema Change Notification

Notify when database schema files are modified:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

file_path = data.get("tool_input", {}).get("file_path", "")

if "schema" in file_path and file_path.endswith(".ts"):
    print("Schema modified. Remember to run: pnpm db:generate")

sys.exit(0)
```

### Protected File Blocker

Block modifications to sensitive files:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import sys

PROTECTED_PATTERNS = [
    ".env",
    ".env.local",
    "credentials",
    "secrets",
    ".git/",
]

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

file_path = data.get("tool_input", {}).get("file_path", "")

for pattern in PROTECTED_PATTERNS:
    if pattern in file_path:
        print(f"Blocked: Cannot modify protected file ({pattern})", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
```

### Post-Write Formatter

Format files automatically after writing based on file type:

```python
#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
import json
import subprocess
import sys
from pathlib import Path

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(1)

file_path = data.get("tool_input", {}).get("file_path", "")

if not file_path or not Path(file_path).exists():
    sys.exit(0)

if file_path.endswith((".ts", ".tsx", ".js", ".jsx")):
    subprocess.run(["npx", "prettier", "--write", file_path], capture_output=True)
elif file_path.endswith(".py"):
    subprocess.run(["ruff", "format", file_path], capture_output=True)
elif file_path.endswith(".md"):
    subprocess.run(["npx", "markdownlint", "--fix", file_path], capture_output=True)

sys.exit(0)
```
