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

## Modify Tool Input Before Execution

Rewrite tool parameters using `updatedInput`. This example adds `--no-cache` to npm commands.

```bash
#!/bin/bash
# .claude/hooks/add-no-cache.sh
INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command')

if [[ "$CMD" == npm\ install* ]] && [[ "$CMD" != *--no-cache* ]]; then
  cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "Added --no-cache flag",
    "updatedInput": {
      "command": "$CMD --no-cache"
    }
  }
}
EOF
else
  exit 0
fi
```

## Agent Hook for Verification

Use an agent hook that can read files and search code to verify conditions.

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "agent",
            "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

## Log All MCP Operations

Track operations from a specific MCP server.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__memory__.*",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'INPUT=$(cat); echo \"$(date -u +\"%Y-%m-%dT%H:%M:%SZ\") $(echo $INPUT | jq -r .tool_name)\" >> \"$CLAUDE_PROJECT_DIR\"/.claude/mcp-operations.log'"
          }
        ]
      }
    ]
  }
}
```

## Skill-Scoped Hook

Define hooks in skill frontmatter. They run only while the skill is active.

```yaml
---
name: secure-operations
description: 'Perform operations with security checks. Use when running sensitive commands.'
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/security-check.sh'
          once: true
---
```

The `once: true` option runs the hook only once per session (skills only, not agents).

## Python Script Hook

For complex logic, use Python with uv for dependency management.

```python
#!/usr/bin/env -S uv run --quiet --script
# .claude/hooks/schema-change.py
import json
import sys

input_data = json.loads(sys.stdin.read())
file_path = input_data.get("tool_input", {}).get("file_path", "")

if "src/modules/db/schema" in file_path:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": "Schema modified. Run: pnpm db:generate"
        }
    }))

sys.exit(0)
```

## Session Cleanup

Run cleanup tasks when a session ends.

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'echo \"Session ended at $(date)\" >> \"$CLAUDE_PROJECT_DIR\"/.claude/session.log'"
          }
        ]
      }
    ]
  }
}
```
