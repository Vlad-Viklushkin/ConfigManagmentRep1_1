#!/usr/bin/env sh
# Этап 3: работа с различными вариантами VFS и обработка ошибок.

. "$(dirname "$0")/common.sh"
EX="$ROOT_DIR/examples"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

title "1. Без VFS"
printf 'vfs-info\nexit\n' | emulator

title "2. Минимальная VFS (пустой корень)"
printf 'vfs-info\nexit\n' | emulator --vfs "$EX/vfs/minimal.xml"

title "3. VFS с несколькими файлами (текст и base64)"
printf 'vfs-info\nexit\n' | emulator --vfs "$EX/vfs/multi_files.xml"

title "4. VFS с тремя и более уровнями вложенности"
printf 'vfs-info\nexit\n' | emulator --vfs "$EX/vfs/deep.xml"

title "5. Стартовый скрипт со всеми командами (deep.xml)"
emulator --vfs "$EX/vfs/deep.xml" --prompt "vfs>" \
    --script "$EX/scripts/stage3_full.emu"
echo "код завершения: $?"

title "6. Ошибка в конце скрипта (остановка)"
emulator --vfs "$EX/vfs/multi_files.xml" \
    --script "$EX/scripts/stage3_error_end.emu"
echo "код завершения: $?"

title "7. Ошибка: VFS-файл не найден"
emulator --vfs "$TMP_DIR/missing.xml"
echo "код завершения: $?"

title "8. Ошибка: некорректный XML"
printf '<vfs><dir name="a">' > "$TMP_DIR/broken.xml"
emulator --vfs "$TMP_DIR/broken.xml"
echo "код завершения: $?"

title "9. Ошибка: неверный base64"
printf '<vfs><file name="x" encoding="base64">!!!</file></vfs>' \
    > "$TMP_DIR/bad_base64.xml"
emulator --vfs "$TMP_DIR/bad_base64.xml"
echo "код завершения: $?"

title "10. Ошибки в интерактивном режиме"
printf 'foo\nexit 1\nvfs-info x\nls\nexit\n' \
    | emulator --vfs "$EX/vfs/deep.xml"
