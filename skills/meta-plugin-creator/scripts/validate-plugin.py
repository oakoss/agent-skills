#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code plugin structure against best practices.

Usage:
    uv run scripts/validate-plugin.py <path>           # Single plugin directory
    uv run scripts/validate-plugin.py <glob-pattern>   # Multiple plugins

Examples:
    uv run scripts/validate-plugin.py ./my-plugin
    uv run scripts/validate-plugin.py ./plugins/
    uv run scripts/validate-plugin.py "./plugins/*"
"""

import glob
import json
import os
import re
import sys
from pathlib import Path


def resolve_plugin_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """
    Resolve a path argument to a list of plugin directories.

    Handles:
        - Direct plugin directory: ./my-plugin (has .claude-plugin/)
        - Parent directory: ./plugins/ (finds all plugin dirs)
        - Glob pattern: ./plugins/*

    Returns:
        Tuple of (list of Path objects, error message if any)
    """
    path = Path(path_arg)

    # Case 1: Direct plugin directory
    if path.is_dir():
        # Check if this is a plugin (has .claude-plugin/)
        if (path / ".claude-plugin").exists():
            return [path], None

        # Check if this is a parent directory containing plugins
        plugin_dirs = [
            d for d in path.iterdir()
            if d.is_dir() and (d / ".claude-plugin").exists()
        ]
        if plugin_dirs:
            return sorted(plugin_dirs), None

        return [], f"No plugins found in: {path} (plugins must have .claude-plugin/ directory)"

    # Case 2: Glob pattern
    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        plugin_dirs = [
            Path(m) for m in matches
            if Path(m).is_dir() and (Path(m) / ".claude-plugin").exists()
        ]
        if plugin_dirs:
            return sorted(plugin_dirs), None
        return [], f"No plugins match pattern: {path_arg}"

    # Path doesn't exist
    return [], f"Path not found: {path_arg}"


def validate_plugin(plugin_path: Path) -> tuple[list[str], list[str]]:
    """Validate a plugin directory structure."""
    errors: list[str] = []
    warnings: list[str] = []

    # Check for .claude-plugin/plugin.json
    manifest_path = plugin_path / ".claude-plugin" / "plugin.json"
    if not manifest_path.exists():
        errors.append("Missing .claude-plugin/plugin.json")
        return errors, warnings

    # Parse manifest
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
        # Check kebab-case
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

    # Check default directories exist (at least one)
    default_dirs = ["commands", "agents", "skills", "hooks"]
    found_components = False
    for dir_name in default_dirs:
        dir_path = plugin_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            found_components = True
            # Check for content
            files = list(dir_path.glob("*"))
            if not files:
                warnings.append(f"Directory '{dir_name}/' exists but is empty")

    # Check for components incorrectly placed in .claude-plugin/
    claude_plugin_dir = plugin_path / ".claude-plugin"
    for dir_name in default_dirs:
        if (claude_plugin_dir / dir_name).exists():
            errors.append(f"'{dir_name}/' found inside .claude-plugin/ - move to plugin root")

    # Check for MCP/LSP config files
    mcp_path = plugin_path / ".mcp.json"
    lsp_path = plugin_path / ".lsp.json"

    if mcp_path.exists():
        try:
            mcp_config = json.loads(mcp_path.read_text())
            if "mcpServers" in mcp_config:
                for server_name, config in mcp_config["mcpServers"].items():
                    if "command" in config:
                        cmd = config["command"]
                        # Check for CLAUDE_PLUGIN_ROOT usage
                        if "/" in cmd and "${CLAUDE_PLUGIN_ROOT}" not in cmd and not cmd.startswith("npx"):
                            warnings.append(f"MCP server '{server_name}': use ${{CLAUDE_PLUGIN_ROOT}} for plugin paths")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in .mcp.json")

    if lsp_path.exists():
        try:
            lsp_config = json.loads(lsp_path.read_text())
            for lang, config in lsp_config.items():
                if "command" not in config:
                    errors.append(f"LSP '{lang}': missing required 'command' field")
                if "extensionToLanguage" not in config:
                    errors.append(f"LSP '{lang}': missing required 'extensionToLanguage' field")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in .lsp.json")

    # Check hooks config
    hooks_path = plugin_path / "hooks" / "hooks.json"
    if hooks_path.exists():
        try:
            hooks_config = json.loads(hooks_path.read_text())
            if "hooks" in hooks_config:
                for event, matchers in hooks_config["hooks"].items():
                    if isinstance(matchers, list):
                        for matcher in matchers:
                            if "hooks" in matcher:
                                for hook in matcher["hooks"]:
                                    if hook.get("type") == "command":
                                        cmd = hook.get("command", "")
                                        if "/" in cmd and "${CLAUDE_PLUGIN_ROOT}" not in cmd:
                                            warnings.append(f"Hook command should use ${{CLAUDE_PLUGIN_ROOT}}: {cmd[:50]}...")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in hooks/hooks.json")

    # Check scripts directory
    scripts_path = plugin_path / "scripts"
    if scripts_path.exists():
        for script in scripts_path.glob("*"):
            if script.is_file() and script.suffix in [".sh", ".py", ".js"]:
                # Check if executable
                if not os.access(script, os.X_OK):
                    warnings.append(f"Script not executable: {script.name} (run chmod +x)")

    if not found_components and "commands" not in manifest and "agents" not in manifest:
        warnings.append("No component directories found (commands/, agents/, skills/, hooks/)")

    return errors, warnings


def print_result(path: Path, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single plugin."""
    plugin_name = path.name

    if errors:
        print(f"❌ {plugin_name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {plugin_name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {plugin_name}: passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate-plugin.py <path>")
        print()
        print("Accepts:")
        print("  - Plugin dir:   ./my-plugin (must have .claude-plugin/)")
        print("  - Parent dir:   ./plugins/ (finds all plugins)")
        print("  - Glob pattern: './plugins/*'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-plugin.py ./my-plugin")
        print("  uv run scripts/validate-plugin.py ./plugins/")
        return 1

    path_arg = sys.argv[1]
    plugin_paths, error = resolve_plugin_paths(path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not plugin_paths:
        print("❌ No plugins found to validate")
        return 1

    # Validate all plugins
    total_errors = 0
    total_warnings = 0
    failed_plugins = []

    # Single plugin - verbose output
    if len(plugin_paths) == 1:
        path = plugin_paths[0]
        errors, warnings = validate_plugin(path)

        if errors:
            print("❌ Plugin validation FAILED\n")
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
            print("✓ Plugin validation passed")
        elif not errors:
            print("✓ Plugin valid (with warnings)")

        return 1 if errors else 0

    # Multiple plugins - summary output
    print(f"Validating {len(plugin_paths)} plugin(s)...\n")

    for path in plugin_paths:
        errors, warnings = validate_plugin(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            failed_plugins.append(path.name)

        print_result(path, errors, warnings, verbose=bool(errors))

    # Summary
    print()
    if failed_plugins:
        print(f"❌ {len(failed_plugins)} plugin(s) failed: {', '.join(failed_plugins)}")
    else:
        print(f"✓ All {len(plugin_paths)} plugin(s) passed")

    if total_warnings:
        print(f"   {total_warnings} total warning(s)")

    return 1 if failed_plugins else 0


if __name__ == "__main__":
    sys.exit(main())
