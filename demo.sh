#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "ERROR: falta .venv. Ejecuta primero: ./setup.sh"
  exit 1
fi

if [ ! -f .env ]; then
  echo "ERROR: falta .env. Crea uno a partir de .env.example"
  exit 1
fi

. .venv/bin/activate
./run_daily.sh

echo
echo "Demo lista:"
echo "- Reporte: out/latest.md"
echo "- JSON: out/latest.json"
