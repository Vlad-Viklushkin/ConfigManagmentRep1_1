"""Команды изменения VFS (только в памяти): rm и rmdir."""

from typing import List, Optional

from shell_emulator.cmd_util import lookup, parse_options
from shell_emulator.errors import CommandError
from shell_emulator.session import Session
from shell_emulator.vfs import ERR_NOT_DIR, Resolved

RM_ERROR = "rm: cannot remove '{path}': {reason}"
RMDIR_ERROR = "rmdir: failed to remove '{path}': {reason}"
ERR_IS_DIR = "Is a directory"
ERR_NOT_EMPTY = "Directory not empty"
ERR_BUSY = "Device or resource busy"


def _check_dir_removal(
    session: Session, path: str, target: Resolved, recursive: bool
) -> None:
    """Проверяет, можно ли удалить каталог командой rm."""
    if not recursive:
        raise CommandError(RM_ERROR.format(path=path, reason=ERR_IS_DIR))
    if target.parent is None:
        raise CommandError(
            f"rm: it is dangerous to operate recursively on '{path}'"
        )
    if session.is_busy(target.path):
        raise CommandError(RM_ERROR.format(path=path, reason=ERR_BUSY))


def _remove_one(
    session: Session, path: str, recursive: bool, force: bool
) -> None:
    """Удаляет один путь; при force несуществующие пути игнорируются."""
    try:
        target = lookup(session, path, RM_ERROR)
    except CommandError:
        if force:
            return
        raise
    if target.node.is_dir:
        _check_dir_removal(session, path, target, recursive)
    target.parent.remove_child(target.node.name)


def cmd_rm(session: Session, args: List[str]) -> str:
    """Команда `rm [-r] [-f] путь...`: удаляет файлы и каталоги.

    Без `-r` каталоги не удаляются, `-f` игнорирует несуществующие
    пути и отсутствие операндов. Изменяется только VFS в памяти.
    """
    flags, paths = parse_options(args, "rRf", "rm")
    force = "f" in flags
    if not paths and not force:
        raise CommandError("rm: missing operand")
    recursive = "r" in flags or "R" in flags
    for path in paths:
        _remove_one(session, path, recursive, force)
    return ""


def _rmdir_problem(session: Session, target: Resolved) -> Optional[str]:
    """Возвращает причину, по которой каталог нельзя удалить, или None."""
    if not target.node.is_dir:
        return ERR_NOT_DIR
    if target.node.children:
        return ERR_NOT_EMPTY
    if target.parent is None or session.is_busy(target.path):
        return ERR_BUSY
    return None


def _rmdir_one(session: Session, path: str) -> None:
    """Удаляет один пустой каталог."""
    target = lookup(session, path, RMDIR_ERROR)
    reason = _rmdir_problem(session, target)
    if reason is not None:
        raise CommandError(RMDIR_ERROR.format(path=path, reason=reason))
    target.parent.remove_child(target.node.name)


def cmd_rmdir(session: Session, args: List[str]) -> str:
    """Команда `rmdir путь...`: удаляет пустые каталоги в памяти."""
    _, paths = parse_options(args, "", "rmdir")
    if not paths:
        raise CommandError("rmdir: missing operand")
    for path in paths:
        _rmdir_one(session, path)
    return ""
