#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# carga env si existe
[ -f .env ] && set -a && . ./.env && set +a

# ejecuta radar
. .venv/bin/activate
python radar.py

# deja un puntero al último md
latest_json="$(ls -1 out/radar_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].json | sort -r | head -n 1)"
latest_md="$(ls -1 out/radar_[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].md | sort -r | head -n 1)"
ln -sf "$(basename "$latest_json")" out/latest.json
ln -sf "$(basename "$latest_md")" out/latest.md

echo "OK daily: $(date) -> $latest_md"
