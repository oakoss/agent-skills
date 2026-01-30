---
name: agent-session-search
description: 'Coding Agent Session Search - unified CLI/TUI to index and search local coding agent history from Claude Code, Codex, Gemini, Cursor, Aider, ChatGPT, Pi-Agent, Factory, and more. Use when searching past agent conversations, indexing coding session history, finding previous solutions across agents, or querying session logs with CASS CLI robot mode.'
---

# Agent Session Search

Unified CLI/TUI to index and search local coding agent history. Aggregates sessions from 11 agents into a single searchable index. Purpose-built for AI agent consumption with robot mode.

**CRITICAL: NEVER run bare `cass` — it launches an interactive TUI that blocks your session. Always use `--robot` or `--json` flags.**

## Essential Commands

| Command                                        | Purpose                                    |
| ---------------------------------------------- | ------------------------------------------ |
| `cass health`                                  | Health check (exit 0=healthy, 1=unhealthy) |
| `cass index --full`                            | Full rebuild of DB and search index        |
| `cass index`                                   | Incremental update since last scan         |
| `cass search "query" --robot`                  | Search with JSON output                    |
| `cass search "query" --robot --fields minimal` | Minimal payload (path, line, agent)        |
| `cass search "query" --robot --limit 5`        | Cap number of results                      |
| `cass view /path -n 42 --json`                 | View source at specific line               |
| `cass expand /path -n 42 -C 5 --json`          | Context around a search result             |
| `cass capabilities --json`                     | Discover available features                |
| `cass introspect --json`                       | Full API schema                            |
| `cass robot-docs guide`                        | LLM-optimized documentation                |

## Supported Agents

| Agent           | Location                                        | Format           |
| --------------- | ----------------------------------------------- | ---------------- |
| Claude Code     | `~/.claude/projects`                            | JSONL            |
| Codex           | `~/.codex/sessions`                             | JSONL            |
| Gemini CLI      | `~/.gemini/tmp`                                 | JSON             |
| Cline           | VS Code global storage                          | Task directories |
| OpenCode        | `.opencode` directories                         | SQLite           |
| Amp             | `~/.local/share/amp` + VS Code                  | Mixed            |
| Cursor          | `~/Library/Application Support/Cursor`          | SQLite           |
| ChatGPT         | `~/Library/Application Support/com.openai.chat` | JSON (v1)        |
| Aider           | `~/.aider.chat.history.md` + per-project        | Markdown         |
| Pi-Agent        | `~/.pi/agent/sessions`                          | JSONL            |
| Factory (Droid) | `~/.factory/sessions`                           | JSONL            |

## Exit Codes

| Code | Meaning              | Action                              |
| ---- | -------------------- | ----------------------------------- |
| 0    | Success              | Parse stdout                        |
| 1    | Health check failed  | `cass index --full`                 |
| 2    | Usage error          | Fix syntax (hint provided)          |
| 3    | Index/DB missing     | `cass index --full`                 |
| 4    | Network error        | Check connectivity                  |
| 5    | Data corruption      | `cass index --full --force-rebuild` |
| 6    | Incompatible version | Update cass                         |
| 7    | Lock/busy            | Retry later                         |
| 8    | Partial result       | Increase `--timeout`                |
| 9    | Unknown error        | Check `retryable` flag              |

## Search Modes

| Mode              | Algorithm              | Best For                           |
| ----------------- | ---------------------- | ---------------------------------- |
| lexical (default) | BM25 full-text         | Exact term matching, code searches |
| semantic          | Vector similarity      | Conceptual queries                 |
| hybrid            | Reciprocal Rank Fusion | Balanced precision and recall      |

## Common Mistakes

| Mistake                | Fix                                          |
| ---------------------- | -------------------------------------------- |
| Running bare `cass`    | Always use `--robot` or `--json`             |
| Missing `--robot` flag | Add `--robot` for JSON output                |
| No index exists        | Run `cass index --full` first                |
| Token budget overflow  | Use `--fields minimal` and `--limit`         |
| Stale search results   | Run `cass index` or enable `--watch`         |
| Parsing stderr as JSON | stdout = JSON only, diagnostics go to stderr |

## Delegation

Use this skill for indexing, searching, and analyzing coding agent session history via CASS CLI.

## References

- [Command Reference](references/command-reference.md) — indexing, search, session analysis, status and diagnostics
- [Robot Mode](references/robot-mode.md) — self-documenting API, forgiving syntax, output formats, token budget, pipeline mode
- [Query Language](references/query-language.md) — boolean operators, wildcards, match types, time formats, auto-fuzzy fallback
- [Search and Ranking](references/search-and-ranking.md) — search modes, ranking modes, scoring formula, aggregation
- [Remote Sources](references/remote-sources.md) — multi-machine search via SSH/rsync, setup wizard, path mappings
- [TUI Reference](references/tui-reference.md) — keyboard shortcuts, themes, saved views, density modes, bookmarks
- [Error Handling](references/error-handling.md) — structured errors, exit codes, troubleshooting
- [Internals](references/internals.md) — response shapes, deduplication, performance, watch mode, semantic search
- [Configuration](references/configuration.md) — environment variables, shell completions, API versioning, installation, integrations
