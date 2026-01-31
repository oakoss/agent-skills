---
title: Troubleshooting and FAQ
description: Fixing common DCG issues and answers to frequently asked questions
tags: [troubleshooting, FAQ, debugging, bypass]
---

# Troubleshooting and FAQ

## Troubleshooting

### Hook Not Blocking Commands

1. Verify `~/.claude/settings.json` has hook configuration
2. Restart Claude Code (or use `/hooks` menu to reload)
3. Check matcher is case-sensitive: `"Bash"` not `"bash"`
4. Test manually:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | dcg
echo $?  # Should print 2
```

5. Enable verbose mode in Claude Code with `Ctrl+O` to see hook output in transcript
6. Run `claude --debug` for full execution details including which hooks matched

### Hook Blocking Safe Commands

1. Check if there is an edge case not covered
2. File a GitHub issue
3. Temporary bypass: `DCG_BYPASS=1` or run command manually

### Processing Timeout

DCG enforces a 200ms maximum processing time. If a command exceeds this threshold, it is immediately allowed with a warning logged. This prevents any single hook invocation from blocking the agent indefinitely.

## FAQ

**Q: Why block `git branch -D` but allow `git branch -d`?**

Lowercase `-d` only deletes branches fully merged. Uppercase `-D` force-deletes regardless of merge status, potentially losing commits.

**Q: Why is `git push --force-with-lease` allowed?**

Force-with-lease refuses to push if the remote has commits you have not seen, preventing accidental overwrites.

**Q: Why block all `rm -rf` outside temp directories?**

Recursive forced deletion is extremely dangerous. A typo or wrong variable can delete critical files. Temp directories are designed to be ephemeral.

**Q: What if I really need to run a blocked command?**

DCG instructs the agent to ask for permission. Run the command manually in a separate terminal after making a conscious decision.

## Integration with Claude Code

DCG integrates natively as a `PreToolUse` hook in Claude Code. The hook receives JSON on stdin containing `tool_name` and `tool_input` fields, and returns structured JSON output or uses exit codes to control execution:

- **Exit code 0**: Command is safe, proceed with execution
- **Exit code 2**: Command is blocked, Claude Code prevents execution and receives the reason

The hook configuration can be placed in any of the three Claude Code settings files:

- `~/.claude/settings.json` (user-global)
- `.claude/settings.json` (project-specific, committed)
- `.claude/settings.local.json` (project-specific, not committed)

DCG also provides a `dcg scan` subcommand that extracts executable command contexts from files and evaluates them using the same pattern engine, suitable for CI integration and repository auditing.

## Agent Compatibility

| Agent       | Hook Support                                                     |
| ----------- | ---------------------------------------------------------------- |
| Claude Code | Full PreToolUse hook support (primary target)                    |
| Aider       | No PreToolUse interception; use git pre-commit hook instead      |
| Codex CLI   | Post-execution hooks only; no pre-execution command interception |
| Continue    | No shell command interception hooks; use git pre-commit hook     |

For agents without PreToolUse support, install DCG as a git pre-commit hook for partial protection (covers git operations only).
