#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code hooks in settings.json files.

Usage:
    uv run scripts/validate-hook.py <path>              # settings.json file
    uv run scripts/validate-hook.py .claude/            # auto-finds settings.json

Examples:
    uv run scripts/validate-hook.py .claude/settings.json
    uv run scripts/validate-hook.py .claude/settings.local.json
    uv run scripts/validate-hook.py .claude/
"""

import glob
import json
import sys
from pathlib import Path


VALID_EVENTS = {
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "UserPromptSubmit",
    "Notification",
    "Stop",
    "SubagentStop",
    "SessionStart",
    "SessionEnd",
    "PreCompact",
}

EVENTS_WITH_MATCHER = {"PreToolUse", "PostToolUse", "PermissionRequest", "Notification", "PreCompact", "SessionStart"}

VALID_HOOK_TYPES = {"command", "prompt"}


def resolve_settings_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """
    Resolve a path argument to a list of settings.json files.

    Handles:
        - Direct file path: .claude/settings.json
        - Directory path: .claude/ (finds settings*.json files)
        - Glob pattern: .claude/settings*.json

    Returns:
        Tuple of (list of Path objects, error message if any)
    """
    path = Path(path_arg)

    # Case 1: Direct file path
    if path.is_file():
        if not path.suffix == ".json":
            return [], f"Expected .json file, got: {path.name}"
        return [path], None

    # Case 2: Directory - find settings*.json files
    if path.is_dir():
        settings_files = list(path.glob("settings*.json"))
        if settings_files:
            return sorted(settings_files), None
        return [], f"No settings*.json files found in: {path}"

    # Case 3: Glob pattern
    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        settings_files = [Path(m) for m in matches if m.endswith(".json")]
        if settings_files:
            return sorted(settings_files), None
        return [], f"No settings files match pattern: {path_arg}"

    # Path doesn't exist
    return [], f"Path not found: {path_arg}"


def validate_hooks(path: Path) -> tuple[list[str], list[str]]:
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

    for event, matchers in hooks.items():
        # Validate event type
        if event not in VALID_EVENTS:
            errors.append(f"Invalid event type: '{event}'. Valid: {sorted(VALID_EVENTS)}")
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
            if event in EVENTS_WITH_MATCHER and not has_matcher:
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

                # Validate hook type
                hook_type = hook.get("type")
                if not hook_type:
                    errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'type'")
                elif hook_type not in VALID_HOOK_TYPES:
                    errors.append(f"Event '{event}' matcher {i} hook {j}: invalid type '{hook_type}'. Valid: {VALID_HOOK_TYPES}")

                # Validate command or prompt
                if hook_type == "command":
                    if "command" not in hook:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'command'")
                    else:
                        cmd = hook["command"]
                        # Check for common issues
                        if "$CLAUDE_PROJECT_DIR" in cmd and '"$CLAUDE_PROJECT_DIR"' not in cmd:
                            warnings.append(f"Event '{event}' matcher {i} hook {j}: $CLAUDE_PROJECT_DIR should be quoted")

                elif hook_type == "prompt":
                    if "prompt" not in hook:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: missing 'prompt'")
                    # Prompt hooks only work well with certain events
                    if event not in {"Stop", "SubagentStop", "UserPromptSubmit", "PreToolUse", "PermissionRequest"}:
                        warnings.append(f"Event '{event}' matcher {i} hook {j}: prompt hooks work best with Stop/SubagentStop")

                # Check timeout
                if "timeout" in hook:
                    timeout = hook["timeout"]
                    if not isinstance(timeout, (int, float)):
                        errors.append(f"Event '{event}' matcher {i} hook {j}: timeout must be a number")
                    elif timeout <= 0:
                        errors.append(f"Event '{event}' matcher {i} hook {j}: timeout must be positive")
                    elif timeout > 300:
                        warnings.append(f"Event '{event}' matcher {i} hook {j}: timeout {timeout}s is very long")

    return errors, warnings


def print_result(path: Path, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single settings file."""
    file_name = path.name

    if errors:
        print(f"❌ {file_name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {file_name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {file_name}: passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate-hook.py <path>")
        print()
        print("Accepts:")
        print("  - File path:    .claude/settings.json")
        print("  - Directory:    .claude/ (finds settings*.json)")
        print("  - Glob pattern: '.claude/settings*.json'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-hook.py .claude/settings.json")
        print("  uv run scripts/validate-hook.py .claude/")
        return 1

    path_arg = sys.argv[1]
    settings_paths, error = resolve_settings_paths(path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not settings_paths:
        print("❌ No settings files found to validate")
        return 1

    # Validate all files
    total_errors = 0
    total_warnings = 0
    failed_files = []

    # Single file - verbose output
    if len(settings_paths) == 1:
        path = settings_paths[0]
        errors, warnings = validate_hooks(path)

        if errors:
            print("❌ Hook validation FAILED\n")
            print("Errors:")
            for error in errors:
                print(f"  ✗ {error}")
            print()

        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
            print()

        if not errors and not warnings:
            print("✓ Hook validation passed")
        elif not errors:
            print("✓ Hooks valid (with warnings)")

        return 1 if errors else 0

    # Multiple files - summary output
    print(f"Validating {len(settings_paths)} settings file(s)...\n")

    for path in settings_paths:
        errors, warnings = validate_hooks(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            failed_files.append(path.name)

        print_result(path, errors, warnings, verbose=bool(errors))

    # Summary
    print()
    if failed_files:
        print(f"❌ {len(failed_files)} file(s) failed: {', '.join(failed_files)}")
    else:
        print(f"✓ All {len(settings_paths)} file(s) passed")

    if total_warnings:
        print(f"   {total_warnings} total warning(s)")

    return 1 if failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
