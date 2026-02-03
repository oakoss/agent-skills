#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code agent structure against best practices.

Usage:
    uv run scripts/validate-agent.py <path>           # Single file or directory
    uv run scripts/validate-agent.py <glob-pattern>   # Multiple agents
    uv run scripts/validate-agent.py .claude/agents/  # All agents in directory

Examples:
    uv run scripts/validate-agent.py .claude/agents/my-agent.md
    uv run scripts/validate-agent.py .claude/agents/
    uv run scripts/validate-agent.py ".claude/agents/*.md"
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


def resolve_agent_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """
    Resolve a path argument to a list of agent .md files.

    Handles:
        - Direct file path: .claude/agents/my-agent.md
        - Directory path: .claude/agents/ (finds all .md files)
        - Glob pattern: .claude/agents/*.md

    Returns:
        Tuple of (list of Path objects, error message if any)
    """
    path = Path(path_arg)

    # Case 1: Direct file path
    if path.is_file():
        if not path.suffix == ".md":
            return [], f"Expected .md file, got: {path.name}"
        return [path], None

    # Case 2: Directory - find all .md files
    if path.is_dir():
        agent_files = [f for f in path.glob("*.md") if f.name != "README.md"]
        if agent_files:
            return sorted(agent_files), None
        return [], f"No agent .md files found in: {path}"

    # Case 3: Glob pattern
    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        agent_files = [Path(m) for m in matches if m.endswith(".md") and not m.endswith("README.md")]
        if agent_files:
            return sorted(agent_files), None
        return [], f"No agent files match pattern: {path_arg}"

    # Path doesn't exist
    return [], f"Path not found: {path_arg}"


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

    # Frontmatter validation
    frontmatter, fm_error = parse_frontmatter(content)
    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        # Required fields
        if "name" not in frontmatter:
            errors.append("Missing required field: 'name'")
        if "description" not in frontmatter:
            errors.append("Missing required field: 'description'")
        else:
            desc = frontmatter["description"].lower()
            if "proactively" not in desc and "use when" not in desc:
                warnings.append("Description should include trigger phrases ('Use proactively' or 'Use when')")

        # Optional but recommended
        if "tools" not in frontmatter:
            warnings.append("Consider adding 'tools' to restrict agent capabilities (omit to inherit all)")

        # Validate model if present
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

    # Code block language specifiers
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            if not in_code and line.strip() == "```":
                errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code = not in_code

    # Check for output format section (good practice for reviewers)
    content_lower = content.lower()
    if "## output" not in content_lower:
        warnings.append("Consider adding '## Output Format' section")

    return errors, warnings


def print_result(path: Path, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single agent."""
    agent_name = path.stem

    if errors:
        print(f"❌ {agent_name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {agent_name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {agent_name}: passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate-agent.py <path>")
        print()
        print("Accepts:")
        print("  - File path:    .claude/agents/my-agent.md")
        print("  - Directory:    .claude/agents/")
        print("  - Glob pattern: '.claude/agents/*.md'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-agent.py .claude/agents/code-reviewer.md")
        print("  uv run scripts/validate-agent.py .claude/agents/")
        return 1

    path_arg = sys.argv[1]
    agent_paths, error = resolve_agent_paths(path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not agent_paths:
        print("❌ No agents found to validate")
        return 1

    # Validate all agents
    total_errors = 0
    total_warnings = 0
    failed_agents = []

    # Single agent - verbose output
    if len(agent_paths) == 1:
        path = agent_paths[0]
        errors, warnings = validate_agent(path)

        if errors:
            print("❌ Agent validation FAILED\n")
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
            print("✓ Agent validation passed")
        elif not errors:
            print("✓ Agent valid (with warnings)")

        return 1 if errors else 0

    # Multiple agents - summary output
    print(f"Validating {len(agent_paths)} agent(s)...\n")

    for path in agent_paths:
        errors, warnings = validate_agent(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            failed_agents.append(path.stem)

        print_result(path, errors, warnings, verbose=bool(errors))

    # Summary
    print()
    if failed_agents:
        print(f"❌ {len(failed_agents)} agent(s) failed: {', '.join(failed_agents)}")
    else:
        print(f"✓ All {len(agent_paths)} agent(s) passed")

    if total_warnings:
        print(f"   {total_warnings} total warning(s)")

    return 1 if failed_agents else 0


if __name__ == "__main__":
    sys.exit(main())
