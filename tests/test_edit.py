"""Тесты команд rm и rmdir."""

import unittest

from helpers import VFS_DIR, make_shell
from shell_emulator.errors import CommandError

BUSY = "Device or resource busy"


class EditTestCase(unittest.TestCase):
    """Базовый класс с оболочкой и вспомогательными методами."""

    def setUp(self):
        """Оболочка со свежей копией глубокой VFS."""
        self.shell = make_shell()

    def run_ok(self, line):
        """Выполняет команду и возвращает вывод."""
        return self.shell.execute(line)

    def fail(self, line):
        """Выполняет команду, ожидая ошибку, возвращает её текст."""
        with self.assertRaises(CommandError) as ctx:
            self.shell.execute(line)
        return str(ctx.exception)


class RmTest(EditTestCase):
    """Проверки rm."""

    def test_remove_file(self):
        """Удаление файла по абсолютному пути."""
        self.assertEqual(self.run_ok("rm /etc/hostname"), "")
        self.assertEqual(self.run_ok("ls /etc"), "")

    def test_remove_relative(self):
        """Удаление по относительному пути."""
        self.run_ok("cd /home/user/docs")
        self.run_ok("rm report.txt")
        self.assertEqual(self.run_ok("ls"), "archive")

    def test_remove_several(self):
        """Несколько операндов."""
        self.run_ok("rm /etc/hostname /home/user/.profile")
        self.assertEqual(self.run_ok("ls -a /home/user"), "docs")

    def test_dir_without_r(self):
        """Каталог без -r не удаляется."""
        self.assertEqual(
            self.fail("rm /home"),
            "rm: cannot remove '/home': Is a directory",
        )
        self.assertEqual(self.run_ok("ls /home"), "user")

    def test_recursive(self):
        """rm -r удаляет каталог с содержимым; -R — синоним."""
        self.run_ok("rm -r /home/user/docs")
        self.assertEqual(self.run_ok("ls /home/user"), "")
        self.run_ok("rm -R /home")
        self.assertEqual(self.run_ok("ls"), "etc\ntmp")

    def test_force(self):
        """-f игнорирует несуществующие пути и отсутствие операндов."""
        self.assertEqual(self.run_ok("rm -f /nothing"), "")
        self.assertEqual(self.run_ok("rm -rf /nothing /tmp"), "")
        self.assertEqual(self.run_ok("rm -f"), "")
        self.assertEqual(self.run_ok("ls"), "etc\nhome")

    def test_force_does_not_hide_dir_error(self):
        """-f без -r всё равно не удаляет каталог."""
        self.assertIn("Is a directory", self.fail("rm -f /home"))

    def test_errors(self):
        """Ошибки rm."""
        messages = {
            "rm /nothing": "rm: cannot remove '/nothing': "
                           "No such file or directory",
            "rm": "rm: missing operand",
            "rm -z x": "rm: invalid option -- 'z'",
            "rm -r /": "rm: it is dangerous to operate recursively on '/'",
        }
        for line, message in messages.items():
            self.assertEqual(self.fail(line), message)

    def test_busy(self):
        """Нельзя удалить текущий каталог и его предков."""
        self.run_ok("cd /home/user")
        for line in ("rm -r .", "rm -r /home/user", "rm -r /home", "rm -r .."):
            self.assertIn(BUSY, self.fail(line))
        self.assertEqual(self.run_ok("ls /home"), "user")

    def test_stops_at_first_error(self):
        """Операнды до ошибки удалены, остальные остаются."""
        self.fail("rm /etc/hostname /nothing /home/user/.profile")
        self.assertEqual(self.run_ok("ls /etc"), "")
        self.assertEqual(self.run_ok("ls -a /home/user"), ".profile\ndocs")

    def test_double_dash(self):
        """После -- имена, начинающиеся с -, считаются путями."""
        self.assertIn("No such file", self.fail("rm -- -a"))


class RmdirTest(EditTestCase):
    """Проверки rmdir."""

    def test_remove_empty(self):
        """Пустой каталог удаляется."""
        self.assertEqual(self.run_ok("rmdir /tmp"), "")
        self.assertEqual(self.run_ok("ls"), "etc\nhome")

    def test_several(self):
        """Несколько каталогов; каталог пустеет после rm."""
        self.run_ok("rm /etc/hostname")
        self.run_ok("rmdir /tmp /etc")
        self.assertEqual(self.run_ok("ls"), "home")

    def test_nested_bottom_up(self):
        """Вложенные каталоги удаляются снизу вверх."""
        self.run_ok("rm /home/user/docs/archive/old.bin")
        self.run_ok("rmdir /home/user/docs/archive")
        self.assertEqual(self.run_ok("ls /home/user/docs"), "report.txt")

    def test_errors(self):
        """Ошибки rmdir."""
        messages = {
            "rmdir /home": "rmdir: failed to remove '/home': "
                           "Directory not empty",
            "rmdir /etc/hostname": "rmdir: failed to remove "
                                   "'/etc/hostname': Not a directory",
            "rmdir /nothing": "rmdir: failed to remove '/nothing': "
                              "No such file or directory",
            "rmdir": "rmdir: missing operand",
            "rmdir -x": "rmdir: invalid option -- 'x'",
        }
        for line, message in messages.items():
            self.assertEqual(self.fail(line), message)

    def test_busy_cwd(self):
        """Текущий каталог удалить нельзя."""
        self.run_ok("cd /tmp")
        self.assertIn(BUSY, self.fail("rmdir ."))
        self.assertIn(BUSY, self.fail("rmdir /tmp"))

    def test_root(self):
        """Пустой корень удалить нельзя."""
        shell = make_shell("minimal.xml")
        with self.assertRaises(CommandError) as ctx:
            shell.execute("rmdir /")
        self.assertIn(BUSY, str(ctx.exception))


class InMemoryTest(EditTestCase):
    """Изменения происходят только в памяти."""

    def test_file_on_disk_unchanged(self):
        """XML-файл VFS не меняется после удалений."""
        path = VFS_DIR / "deep.xml"
        before = path.read_bytes()
        self.run_ok("rm -r /home")
        self.run_ok("rmdir /tmp")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(make_shell().execute("ls"), "etc\nhome\ntmp")


if __name__ == "__main__":
    unittest.main()
