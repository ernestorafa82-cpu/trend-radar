#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

test -s out/latest.md
test -s out/latest.json
grep -q '^# Trend Radar ' out/latest.md

echo "OK: sanity check passed"
