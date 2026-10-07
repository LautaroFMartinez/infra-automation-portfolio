#!/usr/bin/env python3
"""Validate a sanitized n8n/API intake payload without contacting an API."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "event",
    "source",
    "customer",
    "requested_service",
    "requires_human_review",
}


def validate(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload must be a JSON object"]

    missing = sorted(REQUIRED_FIELDS - payload.keys())
    errors.extend(f"missing field: {field}" for field in missing)

    customer = payload.get("customer")
    if not isinstance(customer, dict):
        errors.append("customer must be an object")
    else:
        for field in ("name", "email"):
            if not isinstance(customer.get(field), str) or not customer[field].strip():
                errors.append(f"customer.{field} must be a non-empty string")

    for field in ("event", "source", "requested_service"):
        if not isinstance(payload.get(field), str) or not payload[field].strip():
            errors.append(f"{field} must be a non-empty string")

    if not isinstance(payload.get("requires_human_review"), bool):
        errors.append("requires_human_review must be boolean")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path, help="JSON payload to validate")
    args = parser.parse_args()

    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read valid JSON from {args.payload}: {exc}", file=sys.stderr)
        return 2

    errors = validate(payload)
    if errors:
        print("Invalid intake payload:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1

    route = "human-review" if payload["requires_human_review"] else "automated-processing"
    print(f"Payload valid; route={route}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
