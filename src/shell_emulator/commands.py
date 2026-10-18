"""Реестр команд эмулятора и простые команды."""

from typing import Callable, Dict, List

from shell_emulator.cmd_nav import cmd_cd, cmd_ls
from shell_emulator.cmd_sys import cmd_uname
from shell_emulator.cmd_tree import cmd_tree
from shell_emulator.errors import CommandError
from shell_emulator.session import Session

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


COMMANDS: Dict[str, Handler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "tree": cmd_tree,
    "uname": cmd_uname,
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
