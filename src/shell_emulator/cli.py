"""Точка входа командной строки."""

import sys
from typing import List, Optional, TextIO

from shell_emulator.commands import Session
from shell_emulator.prompt import default_prompt
from shell_emulator.repl import run_repl
from shell_emulator.shell import Shell

EXIT_OK = 0


def main(
    argv: Optional[List[str]] = None,
    stdin: Optional[TextIO] = None,
    stdout: Optional[TextIO] = None,
) -> int:
    """Запускает эмулятор и возвращает код завершения."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    shell = Shell(Session())
    try:
        run_repl(shell, default_prompt(), stdin, stdout)
    except KeyboardInterrupt:
        stdout.write("\n")
    return EXIT_OK
