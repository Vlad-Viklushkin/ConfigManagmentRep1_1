"""Тесты разбора путей и сеанса."""

import unittest

from helpers import make_shell
from shell_emulator.errors import VfsError
from shell_emulator.session import Session
from shell_emulator.vfs import ERR_NOT_DIR, ERR_NOT_FOUND, empty_vfs


class ResolveTest(unittest.TestCase):
    """Проверки Vfs.resolve."""

    def setUp(self):
        """Загружает глубокую VFS."""
        self.vfs = make_shell().session.vfs

    def test_root(self):
        """Корень разбирается и не имеет родителя."""
        res = self.vfs.resolve("/")
        self.assertEqual(res.path, "/")
        self.assertIsNone(res.parent)

    def test_absolute(self):
        """Абсолютный путь."""
        res = self.vfs.resolve("/home/user/docs")
        self.assertEqual(res.path, "/home/user/docs")
        self.assertTrue(res.node.is_dir)
        self.assertEqual(res.parent.name, "user")

    def test_relative(self):
        """Относительный путь от cwd."""
        res = self.vfs.resolve("docs/report.txt", "/home/user")
        self.assertEqual(res.path, "/home/user/docs/report.txt")
        self.assertFalse(res.node.is_dir)

    def test_dots(self):
        """`.` и `..` обрабатываются, выше корня не поднимаемся."""
        res = self.vfs.resolve("./../.././etc", "/home/user")
        self.assertEqual(res.path, "/etc")
        self.assertEqual(self.vfs.resolve("../../..").path, "/")

    def test_extra_slashes(self):
        """Повторные и завершающие слэши игнорируются."""
        res = self.vfs.resolve("//home///user/")
        self.assertEqual(res.path, "/home/user")

    def test_not_found(self):
        """Несуществующий путь."""
        with self.assertRaises(VfsError) as ctx:
            self.vfs.resolve("/home/nobody")
        self.assertEqual(str(ctx.exception), ERR_NOT_FOUND)

    def test_through_file(self):
        """Путь через файл — не каталог."""
        for path in ("/etc/hostname/x", "/etc/hostname/.."):
            with self.assertRaises(VfsError) as ctx:
                self.vfs.resolve(path)
            self.assertEqual(str(ctx.exception), ERR_NOT_DIR)


class SessionTest(unittest.TestCase):
    """Проверки Session."""

    def test_fallback_vfs(self):
        """Без VFS используется пустая."""
        session = Session()
        self.assertEqual(session.active_vfs().stats(), (0, 0))
        self.assertIsNone(session.vfs)

    def test_attach_resets_cwd(self):
        """Подключение VFS переводит в корень."""
        session = Session(cwd="/somewhere")
        session.attach_vfs(empty_vfs())
        self.assertEqual(session.cwd, "/")

    def test_is_busy(self):
        """Текущий каталог и его предки заняты."""
        session = Session(cwd="/a/b")
        self.assertTrue(session.is_busy("/a/b"))
        self.assertTrue(session.is_busy("/a"))
        self.assertTrue(session.is_busy("/"))
        self.assertFalse(session.is_busy("/a/c"))
        self.assertFalse(session.is_busy("/a/bc"))


if __name__ == "__main__":
    unittest.main()
