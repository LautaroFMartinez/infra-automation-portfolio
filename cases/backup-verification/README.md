# Backup verification

## Problem
A compressed backup file is not proof that recovery will work.

## Demonstration

- Create a consistent database snapshot.
- Exclude temporary and regenerable files.
- Compress and encrypt the archive.
- Verify checksum, decryption and archive listing.
- Keep local and remote copies separate.
- Alert only when a backup fails or becomes stale.

## Success criteria

A run is successful only when the resulting artifact can be checked and opened without the live service.

## Run the read-only verifier

The tracked helper checks the archive's SHA-256 (when supplied), opens it with Python's `tarfile` reader and prints the first ten members. It never extracts or modifies the archive.

```bash
cd cases/backup-verification
work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
printf 'synthetic backup proof\n' > "$work_dir/README.txt"
tar -czf "$work_dir/archive.tar.gz" -C "$work_dir" README.txt
checksum=$(sha256sum "$work_dir/archive.tar.gz" | cut -d' ' -f1)
python verify_archive.py "$work_dir/archive.tar.gz" --sha256 "$checksum"
```

The command must finish with `archive_read=OK`. A mismatched checksum returns exit code `2`; the archive is not accepted as verified. This demonstration validates readability and integrity metadata, not encryption or a full application restore.

## Safety

The example uses synthetic data. No private keys, real domains, personal finance data or production logs belong in this repository.
