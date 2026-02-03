#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# ///
"""
Validate Claude Code skill structure against best practices.

Usage:
    uv run scripts/validate-skill.py <path>           # Single file or directory
    uv run scripts/validate-skill.py <glob-pattern>   # Multiple skills
    uv run scripts/validate-skill.py .claude/skills/  # All skills in directory

Examples:
    uv run scripts/validate-skill.py .claude/skills/my-skill/SKILL.md
    uv run scripts/validate-skill.py .claude/skills/my-skill/
    uv run scripts/validate-skill.py ".claude/skills/*/SKILL.md"
    uv run scripts/validate-skill.py .claude/skills/
"""

import glob
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> tuple[dict[str, str] | None, str | None]:
    """
    Parse YAML frontmatter from content.
    Returns (frontmatter_dict, error_message).
    """
    if not content.startswith("---"):
        return None, "YAML frontmatter must start with --- on line 1"

    # Find closing ---
    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, "Invalid YAML frontmatter: missing closing ---"

    # Parse simple key: value pairs
    frontmatter = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, None


def resolve_skill_paths(path_arg: str) -> tuple[list[Path], str | None]:
    """
    Resolve a path argument to a list of SKILL.md files.

    Handles:
        - Direct file path: .claude/skills/my-skill/SKILL.md
        - Directory path: .claude/skills/my-skill/ (finds SKILL.md inside)
        - Parent directory: .claude/skills/ (finds all */SKILL.md)
        - Glob pattern: .claude/skills/*/SKILL.md

    Returns:
        Tuple of (list of Path objects, error message if any)
    """
    path = Path(path_arg)

    # Case 1: Direct file path
    if path.is_file():
        if path.name != "SKILL.md":
            return [], f"Expected SKILL.md file, got: {path.name}"
        return [path], None

    # Case 2: Directory containing SKILL.md
    if path.is_dir():
        skill_file = path / "SKILL.md"
        if skill_file.exists():
            return [skill_file], None

        # Case 3: Parent directory - find all SKILL.md files
        skill_files = list(path.glob("*/SKILL.md"))
        if skill_files:
            return sorted(skill_files), None

        # Check for deeper nesting
        skill_files = list(path.glob("**/SKILL.md"))
        if skill_files:
            return sorted(skill_files), None

        return [], f"No SKILL.md files found in: {path}"

    # Case 4: Glob pattern
    if "*" in path_arg or "?" in path_arg:
        matches = glob.glob(path_arg, recursive=True)
        skill_files = [Path(m) for m in matches if Path(m).name == "SKILL.md"]
        if skill_files:
            return sorted(skill_files), None
        return [], f"No SKILL.md files match pattern: {path_arg}"

    # Path doesn't exist
    return [], f"Path not found: {path_arg}"


