"""Интерактивный цикл REPL."""

from typing import TextIO

from shell_emulator.errors import CommandError
from shell_emulator.shell import Shell


def run_repl(
    shell: Shell, prompt: str, stdin: TextIO, stdout: TextIO
) -> None:
    """Читает строки из stdin и выполняет их до `exit` или конца ввода."""
    while shell.session.running:
        stdout.write(prompt)
        stdout.flush()
        line = stdin.readline()
        if not line:
            stdout.write("\n")
            return
        _handle_line(shell, line, stdout)


def _handle_line(shell: Shell, line: str, stdout: TextIO) -> None:
    """Выполняет одну строку и печатает результат или сообщение об ошибке."""
    try:
        output = shell.execute(line)
    except CommandError as error:
        stdout.write(f"{error}\n")
        return
    if output:
        stdout.write(f"{output}\n")
