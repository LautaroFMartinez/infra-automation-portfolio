#!/usr/bin/env python3
"""Fail when tracked Markdown points at a missing local file or asset."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"!?\[[^]]*\]\(([^)\s]+)")
REMOTE_SCHEMES = ("http://", "https://", "mailto:", "tel:")


def tracked_markdown_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--", "*.md"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def main() -> int:
    missing: list[str] = []

    for markdown in tracked_markdown_files():
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LINK_RE.findall(text):
            target = unquote(raw_target.split("#", 1)[0])
            if not target or target.startswith(REMOTE_SCHEMES) or target.startswith("#"):
                continue

            resolved = (markdown.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{markdown}: {raw_target}")

    if missing:
        print("Missing local Markdown targets:", file=sys.stderr)
        print("\n".join(f"- {item}" for item in missing), file=sys.stderr)
        return 1

    print("Local Markdown links and assets: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
