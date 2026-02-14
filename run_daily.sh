#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# carga env si existe
[ -f .env ] && set -a && . ./.env && set +a

# ejecuta radar
. .venv/bin/activate
python radar.py

# IMPORTANTE:
# No crear symlinks out/latest.* aquí.
# radar.py ya escribe out/latest.json y out/latest.md como COPIA estable.
# Si aquí se crean symlinks, radar.py puede truncar el JSON al copiar.

echo "OK daily: $(date) -> out/latest.md"
