"""Общие помощники для реализации команд."""

from typing import List, Set, Tuple

from shell_emulator.errors import CommandError, VfsError
from shell_emulator.session import Session
from shell_emulator.vfs import Resolved, VfsNode

OPTION_PREFIX = "-"
END_OF_OPTIONS = "--"
HIDDEN_PREFIX = "."


def _is_option(arg: str) -> bool:
    """Аргумент вида `-x` — опция; одиночный `-` — обычный операнд."""
    return arg.startswith(OPTION_PREFIX) and arg != OPTION_PREFIX


def parse_options(
    args: List[str], allowed: str, command: str
) -> Tuple[Set[str], List[str]]:
    """Разделяет аргументы на однобуквенные флаги и операнды.

    Поддерживаются объединённые флаги (`-la`) и `--` как конец опций.
    Недопустимый флаг вызывает CommandError.
    """
    flags: Set[str] = set()
    operands: List[str] = []
    options_done = False
    for arg in args:
        if options_done or not _is_option(arg):
            operands.append(arg)
        elif arg == END_OF_OPTIONS:
            options_done = True
        else:
            flags.update(_check_flags(arg, allowed, command))
    return flags, operands


def _check_flags(arg: str, allowed: str, command: str) -> str:
    """Проверяет буквы опции и возвращает их."""
    letters = arg[len(OPTION_PREFIX):]
    for letter in letters:
        if letter not in allowed:
            raise CommandError(
                f"{command}: invalid option -- '{letter}'"
            )
    return letters


def lookup(session: Session, path: str, template: str) -> Resolved:
    """Находит узел по пути относительно текущего каталога.

    При ошибке бросает CommandError с текстом `template`, куда
    подставляются `{path}` и `{reason}`.
    """
    try:
        return session.active_vfs().resolve(path, session.cwd)
    except VfsError as error:
        raise CommandError(template.format(path=path, reason=error))


def visible_names(node: VfsNode, show_all: bool) -> List[str]:
    """Имена потомков каталога по алфавиту; скрытые — только с show_all."""
    names = [
        name for name in node.children
        if show_all or not name.startswith(HIDDEN_PREFIX)
    ]
    return sorted(names, key=lambda name: (name.lower(), name))
