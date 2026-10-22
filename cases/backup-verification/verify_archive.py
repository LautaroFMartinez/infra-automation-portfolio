#!/usr/bin/env python3
"""Read-only archive verification demo using only the Python standard library."""
from __future__ import annotations

import argparse
import hashlib
import tarfile
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("--sha256", help="expected SHA-256 checksum")
    args = parser.parse_args()
    if not args.archive.is_file():
        parser.error(f"archive does not exist: {args.archive}")
    checksum = sha256(args.archive)
    print(f"sha256={checksum}")
    if args.sha256 and checksum.lower() != args.sha256.lower():
        print("checksum=FAIL")
        return 2
    try:
        with tarfile.open(args.archive, "r:*") as archive:
            members = archive.getmembers()
            print(f"members={len(members)}")
            for member in members[:10]:
                print(f"  {member.name}")
            payloads_read = 0
            for member in members:
                if not member.isfile():
                    continue
                payload = archive.extractfile(member)
                if payload is None:
                    print(f"payload_read=FAIL ({member.name})")
                    return 3
                while payload.read(1024 * 1024):
                    pass
                payloads_read += 1
            print(f"payloads_read={payloads_read}")
    except tarfile.TarError as error:
        print(f"archive_read=FAIL ({error})")
        return 3
    print("archive_read=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
