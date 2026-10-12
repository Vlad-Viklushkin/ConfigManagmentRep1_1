"""Выполнение стартового скрипта."""

from typing import List, TextIO

from shell_emulator.errors import CommandError, EmulatorError
from shell_emulator.shell import Shell

COMMENT_MARK = "#"


def read_script(path: str) -> List[str]:
    """Читает строки скрипта из файла."""
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().splitlines()
    except (OSError, UnicodeDecodeError) as error:
        raise EmulatorError(f"cannot read script '{path}': {error}")


def _is_skipped(line: str) -> bool:
    """Пустые строки и строки-комментарии не выполняются."""
    stripped = line.strip()
    return not stripped or stripped.startswith(COMMENT_MARK)


def run_script(
    shell: Shell, lines: List[str], prompt: str, stdout: TextIO
) -> bool:
    """Выполняет строки скрипта, имитируя диалог с пользователем.

    На экран выводятся и ввод, и вывод. При первой ошибке выполнение
    останавливается, возвращается False. Иначе возвращается True.
    """
    for line in lines:
        if _is_skipped(line):
            continue
        stdout.write(f"{prompt}{line.strip()}\n")
        try:
            output = shell.execute(line)
        except CommandError as error:
            stdout.write(f"{error}\n")
            return False
        if output:
            stdout.write(f"{output}\n")
        if not shell.session.running:
            break
    return True
