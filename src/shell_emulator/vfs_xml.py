"""Загрузка VFS из XML-файла.

Формат::

    <vfs>
      <dir name="home">
        <file name="a.txt">text</file>
        <file name="b.bin" encoding="base64">AAEC</file>
      </dir>
    </vfs>

Корневой элемент `vfs` соответствует корню `/`. Вложенность каталогов
выражается вложенностью элементов `dir`. Содержимое файла — текст
(`encoding="text"`, по умолчанию) или base64 (`encoding="base64"`).
"""

import base64
import binascii
import xml.etree.ElementTree as ET
from typing import Callable, Dict

from shell_emulator.errors import VfsError
from shell_emulator.vfs import Vfs, VfsNode

ROOT_TAG = "vfs"
DIR_TAG = "dir"
FILE_TAG = "file"
ENC_TEXT = "text"
ENC_BASE64 = "base64"
FORBIDDEN_NAMES = ("", ".", "..")
PATH_SEPARATOR = "/"


def load_vfs(path: str) -> Vfs:
    """Читает XML-файл и строит VFS в памяти."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as error:
        raise VfsError(f"cannot read VFS '{path}': {error}")
    return parse_vfs(data, path)


def parse_vfs(data: bytes, source: str) -> Vfs:
    """Разбирает XML-данные и строит VFS."""
    try:
        root_element = ET.fromstring(data)
    except ET.ParseError as error:
        raise VfsError(f"invalid XML in '{source}': {error}")
    if root_element.tag != ROOT_TAG:
        raise VfsError(
            f"root element must be <{ROOT_TAG}>, got <{root_element.tag}>"
        )
    root = VfsNode(name=PATH_SEPARATOR, is_dir=True)
    _fill_directory(root, root_element)
    return Vfs(root=root, source=source)


def _fill_directory(node: VfsNode, element: ET.Element) -> None:
    """Рекурсивно добавляет в каталог потомков из XML-элемента."""
    for child in element:
        if child.tag == DIR_TAG:
            sub = VfsNode(name=_get_name(child), is_dir=True)
            _fill_directory(sub, child)
            node.add_child(sub)
        elif child.tag == FILE_TAG:
            node.add_child(_build_file(child))
        else:
            raise VfsError(f"unexpected element <{child.tag}>")


def _get_name(element: ET.Element) -> str:
    """Возвращает проверенное имя элемента."""
    name = element.get("name")
    if name is None:
        raise VfsError(f"<{element.tag}> without 'name' attribute")
    if name in FORBIDDEN_NAMES or PATH_SEPARATOR in name:
        raise VfsError(f"invalid name '{name}'")
    return name


def _build_file(element: ET.Element) -> VfsNode:
    """Создаёт узел-файл из элемента `file`."""
    if len(element):
        raise VfsError(f"<{FILE_TAG}> must not contain elements")
    name = _get_name(element)
    content = _decode_content(element, name)
    return VfsNode(name=name, is_dir=False, content=content)


def _decode_content(element: ET.Element, name: str) -> bytes:
    """Декодирует содержимое файла согласно атрибуту `encoding`."""
    encoding = element.get("encoding", ENC_TEXT)
    text = element.text or ""
    decoders: Dict[str, Callable[[], bytes]] = {
        ENC_TEXT: lambda: text.encode("utf-8"),
        ENC_BASE64: lambda: _decode_base64(text, name),
    }
    if encoding not in decoders:
        raise VfsError(f"unknown encoding '{encoding}' in '{name}'")
    return decoders[encoding]()


def _decode_base64(text: str, name: str) -> bytes:
    """Декодирует base64, игнорируя пробелы и переводы строк."""
    compact = "".join(text.split())
    try:
        return base64.b64decode(compact, validate=True)
    except (binascii.Error, ValueError):
        raise VfsError(f"invalid base64 in '{name}'")
