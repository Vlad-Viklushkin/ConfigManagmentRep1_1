"""Вспомогательные функции для тестов."""

from pathlib import Path

from shell_emulator.session import Session
from shell_emulator.shell import Shell
from shell_emulator.vfs_xml import load_vfs

ROOT = Path(__file__).resolve().parent.parent
VFS_DIR = ROOT / "examples" / "vfs"
SCRIPTS = ROOT / "examples" / "scripts"


def make_shell(vfs_name: str = "deep.xml") -> Shell:
    """Создаёт оболочку с VFS из examples/vfs; без имени — пустая."""
    session = Session()
    if vfs_name:
        session.attach_vfs(load_vfs(str(VFS_DIR / vfs_name)))
    return Shell(session)
