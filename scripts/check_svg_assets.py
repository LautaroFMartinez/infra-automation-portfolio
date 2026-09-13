#!/usr/bin/env python3
"""Fail when a tracked SVG asset is not well-formed XML."""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def tracked_svg_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--", "*.svg"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def main() -> int:
    invalid: list[str] = []
    checked = tracked_svg_files()

    for svg in checked:
        try:
            ET.parse(svg)
        except (ET.ParseError, OSError) as error:
            invalid.append(f"{svg}: {error}")

    if invalid:
        print("Malformed SVG assets:", file=sys.stderr)
        print("\n".join(f"- {item}" for item in invalid), file=sys.stderr)
        return 1

    print(f"SVG assets: OK ({len(checked)} files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
