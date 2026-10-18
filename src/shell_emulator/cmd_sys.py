"""Системные команды: uname."""

import platform
from typing import List

from shell_emulator.cmd_util import parse_options
from shell_emulator.errors import CommandError
from shell_emulator.session import Session

FIELDS = (
    ("s", "system"),
    ("n", "node"),
    ("r", "release"),
    ("v", "version"),
    ("m", "machine"),
)
DEFAULT_FLAGS = {"s"}
ALL_FLAGS = {key for key, _ in FIELDS}


def cmd_uname(session: Session, args: List[str]) -> str:
    """Команда `uname [-a] [-s] [-n] [-r] [-v] [-m]`: данные об ОС.

    Значения берутся у реальной ОС, в которой запущен эмулятор.
    Без опций печатается имя системы (как `uname -s`).
    """
    flags, operands = parse_options(args, "snrvma", "uname")
    if operands:
        raise CommandError(f"uname: extra operand '{operands[0]}'")
    if "a" in flags:
        flags = ALL_FLAGS
    flags = flags or DEFAULT_FLAGS
    info = platform.uname()
    return " ".join(
        getattr(info, attr) for key, attr in FIELDS if key in flags
    )
