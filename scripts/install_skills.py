#!/usr/bin/env python3
"""Install skill folders into a local agent skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_install_root(target_agent: str, dest_dir: str | None) -> Path:
    if dest_dir:
        return Path(dest_dir).expanduser()
    if target_agent == "codex":
        return Path(
            os.environ.get("CODEX_SKILLS_DIR", Path.home() / ".agents" / "skills")
        ).expanduser()
    if target_agent == "claude":
        return Path(
            os.environ.get("CLAUDE_SKILLS_DIR", Path.home() / ".claude" / "skills")
        ).expanduser()
    raise ValueError(f"unsupported target agent: {target_agent}")


def collect_skills(root: Path, target: str) -> list[Path]:
    source = root / target
    if (source / "SKILL.md").is_file():
        return [source]
    if source.is_dir():
        skills = sorted(
            skill_dir.parent
            for skill_dir in source.glob("*/SKILL.md")
            if skill_dir.is_file()
        )
        if skills:
            return skills
    print(f"error: no such family or skill: {target}", file=sys.stderr)
    raise SystemExit(1)


def copy_skill(skill_dir: Path, destination: Path, replace: bool) -> str:
    if destination.exists():
        if not replace:
            return "skipped"
        shutil.rmtree(destination)
        shutil.copytree(skill_dir, destination)
        return "replaced"
    shutil.copytree(skill_dir, destination)
    return "installed"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install skill folders into a local agent skills directory.",
        epilog=(
            "Examples:\n"
            "  scripts/install-skills developer\n"
            "  scripts/install-skills developer --replace\n"
            "  scripts/install-skills --target claude developer\n"
            "  scripts/install-skills developer/split-pr-stack\n"
            "  scripts/install-skills --fail-fast developer\n"
            "  scripts/install-skills --dest /tmp/agent-skills --dry-run developer"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("target", help="family or family/skill path under the repo root")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--target", dest="target_agent", choices=("codex", "claude"), default="codex")
    parser.add_argument("--dest", dest="dest_dir", default=None)
    args = parser.parse_args(argv)

    root = repo_root()
    install_root = default_install_root(args.target_agent, args.dest_dir)
    skills = collect_skills(root, args.target)

    if not skills:
        print(f"error: no skills found under {args.target}", file=sys.stderr)
        return 1

    if not args.dry_run:
        install_root.mkdir(parents=True, exist_ok=True)

    for skill_dir in skills:
        skill_name = skill_dir.name
        destination = install_root / skill_name

        if args.dry_run:
            if destination.exists() and args.fail_fast:
                print(f"would fail {skill_dir} -> {destination} (already installed)")
            elif destination.exists() and args.replace:
                print(f"would replace {skill_dir} -> {destination}")
            elif destination.exists():
                print(f"would skip {skill_dir} -> {destination} (already installed)")
            else:
                print(f"would install {skill_dir} -> {destination}")
            continue

        if destination.exists() and args.fail_fast:
            print(f"error: {destination} already exists", file=sys.stderr)
            return 1

        if destination.exists() and not args.replace:
            print(f"skipped {skill_name} -> {destination} (already installed)")
            continue

        action = copy_skill(skill_dir, destination, replace=args.replace)
        print(f"{action} {skill_name} -> {destination}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
