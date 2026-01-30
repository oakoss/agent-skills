---
title: Error Handling
description: Structured JSON error responses with actionable hints, exit codes and their meanings, and troubleshooting common issues
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

| Code | Meaning              | Action                                  |
| ---- | -------------------- | --------------------------------------- |
| 0    | Success              | Parse stdout                            |
| 1    | Health check failed  | Run `cass index --full`                 |
| 2    | Usage error          | Fix syntax (hint provided)              |
| 3    | Index/DB missing     | Run `cass index --full`                 |
| 4    | Network error        | Check connectivity                      |
| 5    | Data corruption      | Run `cass index --full --force-rebuild` |
| 6    | Incompatible version | Update cass                             |
| 7    | Lock/busy            | Retry later                             |
| 8    | Partial result       | Increase `--timeout`                    |
| 9    | Unknown error        | Check `retryable` flag                  |

## Troubleshooting

| Issue                | Solution                                              |
| -------------------- | ----------------------------------------------------- |
| "missing index"      | `cass index --full`                                   |
| Stale warning        | Rerun index or enable watch                           |
| Empty results        | Check `cass stats --json`, verify connectors detected |
| JSON parsing errors  | Use `--robot-format compact`                          |
| Watch not triggering | Check `watch_state.json`, verify file event support   |
| Reset TUI state      | `cass tui --reset-state` or `Ctrl+Shift+Del`          |
