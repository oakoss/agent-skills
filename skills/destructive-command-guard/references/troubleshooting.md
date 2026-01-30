---
title: Troubleshooting and FAQ
description: Fixing common DCG issues and answers to frequently asked questions
tags: [troubleshooting, FAQ, debugging, bypass]
---

# Troubleshooting and FAQ

## Troubleshooting

### Hook Not Blocking Commands

1. Verify `~/.claude/settings.json` has hook configuration
2. Restart Claude Code
3. Test manually:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | dcg
```

### Hook Blocking Safe Commands

1. Check if there is an edge case not covered
2. File a GitHub issue
3. Temporary bypass: `DCG_BYPASS=1` or run command manually

## FAQ

**Q: Why block `git branch -D` but allow `git branch -d`?**

Lowercase `-d` only deletes branches fully merged. Uppercase `-D` force-deletes regardless of merge status, potentially losing commits.

**Q: Why is `git push --force-with-lease` allowed?**

Force-with-lease refuses to push if the remote has commits you have not seen, preventing accidental overwrites.

**Q: Why block all `rm -rf` outside temp directories?**

Recursive forced deletion is extremely dangerous. A typo or wrong variable can delete critical files. Temp directories are designed to be ephemeral.

**Q: What if I really need to run a blocked command?**

DCG instructs the agent to ask for permission. Run the command manually in a separate terminal after making a conscious decision.

## Integration with Other Tools

| Tool            | Integration                                       |
| --------------- | ------------------------------------------------- |
| **Claude Code** | Native PreToolUse hook                            |
| **Agent Mail**  | Agents can report blocked commands to coordinator |
| **BV**          | Flag tasks that repeatedly trigger DCG            |
| **CASS**        | Search DCG block patterns across sessions         |
| **RU**          | DCG protects agent-sweep from destructive commits |
