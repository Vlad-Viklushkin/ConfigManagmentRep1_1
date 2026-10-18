"""Тесты команд tree и uname."""

import platform
import unittest
from unittest import mock

from helpers import make_shell
from shell_emulator.errors import CommandError

TREE_ROOT = """.
├── etc
│   └── hostname
├── home
│   └── user
│       └── docs
│           ├── archive
│           │   └── old.bin
│           └── report.txt
└── tmp

6 directories, 3 files"""

FAKE_INFO = platform.uname_result(
    "Linux", "myhost", "6.1.0", "#1 SMP", "x86_64"
)


class TreeTest(unittest.TestCase):
    """Проверки tree."""

    def __init__(self, *args, **kwargs):
        """Оболочка с глубокой VFS."""
        super().__init__(*args, **kwargs)
        self.shell = make_shell()

    def test_root(self):
        """Дерево от текущего каталога."""
        self.assertEqual(self.shell.execute("tree"), TREE_ROOT)

    def test_all(self):
        """-a показывает скрытые файлы."""
        out = self.shell.execute("tree -a /home")
        self.assertIn("├── .profile", out)
        self.assertTrue(out.endswith("3 directories, 3 files"))

    def test_subdir(self):
        """Дерево подкаталога; корень подписан как в аргументе."""
        out = self.shell.execute("tree /home/user/docs/archive")
        self.assertEqual(
            out,
            "/home/user/docs/archive\n└── old.bin\n\n0 directories, 1 file",
        )

    def test_empty_dir(self):
        """Пустой каталог."""
        self.assertEqual(
            self.shell.execute("tree tmp"), "tmp\n\n0 directories, 0 files"
        )

    def test_minimal_vfs(self):
        """Дерево пустой VFS."""
        shell = make_shell("minimal.xml")
        self.assertEqual(shell.execute("tree"), ".\n\n0 directories, 0 files")

    def test_relative(self):
        """Относительный путь от текущего каталога."""
        self.shell.execute("cd /home")
        out = self.shell.execute("tree user")
        self.assertTrue(out.startswith("user\n└── docs"))

    def test_errors(self):
        """Ошибки tree."""
        messages = {
            "tree /nope": "tree: /nope: No such file or directory",
            "tree /etc/hostname": "tree: /etc/hostname: Not a directory",
            "tree a b": "tree: too many arguments",
            "tree -x": "tree: invalid option -- 'x'",
        }
        for line, message in messages.items():
            with self.assertRaises(CommandError) as ctx:
                self.shell.execute(line)
            self.assertEqual(str(ctx.exception), message)


@mock.patch("platform.uname", new=lambda: FAKE_INFO)
class UnameTest(unittest.TestCase):
    """Проверки uname."""

    def __init__(self, *args, **kwargs):
        """Создаёт оболочку без VFS."""
        super().__init__(*args, **kwargs)
        self.shell = make_shell("")

    def test_default(self):
        """Без опций — имя системы."""
        self.assertEqual(self.shell.execute("uname"), "Linux")

    def test_single_options(self):
        """Отдельные опции."""
        expected = {
            "-s": "Linux", "-n": "myhost", "-r": "6.1.0",
            "-v": "#1 SMP", "-m": "x86_64",
        }
        for option, value in expected.items():
            self.assertEqual(self.shell.execute(f"uname {option}"), value)

    def test_all(self):
        """-a — все поля."""
        self.assertEqual(
            self.shell.execute("uname -a"),
            "Linux myhost 6.1.0 #1 SMP x86_64",
        )

    def test_combined_in_fixed_order(self):
        """Опции объединяются, порядок полей фиксирован."""
        self.assertEqual(self.shell.execute("uname -mn"), "myhost x86_64")

    def test_errors(self):
        """Ошибки uname."""
        for line, message in {
            "uname -z": "uname: invalid option -- 'z'",
            "uname foo": "uname: extra operand 'foo'",
        }.items():
            with self.assertRaises(CommandError) as ctx:
                self.shell.execute(line)
            self.assertEqual(str(ctx.exception), message)


class UnameRealDataTest(unittest.TestCase):
    """Проверка данных реальной ОС (без подмены)."""

    def test_real_data(self):
        """Без подмены берутся данные реальной ОС."""
        shell = make_shell("")
        self.assertEqual(shell.execute("uname"), platform.system())


if __name__ == "__main__":
    unittest.main()
