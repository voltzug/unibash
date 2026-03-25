#!/usr/bin/env sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT_DIR="$ROOT_DIR/unibash-py/gen"

#python3 -m pip install -r "$ROOT_DIR/unibash-py/requirements.txt"

mkdir -p "$OUT_DIR"
echo "# Package marker $(date)" > "$OUT_DIR/__init__.py"

antlr4 -Dlanguage=Python3 -o "$OUT_DIR" "$ROOT_DIR/antlr/UnibashLexer.g4"
antlr4 -Dlanguage=Python3 -visitor -listener -lib "$OUT_DIR" -o "$OUT_DIR" "$ROOT_DIR/antlr/UnibashParser.g4"
