#!/usr/bin/env sh
# Этап 5: rm, rmdir, vfs-load; изменения только в памяти.

. "$(dirname "$0")/common.sh"
cd "$ROOT_DIR" || exit 1
EX="examples"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

title "1. Стартовый скрипт: все режимы rm, rmdir, vfs-load"
emulator --vfs "$EX/vfs/deep.xml" --prompt "vfs>" \
    --script "$EX/scripts/stage5_commands.emu"
echo "код завершения: $?"

title "2. Ошибка в конце скрипта (остановка, код 1)"
emulator --vfs "$EX/vfs/deep.xml" \
    --script "$EX/scripts/stage5_error_end.emu"
echo "код завершения: $?"

title "3. Все ошибки rm, rmdir, vfs-load (интерактивный режим)"
printf '%s\n' \
    'rm' 'rm /nope' 'rm /home' 'rm -r /' 'rm -z x' \
    'cd /tmp' 'rm -r .' 'rmdir .' 'cd /' \
    'rmdir' 'rmdir /home' 'rmdir /etc/hostname' 'rmdir /nope' \
    'vfs-load' 'vfs-load a b' 'vfs-load /no/such.xml' \
    'ls' 'exit' \
    | emulator --vfs "$EX/vfs/deep.xml"

title "4. vfs-load: повреждённый файл не заменяет текущую VFS"
printf '<vfs><dir>' > "$TMP_DIR/broken.xml"
printf 'vfs-load %s\nls\nexit\n' "$TMP_DIR/broken.xml" \
    | emulator --vfs "$EX/vfs/deep.xml"

title "5. Изменения только в памяти: XML-файл не меняется"
BEFORE="$(cksum < "$EX/vfs/deep.xml")"
printf 'rm -r /home\nrmdir /tmp\nls\nexit\n' \
    | emulator --vfs "$EX/vfs/deep.xml"
AFTER="$(cksum < "$EX/vfs/deep.xml")"
echo "контрольная сумма до:    $BEFORE"
echo "контрольная сумма после: $AFTER"
[ "$BEFORE" = "$AFTER" ] && echo "файл не изменён: OK"
