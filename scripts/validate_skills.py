#!/usr/bin/env python3
"""Validate the portable Agent Skills shape for this repository."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

KEBAB_CASE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKIPPED_SCRIPT_SUFFIXES = {".jq", ".graphql", ".py", ".cmd", ".ps1"}
FAILED = False


def error(message: str) -> None:
    global FAILED
    print(f"error: {message}", file=sys.stderr)
    FAILED = True


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def frontmatter_value(skill_file: Path, key: str) -> str:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return ""
    for line in lines[1:]:
        if line == "---":
            break
        prefix = f"{key}:"
        if line.startswith(prefix):
            value = line[len(prefix) :].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
            return value
    return ""


def is_invocable_script(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix.lower() in SKIPPED_SCRIPT_SUFFIXES:
        return True

    if path.with_suffix(".py").exists() or path.with_suffix(".cmd").exists():
        return True

    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return False

    if first_line.startswith("#!"):
        if os.name == "nt":
            return True
        return os.access(path, os.X_OK)

    # Non-shebang scripts must be executable on Unix-like systems.
    if os.name == "nt":
        return False
    return os.access(path, os.X_OK)


def validate_skill(skill_dir: Path) -> None:
    skill_file = skill_dir / "SKILL.md"
    dir_name = skill_dir.name
    name = frontmatter_value(skill_file, "name")
    description = frontmatter_value(skill_file, "description")
    lines = len(skill_file.read_text(encoding="utf-8").splitlines())

    if not name:
        error(f"{skill_file} missing frontmatter name")
    if not description:
        error(f"{skill_file} missing frontmatter description")
    if name and name != dir_name:
        error(f"{skill_file} name '{name}' does not match directory '{dir_name}'")
    if name and not KEBAB_CASE.match(name):
        error(f"{skill_file} name must be kebab-case lowercase alphanumeric")
    if name and len(name) > 64:
        error(f"{skill_file} name exceeds 64 characters")
    if description and len(description) > 1024:
        error(f"{skill_file} description exceeds 1024 characters")
    if lines > 500:
        error(f"{skill_file} exceeds 500 lines")

    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return

    for script in sorted(scripts_dir.iterdir()):
        if not script.is_file():
            continue
        if script.suffix.lower() in SKIPPED_SCRIPT_SUFFIXES:
            continue
        if not is_invocable_script(script):
            error(f"{script} is not invocable (missing shebang, launcher, or execute permission)")


def discover_skills(root: Path) -> list[Path]:
    skills: list[Path] = []
    for family in ("developer", "product"):
        family_dir = root / family
        if not family_dir.is_dir():
            continue
        for skill_file in sorted(family_dir.glob("*/SKILL.md")):
            skills.append(skill_file.parent)
    return skills


def main() -> int:
    root = repo_root()
    skills = discover_skills(root)
    for skill_dir in skills:
        validate_skill(skill_dir)
    return 1 if FAILED else 0


if __name__ == "__main__":
    raise SystemExit(main())
