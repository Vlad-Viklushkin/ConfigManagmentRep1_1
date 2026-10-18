"""Модель виртуальной файловой системы, хранящейся в памяти."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from shell_emulator.errors import VfsError

SEP = "/"
ROOT_PATH = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."
EMPTY_SOURCE = "(empty)"
ERR_NOT_FOUND = "No such file or directory"
ERR_NOT_DIR = "Not a directory"


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

    def remove_child(self, name: str) -> None:
        """Удаляет потомка по имени."""
        del self.children[name]

    def size(self) -> int:
        """Размер файла в байтах; для каталога — 0."""
        return 0 if self.is_dir else len(self.content)

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


@dataclass(frozen=True)
class Resolved:
    """Результат разбора пути: абсолютный путь, узел и его родитель."""

    path: str
    node: VfsNode
    parent: Optional[VfsNode]


@dataclass
class Vfs:
    """Виртуальная файловая система: корневой каталог и источник."""

    root: VfsNode
    source: str

    def stats(self) -> Tuple[int, int]:
        """Возвращает (число каталогов, число файлов) без корня."""
        return self.root.count()

    def resolve(self, path: str, cwd: str = ROOT_PATH) -> Resolved:
        """Находит узел по абсолютному или относительному пути.

        Поддерживаются `.` и `..` (выше корня подняться нельзя).
        Бросает VfsError, если путь не существует или проходит
        через файл.
        """
        parts = [] if path.startswith(SEP) else cwd.split(SEP)
        parts += path.split(SEP)
        chain = [self.root]
        names: List[str] = []
        for part in parts:
            self._step(chain, names, part)
        parent = chain[-2] if names else None
        return Resolved(SEP + SEP.join(names), chain[-1], parent)

    def _step(
        self, chain: List[VfsNode], names: List[str], part: str
    ) -> None:
        """Выполняет один шаг разбора пути, изменяя chain и names."""
        if part in ("", CURRENT_DIR):
            return
        if not chain[-1].is_dir:
            raise VfsError(ERR_NOT_DIR)
        if part == PARENT_DIR:
            if names:
                chain.pop()
                names.pop()
            return
        child = chain[-1].children.get(part)
        if child is None:
            raise VfsError(ERR_NOT_FOUND)
        chain.append(child)
        names.append(part)


def empty_vfs() -> Vfs:
    """Создаёт пустую VFS (используется, если VFS не загружена)."""
    return Vfs(root=VfsNode(ROOT_PATH, is_dir=True), source=EMPTY_SOURCE)
