#!/usr/bin/env bash
set -euo pipefail

NAME="linWinPwn-next"
OUT="${1:-${NAME}.zip}"

rm -f "$OUT"

zip -r "$OUT" \
  api core discovery bridge ui configs scripts tests pyproject.toml \
  -x "ui/node_modules/*" \
  -x ".venv/*" \
  -x "__pycache__/*" \
  -x "*.pyc" \
  -x "*.pyo" \
  -x "*.log"

echo "Packaged -> $OUT"
