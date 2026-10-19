#!/usr/bin/env bash
# Reproduce the repository's credential-free validation locally.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

while IFS= read -r -d '' file; do
  python -m py_compile "$file"
done < <(git ls-files -z '*.py')

(cd cases/monitoring-stack && python -m unittest -v test_healthcheck)
(cd cases/ecommerce-webhook-lab && python -m unittest -v)
(cd cases/n8n-api-automation && python -m unittest -v test_validate_payload)
python -m json.tool cases/n8n-api-automation/mock_payload.json >/dev/null
python -m json.tool cases/ecommerce-webhook-lab/fixtures/orders.json >/dev/null
python cases/n8n-api-automation/validate_payload.py cases/n8n-api-automation/mock_payload.json

work_dir=$(mktemp -d)
trap 'rm -rf "$work_dir"' EXIT
printf 'synthetic backup proof\n' > "$work_dir/README.txt"
tar -czf "$work_dir/archive.tar.gz" -C "$work_dir" README.txt
checksum=$(sha256sum "$work_dir/archive.tar.gz" | cut -d' ' -f1)
python cases/backup-verification/verify_archive.py "$work_dir/archive.tar.gz" --sha256 "$checksum"
if python cases/backup-verification/verify_archive.py "$work_dir/archive.tar.gz" --sha256 "$(printf '0%.0s' {1..64})"; then
  echo 'Expected checksum mismatch was accepted' >&2
  exit 1
fi

python scripts/check_svg_assets.py
python scripts/check_local_links.py
python scripts/check_html_assets.py
bash -n cases/linux-docker-audit/audit.sh
(cd cases/ecommerce-webhook-lab && docker compose config --quiet)

if find . -type f \( -name '*.env' -o -name '*.pem' -o -name '*.key' \) -not -path './.git/*' -print -quit | grep -q .; then
  echo 'Potential secret file found in repository' >&2
  exit 1
fi

git diff --check
printf 'Portfolio checks: OK\n'
