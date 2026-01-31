---
title: Error Handling
description: Structured JSON error responses, exit code conventions, and troubleshooting common issues
tags: [error, exit-code, JSON, hint, retryable, troubleshooting, diagnostics]
---

# Error Handling

## Structured Error Responses

Errors are JSON with actionable hints:

```json
{
  "error": {
    "code": 3,
    "kind": "index_missing",
    "message": "Search index not found",
    "hint": "Run 'cass index --full' to build the index",
    "retryable": false
  }
}
```

## Exit Codes

| Code     | Meaning                |
| -------- | ---------------------- |
| 0        | Success (parse stdout) |
| Non-zero | Error occurred         |

stdout contains JSON data only. stderr contains diagnostics and teaching notes.

Run `cass robot-docs exit-codes` for the full exit code reference from your installed version.

## Recovery Pattern

```bash
# Always start with a health check
cass health --json || cass index --full

# If search returns errors, rebuild the index
cass index --full --force-rebuild
```

## Troubleshooting

| Issue                | Solution                                             |
| -------------------- | ---------------------------------------------------- |
| "missing index"      | `cass index --full`                                  |
| Stale warning        | Rerun index or enable watch mode                     |
| Empty results        | Check `cass health --json`, verify agent data exists |
| JSON parsing errors  | Ensure you read stdout only, not stderr              |
| Watch not triggering | Verify file event support on your OS                 |
