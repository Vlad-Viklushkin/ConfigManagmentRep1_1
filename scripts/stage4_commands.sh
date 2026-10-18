#!/usr/bin/env sh
# Этап 4: логика ls, cd, tree, uname и обработка ошибок.

. "$(dirname "$0")/common.sh"
EX="$ROOT_DIR/examples"

title "1. Стартовый скрипт: все режимы команд (deep.xml)"
emulator --vfs "$EX/vfs/deep.xml" --prompt "vfs>" \
    --script "$EX/scripts/stage4_commands.emu"
echo "код завершения: $?"

title "2. Минимальная VFS: ls и tree"
printf 'ls\ntree\nexit\n' | emulator --vfs "$EX/vfs/minimal.xml"

title "3. VFS с файлами: ls -l и tree"
printf 'ls -l\ntree\nexit\n' | emulator --vfs "$EX/vfs/multi_files.xml"

title "4. Ошибка в конце скрипта (остановка, код 1)"
emulator --vfs "$EX/vfs/deep.xml" \
    --script "$EX/scripts/stage4_error_end.emu"
echo "код завершения: $?"

title "5. Все ошибки ls, cd, tree, uname (интерактивный режим)"
printf '%s\n' \
    'ls /nope' 'ls -z' 'ls /etc/hostname/x' \
    'cd /nope' 'cd /etc/hostname' 'cd a b' \
    'tree /nope' 'tree /etc/hostname' 'tree a b' 'tree -x' \
    'uname -z' 'uname foo' 'exit' \
    | emulator --vfs "$EX/vfs/deep.xml"
