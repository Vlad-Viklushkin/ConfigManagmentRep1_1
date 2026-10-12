"""Тесты загрузки VFS из XML и модели VFS."""

import os
import tempfile
import unittest
from pathlib import Path

from shell_emulator.errors import VfsError
from shell_emulator.vfs import VfsNode
from shell_emulator.vfs_xml import load_vfs, parse_vfs

VFS_DIR = Path(__file__).resolve().parent.parent / "examples" / "vfs"
SOURCE = "test.xml"


def parse(xml: str):
    """Разбирает строку XML в VFS."""
    return parse_vfs(xml.encode("utf-8"), SOURCE)


class LoadExamplesTest(unittest.TestCase):
    """Загрузка примеров из examples/vfs."""

    def test_minimal(self):
        """Минимальная VFS — пустой корень."""
        vfs = load_vfs(str(VFS_DIR / "minimal.xml"))
        self.assertEqual(vfs.stats(), (0, 0))
        self.assertTrue(vfs.root.is_dir)

    def test_multi_files(self):
        """Несколько файлов: текст и base64."""
        vfs = load_vfs(str(VFS_DIR / "multi_files.xml"))
        self.assertEqual(vfs.stats(), (0, 4))
        children = vfs.root.children
        self.assertEqual(children["readme.txt"].content, b"Hello, VFS!")
        self.assertEqual(children["data.bin"].content, bytes(range(8)))
        self.assertEqual(children["empty.txt"].content, b"")

    def test_deep(self):
        """Не менее трёх уровней вложенности."""
        vfs = load_vfs(str(VFS_DIR / "deep.xml"))
        self.assertEqual(vfs.stats(), (6, 4))
        docs = vfs.root.children["home"].children["user"].children["docs"]
        old = docs.children["archive"].children["old.bin"]
        self.assertEqual(old.content, b"\xde\xad\xbe\xef")
        self.assertFalse(old.is_dir)

    def test_source_kept(self):
        """Источник VFS запоминается."""
        path = str(VFS_DIR / "minimal.xml")
        self.assertEqual(load_vfs(path).source, path)


class ParseTest(unittest.TestCase):
    """Разбор отдельных конструкций."""

    def test_utf8_text(self):
        """Текст хранится как UTF-8."""
        vfs = parse('<vfs><file name="a">Привет</file></vfs>')
        content = vfs.root.children["a"].content
        self.assertEqual(content.decode("utf-8"), "Привет")

    def test_base64_with_whitespace(self):
        """Пробелы и переводы строк в base64 игнорируются."""
        xml = '<vfs><file name="a" encoding="base64">AAEC\n AwQ=</file></vfs>'
        vfs = parse(xml)
        self.assertEqual(vfs.root.children["a"].content, bytes(range(5)))

    def test_explicit_text_encoding(self):
        """Кодировка text указывается явно."""
        vfs = parse('<vfs><file name="a" encoding="text">x</file></vfs>')
        self.assertEqual(vfs.root.children["a"].content, b"x")


class ErrorsTest(unittest.TestCase):
    """Некорректные входные данные приводят к VfsError."""

    def assert_error(self, xml: str, fragment: str):
        """Проверяет, что разбор падает с сообщением, содержащим фрагмент."""
        with self.assertRaises(VfsError) as ctx:
            parse(xml)
        self.assertIn(fragment, str(ctx.exception))

    def test_broken_xml(self):
        """Нарушенная разметка."""
        self.assert_error("<vfs><dir name='a'>", "invalid XML")

    def test_wrong_root(self):
        """Неверный корневой элемент."""
        self.assert_error("<root/>", "root element")

    def test_unexpected_element(self):
        """Неизвестный элемент."""
        self.assert_error("<vfs><link name='a'/></vfs>", "unexpected")

    def test_missing_name(self):
        """Нет атрибута name."""
        self.assert_error("<vfs><dir/></vfs>", "without 'name'")

    def test_invalid_names(self):
        """Недопустимые имена."""
        for name in ("", ".", "..", "a/b"):
            xml = f'<vfs><file name="{name}"/></vfs>'
            self.assert_error(xml, "invalid name")

    def test_duplicate_names(self):
        """Повтор имени в одном каталоге."""
        xml = '<vfs><file name="a"/><dir name="a"/></vfs>'
        self.assert_error(xml, "duplicate")

    def test_same_name_in_different_dirs(self):
        """Одинаковые имена в разных каталогах допустимы."""
        xml = '<vfs><dir name="d"><file name="a"/></dir><file name="a"/></vfs>'
        self.assertEqual(parse(xml).stats(), (1, 2))

    def test_file_with_children(self):
        """Файл не может содержать элементы."""
        self.assert_error(
            '<vfs><file name="a"><file name="b"/></file></vfs>',
            "must not contain",
        )

    def test_bad_base64(self):
        """Неверный base64."""
        xml = '<vfs><file name="a" encoding="base64">!!!</file></vfs>'
        self.assert_error(xml, "invalid base64")

    def test_unknown_encoding(self):
        """Неизвестная кодировка."""
        xml = '<vfs><file name="a" encoding="rot13">x</file></vfs>'
        self.assert_error(xml, "unknown encoding")

    def test_missing_file(self):
        """Файл не существует."""
        with self.assertRaises(VfsError):
            load_vfs("/no/such/vfs.xml")


class NodeTest(unittest.TestCase):
    """Проверки VfsNode."""

    def test_add_to_file(self):
        """В файл нельзя добавить потомка."""
        node = VfsNode("f", is_dir=False)
        with self.assertRaises(VfsError):
            node.add_child(VfsNode("x", is_dir=False))

    def test_no_disk_changes(self):
        """Загрузка не создаёт файлов на диске."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "v.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write('<vfs><file name="a">x</file></vfs>')
            load_vfs(path)
            self.assertEqual(os.listdir(tmp), ["v.xml"])


if __name__ == "__main__":
    unittest.main()
