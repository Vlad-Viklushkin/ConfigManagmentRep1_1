"""Состояние сеанса эмулятора."""

from dataclasses import dataclass, field
from typing import Optional

from shell_emulator.vfs import ROOT_PATH, SEP, Vfs, empty_vfs


@dataclass
class Session:
    """Состояние сеанса: признак работы, VFS и текущий каталог."""

    running: bool = True
    vfs: Optional[Vfs] = None
    cwd: str = ROOT_PATH
    fallback: Vfs = field(default_factory=empty_vfs, repr=False)

    def active_vfs(self) -> Vfs:
        """Возвращает загруженную VFS или пустую, если VFS не загружена."""
        return self.fallback if self.vfs is None else self.vfs

    def attach_vfs(self, vfs: Vfs) -> None:
        """Подключает новую VFS и переходит в её корень."""
        self.vfs = vfs
        self.cwd = ROOT_PATH

    def is_busy(self, path: str) -> bool:
        """Истина, если path — текущий каталог или один из его предков."""
        prefix = path.rstrip(SEP) + SEP
        return self.cwd == path or self.cwd.startswith(prefix)
