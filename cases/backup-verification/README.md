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

## Safety

The example uses synthetic data. No private keys, real domains, personal finance data or production logs belong in this repository.