def validate_skill(path: Path) -> tuple[list[str], list[str]]:
    """
    Validate a SKILL.md file against best practices.

    Returns:
        Tuple of (errors, warnings)
    """
    errors: list[str] = []
    warnings: list[str] = []

    try:
        content = path.read_text()
    except PermissionError:
        return [f"Permission denied: {path}"], []
    except OSError as e:
        return [f"Cannot read file: {e}"], []

    lines = content.split("\n")

    # === YAML Frontmatter Validation ===
    frontmatter, fm_error = parse_frontmatter(content)

    if fm_error:
        errors.append(fm_error)
    elif frontmatter:
        # Check required fields
        if "name" not in frontmatter:
            errors.append("Missing required field: 'name' in frontmatter")
        else:
            name = frontmatter["name"]
            dir_name = path.parent.name
            if len(name) > 64:
                errors.append(f"Field 'name' exceeds 64 characters ({len(name)} chars)")
            elif not re.match(r"^[a-z0-9:-]+$", name):
                warnings.append(
                    "Field 'name' should use lowercase letters, numbers, hyphens, and colons only"
                )
            # Check name matches directory
            # Allow colon as separator (meta:skill-creator matches meta-skill-creator)
            name_normalized = name.replace(":", "-")
            if name_normalized != dir_name and name != dir_name:
                warnings.append(
                    f"Field 'name' ({name}) should match directory name ({dir_name})"
                )

        if "description" not in frontmatter:
            errors.append("Missing required field: 'description' in frontmatter")
        else:
            desc = frontmatter["description"]
            if len(desc) > 1024:
                errors.append(
                    f"Field 'description' exceeds 1024 characters ({len(desc)} chars)"
                )
            elif "use when" not in desc.lower() and "use for" not in desc.lower():
                warnings.append(
                    "Description should include trigger phrases like 'Use when...' or 'Use for...'"
                )

            # Check for vague patterns that hurt discoverability
            vague_patterns = [
                (r"\bhelps?\s+with\b", "helps with"),
                (r"\bworks?\s+with\b", "works with"),
                (r"\bassists?\s+with\b", "assists with"),
                (r"\bfor\s+working\s+with\b", "for working with"),
                (r"\bhandles?\b", "handles"),
                (r"\bmanages?\b", "manages"),
            ]
            for pattern, term in vague_patterns:
                if re.search(pattern, desc.lower()):
                    warnings.append(
                        f"Vague term '{term}' in description - use specific triggers instead"
                    )
                    break  # Only report first vague term

            # Check trigger density after "Use for"
            desc_lower = desc.lower()
            if "use for" in desc_lower:
                after_use_for = desc_lower.split("use for", 1)[1]
                triggers = extract_trigger_words(after_use_for)
                if len(triggers) < 5:
                    warnings.append(
                        f"Low trigger density: only {len(triggers)} keywords after 'Use for' (recommend 8+)"
                    )

    # === Line Count ===
    line_count = len(lines)
    if line_count > 500:
        errors.append(f"SKILL.md is {line_count} lines (max 500). Split to reference.md")
    elif line_count > 400:
        warnings.append(
            f"SKILL.md is {line_count} lines. Consider splitting to reference.md (~400 recommended)"
        )

    # === Code Block Language Specifiers ===
    in_code_block = False
    code_block_start = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                # Opening fence
                code_block_start = i
                lang = stripped[3:].strip()
                if not lang:
                    errors.append(f"Line {i}: Code block missing language specifier (MD040)")
            in_code_block = not in_code_block

    if in_code_block:
        errors.append(f"Unclosed code block starting at line {code_block_start}")

    # === Required Sections ===
    content_lower = content.lower()

    if "## common mistakes" not in content_lower:
        warnings.append("Missing '## Common Mistakes' section")

    if "## delegation" not in content_lower:
        warnings.append("Missing '## Delegation' section")

    # Check for supporting file links if skill is long
    if line_count > 200:
        # Look for any linked .md files (e.g., [file.md](file.md) or [name](file.md))
        has_md_links = re.search(r'\]\([^)]+\.md\)', content) is not None
        if not has_md_links:
            warnings.append(
                "Long skill without links to supporting .md files"
            )

    # === Directory Structure ===
    skill_dir = path.parent

    # Check if there's a reference.md that should be linked
    ref_path = skill_dir / "reference.md"
    if ref_path.exists():
        if "[reference.md]" not in content:
            warnings.append("reference.md exists but is not linked in SKILL.md")

        # Validate reference.md size - if large, should split into topic files
        ref_content = ref_path.read_text()
        ref_lines = len(ref_content.split("\n"))
        if ref_lines > 500:
            errors.append(
                f"reference.md is {ref_lines} lines (max 500). "
                "Split into topic files (e.g., middleware.md, patterns.md)"
            )

    examples_path = skill_dir / "examples.md"
    if examples_path.exists() and "[examples.md]" not in content:
        warnings.append("examples.md exists but is not linked in SKILL.md")

    # Check scripts directory
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.suffix in [".py", ".sh"]:
                if not script.stat().st_mode & 0o111:
                    warnings.append(f"Script not executable: {script.name} (run chmod +x)")

    return errors, warnings


def extract_trigger_words(description: str) -> set[str]:
    """
    Extract significant trigger words from a description.
    Filters out common words to focus on domain-specific terms.
    """
    common_words = {
        "use", "when", "for", "the", "and", "or", "to", "in", "on", "with",
        "this", "that", "is", "are", "be", "been", "being", "have", "has",
        "had", "do", "does", "did", "will", "would", "could", "should",
        "may", "might", "must", "shall", "can", "need", "about", "into",
        "through", "during", "before", "after", "above", "below", "from",
        "up", "down", "out", "off", "over", "under", "again", "further",
        "then", "once", "here", "there", "all", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own",
        "same", "so", "than", "too", "very", "just", "also", "now", "of",
        "a", "an", "as", "at", "by", "if", "it", "its", "any", "how",
        "what", "which", "who", "whom", "these", "those", "am", "was",
        "were", "you", "your", "they", "them", "their", "we", "our", "i",
        "me", "my", "he", "she", "him", "her", "his", "hers", "skill",
        "skills", "best", "practices", "patterns", "creating", "building",
        "implementing", "working", "handling", "managing", "using",
    }

    words = set(re.findall(r"[a-z]+", description.lower()))
    return words - common_words


