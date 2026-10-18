"""Тесты команды vfs-load и скриптов этапа 5."""

import contextlib
import io
import os
import tempfile
import unittest

from helpers import ROOT, SCRIPTS, VFS_DIR, make_shell
from shell_emulator.cli import EXIT_OK, EXIT_SCRIPT_ERROR, main
from shell_emulator.errors import CommandError

MULTI = str(VFS_DIR / "multi_files.xml")


class VfsLoadTest(unittest.TestCase):
    """Проверки vfs-load."""

    def __init__(self, *args, **kwargs):
        """Оболочка с глубокой VFS."""
        super().__init__(*args, **kwargs)
        self.shell = make_shell()
        self.session = self.shell.session

    def fail(self, line):
        """Выполняет команду, ожидая ошибку, возвращает её текст."""
        with self.assertRaises(CommandError) as ctx:
            self.shell.execute(line)
        return str(ctx.exception)

    def test_load_replaces_vfs(self):
        """Новая VFS заменяет текущую."""
        out = self.shell.execute(f"vfs-load {MULTI}")
        self.assertEqual(out, f"VFS loaded: {MULTI} (0 directories, 4 files)")
        self.assertEqual(self.session.vfs.source, MULTI)
        self.assertIn("readme.txt", self.shell.execute("ls"))
        self.assertNotIn("home", self.shell.execute("ls"))

    def test_load_resets_cwd(self):
        """Текущий каталог становится корнем."""
        self.shell.execute("cd /home/user")
        self.shell.execute(f"vfs-load {MULTI}")
        self.assertEqual(self.session.cwd, "/")

    def test_load_without_initial_vfs(self):
        """vfs-load работает и без стартовой VFS."""
        shell = make_shell("")
        shell.execute(f"vfs-load {MULTI}")
        self.assertIn("Files: 4", shell.execute("vfs-info"))

    def test_reload_restores_removed(self):
        """Повторная загрузка возвращает удалённые файлы."""
        self.shell.execute("rm -r /home")
        self.shell.execute(f"vfs-load {VFS_DIR / 'deep.xml'}")
        self.assertEqual(self.shell.execute("ls"), "etc\nhome\ntmp")

    def test_errors(self):
        """Ошибки vfs-load; прежняя VFS сохраняется."""
        old_source = self.session.vfs.source
        self.assertEqual(self.fail("vfs-load"), "vfs-load: missing path")
        self.assertEqual(
            self.fail("vfs-load a b"), "vfs-load: too many arguments"
        )
        self.assertIn("cannot read VFS", self.fail("vfs-load /no/such.xml"))
        self.assertEqual(self.session.vfs.source, old_source)

    def test_broken_file_keeps_old(self):
        """Некорректный XML не заменяет текущую VFS."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("<vfs><dir>")
            self.assertIn("invalid XML", self.fail(f"vfs-load {path}"))
        self.assertEqual(self.shell.execute("ls"), "etc\nhome\ntmp")


@contextlib.contextmanager
def repo_root_cwd():
    """Временно переходит в корень репозитория."""
    old = os.getcwd()
    os.chdir(ROOT)
    try:
        yield
    finally:
        os.chdir(old)


class Stage5ScriptsTest(unittest.TestCase):
    """Стартовые скрипты этапа 5 (запускаются из корня репозитория)."""

    def call(self, script):
        """Запускает скрипт с deep.xml, возвращает (код, вывод)."""
        out = io.StringIO()
        argv = ["--vfs", str(VFS_DIR / "deep.xml"), "--prompt", "vfs>",
                "--script", str(SCRIPTS / script)]
        with repo_root_cwd():
            code = main(argv, io.StringIO(), out)
        return code, out.getvalue()

    def test_all_modes(self):
        """Скрипт со всеми режимами команд выполняется без ошибок."""
        code, out = self.call("stage5_commands.emu")
        self.assertEqual(code, EXIT_OK)
        self.assertIn("vfs> rm -r /home/user/docs/archive\n", out)
        self.assertIn("VFS loaded: examples/vfs/multi_files.xml", out)

    def test_error_stops_script(self):
        """Ошибка останавливает скрипт."""
        code, out = self.call("stage5_error_end.emu")
        self.assertEqual(code, EXIT_SCRIPT_ERROR)
        self.assertIn("Directory not empty", out)
        self.assertNotIn("never_printed\n", out.split("not empty")[1])


if __name__ == "__main__":
    unittest.main()
