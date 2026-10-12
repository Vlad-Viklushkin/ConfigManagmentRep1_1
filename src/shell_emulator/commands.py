"""Реализация команд эмулятора."""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from shell_emulator.errors import CommandError
from shell_emulator.vfs import Vfs


@dataclass
class Session:
    """Состояние сеанса эмулятора."""

    running: bool = True
    vfs: Optional[Vfs] = None


Handler = Callable[[Session, List[str]], str]


def _stub(name: str, args: List[str]) -> str:
    """Формирует вывод заглушки: имя команды и её аргументы."""
    return " ".join([name] + args)


def cmd_ls(session: Session, args: List[str]) -> str:
    """Команда-заглушка `ls`: выводит своё имя и аргументы."""
    return _stub("ls", args)


def cmd_cd(session: Session, args: List[str]) -> str:
    """Команда-заглушка `cd`: выводит своё имя и аргументы."""
    return _stub("cd", args)


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
    "exit": cmd_exit,
    "vfs-info": cmd_vfs_info,
}
