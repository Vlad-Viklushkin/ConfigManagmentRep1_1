"""Команды навигации по VFS: ls и cd."""

from typing import List, Set, Tuple

from shell_emulator.cmd_util import lookup, parse_options, visible_names
from shell_emulator.errors import CommandError
from shell_emulator.session import Session
from shell_emulator.vfs import ERR_NOT_DIR, ROOT_PATH, Resolved, VfsNode

LS_ERROR = "ls: cannot access '{path}': {reason}"
CD_ERROR = "cd: {path}: {reason}"
SIZE_WIDTH = 8
DIR_MARK = "d"
FILE_MARK = "-"


def _format_entry(name: str, node: VfsNode, long_format: bool) -> str:
    """Форматирует одну запись списка (с типом и размером при -l)."""
    if not long_format:
        return name
    mark = DIR_MARK if node.is_dir else FILE_MARK
    return f"{mark} {node.size():>{SIZE_WIDTH}} {name}"


def _list_target(
    arg: str, target: Resolved, flags: Set[str], with_header: bool
) -> List[str]:
    """Строит строки вывода для одного пути команды ls."""
    long_format = "l" in flags
    if not target.node.is_dir:
        return [_format_entry(arg, target.node, long_format)]
    lines = [f"{arg}:"] if with_header else []
    for name in visible_names(target.node, "a" in flags):
        child = target.node.children[name]
        lines.append(_format_entry(name, child, long_format))
    return lines


def cmd_ls(session: Session, args: List[str]) -> str:
    """Команда `ls [-a] [-l] [путь...]`: содержимое каталога или файл."""
    flags, paths = parse_options(args, "al", "ls")
    paths = paths or ["."]
    targets: List[Tuple[str, Resolved]] = [
        (path, lookup(session, path, LS_ERROR)) for path in paths
    ]
    with_header = bool(paths[1:])
    blocks = [
        "\n".join(_list_target(arg, target, flags, with_header))
        for arg, target in targets
    ]
    return "\n\n".join(blocks)


def cmd_cd(session: Session, args: List[str]) -> str:
    """Команда `cd [путь]`: смена текущего каталога (без пути — в `/`)."""
    if args[1:]:
        raise CommandError("cd: too many arguments")
    path = args[0] if args else ROOT_PATH
    target = lookup(session, path, CD_ERROR)
    if not target.node.is_dir:
        raise CommandError(f"cd: {path}: {ERR_NOT_DIR}")
    session.cwd = target.path
    return ""
