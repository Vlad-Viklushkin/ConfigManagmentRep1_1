"""Сквозные тесты работы эмулятора с VFS."""

import io
import os
import tempfile
import unittest
from pathlib import Path

from shell_emulator.cli import EXIT_OK, EXIT_SCRIPT_ERROR, EXIT_VFS_ERROR
from shell_emulator.cli import main
from shell_emulator.session import Session
from shell_emulator.errors import CommandError
from shell_emulator.shell import Shell
from shell_emulator.vfs_xml import load_vfs

ROOT = Path(__file__).resolve().parent.parent
VFS_DIR = ROOT / "examples" / "vfs"
SCRIPTS = ROOT / "examples" / "scripts"


def call(argv, text=""):
    """Вызывает main, возвращает (код, вывод)."""
    out = io.StringIO()
    code = main(argv, io.StringIO(text), out)
    return code, out.getvalue()


class VfsInfoTest(unittest.TestCase):
    """Проверки служебной команды vfs-info."""

    def test_not_loaded(self):
        """Без VFS команда сообщает, что она не загружена."""
        self.assertEqual(Shell(Session()).execute("vfs-info"),
                         "VFS: not loaded")

    def test_loaded(self):
        """С VFS команда показывает источник и счётчики."""
        vfs = load_vfs(str(VFS_DIR / "deep.xml"))
        out = Shell(Session(vfs=vfs)).execute("vfs-info")
        self.assertIn("Directories: 6", out)
        self.assertIn("Files: 4", out)

    def test_args(self):
        """Аргументы не допускаются."""
        with self.assertRaises(CommandError):
            Shell(Session()).execute("vfs-info x")


class MainVfsTest(unittest.TestCase):
    """Запуск эмулятора с разными VFS."""

    def test_variants(self):
        """Минимальная, с файлами и глубокая VFS загружаются."""
        expected = {
            "minimal.xml": "Directories: 0\nFiles: 0",
            "multi_files.xml": "Directories: 0\nFiles: 4",
            "deep.xml": "Directories: 6\nFiles: 4",
        }
        for name, counters in expected.items():
            path = str(VFS_DIR / name)
            code, out = call(["--vfs", path], "vfs-info\nexit\n")
            self.assertEqual(code, EXIT_OK)
            self.assertIn(counters, out)

    def test_missing_vfs(self):
        """Отсутствующий файл VFS — код EXIT_VFS_ERROR."""
        code, out = call(["--vfs", "/no/such.xml"])
        self.assertEqual(code, EXIT_VFS_ERROR)
        self.assertIn("error: cannot read VFS", out)

    def test_broken_vfs(self):
        """Некорректный XML — код EXIT_VFS_ERROR."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("<vfs>")
            code, out = call(["--vfs", path])
        self.assertEqual(code, EXIT_VFS_ERROR)
        self.assertIn("invalid XML", out)

    def test_full_script(self):
        """Полный стартовый скрипт выполняется без ошибок."""
        argv = ["--vfs", str(VFS_DIR / "deep.xml"), "--prompt", "vfs>",
                "--script", str(SCRIPTS / "stage3_full.emu")]
        code, out = call(argv)
        self.assertEqual(code, EXIT_OK)
        self.assertIn("vfs> cd /home/user\nvfs> cd\n", out)

    def test_error_script(self):
        """Скрипт с ошибкой в конце останавливается с кодом 1."""
        argv = ["--vfs", str(VFS_DIR / "multi_files.xml"),
                "--script", str(SCRIPTS / "stage3_error_end.emu")]
        code, out = call(argv)
        self.assertEqual(code, EXIT_SCRIPT_ERROR)
        self.assertIn("vfs-info: too many arguments", out)
        self.assertNotIn("never_printed\n", out.split("too many")[1])


if __name__ == "__main__":
    unittest.main()
