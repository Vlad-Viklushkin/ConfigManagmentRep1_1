"""Команда tree: вывод дерева каталогов."""

from dataclasses import dataclass
from typing import List

from shell_emulator.cmd_util import lookup, parse_options, visible_names
from shell_emulator.errors import CommandError
from shell_emulator.session import Session
from shell_emulator.vfs import ERR_NOT_DIR, CURRENT_DIR, VfsNode

TREE_ERROR = "tree: {path}: {reason}"
BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
BLANK = "    "
SINGULAR_COUNT = 1


@dataclass
class Counter:
    """Счётчики каталогов и файлов в выводе tree."""

    dirs: int = 0
    files: int = 0


def _plural(count: int, one: str, many: str) -> str:
    """Возвращает форму слова для числа: `1 file`, `2 files`."""
    return f"{count} {one if count == SINGULAR_COUNT else many}"


def _render(
    node: VfsNode,
    prefix: str,
    show_all: bool,
    counter: Counter,
    lines: List[str],
) -> None:
    """Рекурсивно добавляет в lines строки дерева для потомков узла."""
    names = visible_names(node, show_all)
    for index, name in enumerate(names):
        child = node.children[name]
        last = index == len(names) - 1
        lines.append(prefix + (LAST_BRANCH if last else BRANCH) + name)
        if child.is_dir:
            counter.dirs += 1
            extension = BLANK if last else PIPE
            _render(child, prefix + extension, show_all, counter, lines)
        else:
            counter.files += 1


def cmd_tree(session: Session, args: List[str]) -> str:
    """Команда `tree [-a] [путь]`: дерево каталога и итоговые счётчики."""
    flags, paths = parse_options(args, "a", "tree")
    if paths[1:]:
        raise CommandError("tree: too many arguments")
    path = paths[0] if paths else CURRENT_DIR
    target = lookup(session, path, TREE_ERROR)
    if not target.node.is_dir:
        raise CommandError(f"tree: {path}: {ERR_NOT_DIR}")
    counter = Counter()
    lines = [path]
    _render(target.node, "", "a" in flags, counter, lines)
    summary = "{}, {}".format(
        _plural(counter.dirs, "directory", "directories"),
        _plural(counter.files, "file", "files"),
    )
    return "\n".join(lines + ["", summary])
