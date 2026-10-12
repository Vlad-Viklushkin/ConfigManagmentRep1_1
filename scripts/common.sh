#!/usr/bin/env sh
# Общие настройки для демонстрационных скриптов.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR/src"
PYTHON="${PYTHON:-python3}"

emulator() {
    "$PYTHON" -m shell_emulator "$@"
}

title() {
    printf '\n=== %s ===\n' "$1"
}