def check_description_conflicts(
    skill_descriptions: dict[str, str], threshold: float = 0.5
) -> list[str]:
    """
    Check for potential conflicts between skill descriptions.

    Returns list of warnings for skills with similar descriptions.
    """
    warnings = []
    skills = list(skill_descriptions.items())

    for i, (name1, desc1) in enumerate(skills):
        words1 = extract_trigger_words(desc1)
        if not words1:
            continue

        for name2, desc2 in skills[i + 1 :]:
            words2 = extract_trigger_words(desc2)
            if not words2:
                continue

            # Calculate Jaccard similarity
            intersection = words1 & words2
            union = words1 | words2
            similarity = len(intersection) / len(union) if union else 0

            if similarity >= threshold:
                common = sorted(intersection)[:5]
                warnings.append(
                    f"Similar descriptions: '{name1}' and '{name2}' "
                    f"({similarity:.0%} overlap, common: {', '.join(common)})"
                )

    return warnings


def print_result(path: Path, errors: list[str], warnings: list[str], verbose: bool = True) -> None:
    """Print validation results for a single skill."""
    skill_name = path.parent.name

    if errors:
        print(f"❌ {skill_name}: FAILED")
        if verbose:
            for error in errors:
                print(f"   ✗ {error}")
    elif warnings:
        print(f"✓ {skill_name}: valid (with {len(warnings)} warning(s))")
        if verbose:
            for warning in warnings:
                print(f"   ⚠ {warning}")
    else:
        print(f"✓ {skill_name}: passed")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: uv run scripts/validate-skill.py <path>")
        print()
        print("Accepts:")
        print("  - File path:    .claude/skills/my-skill/SKILL.md")
        print("  - Directory:    .claude/skills/my-skill/")
        print("  - Parent dir:   .claude/skills/")
        print("  - Glob pattern: '.claude/skills/*/SKILL.md'")
        print()
        print("Examples:")
        print("  uv run scripts/validate-skill.py .claude/skills/tanstack-form/")
        print("  uv run scripts/validate-skill.py .claude/skills/")
        return 1

    path_arg = sys.argv[1]
    skill_paths, error = resolve_skill_paths(path_arg)

    if error:
        print(f"❌ Error: {error}")
        return 1

    if not skill_paths:
        print("❌ No skills found to validate")
        return 1

    # Validate all skills
    total_errors = 0
    total_warnings = 0
    failed_skills = []

    # Single skill - verbose output
    if len(skill_paths) == 1:
        path = skill_paths[0]
        errors, warnings = validate_skill(path)

        if errors:
            print("❌ Validation FAILED\n")
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
            print("✓ Skill validation passed")
        elif not errors:
            print("✓ Skill valid (with warnings)")

        return 1 if errors else 0

    # Multiple skills - summary output
    print(f"Validating {len(skill_paths)} skill(s)...\n")

    # Collect descriptions for conflict detection
    skill_descriptions: dict[str, str] = {}

    for path in skill_paths:
        errors, warnings = validate_skill(path)
        total_errors += len(errors)
        total_warnings += len(warnings)

        if errors:
            failed_skills.append(path.parent.name)

        print_result(path, errors, warnings, verbose=bool(errors))

        # Collect description for conflict check
        content = path.read_text()
        frontmatter, _ = parse_frontmatter(content)
        if frontmatter and "description" in frontmatter:
            skill_descriptions[path.parent.name] = frontmatter["description"]

    # Check for description conflicts
    conflict_warnings = check_description_conflicts(skill_descriptions)
    total_warnings += len(conflict_warnings)

    # Summary
    print()
    if failed_skills:
        print(f"❌ {len(failed_skills)} skill(s) failed: {', '.join(failed_skills)}")
    else:
        print(f"✓ All {len(skill_paths)} skill(s) passed")

    if conflict_warnings:
        print(f"\n⚠ Description conflicts detected:")
        for warning in conflict_warnings:
            print(f"   {warning}")

    if total_warnings:
        print(f"\n   {total_warnings} total warning(s)")

    return 1 if failed_skills else 0


if __name__ == "__main__":
    sys.exit(main())
