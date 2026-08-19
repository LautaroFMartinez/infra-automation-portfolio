#!/usr/bin/env bash
set -Eeuo pipefail

printf '%s\n' '== Linux/Docker audit (read-only) =='
printf 'date_utc: '; date -u +%FT%TZ
printf 'hostname: '; hostname
printf '\nlistening sockets:\n'
if command -v ss >/dev/null 2>&1; then ss -tuln | sed -n '1,25p'; else echo 'ss unavailable'; fi
printf '\nfilesystem usage:\n'
df -hT / | sed -n '1,3p'
printf '\nDocker containers:\n'
if command -v docker >/dev/null 2>&1; then docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' 2>/dev/null || echo 'docker unavailable or permission denied'; else echo 'docker unavailable'; fi
