#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

test -s out/latest.md
test -s out/latest.json
test -s out/latest.skool.md
test -s out/latest.workbench.md
grep -q '^# Content Trend Radar ' out/latest.md

echo "OK: sanity check passed"
