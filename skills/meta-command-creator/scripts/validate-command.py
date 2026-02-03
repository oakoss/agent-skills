#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code slash command structure against best practices.

Usage:
    uv run scripts/validate-command.py <path>           # Single file or directory
    uv run scripts/validate-command.py <glob-pattern>   # Multiple commands
    uv run scripts/validate-command.py .claude/commands/ # All commands in directory

Examples:
    uv run scripts/validate-command.py .claude/commands/my-command.md
    uv run scripts/validate-command.py .claude/commands/
    uv run scripts/validate-command.py ".claude/commands/**/*.md"
"""

import glob
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


def resolve_command_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """
    Resolve a path argument to a list of command .md files.

    Handles:
        - Direct file path: .claude/commands/my-command.md
        - Directory path: .claude/commands/ (finds all .md files recursively)
        - Glob pattern: .claude/commands/**/*.md

    Returns:
        Tuple of (list of Path objects, error message if any)
    """
    path = Path(path_arg)

    # Case 1: Direct file path
    if path.is_file():
        if not path.suffix == ".md":
            return [], f"Expected .md file, got: {path.name}"
        return [path], None

    # Case 2: Directory - find all .md files recursively
    if path.is_dir():
        cmd_files = [f for f in path.rglob("*.md") if f.name != "README.md"]
        if cmd_files:
            return sorted(cmd_files), None
        return [], f"No command .md files found in: {path}"

    # Case 3: Glob pattern
    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        cmd_files = [Path(m) for m in matches if m.endswith(".md") and not m.endswith("README.md")]
        if cmd_files:
            return sorted(cmd_files), None
        return [], f"No command files match pattern: {path_arg}"

    # Path doesn't exist
    return [], f"Path not found: {path_arg}"


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

    # Frontmatter validation
    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        # Required field
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

    # Code block language specifiers
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code = not in_code

    # Check for steps or instructions (## or ** format)
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


def print_result(path: Path, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single command."""
    # Use relative path from .claude/commands for display
    try:
        rel_path = path.relative_to(Path(".claude/commands"))
        cmd_name = str(rel_path.with_suffix(""))
    except ValueError:
        cmd_name = path.stem

    if errors:
        print(f"❌ {cmd_name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {cmd_name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {cmd_name}: passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate-command.py <path>")
        print()
        print("Accepts:")
        print("  - File path:    .claude/commands/my-command.md")
        print("  - Directory:    .claude/commands/")
        print("  - Glob pattern: '.claude/commands/**/*.md'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-command.py .claude/commands/commit.md")
        print("  uv run scripts/validate-command.py .claude/commands/")
        return 1

    path_arg = sys.argv[1]
    cmd_paths, error = resolve_command_paths(path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not cmd_paths:
        print("❌ No commands found to validate")
        return 1

    # Validate all commands
    total_errors = 0
    total_warnings = 0
    failed_cmds = []

    # Single command - verbose output
    if len(cmd_paths) == 1:
        path = cmd_paths[0]
        errors, warnings = validate_command(path)

        if errors:
            print("❌ Command validation FAILED\n")
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
            print("✓ Command validation passed")
        elif not errors:
            print("✓ Command valid (with warnings)")

        return 1 if errors else 0

    # Multiple commands - summary output
    print(f"Validating {len(cmd_paths)} command(s)...\n")

    for path in cmd_paths:
        errors, warnings = validate_command(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            failed_cmds.append(path.stem)

        print_result(path, errors, warnings, verbose=bool(errors))

    # Summary
    print()
    if failed_cmds:
        print(f"❌ {len(failed_cmds)} command(s) failed: {', '.join(failed_cmds)}")
    else:
        print(f"✓ All {len(cmd_paths)} command(s) passed")

    if total_warnings:
        print(f"   {total_warnings} total warning(s)")

    return 1 if failed_cmds else 0


if __name__ == "__main__":
    sys.exit(main())
