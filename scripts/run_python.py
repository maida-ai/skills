#!/usr/bin/env python3
"""Run another Python script in this directory with a discovered Python 3 interpreter."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def python_command() -> list[str]:
    if os.environ.get("PYTHON"):
        return [os.environ["PYTHON"]]
    if sys.executable:
        return [sys.executable]
    for candidate in ("python3", "python", "py"):
        path = shutil_which(candidate)
        if path:
            cmd = [path]
            if candidate == "py":
                cmd.append("-3")
            return cmd
    print("error: Python 3 is required", file=sys.stderr)
    raise SystemExit(1)


def shutil_which(cmd: str) -> str | None:
    import shutil

    return shutil.which(cmd)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: run_python.py SCRIPT [ARGS...]", file=sys.stderr)
        return 1

    script = Path(sys.argv[1])
    if not script.is_absolute():
        script = Path(__file__).resolve().parent / script
    cmd = [*python_command(), str(script), *sys.argv[2:]]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
