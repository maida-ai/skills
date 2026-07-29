#!/usr/bin/env python3
"""Fetch grouped PR review comments as JSON via gh and jq."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        print(f"error: {name} could not be found", file=sys.stderr)
        raise SystemExit(1)


def gh_json(args: list[str]) -> str:
    result = subprocess.run(
        ["gh", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        if stderr:
            print(stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--owner", default="")
    parser.add_argument("-r", "--repo", default="")
    parser.add_argument("-p", "--pr", default="")
    parser.add_argument(
        "-u",
        "--allow-subject-mapping",
        action="store_true",
        help="enable subject-based remapping when PR commit subjects are unique",
    )
    args = parser.parse_args()

    require_command("gh")
    require_command("jq")

    script_dir = Path(__file__).resolve().parent
    owner = args.owner or gh_json(["repo", "view", "--json", "owner", "--jq", ".owner.login"])
    repo = args.repo or gh_json(["repo", "view", "--json", "name", "--jq", ".name"])
    pr = args.pr or gh_json(["pr", "view", "--json", "number", "--jq", ".number"])

    if not owner or not repo or not pr:
        print("error: owner, repo, and PR are required", file=sys.stderr)
        print(f"usage: {Path(sys.argv[0]).name} -o OWNER -r REPO -p PR [-u]", file=sys.stderr)
        return 1

    graphql_file = script_dir / "pr-review-comments.graphql"
    jq_file = script_dir / "group-by-commit.jq"
    allow_subject_mapping = "true" if args.allow_subject_mapping else "false"

    gh_proc = subprocess.Popen(
        [
            "gh",
            "api",
            "graphql",
            "--paginate",
            "--slurp",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={repo}",
            "-F",
            f"pr={pr}",
            "-F",
            f"query=@{graphql_file}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    jq_proc = subprocess.run(
        [
            "jq",
            "--argjson",
            "allow_subject_mapping",
            allow_subject_mapping,
            "-f",
            str(jq_file),
        ],
        stdin=gh_proc.stdout,
        capture_output=True,
        text=True,
        check=False,
    )
    if gh_proc.stdout is not None:
        gh_proc.stdout.close()
    gh_stderr = gh_proc.stderr.read() if gh_proc.stderr is not None else ""
    gh_code = gh_proc.wait()

    if gh_code != 0:
        if gh_stderr.strip():
            print(gh_stderr.strip(), file=sys.stderr)
        return gh_code

    if jq_proc.returncode != 0:
        if jq_proc.stderr.strip():
            print(jq_proc.stderr.strip(), file=sys.stderr)
        return jq_proc.returncode

    sys.stdout.write(jq_proc.stdout)
    if jq_proc.stdout and not jq_proc.stdout.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
