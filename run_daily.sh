#!/usr/bin/env bash
set -euo pipefail

export LANG=C.UTF-8
export LC_ALL=C.UTF-8
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
