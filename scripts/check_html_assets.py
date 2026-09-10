#!/usr/bin/env python3
"""Fail when the interactive portfolio references a missing local asset."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REMOTE_SCHEMES = {"http", "https", "mailto", "tel", "data"}


class LocalReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in {"src", "href"} and value:
                self.references.append(value)


def main() -> int:
    document = Path("v2/index.html")
    parser = LocalReferenceParser()
    parser.feed(document.read_text(encoding="utf-8"))

    missing: list[str] = []
    for reference in parser.references:
        parsed = urlparse(reference)
        if parsed.scheme in REMOTE_SCHEMES or reference.startswith(("#", "/")):
            continue
        target = (document.parent / parsed.path).resolve()
        if not target.exists():
            missing.append(f"{document}: {reference}")

    if missing:
        print("Missing local HTML assets:", file=sys.stderr)
        print("\n".join(f"- {item}" for item in missing), file=sys.stderr)
        return 1

    print(f"Local HTML assets: OK ({len(parser.references)} references checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
