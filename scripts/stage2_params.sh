#!/usr/bin/env sh
# Этап 2: проверка всех параметров командной строки.

. "$(dirname "$0")/common.sh"
EX="$ROOT_DIR/examples"

title "1. Без параметров (интерактивный ввод из stdin)"
printf 'ls\ncd /tmp\nexit\n' | emulator

title "2. Параметр --prompt"
printf 'ls\nexit\n' | emulator --prompt "custom>"

title "3. Параметр --script (успешный сценарий)"
emulator --script "$EX/scripts/basic.emu"

title "4. Параметр --script (остановка на первой ошибке)"
emulator --script "$EX/scripts/stop_on_error.emu"
echo "код завершения: $?"

title "5. Параметр --script (файл не найден)"
emulator --script "$EX/scripts/missing.emu"
echo "код завершения: $?"

title "6. Все параметры вместе"
emulator --vfs "$EX/vfs/minimal.xml" --prompt "all>" \
    --script "$EX/scripts/basic.emu"
