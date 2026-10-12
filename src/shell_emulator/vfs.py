"""Модель виртуальной файловой системы, хранящейся в памяти."""

from dataclasses import dataclass, field
from typing import Dict, Tuple

from shell_emulator.errors import VfsError


@dataclass
class VfsNode:
    """Узел VFS: каталог (с потомками) или файл (с содержимым)."""

    name: str
    is_dir: bool
    children: Dict[str, "VfsNode"] = field(default_factory=dict)
    content: bytes = b""

    def add_child(self, node: "VfsNode") -> None:
        """Добавляет потомка в каталог; имена в каталоге уникальны."""
        if not self.is_dir:
            raise VfsError(f"'{self.name}' is not a directory")
        if node.name in self.children:
            raise VfsError(
                f"duplicate name '{node.name}' in '{self.name}'"
            )
        self.children[node.name] = node

    def count(self) -> Tuple[int, int]:
        """Возвращает (число каталогов, число файлов) среди потомков."""
        dirs = 0
        files = 0
        for child in self.children.values():
            if child.is_dir:
                dirs += 1
            else:
                files += 1
            sub_dirs, sub_files = child.count()
            dirs += sub_dirs
            files += sub_files
        return dirs, files


@dataclass
class Vfs:
    """Виртуальная файловая система: корневой каталог и источник."""

    root: VfsNode
    source: str

    def stats(self) -> Tuple[int, int]:
        """Возвращает (число каталогов, число файлов) без корня."""
        return self.root.count()
