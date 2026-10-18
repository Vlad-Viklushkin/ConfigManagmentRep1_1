"""Точка входа командной строки."""

import sys
from typing import List, Optional, TextIO

from shell_emulator.session import Session
from shell_emulator.config import Config, format_debug, parse_args
from shell_emulator.errors import EmulatorError
from shell_emulator.prompt import resolve_prompt
from shell_emulator.repl import run_repl
from shell_emulator.script import read_script, run_script
from shell_emulator.shell import Shell
from shell_emulator.vfs_xml import load_vfs

EXIT_OK = 0
EXIT_SCRIPT_ERROR = 1
EXIT_VFS_ERROR = 2


def _run_start_script(
    shell: Shell, config: Config, prompt: str, stdout: TextIO
) -> bool:
    """Выполняет стартовый скрипт, если он задан. False — была ошибка."""
    if config.script_path is None:
        return True
    try:
        lines = read_script(config.script_path)
    except EmulatorError as error:
        stdout.write(f"error: {error}\n")
        return False
    return run_script(shell, lines, prompt, stdout)


def main(
    argv: Optional[List[str]] = None,
    stdin: Optional[TextIO] = None,
    stdout: Optional[TextIO] = None,
) -> int:
    """Запускает эмулятор и возвращает код завершения."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    config = parse_args(argv)
    for line in format_debug(config):
        stdout.write(f"{line}\n")
    session = Session()
    try:
        if config.vfs_path is not None:
            session.attach_vfs(load_vfs(config.vfs_path))
    except EmulatorError as error:
        stdout.write(f"error: {error}\n")
        return EXIT_VFS_ERROR
    shell = Shell(session)
    prompt = resolve_prompt(config.prompt)
    if not _run_start_script(shell, config, prompt, stdout):
        return EXIT_SCRIPT_ERROR
    try:
        run_repl(shell, prompt, stdin, stdout)
    except KeyboardInterrupt:
        stdout.write("\n")
    return EXIT_OK
