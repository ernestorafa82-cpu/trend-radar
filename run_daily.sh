#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# carga env si existe
[ -f .env ] && set -a && . ./.env && set +a

LOG="out/cron.log"
mkdir -p out

# log header
{
  echo "---- $(date) ----"
  . .venv/bin/activate
  python radar.py
  echo "OK daily: $(date) -> out/latest.md"
} >>"$LOG" 2>&1

# mensaje corto a consola (útil si lo ejecutas a mano)
echo "OK daily: $(date) -> out/latest.md"
