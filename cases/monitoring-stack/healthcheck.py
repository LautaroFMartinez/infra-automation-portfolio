#!/usr/bin/env python3
"""Small dependency-free HTTP health check for a documented endpoint."""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    request = urllib.request.Request(args.url, headers={"User-Agent": "portfolio-healthcheck/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            print(f"status={response.status}")
            print(f"content_type={response.headers.get_content_type()}")
            return 0 if 200 <= response.status < 400 else 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"health=FAIL reason={exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
