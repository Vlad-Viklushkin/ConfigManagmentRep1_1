"""Реестр команд эмулятора и простые команды."""

from typing import Callable, Dict, List

from shell_emulator.cmd_edit import cmd_rm, cmd_rmdir
from shell_emulator.cmd_nav import cmd_cd, cmd_ls
from shell_emulator.cmd_sys import cmd_uname
from shell_emulator.cmd_tree import cmd_tree
from shell_emulator.errors import CommandError, VfsError
from shell_emulator.session import Session
from shell_emulator.vfs_xml import load_vfs

Handler = Callable[[Session, List[str]], str]


def cmd_exit(session: Session, args: List[str]) -> str:
    """Команда `exit`: завершает работу эмулятора."""
    if args:
        raise CommandError("exit: too many arguments")
    session.running = False
    return ""


def cmd_vfs_info(session: Session, args: List[str]) -> str:
    """Служебная команда `vfs-info`: сведения о загруженной VFS."""
    if args:
        raise CommandError("vfs-info: too many arguments")
    if session.vfs is None:
        return "VFS: not loaded"
    dirs, files = session.vfs.stats()
    return "\n".join([
        f"VFS: {session.vfs.source}",
        f"Directories: {dirs}",
        f"Files: {files}",
    ])


def cmd_vfs_load(session: Session, args: List[str]) -> str:
    """Команда `vfs-load путь`: загружает новую VFS с диска.

    Текущая VFS заменяется, текущий каталог становится `/`. При ошибке
    прежняя VFS остаётся без изменений.
    """
    if not args:
        raise CommandError("vfs-load: missing path")
    if args[1:]:
        raise CommandError("vfs-load: too many arguments")
    try:
        vfs = load_vfs(args[0])
    except VfsError as error:
        raise CommandError(f"vfs-load: {error}")
    session.attach_vfs(vfs)
    dirs, files = vfs.stats()
    return f"VFS loaded: {args[0]} ({dirs} directories, {files} files)"


COMMANDS: Dict[str, Handler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "tree": cmd_tree,
    "uname": cmd_uname,
    "rm": cmd_rm,
    "rmdir": cmd_rmdir,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
    "vfs-load": cmd_vfs_load,
}
