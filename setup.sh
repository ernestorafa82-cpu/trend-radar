#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "OK: entorno listo"
echo "Activa con: source .venv/bin/activate"
echo "Configura variables copiando .env.example a .env"
