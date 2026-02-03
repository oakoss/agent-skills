#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code components: skills, agents, commands, hooks, and plugins.

Usage:
    uv run scripts/validate-component.py <type> <path>

Types:
    skill   - Validate SKILL.md file(s)
    agent   - Validate agent .md file(s)
    command - Validate command .md file(s)
    hook    - Validate hooks in settings.json file(s)
    plugin  - Validate plugin directory structure

Path accepts:
    - Direct file path: .claude/skills/my-skill/SKILL.md
    - Directory path:   .claude/skills/ (finds all matching files)
    - Glob pattern:     ".claude/skills/*/SKILL.md"

Examples:
    uv run scripts/validate-component.py skill .claude/skills/
    uv run scripts/validate-component.py agent .claude/agents/
    uv run scripts/validate-component.py command .claude/commands/
    uv run scripts/validate-component.py hook .claude/settings.json
    uv run scripts/validate-component.py plugin ./my-plugin
"""

import glob
import json
import os
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict[str, str] | None, str | None]:
    """Parse YAML frontmatter from content."""
    if not content.startswith("---"):
        return None, "YAML frontmatter must start with --- on line 1"

    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, "Invalid YAML frontmatter: missing closing ---"

    frontmatter = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, None


# =============================================================================
# Path Resolution Functions
# =============================================================================


def resolve_skill_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """Resolve path to SKILL.md files."""
    path = Path(path_arg)

    if path.is_file():
        if path.name != "SKILL.md":
            return [], f"Expected SKILL.md file, got: {path.name}"
        return [path], None

    if path.is_dir():
        skill_file = path / "SKILL.md"
        if skill_file.exists():
            return [skill_file], None

        skill_files = list(path.glob("*/SKILL.md"))
        if skill_files:
            return sorted(skill_files), None

        skill_files = list(path.glob("**/SKILL.md"))
        if skill_files:
            return sorted(skill_files), None

        return [], f"No SKILL.md files found in: {path}"

    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        skill_files = [Path(m) for m in matches if Path(m).name == "SKILL.md"]
        if skill_files:
            return sorted(skill_files), None
        return [], f"No SKILL.md files match pattern: {path_arg}"

    return [], f"Path not found: {path_arg}"


def resolve_agent_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """Resolve path to agent .md files."""
    path = Path(path_arg)

    if path.is_file():
        if not path.suffix == ".md":
            return [], f"Expected .md file, got: {path.name}"
        return [path], None

    if path.is_dir():
        agent_files = [f for f in path.glob("*.md") if f.name != "README.md"]
        if agent_files:
            return sorted(agent_files), None
        return [], f"No agent .md files found in: {path}"

    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        agent_files = [Path(m) for m in matches if m.endswith(".md") and not m.endswith("README.md")]
        if agent_files:
            return sorted(agent_files), None
        return [], f"No agent files match pattern: {path_arg}"

    return [], f"Path not found: {path_arg}"


def resolve_command_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """Resolve path to command .md files."""
    path = Path(path_arg)

    if path.is_file():
        if not path.suffix == ".md":
            return [], f"Expected .md file, got: {path.name}"
        return [path], None

    if path.is_dir():
        cmd_files = [f for f in path.rglob("*.md") if f.name != "README.md"]
        if cmd_files:
            return sorted(cmd_files), None
        return [], f"No command .md files found in: {path}"

    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        cmd_files = [Path(m) for m in matches if m.endswith(".md") and not m.endswith("README.md")]
        if cmd_files:
            return sorted(cmd_files), None
        return [], f"No command files match pattern: {path_arg}"

    return [], f"Path not found: {path_arg}"


def resolve_hook_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """Resolve path to settings.json files with hooks."""
    path = Path(path_arg)

    if path.is_file():
        if not path.suffix == ".json":
            return [], f"Expected .json file, got: {path.name}"
        return [path], None

    if path.is_dir():
        settings_files = list(path.glob("settings*.json"))
        if settings_files:
            return sorted(settings_files), None
        return [], f"No settings*.json files found in: {path}"

    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        settings_files = [Path(m) for m in matches if m.endswith(".json")]
        if settings_files:
            return sorted(settings_files), None
        return [], f"No settings files match pattern: {path_arg}"

    return [], f"Path not found: {path_arg}"


def resolve_plugin_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """Resolve path to plugin directories."""
    path = Path(path_arg)

    if path.is_dir():
        if (path / ".claude-plugin").exists():
            return [path], None

        plugin_dirs = [
            d for d in path.iterdir()
            if d.is_dir() and (d / ".claude-plugin").exists()
        ]
        if plugin_dirs:
            return sorted(plugin_dirs), None

        return [], f"No plugins found in: {path} (plugins must have .claude-plugin/ directory)"

    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        plugin_dirs = [
            Path(m) for m in matches
            if Path(m).is_dir() and (Path(m) / ".claude-plugin").exists()
        ]
        if plugin_dirs:
            return sorted(plugin_dirs), None
        return [], f"No plugins match pattern: {path_arg}"

    return [], f"Path not found: {path_arg}"


# =============================================================================
# Validation Functions
# =============================================================================


def validate_skill(path: Path) -> tuple[list[str], list[str]]:
    """Validate a SKILL.md file."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except PermissionError:
        return [f"Permission denied: {path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    lines = content.split("\n")
    line_count = len(lines)

    # Frontmatter
    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        if "name" not in frontmatter:
            errors.append("Missing required field: 'name'")
        else:
            name = frontmatter["name"]
            if len(name) > 64:
                errors.append(f"'name' exceeds 64 chars ({len(name)})")
            elif not re.match(r"^[a-z0-9:-]+$", name):
                warnings.append("'name' should use lowercase letters, numbers, hyphens, colons only")

        if "description" not in frontmatter:
            errors.append("Missing required field: 'description'")
        elif len(frontmatter["description"]) > 1024:
            errors.append("'description' exceeds 1024 chars")
        elif "use when" not in frontmatter["description"].lower() and "use for" not in frontmatter["description"].lower():
            warnings.append("Description should include 'Use when...' trigger phrases")

    # Line count
    if line_count > 500:
        errors.append(f"SKILL.md is {line_count} lines (max 500)")
    elif line_count > 400:
        warnings.append(f"SKILL.md is {line_count} lines (consider splitting at ~400)")

    # Code blocks
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code = not in_code

    # Required sections
    content_lower = content.lower()
    if "## common mistakes" not in content_lower:
        warnings.append("Missing '## Common Mistakes' section")
    if "## delegation" not in content_lower:
        warnings.append("Missing '## Delegation' section")

    # Check for reference.md link if it exists
    skill_dir = path.parent
    ref_path = skill_dir / "reference.md"
    if ref_path.exists() and "[reference.md]" not in content:
        warnings.append("reference.md exists but is not linked in SKILL.md")

    return errors, warnings


def validate_agent(path: Path) -> tuple[list[str], list[str]]:
    """Validate an agent .md file."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except PermissionError:
        return [f"Permission denied: {path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    lines = content.split("\n")

    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        if "name" not in frontmatter:
            errors.append("Missing required field: 'name'")
        if "description" not in frontmatter:
            errors.append("Missing required field: 'description'")
        else:
            desc = frontmatter["description"].lower()
            if "proactively" not in desc and "use when" not in desc:
                warnings.append("Description should include trigger phrases ('Use proactively' or 'Use when')")

        if "tools" not in frontmatter:
            warnings.append("Consider adding 'tools' to restrict agent capabilities")

        if "model" in frontmatter:
            valid_models = ["haiku", "sonnet", "opus", "inherit"]
            if frontmatter["model"] not in valid_models:
                warnings.append(f"Model '{frontmatter['model']}' - expected: {valid_models}")

    # Line count
    line_count = len(lines)
    if line_count > 500:
        errors.append(f"Agent file is {line_count} lines (max 500)")
    elif line_count > 300:
        warnings.append(f"Agent file is {line_count} lines (consider splitting)")

    # Code blocks
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code = not in_code

    # Check for output format section (good practice)
    if "## output" not in content.lower():
        warnings.append("Consider adding '## Output Format' section")

    return errors, warnings


def validate_command(path: Path) -> tuple[list[str], list[str]]:
    """Validate a command .md file."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except PermissionError:
        return [f"Permission denied: {path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    lines = content.split("\n")

    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        if "description" not in frontmatter:
            errors.append("Missing required field: 'description'")

        # Invalid fields check
        invalid_fields = ["name", "category", "tags"]
        for field in invalid_fields:
            if field in frontmatter:
                warnings.append(f"Invalid field '{field}' - will be ignored (name is inferred from filename)")

        # Check if using bash execution without allowed-tools
        if "!" in content and "`" in content:
            if "allowed-tools" not in frontmatter:
                warnings.append("Using !`command` syntax but missing 'allowed-tools' with Bash permission")

    # Line count
    line_count = len(lines)
    if line_count > 500:
        errors.append(f"Command file is {line_count} lines (max 500)")
    elif line_count > 200:
        warnings.append(f"Command file is {line_count} lines (consider splitting into smaller commands)")

    # Code blocks
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code = not in_code

    # Check for steps or instructions
    content_lower = content.lower()
    has_steps = (
        "## steps" in content_lower
        or "## instructions" in content_lower
        or "**steps**" in content_lower
        or "**instructions**" in content_lower
    )
    if not has_steps:
        warnings.append("Consider adding '## Steps' or '## Instructions' section")

    # Check for $ARGUMENTS handling
    if "$ARGUMENTS" in content or "$1" in content:
        if "argument-hint" not in (frontmatter or {}):
            warnings.append("Using $ARGUMENTS but missing 'argument-hint' in frontmatter")

    return errors, warnings


def validate_hook(path: Path) -> tuple[list[str], list[str]]:
    """Validate hooks in a settings.json file."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except PermissionError:
        return [f"Permission denied: {path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    try:
        settings = json.loads(content)
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"], []

    if "hooks" not in settings:
        return ["No 'hooks' key found in settings"], []

    hooks = settings["hooks"]
    if not isinstance(hooks, dict):
        return ["'hooks' must be an object"], []

    valid_events = {
        "PreToolUse", "PostToolUse", "PermissionRequest",
        "UserPromptSubmit", "Notification", "Stop", "SubagentStop",
        "SessionStart", "SessionEnd", "PreCompact"
    }
    events_with_matcher = {"PreToolUse", "PostToolUse", "PermissionRequest", "Notification", "PreCompact", "SessionStart"}
    valid_hook_types = {"command", "prompt"}

    for event, matchers in hooks.items():
        if event not in valid_events:
            errors.append(f"Invalid event type: '{event}'. Valid: {sorted(valid_events)}")
            continue

        if not isinstance(matchers, list):
            errors.append(f"Event '{event}' must have an array of matchers")
            continue

        for i, matcher_config in enumerate(matchers):
            if not isinstance(matcher_config, dict):
                errors.append(f"Event '{event}' matcher {i}: must be an object")
                continue

            # Check matcher field
            has_matcher = "matcher" in matcher_config
            if event in events_with_matcher and not has_matcher:
                warnings.append(f"Event '{event}' matcher {i}: consider adding 'matcher' field")

            # Check hooks array
            if "hooks" not in matcher_config:
                errors.append(f"Event '{event}' matcher {i}: missing 'hooks' array")
                continue

            hook_list = matcher_config["hooks"]
            if not isinstance(hook_list, list):
                errors.append(f"Event '{event}' matcher {i}: 'hooks' must be an array")
                continue

            for j, hook in enumerate(hook_list):
                if not isinstance(hook, dict):
                    errors.append(f"Event '{event}' matcher {i} hook {j}: must be an object")
                    continue

                hook_type = hook.get("type")
                if not hook_type:
                    errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'type'")
                elif hook_type not in valid_hook_types:
                    errors.append(f"Event '{event}' matcher {i} hook {j}: invalid type '{hook_type}'. Valid: {valid_hook_types}")

                if hook_type == "command":
                    if "command" not in hook:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'command'")
                    else:
                        cmd = hook["command"]
                        if "$CLAUDE_PROJECT_DIR" in cmd and '"$CLAUDE_PROJECT_DIR"' not in cmd:
                            warnings.append(f"Event '{event}' matcher {i} hook {j}: $CLAUDE_PROJECT_DIR should be quoted")

                elif hook_type == "prompt":
                    if "prompt" not in hook:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'prompt'")
                    if event not in {"Stop", "SubagentStop", "UserPromptSubmit", "PreToolUse", "PermissionRequest"}:
                        warnings.append(f"Event '{event}' matcher {i} hook {j}: prompt hooks work best with Stop/SubagentStop")

                if "timeout" in hook:
                    timeout = hook["timeout"]
                    if not isinstance(timeout, (int, float)):
                        errors.append(f"Event '{event}' matcher {i} hook {j}: timeout must be a number")
                    elif timeout <= 0:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: timeout must be positive")
                    elif timeout > 300:
                        warnings.append(f"Event '{event}' matcher {i} hook {j}: timeout {timeout}s is very long")

    return errors, warnings


def validate_plugin(path: Path) -> tuple[list[str], list[str]]:
    """Validate a plugin directory structure."""
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = path / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        errors.append("Missing .claude-plugin/plugin.json")
        return errors, warnings

    try:
        manifest = json.loads(manifest_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in plugin.json: {e}")
        return errors, warnings
    except PermissionError:
        return [f"Permission denied: {manifest_path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    # Required fields
    if "name" not in manifest:
        errors.append("Missing required field: 'name'")
    else:
        name = manifest["name"]
        if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
            warnings.append(f"Name '{name}' should be kebab-case (lowercase, hyphens)")

    # Recommended fields
    if "version" not in manifest:
        warnings.append("Consider adding 'version' field (semver)")
    else:
        version = manifest["version"]
        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", version):
            warnings.append(f"Version '{version}' should follow semver (MAJOR.MINOR.PATCH)")

    if "description" not in manifest:
        warnings.append("Consider adding 'description' field")

    # Check component paths
    component_paths = ["commands", "agents", "skills", "hooks", "mcpServers", "lspServers", "outputStyles"]
    for comp in component_paths:
        if comp in manifest:
            value = manifest[comp]
            if isinstance(value, str) and not value.startswith("./"):
                errors.append(f"Path '{comp}' must be relative, starting with './'")
            elif isinstance(value, list):
                for comp_path in value:
                    if isinstance(comp_path, str) and not comp_path.startswith("./"):
                        errors.append(f"Path in '{comp}' must be relative: {comp_path}")

    # Check default directories exist
    default_dirs = ["commands", "agents", "skills", "hooks"]
    found_components = False
    for dir_name in default_dirs:
        dir_path = path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            found_components = True
            files = list(dir_path.glob("*"))
            if not files:
                warnings.append(f"Directory '{dir_name}/' exists but is empty")

    # Check for components incorrectly placed in .claude-plugin/
    claude_plugin_dir = path / ".claude-plugin"
    for dir_name in default_dirs:
        if (claude_plugin_dir / dir_name).exists():
            errors.append(f"'{dir_name}/' found inside .claude-plugin/ - move to plugin root")

    # Check scripts directory
    scripts_path = path / "scripts"
    if scripts_path.exists():
        for script in scripts_path.glob("*"):
            if script.is_file() and script.suffix in [".sh", ".py", ".js"]:
                if not os.access(script, os.X_OK):
                    warnings.append(f"Script not executable: {script.name} (run chmod +x)")

    if not found_components and "commands" not in manifest and "agents" not in manifest:
        warnings.append("No component directories found (commands/, agents/, skills/, hooks/)")

    return errors, warnings


# =============================================================================
# Output Functions
# =============================================================================


def print_result(name: str, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single component."""
    if errors:
        print(f"❌ {name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {name}: passed")


def get_display_name(path: Path, component_type: str) -> str:
    """Get display name for a component."""
    if component_type == "skill":
        return path.parent.name
    if component_type == "plugin":
        return path.name
    return path.stem


# =============================================================================
# Main
# =============================================================================


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: uv run scripts/validate-component.py <type> <path>")
        print()
        print("Types: skill, agent, command, hook, plugin")
        print()
        print("Path accepts:")
        print("  - File path:    .claude/skills/my-skill/SKILL.md")
        print("  - Directory:    .claude/skills/")
        print("  - Glob pattern: '.claude/skills/*/SKILL.md'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-component.py skill .claude/skills/")
        print("  uv run scripts/validate-component.py agent .claude/agents/")
        print("  uv run scripts/validate-component.py command .claude/commands/")
        print("  uv run scripts/validate-component.py hook .claude/settings.json")
        print("  uv run scripts/validate-component.py plugin ./my-plugin")
        return 1

    component_type = sys.argv[1].lower()
    path_arg = sys.argv[2]

    resolvers = {
        "skill": resolve_skill_paths,
        "agent": resolve_agent_paths,
        "command": resolve_command_paths,
        "hook": resolve_hook_paths,
        "plugin": resolve_plugin_paths,
    }

    validators = {
        "skill": validate_skill,
        "agent": validate_agent,
        "command": validate_command,
        "hook": validate_hook,
        "plugin": validate_plugin,
    }

    if component_type not in validators:
        print(f"❌ Unknown type: {component_type}")
        print(f"Valid types: {list(validators.keys())}")
        return 1

    # Resolve paths
    paths, error = resolvers[component_type](path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not paths:
        print(f"❌ No {component_type}s found to validate")
        return 1

    validator = validators[component_type]

    # Single file - verbose output
    if len(paths) == 1:
        path = paths[0]
        errors, warnings = validator(path)

        if errors:
            print(f"❌ {component_type.title()} validation FAILED\n")
            print("Errors:")
            for err in errors:
                print(f"  ✗ {err}")
            print()

        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
            print()

        if not errors and not warnings:
            print(f"✓ {component_type.title()} validation passed")
        elif not errors:
            print(f"✓ {component_type.title()} valid (with warnings)")

        return 1 if errors else 0

    # Multiple files - summary output
    print(f"Validating {len(paths)} {component_type}(s)...\n")

    total_errors = 0
    total_warnings = 0
    failed = []

    for path in paths:
        errors, warnings = validator(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        name = get_display_name(path, component_type)
        if errors:
            failed.append(name)

        print_result(name, errors, warnings, verbose=bool(errors))

    # Summary
    print()
    if failed:
        print(f"❌ {len(failed)} {component_type}(s) failed: {', '.join(failed)}")
    else:
        print(f"✓ All {len(paths)} {component_type}(s) passed")

    if total_warnings:
        print(f"   {total_warnings} total warning(s)")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
